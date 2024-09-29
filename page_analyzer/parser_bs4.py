from bs4 import BeautifulSoup


def get_h1(response: str) -> str:
    """
    Extract the <h1> tag content from the given HTML response.
    """
    soup = BeautifulSoup(response.text, 'html.parser')
    h1_tag = soup.find('h1')
    return h1_tag.text if h1_tag else None


def get_title(response: str) -> str:
    """
    Extract the <title> tag content from the given HTML response.
    """
    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find('title')
    return title_tag.text if title_tag else None


def get_descr(response: str) -> str:
    """
    Extract the content of the <meta name="description"> tag
    from the given HTML response.
    """
    soup = BeautifulSoup(response.text, 'html.parser')
    descr_tag = soup.find('meta', attrs={'name': 'description'})
    if descr_tag and 'content' in descr_tag.attrs:
        content_value = descr_tag['content']
        return content_value
    return None
