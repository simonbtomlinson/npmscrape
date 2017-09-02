from lxml import html
import requests


def get_depended_upon_packages():
    resp = requests.get('https://www.npmjs.com/browse/depended')
    assert resp.ok
    tree = html.fromstring(resp.content)
    for elem in tree.cssselect('.package-details h3 a'):
        yield elem.text_content()
