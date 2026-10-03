import pytest

from shared.steps import common


@pytest.mark.dc_postulacion
@pytest.mark.euv07
def test_euv07_archivos_incompletos(driver, base_url):
    common.login_como_residente(driver, base_url)
    common.verificar_ingreso(driver)

    cards = common.abrir_convocatorias(driver, base_url)
    assert cards, "No hay convocatorias"
    conv_id = common.primera_convocatoria(cards)

    common.pulsar_ver_detalles(driver, base_url, conv_id)
    common.verificar_detalle(driver, base_url, conv_id)
    # Escenarios de solo-UI: si hay bloqueo por postulación existente,
    # se entra directo al wizard (no hacen POST, solo validan la UI).
    if common.pulsar_registrar(driver) == "blocked":
        common.abrir_wizard_directo(driver, base_url, conv_id)
    common.pulsar_continuar(driver, base_url)
    common.cargar_licencia_transito(driver)
    common.verificar_bloqueo_incompleto(driver, base_url)
