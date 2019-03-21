#!/usr/bin/python
import sys
import json
from string import Template
from rdflib import Graph, plugin, URIRef
from rdflib.serializer import Serializer

VERSION = 1.1

def main(filename):
    with open(filename) as f:
        data = f.read()
    g = Graph().parse(data=data, format='json-ld')
    objects = g.triples((None, URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), URIRef('https://platformoftrust.github.io/standards/ontologies/pot.jsonld#Class')))
    result_graphs = []
    for i in list(objects):
        result_dict = {
            '@version': VERSION,
            '@vocab': "https://platformoftrust.github.io/standards/vocabularies/{}.jsonld#".format(i[0].split('#')[1].lower()),
            "pot": {
                "@id": "https://platformoftrust.github.io/standards/ontologies/pot.jsonld#",
                "@prefix": True
            },
            "dli": {
                "@id": "https://digitalliving.github.io/standards/ontologies/dli.jsonld#",
                "@prefix": True
            },
            "data": "dli:data",
            "name": "pot:name",
        }
        for domain in list(g.triples((None, URIRef('http://www.w3.org/2000/01/rdf-schema#domain'), URIRef(i[0])))):
            key = domain[0].split('#')[1]
            if key == 'name':
                continue
            result_dict[key] = {
                '@id': 'pot:{}'.format(key),
                '@nest': 'pot:data',
            }
        with open('result/identity-{}.jsonld'.format(i[0].split('#')[1].lower()), 'w') as f:
            f.write(json.dumps({'@context': result_dict}, indent=4, separators=(',', ': ')))
    


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError:
        print('You have to select file to parse, please use: python parse.py <filename.jsonld>')
        exit()
    main(filename)
    