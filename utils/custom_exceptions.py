"""Framework domain exceptions."""


class FrameworkException(Exception):
    """Base framework exception."""


class BotChallengeDetected(FrameworkException):
    """Amazon CAPTCHA or shopping interstitial encountered."""


class InvalidSearchResult(FrameworkException):
    """A required product or search state is unavailable."""


class CartConsistencyError(FrameworkException):
    """Cart product or price state is inconsistent."""

