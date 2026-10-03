from selenium.webdriver.common.by import By
from shared.pages.BasePage import BasePage
from validacion_horizontal.flujo_residente.properties import SELECTORS


class LoginPage(BasePage):
    def open(self):
        return self.go("/login")

    def login(self, email, password):
        self.type(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_email']}']", email)
        self.type(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_password']}']", password)
        self.click(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_submit']}']")
        return self

    def has_error(self):
        return self.is_visible(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['login_error']}']", timeout=3)

    def is_navbar_visible(self):
        return self.is_visible(By.CSS_SELECTOR, f"[data-testid='{SELECTORS['navbar']}']", timeout=5)
