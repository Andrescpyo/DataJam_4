import socket
import subprocess
import sys
from pathlib import Path


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> None:
    root = Path(__file__).resolve().parent
    app_path = root / "dashboard_interactivo.py"
    port = get_free_port()

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.headless",
        "true",
        "--server.port",
        str(port),
    ]

    print(f"Iniciando dashboard interactivo en http://localhost:{port}")
    subprocess.run(cmd, cwd=root)


if __name__ == "__main__":
    main()
