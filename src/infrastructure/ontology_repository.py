from owlready2 import get_ontology, Imp, sync_reasoner_pellet, ObjectProperty, DataProperty

class OntologyRepository:
    def __init__(self, path: str):
        self.path = path
        self.ontology = None

    def load(self):
        self.ontology = get_ontology(self.path).load()
        onto = self.ontology
        with onto:
            # Data property
            if not hasattr(onto, 'hasStars'):
                class hasStars(onto.DataProperty):
                    domain = [onto.Rating]
                    range = [int]
            # Object properties
            if not hasattr(onto, 'ratedMusic'):
                class ratedMusic(onto.ObjectProperty):
                    domain = [onto.Rating]
                    range = [onto.Music]
            if not hasattr(onto, 'hasSinger'):
                class hasSinger(onto.ObjectProperty):
                    domain = [onto.Music]
                    range = [onto.Singer]
            if not hasattr(onto, 'hasGenre'):
                class hasGenre(onto.ObjectProperty):
                    domain = [onto.Music]
                    range = [onto.Genre]
            if not hasattr(onto, 'hasPreference'):
                class hasPreference(onto.ObjectProperty):
                    domain = [onto.User]
                    range = [onto.Genre, onto.Music]
            if not hasattr(onto, 'hasRated'):
                class hasRated(onto.ObjectProperty):
                    domain = [onto.User]
                    range = [onto.Rating]
        return self.ontology

    def apply_genre_preference_rule(self):
        """
        SWRL: User(?u) ^ Rating(?r) ^ Genre(?g) ^ hasStars(?r, 5) ^ hasRated(?u, ?r) ^ hasGenre(?m, ?g) ^ ratedMusic(?r, ?m) -> hasPreference(?u, ?g)
        """
        if self.ontology is None:
            raise Exception("Ontology not loaded.")
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
        """
        SWRL: User(?u) ^ Genre(?g) ^ Music(?m) ^ hasPreference(?u, ?g) ^ hasGenre(?m, ?g) -> recommendMusic(?u, ?m)
        """
        if self.ontology is None:
            raise Exception("Ontology not loaded.")
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
        """
        SWRL: User(?u) ^ Rating(?r) ^ Music(?m) ^ Singer(?s) ^ hasStars(?r, 5) ^ hasRated(?u, ?r) ^ hasSinger(?m, ?s) ^ ratedMusic(?r, ?m) -> hasPreference(?u, ?s)
        """
        if self.ontology is None:
            raise Exception("Ontology not loaded.")
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
        """
        SWRL: User(?u) ^ Singer(?s) ^ Music(?m) ^ hasPreference(?u, ?s) ^ hasSinger(?m, ?s) -> recommendMusic(?u, ?m)
        """
        if self.ontology is None:
            raise Exception("Ontology not loaded.")
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
