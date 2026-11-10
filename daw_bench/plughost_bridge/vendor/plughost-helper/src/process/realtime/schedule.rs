//! The realtime worker's scheduling, for as long as it runs. On macOS the worker takes the
//! time-constraint policy for its quantum, joins a workgroup interval of its own, which it starts
//! and finishes around each quantum, and holds a latency-critical activity that keeps App Nap away
//! from the helper. On Windows it joins the MMCSS "Pro Audio" task. Each is undone when the worker
//! stops. A part the system refuses leaves the worker as it was and is reported in the helper's
//! diagnostics.

use std::time::Duration;

use plughost_core::ipc::shared::clock;

use crate::Responder;

/// The worker's scheduling, undone on drop.
pub(super) struct Schedule {
    /// Each quantum's deadline after its submission, in [`clock`] ticks.
    deadline: u64,
    platform: platform::Schedule,
}

impl Schedule {
    /// Schedules the calling thread for quanta of `quantum` that must complete within
    /// `deadline` ticks of their submission.
    pub fn enter(quantum: Duration, deadline: u64, responder: &Responder) -> Schedule {
        Schedule {
            deadline,
            platform: platform::Schedule::enter(clock::ticks(quantum), responder),
        }
    }

    /// Marks the work on a quantum submitted at `submitted_at` until the returned guard drops.
    pub fn interval(&self, submitted_at: u64) -> Interval<'_> {
        Interval {
            started: self
                .platform
                .start(submitted_at, submitted_at.saturating_add(self.deadline)),
            schedule: self,
        }
    }
}

/// One quantum's work.
pub(super) struct Interval<'a> {
    schedule: &'a Schedule,
    started: bool,
}

impl Drop for Interval<'_> {
    fn drop(&mut self) {
        if self.started {
            self.schedule.platform.finish();
        }
    }
}

#[cfg(target_os = "macos")]
mod platform {
    use std::ffi::{c_char, c_int, c_void};

    use objc2::rc::Retained;
    use objc2::runtime::{NSObjectProtocol, ProtocolObject};
    use objc2_foundation::{NSActivityOptions, NSProcessInfo, NSString};

    use crate::Responder;
    use crate::errors::{REALTIME_TIME_CONSTRAINT, REALTIME_WORKGROUP};

    const OS_CLOCK_MACH_ABSOLUTE_TIME: u32 = 32;
    const WORKGROUP_NAME: &std::ffi::CStr = c"plughost realtime";
    const ACTIVITY_REASON: &str = "plughost realtime processing";

    /// `os_workgroup_join_token_s` on 64-bit targets.
    #[repr(C)]
    struct JoinToken {
        sig: u32,
        opaque: [u8; 36],
    }

    #[link(name = "AudioToolbox", kind = "framework")]
    unsafe extern "C" {
        fn AudioWorkIntervalCreate(
            name: *const c_char,
            clock: u32,
            attr: *const c_void,
        ) -> *mut c_void;
    }

    unsafe extern "C" {
        fn os_workgroup_join(workgroup: *mut c_void, token: *mut JoinToken) -> c_int;
        fn os_workgroup_leave(workgroup: *mut c_void, token: *mut JoinToken);
        fn os_workgroup_interval_start(
            workgroup: *mut c_void,
            start: u64,
            deadline: u64,
            data: *mut c_void,
        ) -> c_int;
        fn os_workgroup_interval_finish(workgroup: *mut c_void, data: *mut c_void) -> c_int;
        fn os_release(object: *mut c_void);
    }

    /// The joined workgroup interval and its join token.
    struct Workgroup {
        interval: *mut c_void,
        token: JoinToken,
        /// This helper created the interval, so it starts and finishes it around each quantum.
        /// A shared workgroup (the engine's audio device's) is driven by its IO thread instead.
        owned: bool,
    }

    pub struct Schedule {
        workgroup: Option<Workgroup>,
        activity: Retained<ProtocolObject<dyn NSObjectProtocol>>,
    }

