"""Reusable Playwright wrapper with web-first waits and Allure steps."""
from pathlib import Path
from typing import Literal
import allure
from playwright.sync_api import Dialog, Frame, Locator, Page, expect


LocatorSpec = str | Locator


class BasePage:
    def __init__(self, page: Page, timeout_ms: int = 30_000) -> None:
        self.page = page
        self.page.set_default_timeout(timeout_ms)
        self.page.set_default_navigation_timeout(timeout_ms)

    def locator(self, selector: LocatorSpec) -> Locator:
        return selector if isinstance(selector, Locator) else self.page.locator(selector)

    @allure.step("Navigate to {url}")
    def navigate_to(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")

    @allure.step("Reload page")
    def reload_page(self) -> None:
        self.page.reload(wait_until="domcontentloaded")

    @allure.step("Navigate back")
    def go_back(self) -> None:
        self.page.go_back(wait_until="domcontentloaded")

    @allure.step("Wait for page load")
    def wait_for_page_load(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")

    def get_current_url(self) -> str:
        return self.page.url

    def get_page_title(self) -> str:
        return self.page.title()

    @allure.step("Click element")
    def click_element(self, selector: LocatorSpec) -> None:
        loc = self.locator(selector)
        expect(loc).to_be_visible()
        loc.click()

    @allure.step("Double click element")
    def double_click(self, selector: LocatorSpec) -> None:
        loc = self.locator(selector)
        expect(loc).to_be_visible()
        loc.dblclick()

    @allure.step("Hover element")
    def hover_element(self, selector: LocatorSpec) -> None:
        loc = self.locator(selector)
        expect(loc).to_be_visible()
        loc.hover()

    @allure.step("Fill text")
    def fill_text(self, selector: LocatorSpec, text: str) -> None:
        loc = self.locator(selector)
        expect(loc).to_be_visible()
        loc.fill(text)

    @allure.step("Type slowly")
    def type_slowly(self, selector: LocatorSpec, text: str, delay_ms: int = 45) -> None:
        loc = self.locator(selector)
        expect(loc).to_be_visible()
        loc.click()
        loc.type(text, delay=delay_ms)

    @allure.step("Clear and fill")
    def clear_and_fill(self, selector: LocatorSpec, text: str) -> None:
        loc = self.locator(selector)
        expect(loc).to_be_visible()
        loc.fill("")
        loc.fill(text)

    @allure.step("Press key")
    def press_key(self, selector: LocatorSpec, key: str) -> None:
        loc = self.locator(selector)
        expect(loc).to_be_visible()
        loc.press(key)

    @allure.step("Select dropdown by value")
    def select_dropdown_by_value(self, selector: LocatorSpec, value: str) -> None:
        loc = self.locator(selector)
        expect(loc).to_be_visible()
        loc.select_option(value=value)

    @allure.step("Select dropdown by label")
    def select_dropdown_by_label(self, selector: LocatorSpec, label: str) -> None:
        loc = self.locator(selector)
        expect(loc).to_be_visible()
        loc.select_option(label=label)

    @allure.step("Check checkbox")
    def check_checkbox(self, selector: LocatorSpec) -> None:
        loc = self.locator(selector)
        loc.check()

    @allure.step("Uncheck checkbox")
    def uncheck_checkbox(self, selector: LocatorSpec) -> None:
        loc = self.locator(selector)
        loc.uncheck()

    @allure.step("Upload file")
    def upload_file(self, selector: LocatorSpec, file_path: str | Path) -> None:
        self.locator(selector).set_input_files(str(file_path))

    @allure.step("Wait for element visible")
    def wait_for_visible(self, selector: LocatorSpec) -> Locator:
        loc = self.locator(selector)
        expect(loc).to_be_visible()
        return loc

    @allure.step("Wait for element hidden")
    def wait_for_hidden(self, selector: LocatorSpec) -> None:
        expect(self.locator(selector)).to_be_hidden()

    @allure.step("Wait for URL")
    def wait_for_url_contains(self, text: str) -> None:
        self.page.wait_for_url(f"**/*{text}*", wait_until="domcontentloaded")

    def is_element_visible(self, selector: LocatorSpec) -> bool:
        return self.locator(selector).is_visible()

    def is_element_enabled(self, selector: LocatorSpec) -> bool:
        return self.locator(selector).is_enabled()

    def get_element_count(self, selector: LocatorSpec) -> int:
        return self.locator(selector).count()

    def get_text(self, selector: LocatorSpec) -> str:
        loc = self.locator(selector)
        expect(loc).to_be_visible()
        return loc.inner_text().strip()

    def get_all_texts(self, selector: LocatorSpec) -> list[str]:
        loc = self.locator(selector)
        loc.first.wait_for(state="attached")
        return [text.strip() for text in loc.all_inner_texts()]

    def get_attribute(self, selector: LocatorSpec, name: str) -> str | None:
        return self.locator(selector).get_attribute(name)

    def get_input_value(self, selector: LocatorSpec) -> str:
        return self.locator(selector).input_value()

    @staticmethod
    def parse_price_to_float(value: str) -> float:
        import re
        cleaned = re.sub(r"[^\d.,]", "", value)
        cleaned = cleaned.replace(",", "")
        return float(cleaned) if cleaned else 0.0

    @allure.step("Scroll to element")
    def scroll_to_element(self, selector: LocatorSpec) -> None:
        self.locator(selector).scroll_into_view_if_needed()

    @allure.step("Scroll to bottom")
    def scroll_to_bottom(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    @allure.step("Switch to new tab")
    def switch_to_new_tab(self, previous_page_count: int) -> Page:
        self.page.context.wait_for_event("page")
        page = self.page.context.pages[-1]
        page.set_default_timeout(self.page.timeout if hasattr(self.page, "timeout") else 30_000)
        page.wait_for_load_state("domcontentloaded")
        return page

    @allure.step("Handle alert")
    def handle_alert(self, action: Literal["accept", "dismiss"] = "accept", prompt_text: str | None = None) -> str:
        message = ""
        def handler(dialog: Dialog) -> None:
            nonlocal message
            message = dialog.message
            dialog.accept(prompt_text) if prompt_text is not None else (
                dialog.accept() if action == "accept" else dialog.dismiss()
            )
        self.page.once("dialog", handler)
        return message

    @allure.step("Switch to iframe")
    def switch_to_iframe(self, selector: LocatorSpec) -> Frame:
        frame = self.locator(selector).element_handle()
        if frame is None:
            raise AssertionError("Iframe not found")
        content = frame.content_frame()
        if content is None:
            raise AssertionError("Iframe has no content frame")
        return content

    @allure.step("Take screenshot")
    def take_screenshot(self, name: str, full_page: bool = True) -> Path:
        report_dir = Path(__file__).resolve().parents[1] / "reports" / "screenshots"
        report_dir.mkdir(parents=True, exist_ok=True)
        path = report_dir / f"{name}.png"
        self.page.screenshot(path=str(path), full_page=full_page)
        allure.attach.file(str(path), name=name, attachment_type=allure.attachment_type.PNG)
        return path

    @allure.step("Dismiss cookie or location popup")
    def dismiss_cookie_or_location_popup(self) -> bool:
        candidates = [
            "#sp-cc-accept",
            "[name='accept']",
            "button:has-text('Continue')",
            "button:has-text('No thanks')",
        ]
        for selector in candidates:
            loc = self.page.locator(selector).first
            if loc.is_visible(timeout=500):
                loc.click()
                return True
        return False
