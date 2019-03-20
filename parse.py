#!/usr/bin/python
import sys
from string import Template
from rdflib import Graph, plugin, URIRef
from rdflib.serializer import Serializer

CONTEXT = {
    "dli": "https://digitalliving.github.io/standards/ontologies/dli.jsonld#",
    "pot": "https://platformoftrust.github.io/standards/ontologies/pot.jsonld#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "vs": "http://www.w3.org/2003/06/sw-vocab-status/ns#",
    "dct": "http://purl.org/dc/terms/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "cc": "http://creativecommons.org/ns#",
    "rak": "http://uri.suomi.fi/datamodel/ns/rak#",
    "vann": "http://purl.org/vocab/vann/",
    "@vocab": "https://platformoftrust.github.io/standards/ontologies/pot.jsonld#",
    "@base": "https://platformoftrust.github.io/standards/ontologies/pot.jsonld#"
}

def main(filename):
    with open(filename) as f:
        data = f.read()
    g = Graph().parse(data=data, format='json-ld')
    objects = g.triples((None, URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), URIRef('https://platformoftrust.github.io/standards/ontologies/pot.jsonld#Class')))
    result_graphs = []
    for i in list(objects):
        ng = Graph()
        ng.add(i)
        for predicate in list(g.triples((i[0], None, None))):
            ng.add(predicate)
        for domain in list(g.triples((None, URIRef('http://www.w3.org/2000/01/rdf-schema#domain'), URIRef(i[0])))):
            for subject in list(g.triples((domain[0], None, None))):
                ng.add(subject)
        with open('result/{}.jsonld'.format(i[0].split('#')[1]), 'wb') as f:
            f.write(ng.serialize(format='json-ld', indent=4, context=CONTEXT))
    


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError:
        print('You have to select file to parse, please use: python parse.py <filename.jsonld>')
        exit()
    main(filename)
    