    impl Schedule {
        pub fn enter(quantum: u64, responder: &Responder) -> Schedule {
            if !time_constraint(quantum) {
                responder.warn(REALTIME_TIME_CONSTRAINT);
            }
            // serum_llm extension: with PLUGHOST_WORKGROUP_SERVICE set, join the engine's audio
            // device workgroup (served over Mach by the engine) instead of creating an interval
            // of our own. One interval per helper goes through coreaudiod, and at hundreds of
            // helpers that made start-up take over an hour and stalled the device.
            let workgroup = match std::env::var("PLUGHOST_WORKGROUP_SERVICE") {
                Ok(service) => match shared::join(&service) {
                    Ok(workgroup) => {
                        shared::log("shared");
                        Some(workgroup)
                    }
                    Err(error) => {
                        shared::log(&format!("own (shared failed: {error})"));
                        join()
                    }
                },
                Err(_) => join(),
            };
            if workgroup.is_none() {
                responder.warn(REALTIME_WORKGROUP);
            }
            let options = NSActivityOptions::LatencyCritical
                | NSActivityOptions::UserInitiatedAllowingIdleSystemSleep;
            let activity = NSProcessInfo::processInfo()
                .beginActivityWithOptions_reason(options, &NSString::from_str(ACTIVITY_REASON));
            Schedule {
                workgroup,
                activity,
            }
        }

        /// Starts a workgroup interval; whether it started.
        pub fn start(&self, start: u64, deadline: u64) -> bool {
            self.workgroup.as_ref().filter(|workgroup| workgroup.owned).is_some_and(|workgroup| {
                // SAFETY: this thread joined the interval, which lives until `self` drops.
                unsafe {
                    os_workgroup_interval_start(
                        workgroup.interval,
                        start,
                        deadline,
                        std::ptr::null_mut(),
                    ) == 0
                }
            })
        }

        pub fn finish(&self) {
            if let Some(workgroup) = self.workgroup.as_ref().filter(|workgroup| workgroup.owned) {
                // SAFETY: as in `start`, after an interval started.
                unsafe { os_workgroup_interval_finish(workgroup.interval, std::ptr::null_mut()) };
            }
        }
    }

    impl Drop for Schedule {
        fn drop(&mut self) {
            if let Some(mut workgroup) = self.workgroup.take() {
                // SAFETY: this thread joined the interval with `token`; leaving releases nothing
                // else, and the interval's own reference is released last.
                unsafe {
                    os_workgroup_leave(workgroup.interval, &mut workgroup.token);
                    os_release(workgroup.interval);
                }
            }
            // SAFETY: the activity came from `beginActivityWithOptions_reason`.
            unsafe { NSProcessInfo::processInfo().endActivity(&self.activity) };
            default_policy();
        }
    }

    /// Takes the time-constraint policy for periods of `quantum` ticks, of which the work may
    /// take half; whether the system granted it.
    fn time_constraint(quantum: u64) -> bool {
        let quantum = u32::try_from(quantum).unwrap_or(u32::MAX);
        let mut policy = libc::thread_time_constraint_policy {
            period: quantum,
            computation: quantum / 2,
            constraint: quantum,
            preemptible: 1,
        };
        set_policy(
            libc::THREAD_TIME_CONSTRAINT_POLICY,
            (&raw mut policy).cast(),
            libc::THREAD_TIME_CONSTRAINT_POLICY_COUNT,
        )
    }

    /// Returns the thread to the standard policy.
    fn default_policy() {
        let mut policy = libc::thread_standard_policy { no_data: 0 };
        set_policy(
            libc::THREAD_STANDARD_POLICY,
            (&raw mut policy).cast(),
            libc::THREAD_STANDARD_POLICY_COUNT as u32,
        );
    }

    fn set_policy(flavor: c_int, policy: libc::thread_policy_t, count: u32) -> bool {
        // SAFETY: `policy` points to `count` words of the flavor's policy, for this thread.
        unsafe {
            libc::thread_policy_set(
                libc::pthread_mach_thread_np(libc::pthread_self()),
                flavor as u32,
                policy,
                count,
            ) == libc::KERN_SUCCESS
        }
    }

    /// Creates a workgroup interval on the mach clock and joins it.
    fn join() -> Option<Workgroup> {
        // SAFETY: the name is a static C string and the attributes default.
        let interval = unsafe {
            AudioWorkIntervalCreate(
                WORKGROUP_NAME.as_ptr(),
                OS_CLOCK_MACH_ABSOLUTE_TIME,
                std::ptr::null(),
            )
        };
        if interval.is_null() {
            return None;
        }
        let mut workgroup = Workgroup {
            interval,
            token: JoinToken {
                sig: 0,
                opaque: [0; 36],
            },
            owned: true,
        };
        // SAFETY: a valid interval, and a token of the size the system expects.
        if unsafe { os_workgroup_join(workgroup.interval, &mut workgroup.token) } != 0 {
            // SAFETY: the interval was created retained and is not used again.
            unsafe { os_release(workgroup.interval) };
            return None;
        }
        Some(workgroup)
    }

