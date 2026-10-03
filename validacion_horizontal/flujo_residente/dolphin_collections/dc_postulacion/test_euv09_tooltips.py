import pytest

from shared.steps import common


@pytest.mark.dc_postulacion
@pytest.mark.euv09
def test_euv09_postulacion_usando_tooltips(driver, base_url, env, api_check_result):
    """Postulación abriendo todos los tooltips. Si ninguna convocatoria está
    libre, verifica tooltips alcanzables + bloqueo (ruta adaptativa)."""
    common.login_como_residente(driver, base_url)
    common.verificar_ingreso(driver)

    conv_id, via = common.intentar_avanzar_al_wizard(driver, base_url)
    assert conv_id, "No hay convocatorias abiertas"

    if via == "blocked":
        # Ruta B: todo bloqueado; tooltips del detalle + bloqueo
        common.ver_tooltip_registrar(driver)
        common.ver_tooltip_cupos(driver)
        common.ver_tooltip_estado(driver)
        common.verificar_mensaje_bloqueo(driver)
        common.verificar_registro_api(base_url, env, api_check_result, conv_id)
        common.verificar_lista_postulaciones(driver, base_url)
        return

    # Ruta A: postulación completa usando tooltips.
    # Los tooltips del detalle se verifican volviendo atrás (el wizard ya avanzó).
    driver.back()
    common.verificar_detalle(driver, base_url, conv_id)
    common.ver_tooltip_registrar(driver)
    common.ver_tooltip_cupos(driver)
    common.ver_tooltip_estado(driver)
    assert common.pulsar_registrar(driver) == "apply"
    common.ver_tooltip_pazysalvo(driver)
    common.ver_tooltip_continuar(driver)
    common.pulsar_continuar(driver, base_url)
    common.ver_tooltip_documentos(driver)
    common.ver_tooltip_confirmar(driver)
    common.cargar_licencia_transito(driver)
    common.cargar_soat(driver)
    common.cargar_licencia_conduccion(driver)
    common.pulsar_confirmar(driver, base_url)
    app_number = common.verificar_resumen(driver)
    common.verificar_registro_api(base_url, env, api_check_result, conv_id, app_number)
    common.verificar_lista_postulaciones(driver, base_url, app_number)
