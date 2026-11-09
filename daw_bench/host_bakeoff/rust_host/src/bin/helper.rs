//! The plughost helper: plugins load and run in this process, not in host_rs.
//! Packaged as a signed background .app by ../package_helper.sh.
fn main() -> std::process::ExitCode {
    plughost_helper::run()
}
