from application.ontology_service import OntologyService

if __name__ == "__main__":
    service = OntologyService("data/graph.owl")
    service.load_ontology()
