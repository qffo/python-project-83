from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    '''
    Returns a normalized URL, preserving only the scheme and host.
    Example:
        normalize_url("https://www.example.com/some/path?query=param#fragment")
        will return "https://www.example.com".
    '''
    parsed_url = urlparse(url)
    return "://".join([f"{parsed_url.scheme}", parsed_url.hostname])
