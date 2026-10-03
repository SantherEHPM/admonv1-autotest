import json
import os
import subprocess
import time
import requests
from pathlib import Path

PENDING_FILE = Path("reports/pending.json")


def _load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass


def get_branch():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        branch = (out.stdout or "").strip()
        return branch or None
    except Exception:
        return None


def build_payload(euv_id, status, duration_ms, error=None, extra=None):
    from validacion_horizontal.flujo_residente.properties import EUV_PRODUCT_ELEMENTS, EUV_META
    from shared.steps.context import get_steps, get_failed_step
    meta = EUV_META.get(euv_id, {})
    payload = {
        "runId": f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}_{euv_id}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env": os.getenv("TEST_ENV", "local"),
        "euvId": euv_id,
        "euvName": meta.get("name", euv_id),
        "suite": meta.get("suite", "Flujo Residente"),
        "collection": meta.get("collection", ""),
        "status": status,
        "durationMs": duration_ms,
        "error": error,
        "productElements": EUV_PRODUCT_ELEMENTS.get(euv_id, []),
        "failedStep": get_failed_step(),
        "steps": get_steps(),
        "branch": get_branch() if os.getenv("TEST_ENV", "local") == "local" else None,
        "apiCheck": None,
    }
    if extra:
        payload.update(extra)
    return payload


def register_run(payload):
    _load_env()
    gas_url = os.getenv("GAS_URL", "").strip()
    if not gas_url:
        print("[gas_client] GAS_URL no configurado, guardando en pending.json")
        _save_pending(payload)
        return False
    url = gas_url if "action=" in gas_url else f"{gas_url}?action=register"
    try:
        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        print(f"[gas_client] POST {url} -> {resp.status_code} {resp.text[:300]}")
        return resp.ok
    except Exception as e:
        print(f"[gas_client] Error enviando a GAS: {e}")
        _save_pending(payload)
        return False


def _save_pending(payload):
    PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if PENDING_FILE.exists():
        try:
            existing = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    existing.append({**payload, "_savedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    PENDING_FILE.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
