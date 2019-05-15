import os
import sys
import json
from copy import deepcopy
from rdflib import ConjunctiveGraph, RDF, RDFS
from utils import POT, DLI, TripletTuple, uri2niceString
from models import RDFClass
from const import BASE_VOCABULARY_POT, POT_BASE, BASE_IDENTITY_POT

def create_vocab_from_rdf_class(rdf_class, file_path):
    vocabulary_dict = deepcopy(BASE_VOCABULARY_POT)
    vocabulary = '{}vocabularies/{}.jsonld#'.format(POT_BASE, rdf_class.title())
    vocabulary_dict['@context']['vocab'] = vocabulary
    vocabulary_dict['@id'] = vocabulary[:-1]
    supported_class = [
        rdf_class.toPython(),
    ]
    all_classes = rdf_class.get_dependents()
    all_classes.union(set(rdf_class.get_real_parents()))
    all_classes.add(rdf_class.get_type_object())
    all_attrs = set()
    for d in all_classes:
        all_attrs.union(set(d.get_properties()))
        supported_class.append(d.toPython())
    for i in all_attrs:
        supported_class.append(i.toPython())

    vocabulary_dict['pot:supportedClass'] = supported_class
    return vocabulary_dict


def create_identity_directory_from_rdf_class(rdf_class, file_path):
    identity_dict = deepcopy(BASE_IDENTITY_POT)
    if type(rdf_class) == RDFClass:
        children =  rdf_class.get_children()
        identity_graph = [rdf_class.toPython()]
    else:
        children = rdf_class
        identity_graph = []
    for child in children:
        identity_graph.append(child.toPython())
    identity_dict['@graph'] = identity_graph
    del identity_dict['@vocab']
    del identity_dict['data']
    del identity_dict['name']
    return identity_dict




def create_identity_from_rdf_class(rdf_class, file_path):
    identity_dict = deepcopy(BASE_IDENTITY_POT)
    vocabulary = '{}vocabularies/{}.jsonld#'.format(POT_BASE, rdf_class.title())
    identity_dict['@vocab'] = vocabulary
    total_attributes = set(rdf_class.get_properties())
    parents =  rdf_class.get_real_parents()
    for p in parents:
        total_attributes.union(p.get_properties())
    identity_graph = [rdf_class.toPython()]
    for domain in total_attributes:
        key = domain.uriref.split('#')[1]
        if key == 'name':
            continue
        identity_dict[key] = {
            '@id':  uri2niceString(domain.uriref, domain.namespaces()),
            '@nest': 'pot:data'
        }
        identity_graph.append(domain.toPython())
    identity_dict['@graph'] = identity_graph
    

    return identity_dict


def init_class_tree(graph, triplet):
    found = False
    for i in map(TripletTuple._make, list(graph.triples((None, RDFS.subClassOf, triplet.subject)))):
        found = True
        if triplet.subject == i.subject:
            continue
        init_class_tree(graph, i)
    
    return None, True


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
    with open(filename) as f:
        data = f.read()
    graph = ConjunctiveGraph().parse(data=data, format='json-ld')
    graph.namespace_manager.bind('pot', 'https://standards.oftrust.net/ontologies/pot.jsonld#', replace=True)
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
            file_dir = os.path.join('newres/context', directory)
            identiry_file_path = os.path.join(file_dir, '..', '{}.jsonld'.format(current_class.title()))
            directory_file_path = os.path.join(file_dir, '{}.jsonld'.format(current_class.title()))
            os.makedirs(file_dir, exist_ok=True)
            data_to_dump = create_identity_from_rdf_class(current_class,  identiry_file_path)
            data_to_dump = create_identity_from_rdf_class(current_class,  identiry_file_path)
            with open(identiry_file_path, 'w') as f:
                f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': ')))

            if not current_class.get_dependents():
                os.rmdir(file_dir)
            else:
                data_to_dump = create_identity_directory_from_rdf_class(current_class,  identiry_file_path)
                with open(directory_file_path, 'w') as f:
                    f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': ')))
    context_file_path = os.path.join('newres/context', 'Context.jsonld')
    data_to_dump = create_identity_directory_from_rdf_class(top_classes, context_file_path)
    with open(context_file_path, 'w') as f:
        f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': ')))


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError:
        print('You have to select file to parse, please use: python parse.py <filename.jsonld>')
        exit()
    try:
        os.makedirs('result/pot/identities')
        os.makedirs('result/pot/vocabularies')
        os.makedirs('result/dli/identities')
        os.makedirs('result/dli/vocabularies')
    except FileExistsError as e:
        pass
    parse(filename)