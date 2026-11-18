# Method and Tool Reference

## Configuration

### `AmazonSettings`

**File:** `config/config.py`

**Purpose:** Validates environment variables and exposes strongly typed framework settings.

**Why Pydantic:** Pydantic prevents invalid booleans, unsupported browser names, and malformed numeric values from reaching browser setup.

**Pros**

- Type-safe settings.
- `.env` support.
- Clear validation failures.

**Cons**

- Extra dependency.
- Environment aliases require careful naming.

**Use**

```powershell
copy .env.example .env
pytest --environment=india --base-url=https://www.amazon.in
```

### `apply_environment_yaml()`

**Purpose:** Loads a named regional profile and overlays URL, locale, timezone, viewport, and headless settings.

**Use**

```powershell
pytest --environment=india
```

## BasePage

**File:** `pages/base_page.py`

`BasePage` wraps Playwright operations so every page receives consistent waiting, default timeout, screenshot, and Allure behavior.

### Navigation

| Method | Purpose | Why it exists |
|---|---|---|
| `navigate_to(url)` | Navigate with DOM-ready synchronization | Uses Playwright navigation instead of fixed waits |
| `reload_page()` | Reload current page | Centralizes wait behavior |
| `go_back()` | Browser back navigation | Supports journey history |
| `wait_for_page_load()` | Wait for DOM ready | Avoids document timing assumptions |
| `get_current_url()` | Return active URL | Supports route assertions |
| `get_page_title()` | Return document title | Supports page-state assertions |

**Pros:** consistent navigation and timeouts. **Cons:** generic wrappers can hide unsupported navigation edge cases.

### Interactions

| Method | Purpose |
|---|---|
| `click_element(selector)` | Visible click through Playwright |
| `double_click(selector)` | Double-click interaction |
| `hover_element(selector)` | Hover menus or cards |
| `fill_text(selector, text)` | Replace input value |
| `type_slowly(selector, text, delay_ms)` | Human-like typing |
| `clear_and_fill(selector, text)` | Clear then fill |
| `press_key(selector, key)` | Keyboard input |
| `select_dropdown_by_value(value)` | Select by HTML value |
| `select_dropdown_by_label(label)` | Select by visible label |
| `check_checkbox(selector)` | Idempotent checkbox selection |
| `uncheck_checkbox(selector)` | Idempotent checkbox clearing |
| `upload_file(selector, path)` | Set input file |

`type_slowly` adds a configurable delay between keystrokes. It is a resilience aid, not a guarantee against bot detection.

### Smart Waits

| Method | Purpose |
|---|---|
| `wait_for_visible(selector)` | Web-first visible assertion |
| `wait_for_hidden(selector)` | Wait until detached or hidden |
| `wait_for_url_contains(text)` | Wait for expected URL glob |
| `is_element_visible(selector)` | Immediate boolean state check |
| `is_element_enabled(selector)` | Immediate enabled check |
| `get_element_count(selector)` | Locator count |

### Data Extraction

| Method | Purpose |
|---|---|
| `get_text(selector)` | Visible text |
| `get_all_texts(selector)` | Text list |
| `get_attribute(selector, name)` | Attribute value |
| `get_input_value(selector)` | Input value |
| `parse_price_to_float(value)` | Remove symbols and parse a price |

`parse_price_to_float` is designed for display prices. Regional formatting with decimal commas must be handled explicitly before extending it.

### Advanced Browser Handling

| Method | Purpose |
|---|---|
| `scroll_to_element(selector)` | Scroll locator into view |
| `scroll_to_bottom()` | Scroll document bottom |
| `switch_to_new_tab(previous_count)` | Focus a newly opened page |
| `handle_alert(action, prompt_text)` | Accept or dismiss a browser dialog |
| `switch_to_iframe(selector)` | Return a Playwright frame |
| `take_screenshot(name, full_page)` | Save and attach Allure screenshot |
| `dismiss_cookie_or_location_popup()` | Dismiss common consent/location controls |

**Pros:** centralizes iframe, tabs, alerts, scrolling, and screenshot behavior. **Cons:** browser APIs can vary by context; only add wrappers after a real need.

## HomePage

**File:** `pages/home_page.py`

| Method | Purpose |
|---|---|
| `open()` | Navigate home and dismiss common popup |
| `detect_bot_challenge()` | Detect Continue shopping/CAPTCHA text |
| `handle_bot_challenge(skip=True)` | Skip or raise `BotChallengeDetected` |
| `search(term)` | Enter term and navigate to search results |

