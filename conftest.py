import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from shared.utils.gas_client import build_payload, register_run
from shared.steps.context import reset_steps, track, get_failed_step, get_steps


def _default_env():
    env = os.getenv("TEST_ENV", "").strip().lower()
    if env in ("local", "prod"):
        return env
    base = os.getenv("BASE_URL", "")
    return "prod" if "duckdns.org" in base else "local"


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default=os.getenv("BASE_URL", "https://aes-puj.duckdns.org"))
    parser.addoption("--gas-url", action="store", default=os.getenv("GAS_URL", ""))
    parser.addoption("--headless", action="store_true", default=os.getenv("HEADLESS", "false").lower() == "true",
                     help="Ejecutar sin ventana de navegador (CI)")
    parser.addoption("--headed", action="store_true", default=False,
                     help="Forzar navegador visible aunque HEADLESS=true")
    parser.addoption("--slow-mo", action="store", default=os.getenv("SLOW_MO_MS", "700"))
    parser.addoption("--env", action="store", default=_default_env(),
                     help="Entorno: local (con verificación API) o prod (sin verificación API)")
    parser.addoption("--reset-backend", action="store", default=os.getenv("RESET_BACKEND", "test"),
                     help="Reinicio del backend local: no|session|test (solo --env local)")
    parser.addoption("--reset-frontend", action="store", default=os.getenv("RESET_FRONTEND", "test"),
                     help="Reinicio del frontend local: no|session|test (solo --env local)")


@pytest.fixture(scope="function")
def base_url(request):
    return request.config.getoption("--base-url")


@pytest.fixture(scope="function")
def env(request):
    value = (request.config.getoption("--env") or "local").lower()
    os.environ["TEST_ENV"] = value
    return value


@pytest.fixture(scope="session", autouse=True)
def _reset_servers_session(request):
    env = (request.config.getoption("--env") or "local").lower()
    if env != "local":
        return
    if (request.config.getoption("--reset-backend") or "no").lower() == "session":
        from shared.utils.backend_ctl import restart_backend
        print(f"[backend] reinicio de sesión en {restart_backend()}ms")
    if (request.config.getoption("--reset-frontend") or "no").lower() == "session":
        from shared.utils.frontend_ctl import restart_frontend
        print(f"[frontend] reinicio de sesión en {restart_frontend()}ms")


@pytest.fixture(scope="function", autouse=True)
def _test_setup(request):
    from shared.steps.context import reset_steps
    reset_steps()
    env = (request.config.getoption("--env") or "local").lower()
    os.environ["TEST_ENV"] = env
    # Reinicio ANTES de cada prueba (solo --env local): cada escenario
    # parte de BD limpia y frontend fresco. Queda registrado en los pasos.
    if env == "local":
        if (request.config.getoption("--reset-backend") or "no").lower() == "test":
            from shared.utils.backend_ctl import restart_backend
            with track("reiniciar_backend"):
                ms = restart_backend()
            print(f"[backend] reiniciado en {ms}ms (BD limpia)")
        if (request.config.getoption("--reset-frontend") or "no").lower() == "test":
            from shared.utils.frontend_ctl import restart_frontend
            with track("reiniciar_frontend"):
                ms = restart_frontend()
            print(f"[frontend] reiniciado en {ms}ms")
    yield


@pytest.fixture(scope="function")
def driver(request):
    headless = request.config.getoption("--headless") and not request.config.getoption("--headed")
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    else:
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1366,768")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = ChromeService(ChromeDriverManager().install())
        drv = webdriver.Chrome(service=service, options=options)
    except Exception:
        drv = webdriver.Chrome(options=options)

    drv.implicitly_wait(2)
    yield drv
    drv.quit()


_call_outcome = {}


def _euv_id_of(item):
    for marker in item.iter_markers():
        if marker.name.startswith("euv"):
            raw = marker.name  # p. ej. euv01 -> EUV_01
            num = raw.replace("euv", "")
            return f"EUV_{num.zfill(2)}" if num.isdigit() else raw.upper()
    return None


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when in ("setup", "call"):
        # Guarda el resultado de la ejecución; el registro a GAS se hace en
        # teardown para incluir los pasos de reinicio de servidores.
        if rep.when == "call" or item.nodeid not in _call_outcome:
            duration_ms = int((call.stop - call.start) * 1000) if hasattr(call, "stop") else 0
            _call_outcome[item.nodeid] = {
                "status": "PASSED" if rep.passed else "FAILED" if rep.failed else "SKIPPED",
                "duration_ms": duration_ms,
                "error": str(rep.longrepr)[:2000] if rep.failed else None,
            }
    elif rep.when == "teardown":
        result = _call_outcome.pop(item.nodeid, None)
        euv_id = _euv_id_of(item)
        if result and euv_id:
            extra = {"apiCheck": item.funcargs.get("api_check_result") or None}
            try:
                register_run(build_payload(euv_id, result["status"], result["duration_ms"], result["error"], extra))
            except Exception as e:
                print(f"[conftest] fallo registro GAS: {e}")

    if rep.when == "call" and rep.failed:
        drv = item.funcargs.get("driver")
        if drv:
            try:
                os.makedirs("reports/screenshots", exist_ok=True)
                path = f"reports/screenshots/{item.name}_{int(time.time())}.png"
                drv.save_screenshot(path)
                print(f"[screenshot] {path}")
            except Exception:
                pass


@pytest.fixture
def login(driver, base_url):
    from shared.fixtures.auth import login_as_resident
    login_as_resident(driver, base_url)
    return driver


@pytest.fixture(scope="function")
def api_check_result():
    # Dict mutable: los escenarios guardan aquí su verificación API.
    # El hook lo incluye en el payload (None si el escenario no lo pidió).
    return {}
