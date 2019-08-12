import os
import sys
import json
import shutil
from copy import deepcopy
from rdflib import ConjunctiveGraph, RDF, RDFS, OWL, URIRef, BNode
from utils import SW, POT, DLI, TripletTuple, uri2niceString
from models import RDFClass, RDFProperty
from const import BASE_DEFFINITION_POT, POT_BASE, BASE_IDENTITY_POT, BASE_VOCABULARY_POT,\
     CONF_NAME, POT_EXPORT, BASE_DIRECTORY_POT


def create_deffinition_from_rdf_class(rdf_class):
    vocabulary_dict = deepcopy(BASE_DEFFINITION_POT)
    vocabulary = '{}Vocabulary/{}'.format(POT_EXPORT, rdf_class.get_new_type_id()[4:])
    vocabulary_dict['@context']['@vocab'] = vocabulary
    vocabulary_dict['@id'] = vocabulary
    supported_class = rdf_class.toPython()
    supported_attrs = {
        'data': {
            "@id": 'dli:data',
            "@type": "dli:SupportedAttribute",
            "dli:title": "data",
            "dli:description": {
                "en-us": "data"
            },
            "dli:required": False,
        }
    }
    total_attributes = rdf_class.get_properties()
    languages_comments = set()
    for rdf_attribute in total_attributes:
        supported_attrs[rdf_attribute.get_context_name(domain_selected=rdf_class)] = rdf_attribute.toVocab(parent_domain=rdf_class)

        for k, v in rdf_attribute.get_comments(comment_domain_selected=rdf_class).items():
            languages_comments.add(k)
    if len(languages_comments):
        vocabulary_dict['@context']['description'] = {
            '@id': 'dli:description',
            "@container": ['@language', '@set']
        }
    else:
        del vocabulary_dict['@context']['description']

    if not supported_class.get('rdfs:label', None):
        del vocabulary_dict['@context']['label']

    if not supported_class.get('rdfs:comment', None):
        del vocabulary_dict['@context']['comment']

    supported_class['dli:supportedAttribute'] = supported_attrs
    vocabulary_dict['dli:supportedClass'] = supported_class
    return vocabulary_dict


def create_identity_from_rdf_class(rdf_class, flat_definition):
    identity_dict = deepcopy(BASE_IDENTITY_POT)
    vocabulary = '{}ClassDefinitions/{}'.format(POT_EXPORT, rdf_class.get_new_type_id()[4:])
    identity_dict['@vocab'] = '{}Vocabulary/{}'.format(POT_EXPORT, rdf_class.get_new_type_id()[4:])
    identity_dict['@classDefinition'] = vocabulary
    total_attributes = set(rdf_class.get_properties())
    for domain in total_attributes:
        key = domain.get_context_name(domain_selected=rdf_class)
        if uri2niceString(rdf_class.uriref, rdf_class.namespaces()) not in flat_definition:
            identity_dict[key] = {
                '@id':  domain.get_new_type_id(),
            }
            if domain.get_nested_at():
                identity_dict[key]['@nest'] = domain.get_nested_at()
        else:
            identity_dict[key] = domain.get_new_type_id()
    return {
        '@context': identity_dict
    }


def create_vocabulary_from_rdf_class(rdf_class, pot_json, current_onto):
    vocabulary_dict = deepcopy(BASE_VOCABULARY_POT)
    total_attributes = set(rdf_class.get_properties(only_context=current_onto))
    languages_labels = set()
    languages_comments = set()
    force_label = False
    force_comment = False
    for d in pot_json.get('defines'):
        if d.get('@id') == str(rdf_class):
            new_dict = deepcopy(d)
            if new_dict.get('dli:label'):
                all_labels = {}
                force_label = True
                for i in new_dict.get('dli:label'):
                    all_labels[i['rdfs:label']['@language']] = i['rdfs:label']['@value']
                new_dict['rdfs:label'] = all_labels
                del new_dict['dli:label']

            if new_dict.get('dli:comment'):
                all_labels = {}
                force_comment = True
                for i in new_dict.get('dli:comment'):
                    all_labels[i['rdfs:comment']['@language']] = i['rdfs:comment']['@value']
                new_dict['rdfs:comment'] = all_labels
                del new_dict['dli:comment']

            vocabulary_dict[rdf_class.title()] = new_dict
    for domain in total_attributes:
        vocabulary_dict[domain.get_context_name(domain_selected=rdf_class)] = domain.toPython(parent_domain=rdf_class)
        for k, v in domain.get_comments(comment_domain_selected=rdf_class).items():
            languages_comments.add(k)
        for k, v in domain.get_labels(label_domain_selected=rdf_class).items():
            languages_labels.add(k)
    if len(languages_labels) or force_label:
        vocabulary_dict['@context']['label'] = {
            '@id': 'rdfs:label',
            "@container": ['@language', '@set']
        }
    else:
        del vocabulary_dict['@context']['label']
    if len(languages_comments) or force_comment:
        vocabulary_dict['@context']['comment'] = {
            '@id': 'rdfs:comment',
            "@container": ['@language', '@set']
        }
    else:
        del vocabulary_dict['@context']['comment']
    for dependent in rdf_class.get_dependents():
        vocabulary_dict[dependent.title()] = {
            'rdfs:subClassOf': {
                '@id': rdf_class.get_new_type_id()
            }
        }
    return vocabulary_dict


