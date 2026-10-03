import pytest

from shared.steps import common


@pytest.mark.dc_postulacion
@pytest.mark.euv04
def test_euv04_postulacion_con_postulacion_activa(driver, base_url, env, api_check_result):
    common.login_como_residente(driver, base_url)
    common.verificar_ingreso(driver)

    cards = common.abrir_convocatorias(driver, base_url)
    assert cards, "No hay convocatorias"
    conv_id = common.primera_convocatoria(cards)

    # Garantizar postulación activa (autocontenido al correr individual)
    common.pulsar_ver_detalles(driver, base_url, conv_id)
    common.verificar_detalle(driver, base_url, conv_id)
    if common.pulsar_registrar(driver) == "apply":
        common.pulsar_continuar(driver, base_url)
        common.cargar_documentos_validos(driver)
        common.pulsar_confirmar(driver, base_url)
        common.verificar_resumen(driver)
        # Segundo intento sobre la misma convocatoria
        common.abrir_convocatorias(driver, base_url)
        common.pulsar_ver_detalles(driver, base_url, conv_id)
        common.verificar_detalle(driver, base_url, conv_id)
        assert common.pulsar_registrar(driver) == "blocked", "El segundo intento debería bloquearse"

    common.verificar_mensaje_bloqueo(driver)
    common.verificar_registro_api(base_url, env, api_check_result, conv_id)
    common.verificar_lista_postulaciones(driver, base_url)
