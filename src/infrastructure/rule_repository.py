from owlready2 import Imp, sync_reasoner_pellet, get_ontology

class RuleRepository:
    def __init__(self, path: str):
        self.path = path
        self.ontology = None

    def load(self):
        self.ontology = get_ontology(self.path).load()
        return self.ontology

    def apply_genre_preference_rule(self):
        if self.ontology is None:
            self.load()
        onto = self.ontology
        with onto:
            rule = """
                User(?u) ^ Rating(?r) ^ Genre(?g) ^ hasStars(?r, 5) ^ hasRated(?u, ?r) ^ hasGenre(?m, ?g) ^ ratedMusic(?r, ?m) -> hasPreference(?u, ?g)
            """
            imp = Imp()
            imp.set_as_rule(rule)
        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        onto.save(file=self.path)

    def apply_music_recommendation_rule(self):
        if self.ontology is None:
            self.load()
        onto = self.ontology
        with onto:
            if not hasattr(onto, 'recommendMusic'):
                class recommendMusic(onto.ObjectProperty):
                    domain = [onto.User]
                    range = [onto.Music]
            rule = """
                User(?u) ^ Genre(?g) ^ Music(?m) ^ hasPreference(?u, ?g) ^ hasGenre(?m, ?g) -> recommendMusic(?u, ?m)
            """
            imp = Imp()
            imp.set_as_rule(rule)
        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        onto.save(file=self.path)

    def apply_favorite_singer_rule(self):
        if self.ontology is None:
            self.load()
        onto = self.ontology
        with onto:
            if not hasattr(onto, 'hasPreference'):
                class hasPreference(onto.ObjectProperty):
                    domain = [onto.User]
                    range = [onto.Singer]
            rule = """
                User(?u) ^ Rating(?r) ^ Music(?m) ^ Singer(?s) ^ hasStars(?r, 5) ^ hasRated(?u, ?r) ^ hasSinger(?m, ?s) ^ ratedMusic(?r, ?m) -> hasPreference(?u, ?s)
            """
            imp = Imp()
            imp.set_as_rule(rule)
        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        onto.save(file=self.path)

    def apply_singer_recommendation_rule(self):
        if self.ontology is None:
            self.load()
        onto = self.ontology
        with onto:
            if not hasattr(onto, 'recommendMusic'):
                class recommendMusic(onto.ObjectProperty):
                    domain = [onto.User]
                    range = [onto.Music]
            rule = """
                User(?u) ^ Singer(?s) ^ Music(?m) ^ hasPreference(?u, ?s) ^ hasSinger(?m, ?s) -> recommendMusic(?u, ?m)
            """
            imp = Imp()
            imp.set_as_rule(rule)
        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        onto.save(file=self.path) 
