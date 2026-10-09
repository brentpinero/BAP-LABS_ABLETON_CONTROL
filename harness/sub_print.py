"""
sub_print.py — ONE command: collect the Bass group's MIDI, normalize it (lowest note, folded
into the sub octave) and paste it as 'Sub <- Bass' clips on the sub track in the Sub group.
The Remote Script does the work (print_sub); this script just fires it.

    python sub_print.py                      # print now
    python sub_print.py --raw                # plain copy, no mono/fold
    python sub_print.py --floor 29           # fold floor F0 instead of auto
    python sub_print.py --sub "15-Serum 2"   # explicit sub track

System-wide hotkey (works in any set, no per-set key mapping), two ways:

    python sub_print.py --make-shortcut      # writes a signed macOS Shortcut to the Desktop:
                                             # double-click to add it, then in Shortcuts open
                                             # its info panel and set "Run with" to a key combo
    python sub_print.py --install-hotkey "<cmd>+<shift>+b"
                                             # background listener at login (pynput). macOS
                                             # asks once for Input Monitoring / Accessibility
                                             # for python3; grant it, then it just works.
    python sub_print.py --hotkey "<cmd>+<shift>+b"      # same listener, in the foreground
"""

import argparse
import os
import plistlib
import subprocess
import sys
import time
from pathlib import Path

from live_client import LiveClient, LiveError

HERE = Path(__file__).resolve().parent
AGENT_LABEL = "com.baplabs.subprint"
AGENT_PLIST = Path.home() / "Library/LaunchAgents" / (AGENT_LABEL + ".plist")


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def print_sub(args):
    params = {"bass_group": args.bass_group, "sub_group": args.sub_group,
              "normalize": not args.raw, "floor": args.floor}
    if args.sub:
        params["sub_track"] = args.sub
    try:
        with LiveClient(timeout=60) as c:
            r = c.send("print_sub", params)
    except LiveError as e:
        log("Live: %s" % e)
        return 1
    if not r.get("printed"):
        log(r.get("message", "nothing printed"))
        return 1
    log("printed %d notes from %s into %d clip(s) on %r%s"
        % (r["printed"], r["sources"], r["clips"], r["sub_track"],
           "  (mono, floor %s)" % r["floor"] if r.get("normalized") else "  (raw copy)"))
    return 0


def hotkey_loop(args):
    try:
        from pynput import keyboard
    except ImportError:
        log("hotkey mode needs pynput:  pip install pynput")
        return 2
    log("listening for %s  (Ctrl+C to stop)" % args.hotkey)
    with keyboard.GlobalHotKeys({args.hotkey: lambda: print_sub(args)}) as h:
        h.join()
    return 0


def shell_command(args):
    """The command a hotkey runs: this script, with the same print options."""
    cmd = ["%r" % sys.executable, "%r" % str(HERE / "sub_print.py")]
    if args.raw:
        cmd.append("--raw")
    if args.floor is not None:
        cmd += ["--floor", str(args.floor)]
    if args.sub:
        cmd += ["--sub", "%r" % args.sub]
    return " ".join(cmd)


def make_shortcut(args):
    """A signed macOS Shortcut with one 'Run Shell Script' action, written to the Desktop."""
    workflow = {
        "WFWorkflowClientVersion": "2607.0.3",
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowIcon": {"WFWorkflowIconStartColor": 4282601983, "WFWorkflowIconGlyphNumber": 59511},
        "WFWorkflowTypes": [],
        "WFWorkflowInputContentItemClasses": [],
        "WFWorkflowHasShortcutInputVariables": False,
        "WFWorkflowActions": [{
            "WFWorkflowActionIdentifier": "is.workflow.actions.runshellscript",
            "WFWorkflowActionParameters": {
                "Shell": "/bin/zsh", "Script": shell_command(args) + " 2>&1",
                "Input": "", "InputType": "text", "WFIsLegacyAction": False},
        }],
    }
    raw = Path("/tmp/Sub Print.unsigned.shortcut")
    raw.write_bytes(plistlib.dumps(workflow))
    out = Path.home() / "Desktop" / "Sub Print.shortcut"
    subprocess.run(["shortcuts", "sign", "--mode", "anyone", "--input", str(raw),
                    "--output", str(out)], check=True)
    raw.unlink()
    log("wrote %s" % out)
    log("double-click it to add it to Shortcuts, open its info panel (i) and set a key combo under 'Run with'")
    return 0


def install_hotkey(args):
    """LaunchAgent that runs the hotkey listener at login."""
    plist = {"Label": AGENT_LABEL, "RunAtLoad": True, "KeepAlive": True,
             "ProgramArguments": [sys.executable, str(HERE / "sub_print.py"), "--hotkey", args.install_hotkey]
                                 + (["--raw"] if args.raw else [])
                                 + (["--floor", str(args.floor)] if args.floor is not None else [])
                                 + (["--sub", args.sub] if args.sub else []),
             "StandardOutPath": str(Path.home() / "Library/Logs/subprint.log"),
             "StandardErrorPath": str(Path.home() / "Library/Logs/subprint.log")}
    AGENT_PLIST.parent.mkdir(parents=True, exist_ok=True)
    AGENT_PLIST.write_bytes(plistlib.dumps(plist))
    subprocess.run(["launchctl", "unload", str(AGENT_PLIST)], capture_output=True)
    subprocess.run(["launchctl", "load", str(AGENT_PLIST)], check=True)
    log("installed %s (%s); log: ~/Library/Logs/subprint.log" % (AGENT_PLIST.name, args.install_hotkey))
    log("if macOS asks, allow Input Monitoring / Accessibility for python3; remove with --uninstall-hotkey")
    return 0


def uninstall_hotkey():
    subprocess.run(["launchctl", "unload", str(AGENT_PLIST)], capture_output=True)
    if AGENT_PLIST.exists():
        AGENT_PLIST.unlink()
    log("hotkey listener removed")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--sub", help="sub track name or index (default: first MIDI track in the Sub group)")
    ap.add_argument("--bass-group", default="bass")
    ap.add_argument("--sub-group", default="sub")
    ap.add_argument("--raw", action="store_true", help="plain copy, no mono/fold")
    ap.add_argument("--floor", type=int, help="fold floor as a MIDI note (default: auto)")
    ap.add_argument("--hotkey", help='stay running and print on this key, e.g. "<cmd>+<shift>+b"')
    ap.add_argument("--install-hotkey", metavar="KEYS", help="run the listener at login")
    ap.add_argument("--uninstall-hotkey", action="store_true")
    ap.add_argument("--make-shortcut", action="store_true", help="write a signed macOS Shortcut")
    args = ap.parse_args()
    if args.uninstall_hotkey:
        return uninstall_hotkey()
    if args.install_hotkey:
        return install_hotkey(args)
    if args.make_shortcut:
        return make_shortcut(args)
    return hotkey_loop(args) if args.hotkey else print_sub(args)


if __name__ == "__main__":
    sys.exit(main())
