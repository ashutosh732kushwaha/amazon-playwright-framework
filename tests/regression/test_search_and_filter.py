"""Data-driven Amazon search and filter tests."""
import pytest
from utils.custom_exceptions import BotChallengeDetected
from pages.home_page import HomePage
from test_data.data_loader import DataLoader


DATA = DataLoader().json("products.json")


@pytest.mark.regression
@pytest.mark.parametrize("search", DATA["searches"], ids=lambda value: value["term"])
def test_search_returns_product_cards(page, amazon_settings, search):
    home = HomePage(page, amazon_settings.base_url, amazon_settings.timeout_ms)
    home.open()
    try:
        results = home.search(search["term"])
    except BotChallengeDetected:
        pytest.skip("Amazon bot/CAPTCHA interstitial detected")
    if home.detect_bot_challenge():
        pytest.skip("Amazon bot/CAPTCHA interstitial detected")
    results.wait_for_results()
    cards = results.get_product_cards(limit=5)
    assert cards
    assert all(card["title"] for card in cards)


@pytest.mark.regression
@pytest.mark.parametrize("term", ["!!!", "a"], ids=["punctuation", "short-term"])
def test_edge_search_does_not_crash(page, amazon_settings, term):
    home = HomePage(page, amazon_settings.base_url, amazon_settings.timeout_ms)
    home.open()
    try:
        results = home.search(term)
    except BotChallengeDetected:
        pytest.skip("Amazon bot/CAPTCHA interstitial detected")
    assert results.get_current_url().startswith(amazon_settings.base_url)
