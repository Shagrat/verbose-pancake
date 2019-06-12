from collections import namedtuple
import rdflib

POT = rdflib.Namespace('https://standards.oftrust.net/Context/')
DLI = rdflib.Namespace('https://digitalliving.github.io/standards/ontologies/dli.jsonld#')
SW = rdflib.Namespace('http://www.w3.org/2003/06/sw-vocab-status/ns#')

TripletTuple = namedtuple('TripletTuple', 'subject, predicate, object')
 
NAMESPACES_DEFAULT = [
    ("rdf", rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#")),
    ("rdfs", rdflib.URIRef("http://www.w3.org/2000/01/rdf-schema#")),
    ("xml", rdflib.URIRef("http://www.w3.org/XML/1998/namespace")),
    ("xsd", rdflib.URIRef("http://www.w3.org/2001/XMLSchema#")),
    ('foaf', rdflib.URIRef("http://xmlns.com/foaf/0.1/")),
    ("skos", rdflib.URIRef("http://www.w3.org/2004/02/skos/core#")),
    ("owl", rdflib.URIRef("http://www.w3.org/2002/07/owl#")),
    ("dli", rdflib.URIRef("https://digitalliving.github.io/standards/ontologies/dli.jsonld#")),
    ("pot", rdflib.URIRef("https://standards.oftrust.net/Context/")),
]


def inferNamespacePrefix(aUri):
    """
    From a URI returns the last bit and simulates a namespace prefix when rendering the ontology.
    eg from <'http://www.w3.org/2008/05/skos#'>
        it returns the 'skos' string
    """
    stringa = aUri.__str__()
    try:
        prefix = stringa.replace("#", "").replace("pot.jsonld", 'pot').split("/")[-1]
    except:
        prefix = ""
    return prefix


def uri2niceString(aUri, namespaces=None):
    """
    From a URI, returns a nice string representation that uses also the namespace symbols
    Cuts the uri of the namespace, and replaces it with its shortcut (for base, attempts to infer it or leaves it blank)

    Namespaces are a list

    [('xml', rdflib.URIRef('http://www.w3.org/XML/1998/namespace'))
    ('', rdflib.URIRef('http://cohereweb.net/ontology/cohere.owl#'))
    (u'owl', rdflib.URIRef('http://www.w3.org/2002/07/owl#'))
    ('rdfs', rdflib.URIRef('http://www.w3.org/2000/01/rdf-schema#'))
    ('rdf', rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
    (u'xsd', rdflib.URIRef('http://www.w3.org/2001/XMLSchema#'))]

    """
    if not namespaces:
        namespaces = NAMESPACES_DEFAULT

    if not aUri:
        stringa = ""
    elif type(aUri) == rdflib.term.URIRef:
        # we have a URI: try to create a qName
        stringa = aUri.toPython()
        for aNamespaceTuple in namespaces:
            try:  # check if it matches the available NS
                if stringa.find(aNamespaceTuple[1].__str__()) == 0:
                    if aNamespaceTuple[0]:  # for base NS, it's empty
                        stringa = aNamespaceTuple[0] + ":" + stringa[len(
                            aNamespaceTuple[1].__str__()):]
                    else:
                        prefix = inferNamespacePrefix(aNamespaceTuple[1])
                        if prefix:
                            stringa = prefix + ":" + stringa[len(
                                aNamespaceTuple[1].__str__()):]
                        else:
                            stringa = ":" + stringa[len(aNamespaceTuple[1].
                                                        __str__()):]
            except Exception as e:
                stringa = "error"

    elif type(aUri) == rdflib.term.Literal:
        stringa = "\"%s\"" % aUri  # no string casting so to prevent encoding errors
    else:
        # print(type(aUri))
        if type(aUri) == type(u''):
            stringa = aUri
        else:
            stringa = aUri.toPython()
    return stringa


def niceString2uri(aUriString, namespaces=None):
    """
    From a string representing a URI possibly with the namespace qname, returns a URI instance.

    gold:Citation  ==> rdflib.term.URIRef(u'http://purl.org/linguistics/gold/Citation')

    Namespaces are a list

    [('xml', rdflib.URIRef('http://www.w3.org/XML/1998/namespace'))
    ('', rdflib.URIRef('http://cohereweb.net/ontology/cohere.owl#'))
    (u'owl', rdflib.URIRef('http://www.w3.org/2002/07/owl#'))
    ('rdfs', rdflib.URIRef('http://www.w3.org/2000/01/rdf-schema#'))
    ('rdf', rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
    (u'xsd', rdflib.URIRef('http://www.w3.org/2001/XMLSchema#'))]

    """

    if not namespaces:
        namespaces = []

    for aNamespaceTuple in namespaces:
        if aNamespaceTuple[0] and aUriString.find(
                aNamespaceTuple[0].__str__() + ":") == 0:
            aUriString_name = aUriString.split(":")[1]
            return rdflib.term.URIRef(aNamespaceTuple[1] + aUriString_name)

    # we dont handle the 'base' URI case
    return rdflib.term.URIRef(aUriString)
