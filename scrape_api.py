import itertools

from multiprocessing.pool import ThreadPool

import requests
import json
from collections import namedtuple
import networkx as nx
import pickle

ScrapedResult = namedtuple('ScrapedResult', ['name', 'dependencies', 'dev_dependencies'])


def response_to_json(response):
    return json.loads(response.text)


def get_json(name):
    resp = requests.get(f'https://registry.npmjs.org/{name}/latest')
    if resp.ok:
        return response_to_json(resp)
    else:
        return {'name': name}


def get_latest_version(all_versions):
    return max(all_versions)


def get_dependencies(project_json):
    try:
        return project_json['dependencies'].keys()
    except KeyError:
        return []


def get_dev_dependencies(project_json):
    try:
        return project_json['devDependencies'].keys()
    except KeyError:
        return []


def scrape(name):
    try:
        scraped_json = get_json(name)
        dependencies = get_dependencies(scraped_json)
        dev_dependencies = get_dev_dependencies(scraped_json)
        return ScrapedResult(
            name,
            dependencies,
            dev_dependencies
        )
    except Exception as e:
        raise Exception(name).with_traceback(e.__traceback__)


def scrape_all_dependencies(*packages):
    graph = nx.DiGraph()
    to_scrape = list(packages)
    found = set()
    with ThreadPool(128) as pool:
        while to_scrape:
            print('Scraping', len(to_scrape), 'dependencies')
            scraped = pool.map(scrape, to_scrape)
            nested_deps = (itertools.chain(s.dependencies) for s in scraped)
            to_scrape = {dep for dep in itertools.chain(*nested_deps) if dep not in found}
            for s in scraped:
                for d in s.dependencies:
                    graph.add_edge(s.name, d, attr_dict={'type': 'dependency'})
                for d in s.dev_dependencies:
                    graph.add_edge(s.name, d, attr_dict={'type': 'dev_dependency'})
                if s.name not in found:
                    found.add(s.name)
    return graph

from scrape_most_depended_upon import get_depended_upon_packages
graph = scrape_all_dependencies(*get_depended_upon_packages())
with open('top-packages-no-dev.pickle', 'wb') as pickle_file:
    pickle.dump(graph, pickle_file)
