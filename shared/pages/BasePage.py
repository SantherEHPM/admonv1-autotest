from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import time


def _human_delay():
    raw = os.getenv("SLOW_MO_MS", "700")
    try:
        ms = int(raw)
    except Exception:
        ms = 700
    if os.getenv("HEADLESS", "false").lower() == "true":
        ms = min(ms, 100)
    time.sleep(ms / 1000.0)


def _highlight(element, driver):
    try:
        driver.execute_script(
            "arguments[0].style.outline='3px solid #1e40af';"
            "arguments[0].style.outlineOffset='2px';",
            element,
        )
        time.sleep(0.15)
    except Exception:
        pass


class BasePage:
    def __init__(self, driver, base_url, timeout=10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def go(self, path):
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        self.driver.get(url)
        _human_delay()
        return self

    def find(self, by, value):
        el = self.wait.until(EC.presence_of_element_located((by, value)))
        _highlight(el, self.driver)
        _human_delay()
        return el

    def find_clickable(self, by, value):
        el = self.wait.until(EC.element_to_be_clickable((by, value)))
        _highlight(el, self.driver)
        _human_delay()
        return el

    def find_visible(self, by, value):
        el = self.wait.until(EC.visibility_of_element_located((by, value)))
        _highlight(el, self.driver)
        _human_delay()
        return el

    def click(self, by, value):
        el = self.find_clickable(by, value)
        _human_delay()
        # Click JS: el nativo falla en silencio tras scrolls en headless.
        # La visibilidad/habilitado ya se verificó en find_clickable.
        self.driver.execute_script("arguments[0].click();", el)
        _human_delay()
        return el

    def type(self, by, value, text, clear=True):
        el = self.find_visible(by, value)
        _highlight(el, self.driver)
        if clear:
            el.clear()
            _human_delay()
        for ch in text:
            el.send_keys(ch)
            time.sleep(0.04)
        _human_delay()
        return el

    def is_visible(self, by, value, timeout=3):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((by, value)))
            return True
        except TimeoutException:
            return False
