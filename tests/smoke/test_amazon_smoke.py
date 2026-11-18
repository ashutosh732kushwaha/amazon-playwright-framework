"""Critical Amazon smoke journeys."""
import re
import pytest
from playwright.sync_api import expect
from pages.home_page import HomePage
from pages.cart_page import CartPage
from utils.custom_exceptions import BotChallengeDetected


@pytest.mark.smoke
def test_amazon_homepage_loads(page, amazon_settings):
    home = HomePage(page, amazon_settings.base_url, amazon_settings.timeout_ms)
    home.open()
    if home.detect_bot_challenge():
        pytest.skip("Amazon bot/CAPTCHA interstitial detected")
    expect(page).to_have_title(re.compile(r".*Amazon.*"))


@pytest.mark.smoke
def test_amazon_search_smoke(page, amazon_settings):
    home = HomePage(page, amazon_settings.base_url, amazon_settings.timeout_ms)
    home.open()
    try:
        results = home.search("wireless headphones")
    except BotChallengeDetected:
        pytest.skip("Amazon bot/CAPTCHA interstitial detected")
    results.wait_for_results()
    assert results.get_element_count(results.RESULTS) >= 1


@pytest.mark.smoke
def test_api_base_url_is_reachable(api_helper, amazon_settings):
    assert api_helper.verify_status(amazon_settings.base_url) is True
