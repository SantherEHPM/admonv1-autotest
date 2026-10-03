"""
Recurso reutilizable "Igual que" (Enjisst §5.8.1): secuencia de login
compartida por todos los EUVs que requieren sesión, sin duplicar pasos.
Lee selectores y credenciales del properties de la Suite.
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from shared.pages.BasePage import BasePage, _human_delay, _highlight
from validacion_horizontal.flujo_residente.properties import SELECTORS, TEST_USER


def login_as_resident(driver, base_url, timeout=10):
    page = BasePage(driver, base_url, timeout)
    page.go("/login")
    _human_delay()
    page.find_visible(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_form']}']")

    email_el = page.find_visible(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_email']}']")
    _highlight(email_el, driver)
    email_el.clear()
    _human_delay()
    for ch in TEST_USER["email"]:
        email_el.send_keys(ch)
        time.sleep(0.05)
    _human_delay()

    pwd_el = page.find_visible(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_password']}']")
    _highlight(pwd_el, driver)
    pwd_el.clear()
    _human_delay()
    for ch in TEST_USER["password"]:
        pwd_el.send_keys(ch)
        time.sleep(0.05)
    _human_delay()

    btn = page.find_visible(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_submit']}']")
    _highlight(btn, driver)
    _human_delay()
    page.click(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_submit']}']")

    navbar = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, f"[data-testid='{SELECTORS['navbar']}']"))
    )
    _highlight(navbar, driver)
    _human_delay()
    return page
