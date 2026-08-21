"""Serve the repository-backed M0 dashboard without third-party dependencies."""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the M0 Evaluation Explorer")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    handler = partial(SimpleHTTPRequestHandler, directory=str(repo_root))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"M0 dashboard: http://127.0.0.1:{args.port}/tools/m0-dashboard/")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
