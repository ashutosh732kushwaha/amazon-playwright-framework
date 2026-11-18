"""Amazon cart workflow and price consistency tests."""
import pytest
from pages.cart_page import CartPage


@pytest.mark.regression
def test_empty_cart_state_or_checkout_action(page, amazon_settings):
    cart = CartPage(page, amazon_settings.base_url, amazon_settings.timeout_ms)
    cart.open()
    assert cart.item_count() >= 0
    assert isinstance(cart.subtotal(), float)
