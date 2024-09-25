import validators


def validate(url):
    """Check if the URL is valid."""
    return validators.url(url) and len(url) <= 255
