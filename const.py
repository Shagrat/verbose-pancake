VERSION = 1.1
LABEL_REF = 'http://www.w3.org/2000/01/rdf-schema#label'
COMMENT_REF = 'http://www.w3.org/2000/01/rdf-schema#comment'
RANGE_REF = 'http://www.w3.org/2000/01/rdf-schema#range'
SUBCLASS_REF = 'http://www.w3.org/2000/01/rdf-schema#subClassOf'
#POT_BASE = 'https://standards.oftrust.net/'
POT_BASE = 'http://verbose.terrikon.co/v1/'
POT_EXPORT = 'https://standards.oftrust.net/v1/'
DLI_BASE = 'https://digitalliving.github.io/standards/'
DLI_EXPORT = 'https://standards.lifeengine.io/v1/'
CONF_NAME = 'settings.conf'

BASE_IDENTITY_POT = {
    '@version': VERSION,
    '@vocab': "{}vocabularies/.jsonld#".format(POT_EXPORT),
    '@classDefinition':'',
    "pot": {
        "@id": "{}Vocabulary/".format(POT_EXPORT),
        "@prefix": True
    },
    "dli": {
        "@id": "https://standards.lifeengine.io/v1/Vocabulary/",
        "@prefix": True
    },
    "data": "dli:data",
    "metadata": "dli:metadata",
}

BASE_DIRECTORY_POT = {
    '@context': {
        '@version': VERSION,
        "pot": {
            "@id": "{}Vocabulary/".format(POT_EXPORT),
            "@prefix": True
        },
        "dli": {
            "@id": "https://standards.lifeengine.io/v1/Vocabulary/",
            "@prefix": True
        },
        "owl": {
            "@id": "http://www.w3.org/2002/07/owl#",
            "@prefix": True
        },
        "vs": {
            "@id": "http://www.w3.org/2003/06/sw-vocab-status/ns#",
            "@prefix": True
        },
        "xsd": {
            "@id": "http://www.w3.org/2001/XMLSchema#",
            "@prefix": True
        },
        "label": {
            '@id': 'rdfs:label',
            "@container": ['@language', '@set']
        },
        "comment": {
            '@id': 'rdfs:comment',
            "@container": ['@language', '@set']
        }
    }
}

BASE_DEFFINITION_POT = {
    "@context": {
        "@version": VERSION,
        "xsd": {
            "@id": "http://www.w3.org/2001/XMLSchema#",
            "@prefix": True
        },
        "dli": {
            "@id": "https://standards.lifeengine.io/v1/Vocabulary/",
            "@prefix": True
        },
        "pot": {
            "@id": "{}Vocabulary/".format(POT_EXPORT),
            "@prefix": True
        },
        "description": {},
        "label": {
            '@id': 'rdfs:label',
            "@container": ['@language', '@set']
        },
        "comment": {
            '@id': 'rdfs:comment',
            "@container": ['@language', '@set']
        }
    },
    "@id": "{}vocabularies/.jsonld".format(POT_EXPORT),
}


BASE_VOCABULARY_POT = {
    "@context": {
        '@version': VERSION,
        "pot": {
            "@id": "{}Vocabulary/".format(POT_EXPORT),
            "@prefix": True
        },
        "dli": {
            "@id": "https://standards.lifeengine.io/v1/Vocabulary/",
            "@prefix": True
        },
        "rdf": {
            "@id": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "@prefix": True
        },
        "rdfs": {
            "@id": "http://www.w3.org/2000/01/rdf-schema#",
            "@prefix": True
        },
        "owl": {
            "@id": "http://www.w3.org/2002/07/owl#",
            "@prefix": True
        },
        "vs": {
            "@id": "http://www.w3.org/2003/06/sw-vocab-status/ns#",
        },
        "xsd": {
            "@id": "http://www.w3.org/2001/XMLSchema#",
            "@prefix": True
        },
        "label": "",
        "comment": ""
    }
}


BASE_IDENTITY_DLI = {
    '@version': VERSION,
    '@vocab': "{}vocabularies/.jsonld#".format(DLI_EXPORT),
    "dli": {
        "@id": "https://standards.lifeengine.io/v1/Vocabulary/",
        "@prefix": True
    },
    "data": "dli:data",
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
            "@id": "https://standards.lifeengine.io/v1/Vocabulary/",
            "@prefix": True
        },
        "vocab": "{}vocabularies/.jsonld#".format(DLI_EXPORT)
    },
    "@id": "{}vocabularies/.jsonld".format(DLI_EXPORT),
    "@type": "dli:Vocabulary",
}
