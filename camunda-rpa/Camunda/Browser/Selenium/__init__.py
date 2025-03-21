from typing import Union, Optional
from robot.api.deco import keyword
from RPA.Browser.common import AUTO, auto_headless
from RPA.Browser.Selenium import (
    BrowserManagementKeywords as _BrowserManagementKeywords,
    Selenium as _Selenium,
    ArgOptions,
    OptionsType,
)
from robot.api import logger


class BrowserManagementKeywords(_BrowserManagementKeywords):
    """Overridden keywords for browser management."""

    def __init__(self, ctx):
        super().__init__(ctx)

    @keyword
    @auto_headless
    def open_browser(
        self,
        *args,
        browser: str = "firefox",
        headless: Union[bool, str] = AUTO,
        sandbox: bool = False,
        options: Optional[OptionsType] = None,
        **kwargs,
    ) -> str:
        if headless:
            # Map the headless argument to the browser argument
            # firefox, ff => headlessfirefox
            # googlechrome, chrome, gc => headlesschrome

            if browser == "firefox" or browser == "ff":
                browser = "headlessfirefox"

            if browser == "googlechrome" or browser == "chrome" or browser == "gc":
                browser = "headlesschrome"

        # Disable sandbox by default
        options: ArgOptions = self.ctx.normalize_options(options, browser=browser)
        if not sandbox:
            options.add_argument("--no-sandbox")

        super().open_browser(*args, browser=browser, options=options, **kwargs)

    open_browser.__doc__ = _BrowserManagementKeywords.open_browser.__doc__


class Selenium(_Selenium):
    def __init__(self, *args, **kwargs):
        self.AVAILABLE_OPTIONS["headlesschrome"] = self.AVAILABLE_OPTIONS["chrome"]
        self.AVAILABLE_OPTIONS["headlessfirefox"] = self.AVAILABLE_OPTIONS["firefox"]

        super().__init__(*args, **kwargs)

        self.browser_management = BrowserManagementKeywords(self)
        self.add_library_components([self.browser_management])
