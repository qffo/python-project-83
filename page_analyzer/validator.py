import validators


def validate(url: str) -> bool:
    """Check if the URL is valid."""
    return validators.url(url) and len(url) <= 255
