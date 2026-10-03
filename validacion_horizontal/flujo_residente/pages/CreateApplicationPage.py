from selenium.webdriver.common.by import By
from shared.pages.BasePage import BasePage
from validacion_horizontal.flujo_residente.properties import SELECTORS


class CreateApplicationPage(BasePage):
    def open(self, conv_id):
        return self.go(f"/convocations/{conv_id}/apply")

    def click_continue(self):
        self.click(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['create_continue']}']")
        return self

    def is_submit_enabled(self):
        btn = self.find(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['create_submit']}']")
        return btn.is_enabled()

    def click_submit(self):
        self.click(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['create_submit']}']")
        return self
