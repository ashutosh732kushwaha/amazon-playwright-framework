"""Amazon cart page object."""
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage


class CartPage(BasePage):
    SUBTOTAL = "#sc-subtotal-amount-activecart"
    CART_ITEMS = "[data-name='Active Items'] [data-asin]"
    QUANTITY_SELECT = "select[name*='quantity']"
    DELETE_BUTTON = "input[value='Delete'], button:has-text('Delete')"
    PROCEED = "[name='proceedToRetailCheckout'], [name='proceedToCheckout']"

    def __init__(self, page: Page, base_url: str, timeout_ms: int) -> None:
        super().__init__(page, timeout_ms)
        self.base_url = base_url

    def open(self) -> "CartPage":
        self.navigate_to(f"{self.base_url}/gp/cart/view.html")
        return self

    def subtotal(self) -> float:
        locator = self.page.locator(self.SUBTOTAL).first
        if locator.count() == 0:
            return 0.0
        return self.parse_price_to_float(locator.inner_text())

    def item_count(self) -> int:
        return self.page.locator(self.CART_ITEMS).count()

    @allure.step("Update quantity")
    def update_quantity(self, quantity: int, item_index: int = 0) -> None:
        select = self.page.locator(self.QUANTITY_SELECT).nth(item_index)
        select.select_option(str(quantity))
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("Delete cart item")
    def delete_item(self, item_index: int = 0) -> None:
        item = self.page.locator(self.CART_ITEMS).nth(item_index)
        item.locator(self.DELETE_BUTTON).first.click()

    def can_proceed_to_checkout(self) -> bool:
        return self.is_element_visible(self.PROCEED)
