import pytest

from shared.steps import common


@pytest.mark.dc_postulacion
@pytest.mark.euv10
def test_euv10_listado_corresponde_al_usuario(driver, base_url, env, api_check_result):
    """EUV_10: Mis Postulaciones muestra exactamente las postulaciones del
    usuario logueado (cruce UI vs API + un solo residentId)."""
    common.login_como_residente(driver, base_url)
    common.verificar_ingreso(driver)

    cards = common.abrir_mis_postulaciones(driver, base_url)
    if not cards:
        # Autocontenido: crea una postulación base y vuelve al listado
        conv_id, via = common.intentar_avanzar_al_wizard(driver, base_url)
        assert via == "apply" and conv_id, "No se pudo crear postulación base"
        common.pulsar_continuar(driver, base_url)
        common.cargar_documentos_validos(driver)
        common.pulsar_confirmar(driver, base_url)
        common.verificar_resumen(driver)
        cards = common.abrir_mis_postulaciones(driver, base_url)
    assert cards, "No hay postulaciones ni se pudo crear una"

    api_items = common.obtener_postulaciones_api(base_url, env, api_check_result)
    common.verificar_titularidad_lista(driver, api_items, solo_ui=(env == "prod"))
