#!/usr/bin/env python3
"""Entry point for BAP Labs Ableton Sleeve. Run bridge modules from harness/."""
import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'harness'))

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'mlx'
    # Pass remaining args back so bridges see their own flags (e.g. -c)
    sys.argv = [sys.argv[0]] + sys.argv[2:]

    if mode == 'mlx':
        from mlx_mcp_bridge import main
        asyncio.run(main())
    elif mode == 'claude':
        from claude_mcp_bridge import main
        main()
    elif mode == 'gemini':
        from gemini_native_bridge import main
        main()
    elif mode == 'mix':
        from mix_assistant_bridge import main
        asyncio.run(main())
    elif mode == 'calibrate':
        # fidelity calibration: measures headless-vs-Live parity (drives open Live!)
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sandbox'))
        from eval_fidelity import main as cal_main
        sys.exit(cal_main())
    elif mode == 'review':
        # local approval-workflow UI (http://127.0.0.1:8765)
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sandbox'))
        from review_ui import main
        main()
    elif mode == 'ears':
        # live-Ableton listening daemon: OSC 9880 -> snapshot JSON for MCP tools
        from live_ears import main
        asyncio.run(main())
    else:
        print(f"Unknown mode: {mode}. Use: mlx, claude, gemini, mix, ears, calibrate, review")
        sys.exit(1)
