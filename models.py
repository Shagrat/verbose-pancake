from rdflib import RDF, RDFS, Literal, OWL, XSD, BNode
from utils import uri2niceString, SW, POT
from const import POT_BASE

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
        labels = []
        for label in self.graph.triples((self.uriref, POT.label, None)):
            if not isinstance(label[2], BNode):
                continue
            label_node = list(self.graph.triples((label[2], None, None)))[0]
            if type(label_node[2]) != Literal or label_node[2].language != 'en':
                continue
            title = label_node[2]

        if not title:
            title = str(self)
        return title

    def get_properties(self):
        attributes = []

        parents =  [RDFClass(x[2], self.graph) for x in self.graph.triples((self.uriref, RDFS.subClassOf, None))]
        while len(parents):
            tParents = []
            for parent in parents:
                if parent.uriref == self.uriref:
                    continue
                for attr in self.graph.triples((None, RDFS.domain, parent.uriref)):
                    attributes.append(RDFProperty(attr[0], self.graph))
                tParents +=  [RDFClass(x[2], self.graph) for x in self.graph.triples((parent.uriref, RDFS.subClassOf, None))]
            parents = tParents.copy()
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
            return None
        return rdf_type

    def get_type(self):
        try:            
            rdf_type = uri2niceString(next(self.graph.triples((self.uriref, RDF.type, None)))[2], self.graph.namespaces())
        except Exception as e:
            return None
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

    def get_new_type_id(self):
        base = POT_BASE + 'context/'
        parents_path = ''
        if self.get_real_parents():
            real_parent = self.get_real_parents()[0]
            while real_parent:
                parents_path = real_parent.title() + '/' + parents_path
                if real_parent.get_real_parents():
                    real_parent = real_parent.get_real_parents()[0]
                else:
                    real_parent = None
        name = uri2niceString(self.uriref, self.namespaces())
        uri, name = name.split(':')
        return uri + ':' + parents_path + self.title()

    def get_labels(self):
        labels = []
        for label in self.graph.triples((self.uriref, POT.label, None)):
            if not isinstance(label[2], BNode):
                continue
            label_node = list(self.graph.triples((label[2], None, None)))[0]
            labels.append({
                '@language': label_node[2].language,
                '@value': str(label_node[2]),
            })
        return labels

    def toPython(self):
        result = {
            '@id': self.get_new_type_id(),
            '@type': self.get_type()
        }

        #Parents
        if self.get_real_parents():
            result['subClassOf'] = self.get_real_parents()[0].get_new_type_id()
        else:
            parents = list(self.graph.triples((self.uriref, RDFS.subClassOf, None)))
            if len(parents) > 1:
                result['subClassOf'] = [x.get_new_type_id() for x in parents]
            elif len(parents) == 1:
                result['subClassOf'] = uri2niceString(parents[0][2], self.graph)

        #Labels
        labels = self.get_labels()
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

    def title(self):
        name = uri2niceString(self.uriref, self.namespaces())
        uri, name = name.split(':')
        return name

    def label(self, label_domain_selected=None):
        title = None
        for label in self.get_labels(label_domain_selected=label_domain_selected):
            if label.get('@language') == 'en-us':
                title = label.get('@value')
        if not title:
            title = str(self)
        return title

    def get_supported_range(self):
        supported = []
        for item in self.graph.triples((self.uriref, RDFS.range, None)):
            supported.append(RDFClass(item[2], self.graph))
        return supported

    def get_restrictions(self):
        restriction = {}
        for item in self.graph.triples((self.uriref, XSD.restriction, None)):
            for bnode in self.graph.triples((item[2], None, None)):
                restriction[uri2niceString(bnode[1])] = bnode[2]
        return restriction

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

    def get_labels(self, label_domain_selected=None):
        labels = []
        domains = [uri2niceString(x[2]) for x in self.graph.triples((self.uriref, RDFS.domain, None))]
        for label in self.graph.triples((self.uriref, POT.label, None)):
            if not isinstance(label[2], BNode):
                continue
            label_domain = list(self.graph.triples((label[2], POT.domain, None)))[0]
            label_text = list(self.graph.triples((label[2], RDFS.label, None)))[0]
            if isinstance(label_domain[2], Literal):
                label_domain = str(label_domain[2])
            if label_domain not in domains:
                continue
            if label_domain_selected and str(label_domain_selected) != label_domain:
                not_found = True
                parents =  [RDFClass(x[2], self.graph) for x in self.graph.triples((label_domain_selected.uriref, RDFS.subClassOf, None))]
                while len(parents):
                    tParents = []
                    for parent in parents:
                        if parent.uriref == self.uriref:
                            continue
                        if str(parent) == label_domain:
                            not_found = False
                            break
                        tParents +=  [RDFClass(x[2], self.graph) for x in self.graph.triples((parent.uriref, RDFS.subClassOf, None))]
                    parents = tParents.copy()
                if not_found:
                    continue
            labels.append({
                '@language': label_text[2].language,
                '@value': str(label_text[2]),
            })
        return labels

    def get_comments(self, comment_domain_selected=None):
        comments = []
        domains = [uri2niceString(x[2]) for x in self.graph.triples((self.uriref, RDFS.domain, None))]
        for comment in self.graph.triples((self.uriref, POT.comment, None)):
            if not isinstance(comment[2], BNode):
                continue
            comment_domain = list(self.graph.triples((comment[2], POT.domain, None)))[0]
            comment_text = list(self.graph.triples((comment[2], RDFS.comment, None)))[0]
            if isinstance(comment_domain[2], Literal):
                comment_domain = str(comment_domain[2])
            if comment_domain not in domains:
                continue
            if comment_domain_selected and str(comment_domain_selected) != comment_domain:
                not_found = True
                parents =  [RDFClass(x[2], self.graph) for x in self.graph.triples((comment_domain_selected.uriref, RDFS.subClassOf, None))]
                while len(parents):
                    tParents = []
                    for parent in parents:
                        if parent.uriref == self.uriref:
                            continue
                        if str(parent) == comment_domain:
                            not_found = False
                            break
                        tParents +=  [RDFClass(x[2], self.graph) for x in self.graph.triples((parent.uriref, RDFS.subClassOf, None))]
                    parents = tParents.copy()
                if not_found:
                    continue
            comments.append({
                '@language': comment_text[2].language,
                '@value': str(comment_text[2]),
            })
        return comments

    def toVocab(self, noId=False, parent_domain=None):
        result = {
            '@id': uri2niceString(self.uriref, self.namespaces()),
            '@type': 'pot:SupportedAttribute',
            "dli:title": self.label(parent_domain),
            "dli:required": False
        }        

        if noId:
            del result['@id']


        comments = self.get_comments(comment_domain_selected=parent_domain)
        if len(comments):
            result['dli:description'] = comments

        #Doamin
        if len(self.get_supported_range()):
            result['dli:valueType'] = [x.get_new_type_id() for x in self.get_supported_range()]

        #Restriction
        result['xsd:restriction'] = self.get_restrictions()

        return result
    
    def toPython(self, noId=False, parent_domain=None):
        result = {
            '@id': uri2niceString(self.uriref, self.namespaces())
        }

        if noId:
            del result['@id']

        # Determine type
        result['@type'] = self.get_type()

        #Labels
        labels = self.get_labels(label_domain_selected=parent_domain)
        if len(labels):
            result['rdfs:label'] = labels

        #Comments
        comments = self.get_comments(comment_domain_selected=parent_domain)
        if len(comments):
            result['rdfs:comment'] = comments

        #Doamin
        domains = []
        for domain in self.graph.triples((self.uriref, RDFS.domain, None)):
            domains.append(uri2niceString(domain[2]))
        if len(domains):
            result['domain'] = domains

        #Ranges
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