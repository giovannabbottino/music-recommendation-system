from owlready2 import get_ontology, Imp, sync_reasoner_pellet

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
