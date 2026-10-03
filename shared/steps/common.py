"""Pasos comunes definidos UNA sola vez y reutilizados por los escenarios.

Granularidad campo por campo: cada ingreso de información o click a un
botón es un paso propio con su track(). Los helpers compuestos
(login_como_residente, cargar_documentos_validos) NO trackean: solo
encadenan primitivas para no duplicar registros.
"""
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from shared.steps.context import track, note_backend_ms
from shared.utils import api_check
from validacion_horizontal.flujo_residente.properties import (
    SELECTORS, TEST_USER, REQUIRED_DOC_CODES, MAX_DOC_BYTES,
)


# ---------------------------------------------------------------- archivos
def make_pdf(path, size_bytes=50 * 1024):
    body = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
    with open(path, "wb") as f:
        f.write(body)
        remaining = size_bytes - len(body)
        if remaining > 0:
            f.write(b"0" * remaining)


def make_txt(path, text="archivo de formato erroneo"):
    with open(path, "w") as f:
        f.write(text)


# ---------------------------------------------------------------- ingreso
def abrir_pagina_login(driver, base_url):
    from validacion_horizontal.flujo_residente.pages.LoginPage import LoginPage
    with track("abrir_login"):
        page = LoginPage(driver, base_url)
        page.open()
        assert page.is_visible(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_form']}']")
        return page


def escribir_email(driver, email):
    with track("escribir_email"):
        el = driver.find_element(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_email']}']")
        el.clear()
        time.sleep(0.3)
        for ch in email:
            el.send_keys(ch)
            time.sleep(0.04)
        time.sleep(0.4)


def escribir_password(driver, password):
    with track("escribir_password"):
        el = driver.find_element(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_password']}']")
        el.clear()
        time.sleep(0.3)
        for ch in password:
            el.send_keys(ch)
            time.sleep(0.04)
        time.sleep(0.4)


def pulsar_ingresar(driver):
    with track("pulsar_ingresar", backend=True, endpoint="POST /api/auth/login"):
        el = driver.find_element(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_submit']}']")
        try:
            el.click()
        except Exception:
            driver.execute_script("arguments[0].click();", el)
        time.sleep(1.2)


def verificar_ingreso(driver):
    with track("verificar_ingreso"):
        WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f"[data-testid='{SELECTORS['navbar']}']"))
        )
        assert "convocations" in driver.current_url or driver.current_url.endswith("/")


def verificar_rechazo_login(driver):
    with track("verificar_rechazo_login"):
        assert "login" in driver.current_url, "No debería salir de /login"
        err = driver.find_elements(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_error']}']")
        nav = driver.find_elements(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['navbar']}']")
        assert err or not nav, "Esperaba error o ausencia de navbar"


def login_como_residente(driver, base_url, email=None, password=None):
    email = email or TEST_USER["email"]
    password = password or TEST_USER["password"]
    abrir_pagina_login(driver, base_url)
    escribir_email(driver, email)
    escribir_password(driver, password)
    pulsar_ingresar(driver)


# ---------------------------------------------------------------- convocatorias
def abrir_convocatorias(driver, base_url):
    from validacion_horizontal.flujo_residente.pages.ConvocationsPage import ConvocationsPage
    with track("abrir_convocatorias", backend=True, endpoint="GET /api/calls"):
        ConvocationsPage(driver, base_url).open()
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "[data-testid^='convocation-card-']")) > 0
            or "No hay convocatorias" in d.page_source
        )
        time.sleep(0.5)
        return driver.find_elements(By.CSS_SELECTOR, "[data-testid^='convocation-card-']")


def primera_convocatoria(cards):
    """Regla fija: los EUVs de postulación trabajan siempre sobre la primera
    convocatoria consultada (cards[0]), sin buscar ni iterar."""
    assert cards, "No hay convocatorias consultadas"
    return cards[0].get_attribute("data-testid").replace("convocation-card-", "")


def pulsar_ver_detalles(driver, base_url, conv_id):
    from validacion_horizontal.flujo_residente.pages.ConvocationsPage import ConvocationsPage
    with track("pulsar_ver_detalles"):
        ConvocationsPage(driver, base_url).click_view_details(conv_id)


