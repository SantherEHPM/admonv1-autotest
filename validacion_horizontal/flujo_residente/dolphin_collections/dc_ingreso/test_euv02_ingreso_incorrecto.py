import pytest

from shared.steps import common
from validacion_horizontal.flujo_residente.properties import WRONG_USER


@pytest.mark.dc_ingreso
@pytest.mark.euv02
def test_euv02_ingreso_credenciales_incorrectas(driver, base_url):
    common.abrir_pagina_login(driver, base_url)
    common.escribir_email(driver, WRONG_USER["email"])
    common.escribir_password(driver, WRONG_USER["password"])
    common.pulsar_ingresar(driver)
    common.verificar_rechazo_login(driver)