**Why:** Amazon can block automation. Detection prevents misleading CSS or timeout failures.

**Pros:** clean skips and domain-specific diagnostics. **Cons:** challenge text can vary by locale.

## SearchResultsPage

**File:** `pages/search_results_page.py`

| Method | Purpose |
|---|---|
| `wait_for_results()` | Wait for first search card |
| `get_product_cards(limit)` | Extract title, URL, and price |
| `sort_by(label)` | Sort visible results |
| `filter_prime()` | Apply Prime filter |
| `filter_brand(brand)` | Apply accessible brand checkbox |
| `filter_rating(minimum)` | Apply a star filter |
| `open_product(index)` | Open a product and return detail page |
| `next_page()` | Navigate to next result page |

**Pros:** stable product-card extraction. **Cons:** Amazon markup changes and regional card variants may require robust fallbacks.

## ProductDetailPage

**File:** `pages/product_detail_page.py`

| Method | Purpose |
|---|---|
| `title()` | Read product title |
| `price()` | Parse visible price |
| `is_available()` | Infer stock state |
| `select_size(label)` | Select size variant |
| `select_color(label)` | Select color variant |
| `add_to_cart()` | Add item and return cart page |
| `buy_now()` | Start Buy Now journey |

**Use safely:** never execute authenticated checkout transactions with real credentials or payment.

## CartPage

**File:** `pages/cart_page.py`

| Method | Purpose |
|---|---|
| `open()` | Open cart route |
| `subtotal()` | Parse cart subtotal |
| `item_count()` | Count active cart items |
| `update_quantity(quantity, index)` | Change item quantity |
| `delete_item(index)` | Remove item |
| `can_proceed_to_checkout()` | Verify checkout action exists |

**Pros:** covers quantity and subtotal consistency. **Cons:** cart markup varies and account state can affect availability.

## Data and Utilities

### `DataLoader`

**Purpose:** Loads JSON/CSV and creates Faker-derived dynamic values.

**Pros:** external and repeatable data. **Cons:** random data must be seeded for deterministic failures.

### `ApiHelper`

**Purpose:** Lightweight HTTP status verification using Requests.

**Why Requests:** API checks remain simple and avoid browser overhead.

**Pros:** fast reachability validation and HTTP reuse.

**Cons:** it does not mock or authenticate Amazon private APIs.

### `logger`

**Purpose:** Writes color-coded console output and rotating ZIP-compressed log files.

**Pros:** structured operation logs and bounded disk usage.

**Cons:** async enqueue behavior can require process flush on abrupt termination.

### Custom exceptions

- `FrameworkException`: base framework error
- `BotChallengeDetected`: automated traffic challenge
- `InvalidSearchResult`: required product unavailable
- `CartConsistencyError`: cart state mismatch

**Pros:** errors explain business meaning.

**Cons:** exceptions must be caught at the correct journey level.

## Pytest and Playwright Tools

| Tool | Why used | Pros | Cons |
|---|---|---|---|
| Playwright | Real browser automation | Web-first locators, tracing, video | Live site changes |
| pytest-playwright | Browser/context fixtures | Clean lifecycle | Some options conflict with custom context setup |
| xdist | Parallel test runs | Faster CI | Shared state and live-site blocks |
| rerunfailures | Retry flaky runs | Handles transient failures | Can hide real defects if overused |
| pytest-html | Standalone HTML report | Easy artifact viewing | Less detailed than Allure |
| Allure | Rich report | Steps and attachments | Requires Allure CLI to render locally |
| Pydantic | Settings validation | Typed fail-fast config | Alias complexity |
| python-dotenv | `.env` loading | Local secret convenience | Never commit `.env` |
| Loguru | Logging | Minimal setup and rotation | Less ecosystem standard than stdlib logging |
| Faker | Dynamic test data | Realistic inputs | Needs seed for reproducibility |
| Requests | API checks | Lightweight HTTP | No Playwright browser identity |

## Common Commands

```powershell
py -3.13 -m pytest --collect-only
py -3.13 -m pytest tests/smoke/test_amazon_smoke.py
py -3.13 -m pytest tests/regression -n 2 --reruns 1
py -3.13 -m pytest --headed --browser-name=chromium
py -3.13 -m pytest --environment=india --base-url=https://www.amazon.in
py -3.13 -m pytest --alluredir=reports/allure-results
```
