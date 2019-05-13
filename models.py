from rdflib import RDF, RDFS, Literal, OWL
from utils import uri2niceString, SW


class RDFClass:
    def __init__(self, uriref, graph):
        self.uriref = uriref
        self.namespaces = graph.namespaces
        self.graph = graph

    def title(self):
        name = uri2niceString(self.uriref, self.namespaces())
        uri, name = name.split(':')
        return name

    def label(self):
        title = None
        for title_triplet in self.graph.triples((self.uriref, RDFS.label, None)):
            if type(title_triplet[2]) != Literal or title_triplet[2].language != 'en':
                continue
            title = title_triplet[2]
        if not title:
            title = str(self)
        return title

    def get_properties(self):
        attributes = []
        for attr in self.graph.triples((None, RDFS.domain, self.uriref)):
            attributes.append(RDFProperty(attr[0], self.graph))
        attributes = sorted(attributes, key=lambda x: str(x))
        return attributes

    def get_real_parents(self):
        parents = []
        try:
            for parent in list(self.graph.triples((self.uriref, RDFS.subClassOf, None))):
                if len(list(self.graph.triples((parent[2], None, None)))) and self.uriref != parent[2]:
                    parents.append(RDFClass(parent[2], self.graph))
        except IndexError:
            return []
        return parents

    def get_type_object(self):
        try:            
            rdf_type = RDFClass(next(self.graph.triples((self.uriref, RDF.type, None)))[2], self.graph)
        except Exception as e:
            raise
        return rdf_type

    def get_type(self):
        try:            
            rdf_type = uri2niceString(next(self.graph.triples((self.uriref, RDF.type, None)))[2], self.graph.namespaces())
        except Exception as e:
            raise
        return rdf_type

    def get_dependents(self):
        all_dependees = set()
        for i in self.graph.triples((None, RDFS.subClassOf, self.uriref)):
            if i[0] == self.uriref:
                continue
            all_dependees.add(RDFClass(i[0], self.graph))
            all_dependees.union(RDFClass(i[0], self.graph).get_dependents())

        for i in self.graph.triples((None, RDF.type, self.uriref)):
            if i[0] == self.uriref:
                continue
            all_dependees.add(RDFClass(i[0], self.graph))
            all_dependees.union(RDFClass(i[0], self.graph).get_dependents())
        
        return all_dependees

    def get_children(self):
        all_dependees = set()
        for i in self.graph.triples((None, RDFS.subClassOf, self.uriref)):
            if i[0] == self.uriref:
                continue
            all_dependees.add(RDFClass(i[0], self.graph))        
        return all_dependees

    def toPython(self):
        result = {
            '@id': uri2niceString(self.uriref, self.namespaces()),
            '@type': self.get_type()
        }

        #Parents
        parents = list(self.graph.triples((self.uriref, RDFS.subClassOf, None)))
        if len(parents) > 1:
            result['subClassOf'] = [uri2niceString(x[2], self.graph) for x in parents]
        elif len(parents) == 1:
            result['subClassOf'] = uri2niceString(parents[0][2], self.graph)

        #Labels
        labels = []
        for label in self.graph.triples((self.uriref, RDFS.label, None)):
            if type(label[2]) != Literal:
                continue
            labels.append({
                '@language': label[2].language,
                '@value': str(label[2]),
            })
        if len(labels):
            result['rdfs:label'] = labels

        #Comments
        comments = []
        for comment in self.graph.triples((self.uriref, RDFS.comment, None)):
            if type(comment[2]) != Literal:
                continue
            comments.append({
                '@language': comment[2].language,
                '@value': str(comment[2]),
            })
        if len(comments):
            result['rdfs:comment'] = comments

        # OWL Version Info
        try:            
            result['owl:versionInfo'] = next(self.graph.triples((self.uriref, OWL.versionInfo, None)))[2]
        except Exception as e:
            pass

        # VS Status
        try:            
            result['vs:term_status'] = next(self.graph.triples((self.uriref, SW.term_status, None)))[2]
        except Exception as e:
            pass

        return result

    def __hash__(self):
        return hash((str(self), self.get_type()))

    def __str__(self):
        return uri2niceString(self.uriref, self.namespaces())


class RDFProperty:
    def __init__(self, uriref, graph):
        self.uriref = uriref
        self.namespaces = graph.namespaces
        self.graph = graph

    def label(self):
        title = None
        for title_triplet in self.graph.triples((self.uriref, RDFS.label, None)):
            if type(title_triplet[2]) != Literal or title_triplet[2].language != 'en':
                continue
            title = title_triplet[2]
        if not title:
            title = str(self)
        return title

    def get_supported_range(self):
        supported = []
        for item in self.graph.triples((self.uriref, RDFS.range, None)):
            supported.append(RDFClass(item[2], self.graph))
        return supported

    def get_domains(self):
        domains = []
        for domain in self.graph.triples((self.uriref, RDFS.domain, None)):
            domains.append(RDFClass(domain[2], self.graph))
        return domains

    def get_type(self):
        try:            
            rdf_type = uri2niceString(next(self.graph.triples((self.uriref, RDF.type, None)))[2], self.graph.namespaces())
        except Exception as e:
            raise
        return rdf_type

    def toPython(self):
        result = {
            '@id': uri2niceString(self.uriref, self.namespaces())
        }

        # Determine type
        result['@type'] = self.get_type()

        #Labels
        labels = []
        for label in self.graph.triples((self.uriref, RDFS.label, None)):
            if type(label[2]) != Literal:
                continue
            labels.append({
                '@language': label[2].language,
                '@value': str(label[2]),
            })
        if len(labels):
            result['rdfs:label'] = labels

        #Comments
        comments = []
        for comment in self.graph.triples((self.uriref, RDFS.comment, None)):
            if type(comment[2]) != Literal:
                continue
            comments.append({
                '@language': comment[2].language,
                '@value': str(comment[2]),
            })
        if len(comments):
            result['rdfs:comment'] = comments

        #Doamin
        domains = []
        for domain in self.graph.triples((self.uriref, RDFS.domain, None)):
            domains.append(uri2niceString(domain[2]))
        if len(domains):
            result['domain'] = domains

        #Doamin
        ranges = []
        for r in self.graph.triples((self.uriref, RDFS.range, None)):
            ranges.append(uri2niceString(r[2]))
        if len(ranges):
            result['range'] = ranges
        
        # OWL Version Info
        try:            
            result['owl:versionInfo'] = next(self.graph.triples((self.uriref, OWL.versionInfo, None)))[2]
        except Exception as e:
            pass

        # VS Status
        try:            
            result['vs:term_status'] = next(self.graph.triples((self.uriref, SW.term_status, None)))[2]
        except Exception as e:
            pass

        return result

    def __hash__(self):
        return hash((str(self), self.get_type()))

    def __str__(self):
        return uri2niceString(self.uriref, self.namespaces())