from infrastructure.rule_repository import RuleRepository

class RuleService:
    def __init__(self, ontology_path: str):
        self.repo = RuleRepository(ontology_path)
        self.ontology = None

    def load_ontology(self):
        self.ontology = self.repo.load()
        return self.ontology

    def apply_genre_preference_rule(self):
        self.repo.apply_genre_preference_rule()

    def apply_music_recommendation_rule(self):
        self.repo.apply_music_recommendation_rule()

    def apply_favorite_singer_rule(self):
        self.repo.apply_favorite_singer_rule()

    def apply_singer_recommendation_rule(self):
        self.repo.apply_singer_recommendation_rule() 
