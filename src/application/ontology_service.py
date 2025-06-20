from infrastructure.ontology_repository import OntologyRepository

class OntologyService:
    def __init__(self, ontology_path: str):
        self.repo = OntologyRepository(ontology_path)
        self.ontology = None

    def load_ontology(self):
        self.ontology = self.repo.load()
        print(f"Ontologia carregada com {len(list(self.ontology.classes()))} classes.")
        return self.ontology 

    def apply_genre_preference_rule(self):
        self.repo.apply_genre_preference_rule()

    def apply_music_recommendation_rule(self):
        self.repo.apply_music_recommendation_rule()

    def apply_favorite_singer_rule(self):
        self.repo.apply_favorite_singer_rule()
