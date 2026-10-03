"""Control del frontend local por proceso (vite dev en :5173).

Uso: restart_frontend() antes de cada escenario con --env local.
Log en reports/frontend.log y pid en reports/frontend.pid.
"""
import os
import signal
import socket
import subprocess
import time
from pathlib import Path

def _repo_dir(name):
    """Ubicación del repo hermano (portable entre equipos).

    Orden: 1) AUTOTEST_FRONTEND explícito, 2) AUTOTEST_WORKSPACE/<repo>,
    3) carpeta junto a admonv1-autotest (layout estándar), 4) ../<repo>.
    """
    explicit = os.getenv("AUTOTEST_FRONTEND")
    if explicit:
        return Path(explicit)
    root = os.getenv("AUTOTEST_WORKSPACE")
    if root:
        return Path(root) / f"admonv1-{name}"
    here = Path(__file__).resolve()
    for p in [here] + list(here.parents):
        if p.name == "admonv1-autotest":
            return p.parent / f"admonv1-{name}"
    return Path.cwd().parent / f"admonv1-{name}"


FRONTEND_DIR = _repo_dir("frontend")
REPORTS_DIR = Path("reports")
PID_FILE = REPORTS_DIR / "frontend.pid"
LOG_FILE = REPORTS_DIR / "frontend.log"
PORT = 5173


def port_open(port=PORT):
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def find_frontend_pids():
    pids = []
    for pid in filter(str.isdigit, os.listdir("/proc")):
        try:
            cmd = Path(f"/proc/{pid}/cmdline").read_bytes().decode(errors="ignore")
        except Exception:
            continue
        if "vite" in cmd and ("frontend_ctl" not in cmd):
            pids.append(int(pid))
    return pids


def start_frontend(timeout=90):
    if port_open():
        return "already-up"
    if not FRONTEND_DIR.is_dir():
        raise RuntimeError(
            f"No existe el frontend en {FRONTEND_DIR}. "
            "Clónalo junto a admonv1-autotest o define AUTOTEST_FRONTEND / AUTOTEST_WORKSPACE."
        )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    log = open(LOG_FILE, "a")
    proc = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", str(PORT), "--host", "127.0.0.1", "--strictPort"],
        cwd=str(FRONTEND_DIR), stdout=log, stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    PID_FILE.write_text(str(proc.pid))
    if not wait_healthy(timeout):
        raise RuntimeError("Frontend no levantó en %ss (ver %s)" % (timeout, LOG_FILE))
    return "started"


def stop_frontend(timeout=20):
    pids = []
    if PID_FILE.exists():
        try:
            pids.append(int(PID_FILE.read_text().strip()))
        except Exception:
            pass
    # npm + node hijos (vite corre como hijo de npm)
    import subprocess as sp
    try:
        out = sp.run(["pgrep", "-f", "vite"], capture_output=True, text=True, timeout=5).stdout
        for line in out.split():
            if line.strip().isdigit() and int(line) not in pids:
                pids.append(int(line))
    except Exception:
        pass
    pids += [p for p in find_frontend_pids() if p not in pids]
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not port_open() and not find_frontend_pids():
            break
        time.sleep(1)
    for pid in find_frontend_pids():
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        PID_FILE.unlink()
    except Exception:
        pass


def wait_healthy(timeout=90):
    import requests
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"http://127.0.0.1:{PORT}/", timeout=5)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def restart_frontend(timeout=90):
    start = time.time()
    stop_frontend()
    start_frontend(timeout)
    return int((time.time() - start) * 1000)
