import pytest

from shared.steps import common


@pytest.mark.dc_postulacion
@pytest.mark.euv03
def test_euv03_postulacion_normal_con_verificacion(driver, base_url, env, api_check_result):
    common.login_como_residente(driver, base_url)
    common.verificar_ingreso(driver)

    conv_id, via = common.intentar_avanzar_al_wizard(driver, base_url)
    assert via == "apply" and conv_id, "Ninguna convocatoria permite postular (todas bloqueadas)"
    common.pulsar_continuar(driver, base_url)
    common.cargar_licencia_transito(driver)
    common.cargar_soat(driver)
    common.cargar_licencia_conduccion(driver)
    common.pulsar_confirmar(driver, base_url)
    app_number = common.verificar_resumen(driver)
    common.verificar_registro_api(base_url, env, api_check_result, conv_id, app_number)
    common.verificar_lista_postulaciones(driver, base_url, app_number)