def verificar_detalle(driver, base_url, conv_id):
    from validacion_horizontal.flujo_residente.pages.ConvocationDetailPage import ConvocationDetailPage
    with track("verificar_detalle", backend=True, endpoint="GET /api/calls/:id"):
        try:
            WebDriverWait(driver, 10).until(lambda d: f"/convocations/{conv_id}" in d.current_url)
        except Exception:
            ConvocationDetailPage(driver, base_url).open(conv_id)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f"[data-testid='{SELECTORS['convocation_register_button']}']"))
        )
        time.sleep(0.5)


# ---------------------------------------------------------------- postulación
def pulsar_registrar(driver):
    """Click en Registrar. Retorna 'apply' si navegó al wizard o 'blocked' si hubo mensaje."""
    with track("pulsar_registrar", backend=True, endpoint="GET /api/applications/check?callId="):
        btn = driver.find_element(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['convocation_register_button']}']")
        assert btn.is_enabled(), "Registrar Postulación deshabilitado"
        driver.execute_script("arguments[0].click();", btn)
        try:
            WebDriverWait(driver, 8).until(
                lambda d: "/apply" in d.current_url
                or d.find_elements(By.CLASS_NAME, SELECTORS["eligibility_message_class"])
            )
        except Exception:
            pass
        time.sleep(0.8)
        if "/apply" in driver.current_url:
            return "apply"
        msgs = driver.find_elements(By.CLASS_NAME, SELECTORS["eligibility_message_class"])
        if msgs and msgs[0].text.strip():
            return "blocked"
        return "apply" if "/apply" in driver.current_url else "blocked"


def verificar_mensaje_bloqueo(driver):
    with track("verificar_mensaje_bloqueo"):
        try:
            WebDriverWait(driver, 8).until(
                lambda d: any(m.text.strip() for m in d.find_elements(By.CLASS_NAME, SELECTORS["eligibility_message_class"]))
            )
        except Exception:
            pass
        msgs = [m for m in driver.find_elements(By.CLASS_NAME, SELECTORS["eligibility_message_class"]) if m.text.strip()]
        assert msgs, "Falta mensaje de bloqueo"
        txt = msgs[0].text.lower()
        assert "ya tienes" in txt or "postulación" in txt, f"Mensaje inesperado: {msgs[0].text}"
        return msgs[0].text


def pulsar_continuar(driver, base_url):
    from validacion_horizontal.flujo_residente.pages.CreateApplicationPage import CreateApplicationPage
    with track("pulsar_continuar"):
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f"[data-testid='{SELECTORS['create_continue']}']"))
        )
        time.sleep(0.4)
        CreateApplicationPage(driver, base_url).click_continue()
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f"[data-testid='{SELECTORS['create_submit']}']"))
        )
        time.sleep(0.4)


def subir_archivo_a_tipo(driver, code, file_path, timeout=20):
    inp = driver.find_element(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['doc_input_prefix']}{code}']")
    inp.send_keys(file_path)
    WebDriverWait(driver, timeout).until(
        lambda d: d.find_elements(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['doc_remove_file_prefix']}{code}']")
        or d.find_elements(By.CSS_SELECTOR, f"[data-testid='document-upload-remove-error-{code}']")
        or "Carga exitosa" in d.page_source
        or "Solo se permiten archivos PDF" in d.page_source
        or "excede el tamaño máximo" in d.page_source
    )
    time.sleep(0.6)
    errs = driver.find_elements(By.CSS_SELECTOR, f"[data-testid='document-upload-remove-error-{code}']")
    if errs:
        print(f"[upload] error en {code}: {driver.find_element(By.CSS_SELECTOR, f'[data-testid=document-type-block-{code}]').text[:200]}")


def _cargar_pdf_en_tipo(driver, code, size_bytes=50 * 1024):
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        make_pdf(path, size_bytes)
        subir_archivo_a_tipo(driver, code, path)
        ok = driver.find_elements(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['doc_remove_file_prefix']}{code}']")
        assert ok, f"Documento {code} no quedó en done"
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


def cargar_licencia_transito(driver):
    with track("cargar_licencia_transito", backend=True, endpoint="POST /api/documents/presigned-url + PUT + POST /api/documents/:id/complete"):
        _cargar_pdf_en_tipo(driver, "LICENCIA_TRANSITO")


