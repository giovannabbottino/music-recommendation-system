from owlready2 import get_ontology, Imp, sync_reasoner_pellet, ObjectProperty, DataProperty, Thing

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

    def add_user(self, userName: str, birthYear: str, email: str):
        if self.ontology is None:
            self.ontology = self.load()
        onto = self.ontology
        with onto:
            if not hasattr(onto, 'User') or onto.User is None or not callable(onto.User):
                class User(Thing):
                    pass
                setattr(onto, 'User', User)
            if not hasattr(onto, 'birthYear') or onto.birthYear is None:
                class BirthYearProperty(DataProperty):
                    domain = [onto.User]
                    range = [str]
                setattr(onto, 'birthYear', BirthYearProperty)
            if not hasattr(onto, 'email') or onto.email is None:
                class EmailProperty(DataProperty):
                    domain = [onto.User]
                    range = [str]
                setattr(onto, 'email', EmailProperty)
            user = onto.User(userName)
            user.birthYear = [birthYear]
            user.email = [email]
        onto.save(file=self.path)
        return user 