    /// serum_llm extension (not upstream plughost): joining the engine's audio device workgroup.
    /// The engine serves the workgroup's Mach port (os_workgroup_copy_port) from a bootstrap
    /// service; the helper inherits the service's name in PLUGHOST_WORKGROUP_SERVICE, asks for
    /// the port with one Mach request/reply, and joins with os_workgroup_create_with_port.
    pub(super) mod shared {
        use std::ffi::{CString, c_char, c_int, c_void};
        use std::io::Write;

        use super::{JoinToken, Workgroup, os_release, os_workgroup_join};

        type MachPort = u32;

        /// `mach_msg_header_t`.
        #[repr(C)]
        #[derive(Clone, Copy)]
        pub(crate) struct Header {
            pub bits: u32,
            pub size: u32,
            pub remote: MachPort,
            pub local: MachPort,
            pub voucher: MachPort,
            pub id: i32,
        }

        /// `mach_msg_port_descriptor_t` (64-bit): name, pad1, then pad2:16 disposition:8 type:8.
        #[repr(C, packed(4))]
        #[derive(Clone, Copy)]
        pub(crate) struct PortDescriptor {
            pub name: MachPort,
            pub pad1: u32,
            pub pad2: u16,
            pub disposition: u8,
            pub kind: u8,
        }

        /// The engine's reply: a complex message carrying one port.
        #[repr(C, packed(4))]
        #[derive(Clone, Copy)]
        pub(crate) struct Reply {
            pub header: Header,
            pub descriptor_count: u32,
            pub port: PortDescriptor,
        }

        #[repr(C, align(8))]
        struct Buffer([u8; 512]);

        const MACH_SEND_MSG: c_int = 0x1;
        const MACH_RCV_MSG: c_int = 0x2;
        const MACH_SEND_TIMEOUT: c_int = 0x10;
        const MACH_RCV_TIMEOUT: c_int = 0x100;
        const MACH_MSG_TYPE_COPY_SEND: u32 = 19;
        const MACH_MSG_TYPE_MAKE_SEND_ONCE: u32 = 21;
        const MACH_MSGH_BITS_COMPLEX: u32 = 0x8000_0000;
        const MACH_PORT_RIGHT_RECEIVE: u32 = 1;
        /// The request's msgh_id ("PHWG"); the engine answers only this.
        pub(crate) const REQUEST_ID: i32 = 0x5048_5747;

        unsafe extern "C" {
            static bootstrap_port: MachPort;
            static mach_task_self_: MachPort;
            fn bootstrap_look_up(bp: MachPort, name: *const c_char, service: *mut MachPort) -> c_int;
            fn mach_reply_port() -> MachPort;
            fn mach_msg(msg: *mut Header, option: c_int, send_size: u32, rcv_size: u32, rcv_name: MachPort,
                        timeout: u32, notify: MachPort) -> c_int;
            fn mach_port_deallocate(task: MachPort, name: MachPort) -> c_int;
            fn mach_port_mod_refs(task: MachPort, name: MachPort, right: u32, delta: i32) -> c_int;
            fn os_workgroup_create_with_port(name: *const c_char, port: MachPort) -> *mut c_void;
        }