def cargar_soat(driver):
    with track("cargar_soat", backend=True, endpoint="POST /api/documents/presigned-url + PUT + POST /api/documents/:id/complete"):
        _cargar_pdf_en_tipo(driver, "SOAT_VIGENTE")


def cargar_licencia_conduccion(driver):
    with track("cargar_licencia_conduccion", backend=True, endpoint="POST /api/documents/presigned-url + PUT + POST /api/documents/:id/complete"):
        _cargar_pdf_en_tipo(driver, "LICENCIA_CONDUCCION")


def cargar_documentos_validos(driver, codes=None):
    for code in (codes or REQUIRED_DOC_CODES):
        {"LICENCIA_TRANSITO": cargar_licencia_transito,
         "SOAT_VIGENTE": cargar_soat,
         "LICENCIA_CONDUCCION": cargar_licencia_conduccion}[code](driver)


def pulsar_confirmar(driver, base_url):
    from validacion_horizontal.flujo_residente.pages.CreateApplicationPage import CreateApplicationPage
    with track("pulsar_confirmar", backend=True, endpoint="POST /api/applications"):
        page = CreateApplicationPage(driver, base_url)
        WebDriverWait(driver, 10).until(lambda d: page.is_submit_enabled())
        assert page.is_submit_enabled()
        page.click_submit()
        WebDriverWait(driver, 15).until(
            lambda d: "¡Postulación Exitosa!" in d.page_source or "Resumen de la Solicitud" in d.page_source
        )
        time.sleep(0.8)


def verificar_resumen(driver):
    with track("verificar_resumen"):
        assert "¡Postulación Exitosa!" in driver.page_source or "Resumen de la Solicitud" in driver.page_source
        nums = driver.find_elements(By.CSS_SELECTOR, ".success-detail-value.teal")
        return nums[0].text.strip() if nums else None


def verificar_registro_api(base_url, env, api_check_result, conv_id, app_number=None):
    with track("verificar_registro_api", backend=True, endpoint="POST /api/auth/login + GET /api/applications"):
        if env == "prod":
            api_check_result.update(api_check.skipped_api())
            return
        login_r = api_check.api_login(base_url, TEST_USER["email"], TEST_USER["password"])
        assert login_r["ok"], f"Login API falló: {login_r['detail']}"
        note_backend_ms(login_r["ms"])
        list_r = api_check.api_list_applications(base_url, login_r["token"])
        assert list_r["ok"], f"Listado API falló: {list_r['detail']}"
        note_backend_ms(list_r["ms"])
        items = list_r.get("items", [])
        assert items, "La API no devuelve postulaciones"
        found = any(
            (app_number and it.get("applicationNumber") == app_number)
            or str(it.get("callId", "")) == str(conv_id)
            for it in items
        )
        assert found, "La postulación no aparece en la API"
        api_check_result.update({**list_r, "detail": f"Registro verificado: {app_number or conv_id}"})


def verificar_lista_postulaciones(driver, base_url, app_number=None, min_count=1):
    with track("verificar_lista_postulaciones", backend=True, endpoint="GET /api/applications"):
        driver.get(f"{base_url}/mis-postulaciones")
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "[data-testid^='application-card-']")) > 0
            or "No tiene postulaciones" in d.page_source
        )
        time.sleep(0.6)
        cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid^='application-card-']")
        assert len(cards) >= min_count, "La postulación no aparece en la lista"
        if app_number:
            assert any(app_number in c.text for c in cards), "Número no visible en lista"


# ---------------------------------------------------------------- tooltips
def _textos_tooltips(driver):
    pares = []
    triggers = driver.find_elements(By.CSS_SELECTOR, "[data-testid='tooltip-trigger']")
    for trg in triggers:
        try:
            ActionChains(driver).move_to_element(trg).perform()
            time.sleep(0.35)
            box = trg.find_element(By.XPATH, "./following-sibling::*[@role='tooltip']")
            txt = (box.get_attribute("textContent") or "").strip()
            pares.append((trg, txt))
        except Exception:
            pares.append((trg, ""))
    return pares


def intentar_avanzar_al_wizard(driver, base_url):
    """Avanza al wizard siempre sobre la primera convocatoria consultada.
    Retorna (conv_id, 'apply'|'blocked'). No trackea: los intentos quedan
    registrados por pulsar_ver_detalles/verificar_detalle/pulsar_registrar."""
    cards = abrir_convocatorias(driver, base_url)
    cid = primera_convocatoria(cards)
    pulsar_ver_detalles(driver, base_url, cid)
    verificar_detalle(driver, base_url, cid)
    return cid, pulsar_registrar(driver)


