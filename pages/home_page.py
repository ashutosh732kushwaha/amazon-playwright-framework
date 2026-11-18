"""Amazon home page object."""
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.custom_exceptions import BotChallengeDetected
from utils.logger import logger


class HomePage(BasePage):
    SEARCH_BOX = "#twotabsearchtextbox"
    SEARCH_BUTTON = "#nav-search-submit-button"
    LOCATION_LINK = "#nav-global-location-popover-link"
    CAPTCHA_HEADINGS = (
        "text=/Continue shopping|Type the characters|Enter the characters|"
        "Sorry, we just need to make sure you're not a robot|automated access/i"
    )
    ACCOUNT_MENU = "#nav-link-accountList"

    def __init__(self, page: Page, base_url: str, timeout_ms: int) -> None:
        super().__init__(page, timeout_ms)
        self.base_url = base_url
        self.timeout_ms = timeout_ms

    @allure.step("Open Amazon home page")
    def open(self) -> "HomePage":
        self.navigate_to(self.base_url)
        self.dismiss_cookie_or_location_popup()
        return self

    def detect_bot_challenge(self) -> bool:
        challenge = self.page.locator(self.CAPTCHA_HEADINGS).first
        captcha_form = self.page.locator(
            "#captchacharacters, form[action*='validateCaptcha']"
        ).first
        challenge_url = "/checkpoint/" in self.page.url.lower()
        if (
            challenge_url
            or challenge.is_visible(timeout=750)
            or captcha_form.is_visible(timeout=750)
        ):
            logger.warning("Amazon bot/CAPTCHA interstitial detected; test journey skipped.")
            allure.attach("Amazon bot/CAPTCHA interstitial detected", "Bot resilience",
                           allure.attachment_type.TEXT)
            return True
        return False

    def handle_bot_challenge(self, skip: bool = True) -> None:
        if self.detect_bot_challenge():
            if skip:
                raise BotChallengeDetected("Amazon displayed a CAPTCHA or Continue shopping page")

    @allure.step("Search for '{term}'")
    def search(self, term: str) -> "SearchResultsPage":
        self.handle_bot_challenge()
        search = self.wait_for_visible(self.SEARCH_BOX)
        search.fill("")
        self.type_slowly(search, term)
        self.click_element(self.SEARCH_BUTTON)
        self.page.wait_for_load_state("domcontentloaded")
        if self.detect_bot_challenge():
            raise BotChallengeDetected("Amazon redirected to a CAPTCHA checkpoint")
        self.wait_for_url_contains("s?")
        from pages.search_results_page import SearchResultsPage
        return SearchResultsPage(self.page, self.base_url, self.timeout_ms)
