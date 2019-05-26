VERSION = 1.1
LABEL_REF = 'http://www.w3.org/2000/01/rdf-schema#label'
COMMENT_REF = 'http://www.w3.org/2000/01/rdf-schema#comment'
RANGE_REF = 'http://www.w3.org/2000/01/rdf-schema#range'
SUBCLASS_REF = 'http://www.w3.org/2000/01/rdf-schema#subClassOf'
#POT_BASE = 'https://standards.oftrust.net/'
POT_BASE = 'http://verbose.terrikon.co/v1/'
DLI_BASE = 'https://digitalliving.github.io/standards/'
CONF_NAME = 'settings.conf'

BASE_IDENTITY_POT = {
    '@version': VERSION,
    '@vocab': "{}vocabularies/.jsonld#".format(POT_BASE),
    "pot": {
        "@id": "{}Vocabulary/".format(POT_BASE),
        "@prefix": True
    },
    "dli": {
        "@id": "https://digitalliving.github.io/standards/ontologies/dli.jsonld#",
        "@prefix": True
    },
    "data": "dli:data",
    "name": "pot:name",
}

BASE_DEFFINITION_POT = {
    "@context": {
        "@version": VERSION,
        "rdf": {
            "@id": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "@prefix": True
        },
        "rdfs": {
            "@id": "http://www.w3.org/2000/01/rdf-schema#",
            "@prefix": True
        },
        "dli": {
            "@id": "https://digitalliving.github.io/standards/ontologies/dli.jsonld#",
            "@prefix": True
        },
        "pot": {
            "@id": "{}Vocabulary/".format(POT_BASE),
            "@prefix": True
        },
        "vocab": "{}vocabularies/.jsonld".format(POT_BASE)
    },
    "@id": "{}vocabularies/.jsonld".format(POT_BASE),
    "@type": "pot:Vocabulary",
}


BASE_VOCABULARY_POT = {
    '@version': VERSION,
    "pot": {
        "@id": "{}Vocabulary/".format(POT_BASE),
        "@prefix": True
    },
    "dli": {
        "@id": "https://digitalliving.github.io/standards/ontologies/dli.jsonld#",
        "@prefix": True
    }
}


BASE_IDENTITY_DLI = {
    '@version': VERSION,
    '@vocab': "{}vocabularies/.jsonld#".format(DLI_BASE),
    "dli": {
        "@id": "https://digitalliving.github.io/standards/ontologies/dli.jsonld#",
        "@prefix": True
    },
    "data": "dli:data",
    "name": "dli:name",
}

BASE_VOCABULARY_DLI = {
    "@context": {
        "@version": VERSION,
        "rdf": {
            "@id": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "@prefix": True
        },
        "rdfs": {
            "@id": "http://www.w3.org/2000/01/rdf-schema#",
            "@prefix": True
        },
        "dli": {
            "@id": "https://digitalliving.github.io/standards/ontologies/dli.jsonld#",
            "@prefix": True
        },
        "vocab": "{}vocabularies/.jsonld#".format(DLI_BASE)
    },
    "@id": "{}vocabularies/.jsonld".format(DLI_BASE),
    "@type": "dli:Vocabulary",
}