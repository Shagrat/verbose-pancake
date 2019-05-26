import os
import sys
import json
from copy import deepcopy
from rdflib import ConjunctiveGraph, RDF, RDFS, OWL, URIRef
from utils import POT, DLI, TripletTuple, uri2niceString
from models import RDFClass, RDFProperty
from const import BASE_DEFFINITION_POT, POT_BASE, BASE_IDENTITY_POT, BASE_VOCABULARY_POT, CONF_NAME


def create_deffinition_from_rdf_class(rdf_class):
    vocabulary_dict = deepcopy(BASE_DEFFINITION_POT)
    vocabulary = '{}Vocabulary/{}'.format(POT_BASE, rdf_class.get_new_type_id()[4:])
    vocabulary_dict['@context']['@vocab'] = vocabulary
    vocabulary_dict['@id'] = vocabulary
    supported_class = rdf_class.toPython()
    supported_attrs = {
        'name': {
            "@id": 'pot:name',
            "@type": "pot:SupportedAttribute",
            "dli:title": "name",
            "dli:description": "name",
            "dli:required": True
        },
        'data':{
            "@id": 'dli:data',
            "@type": "pot:SupportedAttribute",
            "dli:title": "data",
            "dli:description": "data",
            "dli:required": True,
        }
    }
    for rdf_attribute in rdf_class.get_properties():
        supported_attrs[rdf_attribute.title()]= rdf_attribute.toVocab()
    supported_class['pot:supportedAttribute'] = supported_attrs
    vocabulary_dict['pot:supportedClass'] = supported_class
    return vocabulary_dict


def create_identity_from_rdf_class(rdf_class, flat_definition):
    identity_dict = deepcopy(BASE_IDENTITY_POT)
    vocabulary = '{}ClassDefinitions/{}'.format(POT_BASE, rdf_class.get_new_type_id()[4:])
    identity_dict['@vocab'] = '{}Vocabulary/{}'.format(POT_BASE, rdf_class.get_new_type_id()[4:])
    identity_dict['@classDefinition'] = vocabulary
    total_attributes = set(rdf_class.get_properties())
    for domain in total_attributes:
        key = domain.title()
        if key == 'name':
            continue
        if uri2niceString(rdf_class.uriref, rdf_class.namespaces()) not in flat_definition:
            identity_dict[key] = {
                '@id':  uri2niceString(domain.uriref, domain.namespaces()),
                '@nest': 'data'
            }
        else:
            identity_dict[key] = uri2niceString(domain.uriref, domain.namespaces())
    return {
        '@context': identity_dict
    }


def create_vocabulary_from_rdf_class(rdf_class):
    vocabulary_dict = deepcopy(BASE_VOCABULARY_POT)
    total_attributes = set(rdf_class.get_properties())
    for domain in total_attributes:
        vocabulary_dict[domain.title()] = domain.toPython()
    for dependent in rdf_class.get_dependents():
        vocabulary_dict[dependent.title()] = {
            'rdfs:subClassOf':{
                '@id': rdf_class.get_new_type_id()
            }
        }
    return vocabulary_dict


def create_identity_directory_from_rdf_class(top_classes, file_path):
    identity_dict = deepcopy(BASE_IDENTITY_POT)
    for child in top_classes:
        identity_dict[child.title()] = child.toPython()
    
    del identity_dict['@vocab']
    del identity_dict['data']
    del identity_dict['name']
    return {
        '@context': identity_dict,
    }


def build_directories(rdf_class):
    parents = rdf_class.get_real_parents()
    if len(parents):
        for i in rdf_class.get_real_parents():
            directories = build_directories(i)
            new_directories = []
            for directory in directories:
                new_directories.append(os.path.join(directory, rdf_class.title()))
        return new_directories
    else:
        directories = [rdf_class.title(), ]
    return directories


def parse(filename):
    with open(CONF_NAME) as f:
        data = f.read()
    try:
        settings = json.loads(data)
    except (SyntaxError, json.decoder.JSONDecodeError):
        print('Settings conf file syntax error')
        exit()

    with open(filename) as f:
        data = f.read()
    graph = ConjunctiveGraph().parse(data=data, format='json-ld')
    graph.namespace_manager.bind('pot', POT_BASE + 'Classes/', replace=True)
    graph.namespace_manager.bind('pot', 'https://standards.oftrust.net/Classes/', replace=True)
    graph.namespace_manager.bind('dli', 'https://digitalliving.github.io/standards/ontologies/dli.jsonld#', replace=True)
    all_iters = list(graph.triples((None, RDF.type, POT.Class)))
    all_iters.extend(list(graph.triples((None, RDF.type, DLI.Class))))
    all_iters.extend(list(graph.triples((None, RDF.type, RDFS.Class))))
    all_classes = []
    for triplet in map(TripletTuple._make, all_iters):
        all_classes.append(RDFClass(triplet.subject, graph))
    top_classes = []
    for current_class in all_classes:
        if not current_class.get_real_parents():
            top_classes.append(current_class)
        for directory in build_directories(current_class):
            identity_dir = os.path.join('newres/Classes', directory)
            identiry_file_path = os.path.join(identity_dir, '..', '{}.jsonld'.format(current_class.title()))
            os.makedirs(identity_dir, exist_ok=True)
            data_to_dump = create_identity_from_rdf_class(current_class, settings.get('flat_definition', []))
            with open(identiry_file_path, 'w') as f:
                f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': ')))

            if not current_class.get_dependents():
                os.rmdir(identity_dir)
            
            deffinition_dir = os.path.join('newres/ClassDefinitions', directory)
            deffinition_file_path = os.path.join(deffinition_dir, '..', '{}.jsonld'.format(current_class.title()))
            os.makedirs(deffinition_dir, exist_ok=True)
            data_to_dump = create_deffinition_from_rdf_class(current_class)
            with open(deffinition_file_path, 'w') as f:
                f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': ')))
            
            if not current_class.get_dependents():
                os.rmdir(deffinition_dir)

            vocabulary_dir = os.path.join('newres/Vocabulary', directory)
            vocabulary_file_path = os.path.join(vocabulary_dir, '..', '{}.jsonld'.format(current_class.title()))
            os.makedirs(vocabulary_dir, exist_ok=True)
            data_to_dump = create_vocabulary_from_rdf_class(current_class)
            with open(vocabulary_file_path, 'w') as f:
                f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': ')))
            
            if not current_class.get_dependents():
                os.rmdir(vocabulary_dir)

    context_file_path = os.path.join('newres/Vocabulary', 'vocabulary.jsonld')
    data_to_dump = create_identity_directory_from_rdf_class(top_classes, context_file_path)
    with open(context_file_path, 'w') as f:
        f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': ')))
    context_file_path = os.path.join('newres/Vocabulary', 'Vocabulary.jsonld')
    with open(context_file_path, 'w') as f:
        f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': ')))
    context_file_path = os.path.join('newres', 'vocabulary.jsonld')
    with open(context_file_path, 'w') as f:
        f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': ')))
    context_file_path = os.path.join('newres', 'Vocabulary.jsonld')
    with open(context_file_path, 'w') as f:
        f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': ')))

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError:
        print('You have to select file to parse, please use: python parse.py <filename.jsonld>')
        exit()
    parse(filename)