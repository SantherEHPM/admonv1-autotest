import pytest

from shared.steps import common


@pytest.mark.dc_postulacion
@pytest.mark.euv11
def test_euv11_cancelar_postulacion(driver, base_url, env, api_check_result):
    """EUV_11: cancelar una postulación REGISTERED desde su detalle con
    confirmación en modal; verifica estado Cancelada en UI, API y lista."""
    common.login_como_residente(driver, base_url)
    common.verificar_ingreso(driver)

    # Garantizar base cancelable en la primera convocatoria (autocontenido)
    conv_id, via = common.intentar_avanzar_al_wizard(driver, base_url)
    assert conv_id, "No hay convocatorias consultadas"
    if via == "apply":
        common.pulsar_continuar(driver, base_url)
        common.cargar_documentos_validos(driver)
        common.pulsar_confirmar(driver, base_url)
        common.verificar_resumen(driver)

    cards = common.abrir_mis_postulaciones(driver, base_url)
    assert cards, "No hay postulaciones ni se pudo crear una"
    app_id = cards[0].get_attribute("data-testid").replace("application-card-", "")
    common.abrir_detalle_postulacion(driver, app_id)

    if common.tiene_boton_cancelar(driver):
        common.pulsar_cancelar_postulacion(driver)
        common.confirmar_cancelacion(driver)
    else:
        # Ya cancelada (re-ejecución): se valida el estado final alcanzado
        assert "Cancelada" in driver.page_source, "Sin botón ni estado Cancelada"

    common.verificar_cancelacion_api(base_url, env, api_check_result, app_id)
    common.verificar_estado_cancelada_lista(driver, base_url)
