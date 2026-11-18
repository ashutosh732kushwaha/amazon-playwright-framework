"""Amazon product detail page object."""
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.custom_exceptions import InvalidSearchResult


class ProductDetailPage(BasePage):
    TITLE = "#productTitle"
    PRICE = "#corePrice_feature_div .a-offscreen"
    AVAILABILITY = "#availability"
    ADD_TO_CART = "#add-to-cart-button"
    BUY_NOW = "#buy-now-button"

    def __init__(self, page: Page, base_url: str, timeout_ms: int) -> None:
        super().__init__(page, timeout_ms)
        self.base_url = base_url

    def title(self) -> str:
        return self.get_text(self.TITLE)

    def price(self) -> float:
        locator = self.page.locator(self.PRICE).first
        if locator.count() == 0:
            return 0.0
        return self.parse_price_to_float(locator.inner_text())

    def is_available(self) -> bool:
        locator = self.page.locator(self.AVAILABILITY)
        if locator.count():
            text = locator.inner_text().lower()
            return "unavailable" not in text and "currently unavailable" not in text
        return self.is_element_visible(self.ADD_TO_CART)

    @allure.step("Select size")
    def select_size(self, label: str) -> None:
        self.click_element(self.page.get_by_role("button", name=label))

    @allure.step("Select color")
    def select_color(self, label: str) -> None:
        self.click_element(self.page.get_by_role("button", name=label))

    @allure.step("Add product to cart")
    def add_to_cart(self) -> "CartPage":
        if not self.is_element_visible(self.ADD_TO_CART):
            raise InvalidSearchResult("Add to Cart is unavailable for this product")
        self.click_element(self.ADD_TO_CART)
        self.page.wait_for_load_state("domcontentloaded")
        from pages.cart_page import CartPage
        return CartPage(self.page, self.base_url, 30_000)

    @allure.step("Click Buy Now")
    def buy_now(self) -> None:
        self.click_element(self.BUY_NOW)