def create_identity_directory_from_rdf_class(top_classes, file_path):
    identity_dict = deepcopy(BASE_DIRECTORY_POT)
    for child in top_classes:
        identity_dict[child.title()] = child.toPython()

    return identity_dict


def build_directories(rdf_class):
    parents = rdf_class.get_real_parents()
    new_directories = []
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
    with open(CONF_NAME, encoding='utf-8') as f:
        data = f.read()
    try:
        settings = json.loads(data)
    except (SyntaxError, json.decoder.JSONDecodeError):
        print('Settings conf file syntax error')
        exit()

    with open(filename, encoding='utf-8') as f:
        data = f.read()
    context_name, file_extension = os.path.splitext(filename)
    result_dir_name = os.path.join('newres', context_name)
    pot_json = json.loads(data)
    graph = ConjunctiveGraph().parse(data=data, format='json-ld')
    graph.namespace_manager.bind('pot', POT_BASE + 'Classes/', replace=True)
    graph.namespace_manager.bind('pot', 'https://standards.oftrust.net/Classes/', replace=True)
    graph.namespace_manager.bind('dli', 'https://digitalliving.github.io/standards/ontologies/dli.jsonld#', replace=True)
    all_classes = []
    all_iters = list(graph.triples((None, RDF.type, POT.Class)))
    all_iters.extend(list(graph.triples((None, RDF.type, DLI.Class))))
    all_iters.extend(list(graph.triples((None, RDF.type, RDFS.Class))))
    all_classes = []
    for triplet in map(TripletTuple._make, all_iters):
        rdf_class = RDFClass(triplet.subject, graph)
        all_classes.append(rdf_class)
    top_classes = []
    for current_class in all_classes:
        if not current_class.get_real_parents():
            top_classes.append(current_class)
        for directory in build_directories(current_class):
            if str(current_class) not in settings.get('pot_exclude'):
                identity_dir = os.path.join(result_dir_name, 'Context', directory)
                identiry_file_path = os.path.join(identity_dir, '..', '{}.jsonld'.format(current_class.title()))
                os.makedirs(identity_dir, exist_ok=True)
                data_to_dump = create_identity_from_rdf_class(current_class, settings.get('flat_definition', []))
                with open(identiry_file_path, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': '), ensure_ascii=False))

                if not current_class.get_dependents():
                    os.rmdir(identity_dir)

                deffinition_dir = os.path.join(result_dir_name, 'ClassDefinitions', directory)
                deffinition_file_path = os.path.join(deffinition_dir, '..', '{}.jsonld'.format(current_class.title()))
                os.makedirs(deffinition_dir, exist_ok=True)
                data_to_dump = create_deffinition_from_rdf_class(current_class)
                with open(deffinition_file_path, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': '), ensure_ascii=False))

                if not current_class.get_dependents():
                    os.rmdir(deffinition_dir)

            vocabulary_dir = os.path.join(result_dir_name, 'Vocabulary', directory)
            vocabulary_file_path = os.path.join(vocabulary_dir, '..', '{}.jsonld'.format(current_class.title()))
            os.makedirs(vocabulary_dir, exist_ok=True)
            data_to_dump = create_vocabulary_from_rdf_class(current_class, pot_json, context_name)
            with open(vocabulary_file_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': '), ensure_ascii=False))

            if not current_class.get_dependents():
                os.rmdir(vocabulary_dir)

    context_file_path = os.path.join(result_dir_name, 'Vocabulary', 'vocabulary.jsonld')
    data_to_dump = create_identity_directory_from_rdf_class(top_classes, context_file_path)
    with open(context_file_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': '), ensure_ascii=False))
    context_file_path = os.path.join(result_dir_name, 'Vocabulary', 'Vocabulary.jsonld')
    with open(context_file_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': '), ensure_ascii=False))
    context_file_path = os.path.join(result_dir_name, 'vocabulary.jsonld')
    with open(context_file_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': '), ensure_ascii=False))
    context_file_path = os.path.join(result_dir_name, 'Vocabulary.jsonld')
    with open(context_file_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data_to_dump, indent=4, separators=(',', ': '), ensure_ascii=False))

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError:
        print('You have to select file to parse, please use: python parse.py <filename.jsonld>')
        exit()
    parse(filename)
    try:
        archive = sys.argv[2]
        if archive == '-a':
            shutil.make_archive('generated', 'zip', 'newres')
    except:
        pass
