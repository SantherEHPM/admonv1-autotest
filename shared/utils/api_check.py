"""Verificación por API contra el backend (solo entorno local).

En producción (link duckdns) no se verifica por API: las funciones devuelven
performed=False y los escenarios omiten esa parte.
"""
import time
import requests


def api_base(base_url):
    return base_url.rstrip("/") + "/api"


def is_prod(base_url):
    return "duckdns.org" in (base_url or "")


def api_login(base_url, email, password, timeout=10):
    url = f"{api_base(base_url)}/auth/login"
    start = time.time()
    try:
        r = requests.post(url, json={"email": email, "password": password}, timeout=timeout)
        ms = int((time.time() - start) * 1000)
        if not r.ok:
            return {"performed": True, "httpStatus": r.status_code, "ms": ms, "ok": False, "detail": r.text[:300]}
        token = r.json()["data"]["token"]
        return {"performed": True, "httpStatus": r.status_code, "ms": ms, "ok": True, "detail": "login ok", "token": token}
    except Exception as e:
        return {"performed": True, "httpStatus": None, "ms": int((time.time() - start) * 1000), "ok": False, "detail": str(e)[:300]}


def api_list_applications(base_url, token, timeout=10, size=100):
    url = f"{api_base(base_url)}/applications?page=0&size={size}"
    start = time.time()
    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=timeout)
        ms = int((time.time() - start) * 1000)
        if not r.ok:
            return {"performed": True, "httpStatus": r.status_code, "ms": ms, "ok": False, "detail": r.text[:300]}
        data = r.json().get("data", [])
        items = data if isinstance(data, list) else data.get("content", data)
        total = data if isinstance(data, int) else (data.get("totalElements", len(items)) if isinstance(data, dict) else len(items))
        return {"performed": True, "httpStatus": r.status_code, "ms": ms, "ok": True, "detail": f"{len(items)} postulaciones", "items": items, "total": total}
    except Exception as e:
        return {"performed": True, "httpStatus": None, "ms": int((time.time() - start) * 1000), "ok": False, "detail": str(e)[:300]}


def api_get_application(base_url, token, app_id, timeout=10):
    url = f"{api_base(base_url)}/applications/{app_id}"
    start = time.time()
    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=timeout)
        ms = int((time.time() - start) * 1000)
        if not r.ok:
            return {"performed": True, "httpStatus": r.status_code, "ms": ms, "ok": False, "detail": r.text[:300]}
        return {"performed": True, "httpStatus": r.status_code, "ms": ms, "ok": True,
                "detail": f"detalle {app_id}", "data": r.json().get("data")}
    except Exception as e:
        return {"performed": True, "httpStatus": None, "ms": int((time.time() - start) * 1000), "ok": False, "detail": str(e)[:300]}


def api_check_eligibility(base_url, token, call_id, timeout=10):
    url = f"{api_base(base_url)}/applications/check?callId={call_id}"
    start = time.time()
    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=timeout)
        ms = int((time.time() - start) * 1000)
        body = r.json() if r.headers.get("Content-Type", "").startswith("application/json") else {}
        return {"performed": True, "httpStatus": r.status_code, "ms": ms, "ok": r.ok,
                "detail": str(body.get("message", r.text[:200])), "data": body.get("data")}
    except Exception as e:
        return {"performed": True, "httpStatus": None, "ms": int((time.time() - start) * 1000), "ok": False, "detail": str(e)[:300]}


def skipped_api(reason="entorno producción: sin verificación API"):
    return {"performed": False, "httpStatus": None, "ms": 0, "ok": None, "detail": reason}
