import validators


def validate(url):
    """Check if the URL is valid."""
    if validators.url(url) and len(url) <= 255:
        return True
    return False
