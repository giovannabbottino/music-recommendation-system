from owlready2 import get_ontology, Imp, sync_reasoner_pellet, ObjectProperty

class OntologyRepository:
    def __init__(self, path: str):
        self.path = path
        self.ontology = None

    def load(self):
        self.ontology = get_ontology(self.path).load()
        return self.ontology

    def apply_genre_preference_rule(self):
        """
        Adds and applies a SWRL rule:
        If a user rated a music of a genre with 5 stars, infer that the user has a preference for that genre.
        SWRL: User(?u) ^ Rating(?r) ^ Genre(?g) ^ hasRating(?r, 5) ^ ratedBy(?r, ?u) ^ hasGenre(?r, ?g) -> hasPreference(?u, ?g)
        """
        if self.ontology is None:
            raise Exception("Ontology not loaded.")
        onto = self.ontology
        with onto:
            rule = """
                User(?u) ^ Rating(?r) ^ Genre(?g) ^ hasRating(?r, 5) ^ ratedBy(?r, ?u) ^ hasGenre(?r, ?g) -> hasPreference(?u, ?g)
            """
            imp = Imp()
            imp.set_as_rule(rule)
        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        onto.save(file=self.path)

    def apply_music_recommendation_rule(self):
        """
        Adds and applies a SWRL rule for music recommendation:
        If a user has a preference for a genre, recommend music of that genre.
        SWRL: User(?u) ^ Genre(?g) ^ Music(?m) ^ hasPreference(?u, ?g) ^ musicHasGenre(?m, ?g) -> recommendMusic(?u, ?m)
        """
        if self.ontology is None:
            raise Exception("Ontology not loaded.")
        onto = self.ontology
        with onto:
            if not hasattr(onto, 'recommendMusic'):
                class recommendMusic(ObjectProperty):
                    domain = [onto.User]
                    range = [onto.Music]
            
            rule = """
                User(?u) ^ Genre(?g) ^ Music(?m) ^ hasPreference(?u, ?g) ^ musicHasGenre(?m, ?g) -> recommendMusic(?u, ?m)
            """
            imp = Imp()
            imp.set_as_rule(rule)
        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        onto.save(file=self.path)

    def apply_favorite_singer_rule(self):
        """
        Adds and applies a SWRL rule:
        If a user rated a music of a singer with 5 stars, infer that the singer is a favorite of the user.
        SWRL: User(?u) ^ Rating(?r) ^ Music(?m) ^ Singer(?s) ^ hasRating(?r, 5) ^ ratedBy(?r, ?u) ^ hasSinger(?m, ?s) ^ ratesMusic(?r, ?m) -> favoriteSinger(?u, ?s)
        """
        if self.ontology is None:
            raise Exception("Ontology not loaded.")
        onto = self.ontology
        with onto:
            if not hasattr(onto, 'favoriteSinger'):
                class favoriteSinger(ObjectProperty):
                    domain = [onto.User]
                    range = [onto.Singer]
            rule = """
                User(?u) ^ Rating(?r) ^ Music(?m) ^ Singer(?s) ^ hasRating(?r, 5) ^ ratedBy(?r, ?u) ^ hasSinger(?m, ?s) ^ ratesMusic(?r, ?m) -> favoriteSinger(?u, ?s)
            """
            imp = Imp()
            imp.set_as_rule(rule)
        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        onto.save(file=self.path) 
