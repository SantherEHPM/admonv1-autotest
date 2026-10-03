"""Seguimiento de pasos por ejecución: qué paso corre, cuánto tarda,
dónde falló y cuánto tiempo de backend consumió.

Cada registro: {name, ms, ok, backend, backendMs}.
- backend=True: el paso hace peticiones al backend.
- backendMs: tiempo atribuible al backend. Si el paso no anota un valor
  preciso con note_backend_ms(), se usa el tiempo total del paso (roundtrip).
"""
import time
from contextlib import contextmanager

_state = {"current": None, "steps": [], "failed": None}


def reset_steps():
    _state["current"] = None
    _state["steps"] = []
    _state["failed"] = None


@contextmanager
def track(name, backend=False, endpoint=None):
    rec = {"name": name, "ms": 0, "ok": True, "backend": backend,
           "backendMs": 0 if backend else None,
           "endpoint": endpoint if backend else None}
    _state["current"] = rec
    start = time.time()
    try:
        yield rec
        rec["ok"] = True
    except Exception:
        rec["ok"] = False
        _state["failed"] = name
        raise
    finally:
        rec["ms"] = int((time.time() - start) * 1000)
        if backend and not rec["backendMs"]:
            rec["backendMs"] = rec["ms"]
        _state["steps"].append(rec)
        _state["current"] = None


def note_backend_ms(ms):
    """Suma tiempo preciso de backend al paso en curso (p. ej. API directa)."""
    rec = _state["current"]
    if rec is not None and rec["backend"]:
        rec["backendMs"] = (rec["backendMs"] or 0) + ms


def get_steps():
    return list(_state["steps"])


def get_failed_step():
    return _state["failed"]
