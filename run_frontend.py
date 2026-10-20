"""
PhishShield AI — Frontend Launcher Script
Launches the FastAPI backend and serves the frontend dashboard at http://localhost:8050
"""

import os
import threading
import time
import webbrowser
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    host = "127.0.0.1"
    url = f"http://{host}:{port}"

    print("=" * 65)
    print("  PHISHSHIELD AI — PHISHING EMAIL ML CLASSIFIER FRONTEND")
    print("=" * 65)
    print(f"[*] Dashboard URL: {url}")
    print("[*] Models: 6 ML Classifiers (TF-IDF + 14 Engineered Features)")
    print("[*] Press Ctrl+C in this terminal to stop the server.")
    print("=" * 65)

    server = uvicorn.Server(
        uvicorn.Config("server:app", host=host, port=port, reload=False)
    )
    server_thread = threading.Thread(target=server.run)
    server_thread.start()

    try:
        while server_thread.is_alive() and not server.started:
            time.sleep(0.1)

        if not server.started:
            raise RuntimeError("The web server stopped before it finished starting.")

        if not webbrowser.open(url):
            print(f"[!] Could not open a browser automatically. Visit {url}")

        server_thread.join()
    except KeyboardInterrupt:
        server.should_exit = True
        server_thread.join()
