from selenium.webdriver.common.by import By
from shared.pages.BasePage import BasePage
from validacion_horizontal.flujo_residente.properties import SELECTORS


class ConvocationDetailPage(BasePage):
    def open(self, conv_id):
        return self.go(f"/convocations/{conv_id}")

    def is_register_button_enabled(self):
        btn = self.find(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['convocation_register_button']}']")
        return btn.is_enabled()

    def get_eligibility_message(self):
        if self.is_visible(By.CLASS_NAME, SELECTORS["eligibility_message_class"], timeout=3):
            return self.find(By.CLASS_NAME, SELECTORS["eligibility_message_class"]).text
        return None
