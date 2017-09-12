from lxml import html
import requests
import itertools


def get_depended_upon_packages(offset=0):
    resp = requests.get(f'https://www.npmjs.com/browse/depended?offset={offset}')
    assert resp.ok
    tree = html.fromstring(resp.content)
    for elem in tree.cssselect('.package-details h3 a'):
        yield elem.text_content()

def get_first_n_depended_upon_packages(n):
    all_packages = itertools.chain.from_iterable(map(get_depended_upon_packages, itertools.count(0, 36)))
    yield from itertools.islice(all_packages, 0, n)
