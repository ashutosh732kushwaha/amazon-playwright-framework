"""Amazon search results page object."""
from typing import Any
import allure
from playwright.sync_api import Locator, Page
from pages.base_page import BasePage


class SearchResultsPage(BasePage):
    RESULTS = "[data-component-type='s-search-result']"
    RESULT_TITLE = "h2 a"
    RESULT_PRICE = ".a-price .a-offscreen"
    PRIME_FILTER = "li[data-csa-c-slot-id*='prime']"
    SORT_DROPDOWN = "#s-result-sort-select"
    NEXT_PAGE = "a.s-pagination-next"

    def __init__(self, page: Page, base_url: str, timeout_ms: int) -> None:
        super().__init__(page, timeout_ms)
        self.base_url = base_url

    def result_cards(self) -> Locator:
        return self.page.locator(self.RESULTS)

    def wait_for_results(self) -> None:
        self.wait_for_visible(self.RESULTS)

    def get_product_cards(self, limit: int = 10) -> list[dict[str, Any]]:
        cards = self.result_cards()
        count = min(cards.count(), limit)
        products: list[dict[str, Any]] = []
        for index in range(count):
            card = cards.nth(index)
            title_locator = card.locator(self.RESULT_TITLE)
            title = title_locator.inner_text().strip() if title_locator.count() else ""
            url = title_locator.get_attribute("href") if title_locator.count() else None
            price_locator = card.locator(self.RESULT_PRICE)
            price = price_locator.first.inner_text().strip() if price_locator.count() else ""
            products.append({"title": title, "url": url, "price": price})
        return products

    @allure.step("Sort search results")
    def sort_by(self, label: str) -> None:
        self.select_dropdown_by_label(self.SORT_DROPDOWN, label)

    @allure.step("Filter by Prime")
    def filter_prime(self) -> None:
        locator = self.page.locator("li[data-csa-c-content-id='p_85/1']").first
        locator.check() if locator.count() else self.click_element("text=Prime")

    @allure.step("Apply brand filter")
    def filter_brand(self, brand: str) -> None:
        checkbox = self.page.get_by_role("checkbox", name=brand)
        if checkbox.count():
            checkbox.first.check()

    @allure.step("Apply rating filter")
    def filter_rating(self, minimum: int) -> None:
        self.click_element(f"section:has-text('{minimum} Stars') a")

    @allure.step("Open product at index")
    def open_product(self, index: int = 0) -> "ProductDetailPage":
        card = self.result_cards().nth(index)
        card.locator(self.RESULT_TITLE).first.click()
        self.page.wait_for_load_state("domcontentloaded")
        from pages.product_detail_page import ProductDetailPage
        return ProductDetailPage(self.page, self.base_url, 30_000)

    @allure.step("Go to next search results page")
    def next_page(self) -> None:
        self.click_element(self.NEXT_PAGE)
        self.page.wait_for_load_state("domcontentloaded")
