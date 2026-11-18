# Amazon Playwright Framework - Architecture

## 1. Executive Summary

This repository is a production-oriented UI and API test automation framework for Amazon regional domains. It uses Python, Playwright's synchronous API, Pytest, Pydantic, Loguru, Allure, and Requests.

The main design goal is maintainability: tests describe business journeys, page objects describe Amazon surfaces, `BasePage` describes browser operations, and configuration fixtures control environment and lifecycle behavior.

## 2. Architecture Overview

```text
Test cases
    |
    v
Pytest fixtures + Pydantic configuration
    |
    v
Page Object Model
    |
    v
BasePage browser abstraction
    |
    v
Playwright Sync API
```

Supporting concerns:

- External test data: `test_data/products.json`
- Dynamic data: Faker through `DataLoader`
- HTTP validation: `ApiHelper`
- Structured logs: Loguru
- Rich diagnostics: Allure, screenshots, videos, and traces
- CI execution: GitHub Actions with parallel tests

## 3. Design Patterns

### Page Object Model

Page classes isolate Amazon locators and interactions. Tests call methods such as `home.search(...)` instead of browser selectors.

**Pros**

- Reduces selector duplication.
- Keeps tests focused on behavior.
- Makes locator changes smaller and safer.

**Cons**

- Poorly designed page objects become large "god classes."
- Page objects can leak low-level assertions into test code.

**Mitigation**

- Use `BasePage` for generic browser operations.
- Keep a page object responsible for one Amazon surface.
- Return the next page object from navigation methods.

### Dependency Injection

Pytest fixtures inject `page`, `amazon_settings`, and `api_helper`.

**Pros**

- Central browser lifecycle.
- Explicit dependencies in tests.
- Environment changes do not require test rewrites.

**Cons**

- Excessive fixtures can hide setup complexity.

**Mitigation**

- Keep fixtures in `tests/conftest.py`.
- Expose only dependencies needed by tests.

### Factory / Navigation Pattern

Methods such as `HomePage.search()` create and return `SearchResultsPage`. `SearchResultsPage.open_product()` creates `ProductDetailPage`.

**Pros**

- Makes journeys readable.
- Gives each returned page the correct business context.

**Cons**

- It is easy to blur navigation and action responsibilities.

**Mitigation**

- Navigation methods return page objects.
- Data extraction methods return typed or plain Python values.

### Configuration as Code

`AmazonSettings` merges `.env`, CLI overrides, and `environments.yaml`.

**Pros**

- Typed and validated configuration.
- Same test suite works across regions.
- No credentials committed to source control.

**Cons**

- Multiple override sources can be difficult to debug.

**Mitigation**

- Define and document precedence.
- Log the selected environment and region at session start.

## 4. Configuration Precedence

Highest to lowest:

1. CLI options
2. Environment variables
3. `environments.yaml`
4. Pydantic defaults

Use `AMAZON_ENV=india` for regional settings or pass `--base-url=https://www.amazon.in`.

## 5. Bot and Regional Resilience

Amazon detects automated traffic in some regions. The framework recognizes common interstitial or challenge markers and converts them into clean test skips where appropriate.

Design rules:

- Never use fixed `time.sleep()` calls.
- Prefer Playwright web-first assertions.
- Continue shopping/CAPTCHA states are environment blocks, not selector regressions.
- Reduce false failures with realistic viewport, locale, timezone, and user agent configuration.

## 6. Failure Diagnostics

The failure hook captures:

- Full-page PNG screenshot
- Playwright `.zip` trace
- Recorded WebM video
- All three artifacts are attached to Allure

This is intentionally failure-oriented to avoid unnecessary report size.

## 7. CI/CD

GitHub Actions:

- Checks out source.
- Creates Python 3.11.
- Installs dependencies and Chromium.
- Executes tests with xdist and reruns.
- Produces HTML and Allure output.
- Uploads `reports/` as a workflow artifact.

Live Amazon tests can be region-blocked. CI policy should therefore treat clean bot skips as environmental limitations and gate code-level failures separately.

