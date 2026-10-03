import pytest

from shared.steps import common
from validacion_horizontal.flujo_residente.properties import TEST_USER


@pytest.mark.dc_ingreso
@pytest.mark.euv01
def test_euv01_ingreso_credenciales_correctas(driver, base_url):
    common.abrir_pagina_login(driver, base_url)
    common.escribir_email(driver, TEST_USER["email"])
    common.escribir_password(driver, TEST_USER["password"])
    common.pulsar_ingresar(driver)
    common.verificar_ingreso(driver)
