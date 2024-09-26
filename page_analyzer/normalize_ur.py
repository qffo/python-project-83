from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    '''
    Returns a normalized URL, preserving only the scheme and host.
    Example:
        normalize_url("https://www.example.com/some/path?query=param#fragment")
        will return "https://www.example.com".
    '''
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, parsed_url.hostname, '', '', '', ''))
