VERSION = 1.1
LABEL_REF = 'http://www.w3.org/2000/01/rdf-schema#label'
COMMENT_REF = 'http://www.w3.org/2000/01/rdf-schema#comment'
RANGE_REF = 'http://www.w3.org/2000/01/rdf-schema#range'

BASE_IDENTITY = {
    '@version': VERSION,
    '@vocab': "https://platformoftrust.github.io/standards/vocabularies/.jsonld#",
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

BASE_VOCABULARY = {
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
            "@id": "https://platformoftrust.github.io/standards/ontologies/pot.jsonld#",
            "@prefix": True
        },
        "vocab": "https://platformoftrust.github.io/standards/vocabularies/building.jsonld#"
    },
    "@id": "https://platformoftrust.github.io/standards/vocabularies/building.jsonld",
    "@type": "pot:Vocabulary",
}