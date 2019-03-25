#!/usr/bin/python
import sys
import json
import os
from collections import namedtuple
from copy import deepcopy
from string import Template
from rdflib import Graph, plugin, URIRef, Literal
from rdflib.serializer import Serializer
from const import BASE_IDENTITY, BASE_VOCABULARY, VERSION, LABEL_REF, COMMENT_REF, RANGE_REF, SUBCLASS_REF

Triplet = namedtuple('Triplet', 'subject, predicate, object')


def get_title_and_description(subject_uriref, graph):
    title = None
    for title_triplet in map(Triplet._make, list(graph.triples((subject_uriref, URIRef(LABEL_REF), None)))):
        if type(title_triplet.object) != Literal or title_triplet.object.language != 'en':
            continue
        title = title_triplet.object
    if not title:
        title = str(subject_uriref).split('#')[1]
    
    description = None
    for description_triplet in map(Triplet._make, list(graph.triples((subject_uriref, URIRef(COMMENT_REF), None)))):
        if type(description_triplet.object) != Literal or description_triplet.object.language != 'en':
            continue
        description = description_triplet.object
    if not description:
        description = title
    return title, description


def get_supported_types(subject_uriref, graph):
    supported_types = []
    for type_triplet in map(Triplet._make, list(graph.triples((subject_uriref, URIRef(RANGE_REF), None)))):
        supported_types.append('pot:{}'.format(type_triplet.object.split('#')[1]))
    return supported_types



def build_vocabulary(graph, class_triplet):
    vocabulary_dict = deepcopy(BASE_VOCABULARY)
    class_key = class_triplet.subject.split('#')[1]
    vocabulary = 'https://platformoftrust.github.io/standards/vocabularies/{}.jsonld#'.format(class_key.lower())
    vocabulary_dict['@context']['vocab'] = vocabulary
    vocabulary_dict['@id'] = vocabulary[:-1]
    title, description = get_title_and_description(class_triplet.subject, graph)
    total_attributes = []
    parents =  list(map(Triplet._make, list(graph.triples((class_triplet.subject, URIRef(SUBCLASS_REF), None)))))
    while len(parents):
        tParents = []
        for parent in parents:
            total_attributes += map(Triplet._make, list(graph.triples((None, URIRef('http://www.w3.org/2000/01/rdf-schema#domain'), parent.object))))
            tParents +=  list(map(Triplet._make, list(graph.triples((parent.object, URIRef(SUBCLASS_REF), None)))))      
        parents = tParents.copy()

    total_attributes += map(Triplet._make, list(graph.triples((None, URIRef('http://www.w3.org/2000/01/rdf-schema#domain'), class_triplet.subject))))
    supported_class = {
      "@id": "pot:{}".format(class_key),
      "@type": "pot:{}".format(class_key),
      "dli:title": title,
      "dli:description": description,
    }
    supported_attributes = [
        {
          "@type": "pot:SupportedAttribute",
          "dli:attribute": "pot:name",
          "dli:title": "name",
          "dli:description": "name",
          "dli:required": True
        },
        {
          "@type": "pot:SupportedAttribute",
          "dli:attribute": "dli:data",
          "dli:title": "data",
          "dli:description": "data",
          "dli:required": True,
          "dli:valueType": "xsd:object"
        },
    ]
    for domain in total_attributes:
        key = domain.subject.split('#')[1]
        if key.lower() == 'name':
            continue
        title, description = get_title_and_description(domain.subject, graph)
        supported_types = get_supported_types(domain.subject, graph)
        supported_attribute = {
            "@type": "pot:SupportedAttribute",
            "dli:attribute": "pot:{}".format(key),
            "dli:title": title,
            "dli:description": description,
            "dli:required": False
        }
        if len(supported_types) > 0:
            supported_attribute['dli:valueType'] = supported_types
        if not next((attribute for attribute in supported_attributes if attribute["dli:attribute"] == supported_attribute["dli:attribute"]), None):
            supported_attributes.append(supported_attribute)
    supported_class['pot:supportedAttribute'] = supported_attributes
    vocabulary_dict['pot:supportedClass'] = supported_class

    return vocabulary_dict, vocabulary


def build_identity(graph, class_triplet, vocabulary):
    identity_dict = deepcopy(BASE_IDENTITY)
    identity_dict['@vocab'] = vocabulary
    rdf_class_uriref = class_triplet.subject
    total_attributes = []
    parents =  list(map(Triplet._make, list(graph.triples((class_triplet.subject, URIRef(SUBCLASS_REF), None)))))
    while len(parents):
        tParents = []
        for parent in parents:
            total_attributes += map(Triplet._make, list(graph.triples((None, URIRef('http://www.w3.org/2000/01/rdf-schema#domain'), parent.object))))
            tParents +=  list(map(Triplet._make, list(graph.triples((parent.object, URIRef(SUBCLASS_REF), None)))))      
        parents = tParents.copy()

    total_attributes += map(Triplet._make, list(graph.triples((None, URIRef('http://www.w3.org/2000/01/rdf-schema#domain'), class_triplet.subject))))

    for domain in total_attributes:
        key = domain.subject.split('#')[1]
        if key == 'name':
            continue
        identity_dict[key] = {
            '@id': 'pot:{}'.format(key),
            '@nest': 'pot:data',
        }
    return identity_dict

def parse(filename):
    with open(filename) as f:
        data = f.read()
    graph = Graph().parse(data=data, format='json-ld')
    class_triples = graph.triples((None, URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), URIRef('https://platformoftrust.github.io/standards/ontologies/pot.jsonld#Class')))
    for class_triplet in map(Triplet._make, list(class_triples)):
        vocabulary_dict, vocabulary = build_vocabulary(graph, class_triplet)
        identity_dict = build_identity(graph, class_triplet, vocabulary)

        with open('identities/identity-{}.jsonld'.format(class_triplet.subject.split('#')[1].lower()), 'w') as f:
            f.write(json.dumps({'@context': identity_dict}, indent=4, separators=(',', ': ')))
        with open('vocabularies/{}.jsonld'.format(class_triplet.subject.split('#')[1].lower()), 'w') as f:
            f.write(json.dumps(vocabulary_dict, indent=4, separators=(',', ': ')))


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError:
        print('You have to select file to parse, please use: python parse.py <filename.jsonld>')
        exit()
    try:
        os.makedirs('identities')
        os.makedirs('vocabularies')
    except FileExistsError as e:
        pass
    parse(filename)
    