"""Pytest fixtures, browser lifecycle, CLI overrides, and failure artifacts."""
from pathlib import Path
from typing import Generator
import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page
from config.config import AmazonSettings, settings
from utils.api_helper import ApiHelper
from utils.logger import logger


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--environment", action="store", default=None)
    parser.addoption("--browser-name", action="store", choices=["chromium", "firefox", "webkit"], default=None)


@pytest.fixture(scope="session")
def amazon_settings(request: pytest.FixtureRequest) -> AmazonSettings:
    runtime = AmazonSettings()
    runtime.apply_environment_yaml()
    environment = request.config.getoption("--environment")
    base_url = request.config.getoption("--base-url")
    if environment:
        runtime.env = environment
        runtime.apply_environment_yaml()
    if base_url:
        runtime.base_url = base_url
    if request.config.getoption("--headed"):
        runtime.headless = False
    browser_name = request.config.getoption("--browser-name")
    if browser_name:
        runtime.browser = browser_name
    logger.info("Running Amazon framework in {} using {}", runtime.env, runtime.base_url)
    return runtime


@pytest.fixture(scope="session")
def browser_name(amazon_settings: AmazonSettings) -> str:
    return amazon_settings.browser


@pytest.fixture(scope="session")
def browser_type_launch_args(amazon_settings: AmazonSettings) -> dict:
    return {"headless": amazon_settings.headless}


@pytest.fixture(scope="session")
def browser_context_args(amazon_settings: AmazonSettings) -> dict:
    return {
        "viewport": {"width": amazon_settings.viewport_width, "height": amazon_settings.viewport_height},
        "locale": amazon_settings.locale,
        "timezone_id": amazon_settings.timezone,
        "user_agent": amazon_settings.user_agent,
        "ignore_https_errors": True,
        "record_video_dir": str(Path(__file__).resolve().parents[1] / "reports" / "videos"),
        "record_video_size": {"width": 1280, "height": 720},
    }


@pytest.fixture
def context(browser: Browser, browser_context_args: dict) -> Generator[BrowserContext, None, None]:
    video_dir = Path(browser_context_args["record_video_dir"])
    video_dir.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(**browser_context_args)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context
    context.tracing.stop()
    context.close()


@pytest.fixture
def api_helper(amazon_settings: AmazonSettings) -> Generator[ApiHelper, None, None]:
    helper = ApiHelper(timeout=amazon_settings.timeout_ms // 1000)
    yield helper
    helper.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Generator:
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    page: Page | None = item.funcargs.get("page")
    if page is None:
        return
    reports = Path(__file__).resolve().parents[1] / "reports"
    screenshots = reports / "screenshots"
    traces = reports / "traces"
    videos = reports / "videos"
    screenshots.mkdir(parents=True, exist_ok=True)
    traces.mkdir(parents=True, exist_ok=True)
    videos.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(char if char.isalnum() or char in "-_" else "_" for char in item.name)
    screenshot_path = screenshots / f"{safe_name}.png"
    trace_path = traces / f"{safe_name}.zip"
    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
        allure.attach.file(str(screenshot_path), name="Failure screenshot",
                           attachment_type=allure.attachment_type.PNG)
        context = page.context
        context.tracing.stop(path=str(trace_path))
        allure.attach.file(str(trace_path), name="Playwright trace",
                           attachment_type="application/zip")
        if page.video:
            video_path = videos / f"{safe_name}.webm"
            page.video.save_as(str(video_path))
            allure.attach.file(str(video_path), name="Failure video",
                               attachment_type=allure.attachment_type.WEBM)
    except Exception as exc:
        logger.exception("Could not capture failure artifacts: {}", exc)
