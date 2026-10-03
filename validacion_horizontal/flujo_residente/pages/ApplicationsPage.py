from selenium.webdriver.common.by import By
from shared.pages.BasePage import BasePage
from validacion_horizontal.flujo_residente.properties import SELECTORS


class ApplicationsPage(BasePage):
    def open(self):
        return self.go("/mis-postulaciones")

    def get_cards(self):
        return self.driver.find_elements(By.CSS_SELECTOR, f"[data-testid^='{SELECTORS['application_card_prefix']}']")
