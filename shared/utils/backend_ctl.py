"""Control del backend local por proceso (reinicio = BD H2 limpia + seed).

Uso: restart_backend() antes de cada escenario con --env local.
El backend se lanza con `java -cp` directo (mismo main que IntelliJ),
log en reports/backend.log y pid en reports/backend.pid.
"""
import os
import signal
import socket
import subprocess
import tempfile
import time
from pathlib import Path


def _repo_dir(name):
    """Ubicación del repo hermano (portable entre equipos).

    Orden: 1) AUTOTEST_BACKEND explícito, 2) AUTOTEST_WORKSPACE/<repo>,
    3) carpeta junto a admonv1-autotest (layout estándar), 4) ../<repo>.
    """
    explicit = os.getenv("AUTOTEST_BACKEND")
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


BACKEND_DIR = _repo_dir("backend")
REPORTS_DIR = Path("reports")
PID_FILE = REPORTS_DIR / "backend.pid"
LOG_FILE = REPORTS_DIR / "backend.log"
CP_FILE = Path(tempfile.gettempdir()) / "admonv1-cp.txt"
MAIN_CLASS = "com.administracionback.admonv1.Admonv1Application"
PORT = 8080


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


def find_backend_pids():
    pids = []
    for pid in filter(str.isdigit, os.listdir("/proc")):
        try:
            cmd = Path(f"/proc/{pid}/cmdline").read_bytes().decode(errors="ignore")
        except Exception:
            continue
        if MAIN_CLASS in cmd and "backend_ctl" not in cmd:
            pids.append(int(pid))
    return pids


def _ensure_classpath():
    if not BACKEND_DIR.is_dir():
        raise RuntimeError(
            f"No existe el backend en {BACKEND_DIR}. "
            "Clónalo junto a admonv1-autotest o define AUTOTEST_BACKEND / AUTOTEST_WORKSPACE."
        )
    if CP_FILE.exists() and CP_FILE.stat().st_size > 1000:
        return CP_FILE.read_text().strip()
    out = subprocess.run(
        ["./mvnw", "-q", "dependency:build-classpath",
         "-Dmdep.outputFile=" + str(CP_FILE), "-Dmdep.includeScope=runtime"],
        cwd=str(BACKEND_DIR), capture_output=True, text=True, timeout=300,
    )
    if not CP_FILE.exists():
        raise RuntimeError("No se pudo generar classpath: " + (out.stderr or out.stdout)[-500:])
    return CP_FILE.read_text().strip()


def start_backend(timeout=180):
    if port_open():
        return "already-up"
    cp = _ensure_classpath()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    log = open(LOG_FILE, "a")
    proc = subprocess.Popen(
        ["java", "-cp", f"target/classes:{cp}", MAIN_CLASS],
        cwd=str(BACKEND_DIR), stdout=log, stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    PID_FILE.write_text(str(proc.pid))
    if not wait_healthy(timeout):
        raise RuntimeError("Backend no levantó en %ss (ver %s)" % (timeout, LOG_FILE))
    return "started"


def stop_backend(timeout=30):
    pids = []
    if PID_FILE.exists():
        try:
            pids.append(int(PID_FILE.read_text().strip()))
        except Exception:
            pass
    pids += [p for p in find_backend_pids() if p not in pids]
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not port_open() and not [p for p in find_backend_pids()]:
            break
        time.sleep(1)
    for pid in find_backend_pids():
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        PID_FILE.unlink()
    except Exception:
        pass


def wait_healthy(timeout=180):
    import requests
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.post(
                f"http://127.0.0.1:{PORT}/api/auth/login",
                json={"email": "residente@test.com", "password": "123456"},
                timeout=5,
            )
            if r.status_code in (200, 400, 401):
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def restart_backend(timeout=180):
    start = time.time()
    stop_backend()
    start_backend(timeout)
    return int((time.time() - start) * 1000)
