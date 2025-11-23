#!/usr/bin/env python3
"""
Simple menu bar app for Serum AI
Starts the Flask server in background and provides status indicator
"""
import rumps
import subprocess
import requests
import threading
import time
from pathlib import Path

class SerumAIApp(rumps.App):
    def __init__(self):
        super(SerumAIApp, self).__init__("Serum AI", "🎛️")
        self.server_process = None
        self.server_running = False

        # Menu items
        self.menu = [
            rumps.MenuItem("Starting server...", callback=None),
            rumps.separator,
            rumps.MenuItem("Open in Browser", callback=self.open_browser),
            rumps.separator,
        ]

        # Start server in background thread
        threading.Thread(target=self.start_server, daemon=True).start()

        # Start health check loop
        threading.Thread(target=self.health_check_loop, daemon=True).start()

    def start_server(self):
        """Start the Flask API server"""
        print("🚀 Starting Serum AI server...")

        # Determine server script path
        import sys
        if getattr(sys, 'frozen', False):
            # Running as bundled app
            server_dir = Path(sys._MEIPASS) / "server"
        else:
            # Running in development
            server_dir = Path(__file__).parent / "server"

        server_script = server_dir / "api_server.py"

        # Start server process
        self.server_process = subprocess.Popen(
            ["python", str(server_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print("✅ Server started")

    def health_check_loop(self):
        """Periodically check if server is healthy"""
        while True:
            time.sleep(2)
            try:
                response = requests.get("http://localhost:8080/health", timeout=1)
                if response.status_code == 200:
                    if not self.server_running:
                        self.server_running = True
                        self.menu["Starting server..."].title = "✅ Server Running"
                        self.title = "🎛️✅"
                else:
                    self.handle_server_down()
            except:
                self.handle_server_down()

    def handle_server_down(self):
        """Handle server being down"""
        if self.server_running:
            self.server_running = False
            self.menu["✅ Server Running"].title = "❌ Server Down"
            self.title = "🎛️❌"

    def open_browser(self, _):
        """Open server URL in browser"""
        import webbrowser
        webbrowser.open("http://localhost:8080/health")

    def quit_app(self, _):
        """Quit the app and stop the server"""
        if self.server_process:
            # Try graceful shutdown first
            try:
                requests.post("http://localhost:8080/shutdown", timeout=1)
            except:
                pass

            # Force kill if still running
            time.sleep(1)
            if self.server_process.poll() is None:
                self.server_process.terminate()

        rumps.quit_application()

if __name__ == "__main__":
    # Check if rumps is installed
    try:
        import rumps
    except ImportError:
        print("❌ rumps not found. Installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "rumps"])
        import rumps

    app = SerumAIApp()
    app.run()