def abrir_wizard_directo(driver, base_url, conv_id):
    """Navegación directa al wizard. Solo para escenarios que validan UI
    (formato/peso/incompletos/sin docs) sin hacer POST. No es paso de catálogo."""
    from validacion_horizontal.flujo_residente.pages.CreateApplicationPage import CreateApplicationPage
    CreateApplicationPage(driver, base_url).open(conv_id)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, f"[data-testid='{SELECTORS['create_continue']}']"))
    )
    time.sleep(0.5)


def _ver_tooltip_con_texto(driver, step_name, fragmento):
    with track(step_name):
        pares = _textos_tooltips(driver)
        assert pares, "No hay tooltips en pantalla"
        ok = any(fragmento.lower() in (txt or "").lower() for _, txt in pares)
        assert ok, f"Ningún tooltip contiene '{fragmento}': {[t for _, t in pares]}"


def ver_tooltip_registrar(driver):
    _ver_tooltip_con_texto(driver, "ver_tooltip_registrar", "adjuntar los documentos")


def ver_tooltip_cupos(driver):
    _ver_tooltip_con_texto(driver, "ver_tooltip_cupos", "asignados")


def ver_tooltip_estado(driver):
    _ver_tooltip_con_texto(driver, "ver_tooltip_estado", "abierta")


def ver_tooltip_pazysalvo(driver):
    _ver_tooltip_con_texto(driver, "ver_tooltip_pazysalvo", "paz y salvo")


def ver_tooltip_continuar(driver):
    _ver_tooltip_con_texto(driver, "ver_tooltip_continuar", "carga de documentos")


def ver_tooltip_confirmar(driver):
    _ver_tooltip_con_texto(driver, "ver_tooltip_confirmar", "obligatorios")


def ver_tooltip_documentos(driver):
    with track("ver_tooltip_documentos"):
        pares = _textos_tooltips(driver)
        con_pdf = [t for _, t in pares if "Formato: PDF" in (t or "")]
        assert con_pdf, "Ningún tooltip de documento con 'Formato: PDF'"


# ---------------------------------------------------------------- errores
def cargar_archivo_formato_erroneo(driver):
    import tempfile
    with track("cargar_archivo_formato_erroneo"):
        fd, path = tempfile.mkstemp(suffix=".txt")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("esto no es un pdf")
            subir_archivo_a_tipo(driver, REQUIRED_DOC_CODES[0], path)
        finally:
            try:
                os.unlink(path)
            except Exception:
                pass


def verificar_error_formato(driver):
    with track("verificar_error_formato"):
        assert "Solo se permiten archivos PDF" in driver.page_source, "Falta mensaje de formato"


def cargar_archivo_pesado(driver):
    import tempfile
    with track("cargar_archivo_pesado"):
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        try:
            make_pdf(path, size_bytes=MAX_DOC_BYTES + 512 * 1024)
            subir_archivo_a_tipo(driver, REQUIRED_DOC_CODES[0], path, timeout=10)
        finally:
            try:
                os.unlink(path)
            except Exception:
                pass


def verificar_error_peso(driver):
    with track("verificar_error_peso"):
        assert "excede el tamaño máximo" in driver.page_source, "Falta mensaje de peso"


def verificar_bloqueo_incompleto(driver, base_url):
    from validacion_horizontal.flujo_residente.pages.CreateApplicationPage import CreateApplicationPage
    with track("verificar_bloqueo_incompleto"):
        page = CreateApplicationPage(driver, base_url)
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f"[data-testid='{SELECTORS['create_submit']}']"))
        )
        assert not page.is_submit_enabled(), "Confirmar no debería habilitarse incompleto"


def verificar_bloqueo_sin_docs(driver, base_url):
    from validacion_horizontal.flujo_residente.pages.CreateApplicationPage import CreateApplicationPage
    with track("verificar_bloqueo_sin_docs"):
        page = CreateApplicationPage(driver, base_url)
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f"[data-testid='{SELECTORS['create_submit']}']"))
        )
        assert not page.is_submit_enabled(), "Confirmar no debería habilitarse sin documentos"
