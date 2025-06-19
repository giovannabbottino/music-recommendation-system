from owlready2 import get_ontology

class OntologyRepository:
    def __init__(self, path: str):
        self.path = path
        self.ontology = None

    def load(self):
        self.ontology = get_ontology(self.path).load()
        return self.ontology 
