from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from shared.pages.BasePage import BasePage
from validacion_horizontal.flujo_residente.properties import SELECTORS
import time
import os


class ConvocationsPage(BasePage):
    def open(self):
        return self.go("/convocations")

    def get_cards(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "[data-testid^='convocation-card-']")

    def click_view_details(self, conv_id):
        el = self.find_clickable(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['convocation_view_details_prefix']}{conv_id}']")
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", el)
        except Exception:
            pass
        time.sleep(int(os.getenv("SLOW_MO_MS", "700")) / 1000.0 / 2)
        self.driver.execute_script("arguments[0].click();", el)
        try:
            WebDriverWait(self.driver, 8).until(lambda d: f"/convocations/{conv_id}" in d.current_url)
        except Exception:
            pass
        time.sleep(0.5)
        return self