        /// Asks the engine's service for a send right to its device workgroup's port.
        fn port(service: &str) -> Result<MachPort, String> {
            let name = CString::new(service).map_err(|e| e.to_string())?;
            let mut server: MachPort = 0;
            // SAFETY: a NUL-terminated name; the bootstrap port is the process's own.
            let kr = unsafe { bootstrap_look_up(bootstrap_port, name.as_ptr(), &mut server) };
            if kr != 0 {
                return Err(format!("bootstrap_look_up({service}) = {kr}"));
            }
            // SAFETY: plain Mach calls on ports this function owns; the buffer holds the reply.
            unsafe {
                let reply = mach_reply_port();
                let mut buffer = Buffer([0; 512]);
                let header = buffer.0.as_mut_ptr().cast::<Header>();
                header.write(Header {
                    bits: MACH_MSG_TYPE_COPY_SEND | (MACH_MSG_TYPE_MAKE_SEND_ONCE << 8),
                    size: size_of::<Header>() as u32,
                    remote: server,
                    local: reply,
                    voucher: 0,
                    id: REQUEST_ID,
                });
                let kr = mach_msg(header, MACH_SEND_MSG | MACH_RCV_MSG | MACH_SEND_TIMEOUT | MACH_RCV_TIMEOUT,
                                  size_of::<Header>() as u32, 512, reply, 2000, 0);
                mach_port_mod_refs(mach_task_self_, reply, MACH_PORT_RIGHT_RECEIVE, -1);
                mach_port_deallocate(mach_task_self_, server);
                if kr != 0 {
                    return Err(format!("mach_msg = {kr:#x}"));
                }
                let msg = buffer.0.as_ptr().cast::<Reply>().read_unaligned();
                if msg.header.bits & MACH_MSGH_BITS_COMPLEX == 0 || msg.descriptor_count != 1 {
                    return Err("reply without a port".into());
                }
                Ok(msg.port.name)
            }
        }

        /// Joins the engine's device workgroup. The device's IO thread starts and finishes its
        /// intervals, so this worker only joins it.
        pub(super) fn join(service: &str) -> Result<Workgroup, String> {
            let port = port(service)?;
            // SAFETY: a send right to a workgroup port, and a static name.
            let interval = unsafe { os_workgroup_create_with_port(c"plughost shared".as_ptr(), port) };
            // SAFETY: our send right; the workgroup object keeps what it needs.
            unsafe { mach_port_deallocate(mach_task_self_, port) };
            if interval.is_null() {
                return Err("os_workgroup_create_with_port failed".into());
            }
            let mut workgroup = Workgroup { interval, token: JoinToken { sig: 0, opaque: [0; 36] }, owned: false };
            // SAFETY: a valid workgroup and a token of the size the system expects.
            let joined = unsafe { os_workgroup_join(workgroup.interval, &mut workgroup.token) };
            if joined != 0 {
                // SAFETY: created retained above and not used again.
                unsafe { os_release(workgroup.interval) };
                return Err(format!("os_workgroup_join = {joined}"));
            }
            Ok(workgroup)
        }

        /// One line per helper to PLUGHOST_WORKGROUP_LOG (a benchmark's check that helpers joined).
        pub(super) fn log(what: &str) {
            if let Some(path) = std::env::var_os("PLUGHOST_WORKGROUP_LOG")
                && let Ok(mut file) = std::fs::OpenOptions::new().create(true).append(true).open(path)
            {
                let _ = writeln!(file, "{} {what}", std::process::id());
            }
        }

        #[cfg(test)]
        mod tests {
            use super::*;

            #[test]
            fn mach_layouts_match_the_system_headers() {
                assert_eq!(size_of::<Header>(), 24);
                assert_eq!(size_of::<PortDescriptor>(), 12);
                assert_eq!(size_of::<Reply>(), 40);
            }
        }
    }
}

#[cfg(windows)]
mod platform {
    use windows_sys::Win32::Foundation::HANDLE;
    use windows_sys::Win32::System::Threading::{
        AvRevertMmThreadCharacteristics, AvSetMmThreadCharacteristicsW,
    };

    use crate::Responder;
    use crate::errors::REALTIME_MMCSS;

    pub struct Schedule {
        task: HANDLE,
    }

    impl Schedule {
        pub fn enter(_quantum: u64, responder: &Responder) -> Schedule {
            let name: Vec<u16> = "Pro Audio".encode_utf16().chain([0]).collect();
            let mut index = 0;
            // SAFETY: a NUL-terminated task name and a valid index.
            let task = unsafe { AvSetMmThreadCharacteristicsW(name.as_ptr(), &mut index) };
            if task.is_null() {
                responder.warn(REALTIME_MMCSS);
            }
            Schedule { task }
        }

        /// MMCSS has no intervals.
        pub fn start(&self, _start: u64, _deadline: u64) -> bool {
            false
        }

        pub fn finish(&self) {}
    }

    impl Drop for Schedule {
        fn drop(&mut self) {
            if !self.task.is_null() {
                // SAFETY: the task handle this thread joined.
                unsafe { AvRevertMmThreadCharacteristics(self.task) };
            }
        }
    }
}
