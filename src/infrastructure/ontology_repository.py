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

    def add_music(self, title: str, year: str, singer: str, genre: str):
        if self.ontology is None:
            self.ontology = self.load()
        onto = self.ontology
        with onto:
            if not hasattr(onto, 'Genre') or onto.Genre is None or not callable(onto.Genre):
                class Genre(Thing):
                    pass
                setattr(onto, 'Genre', Genre)
            genre_instance = onto.search_one(iri="*#" + genre) or onto.Genre(genre)
            if not hasattr(onto, 'Singer') or onto.Singer is None or not callable(onto.Singer):
                class Singer(Thing):
                    pass
                setattr(onto, 'Singer', Singer)
            singer_instance = onto.search_one(iri="*#" + singer) or onto.Singer(singer)

            if not hasattr(onto, 'Music') or onto.Music is None or not callable(onto.Music):
                class Music(Thing):
                    pass
                setattr(onto, 'Music', Music)
            if not hasattr(onto, 'hasYear'):
                class hasYear(onto.DataProperty):
                    domain = [onto.Music]
                    range = [str]
            if not hasattr(onto, 'hasSinger'):
                class hasSinger(onto.ObjectProperty):
                    domain = [onto.Music]
                    range = [onto.Singer]
            if not hasattr(onto, 'hasGenre'):
                class hasGenre(onto.ObjectProperty):
                    domain = [onto.Music]
                    range = [onto.Genre]
            music = onto.Music(title)
            if not hasattr(music, 'hasYear'):
                setattr(music, 'hasYear', [])
            if not hasattr(music, 'hasSinger'):
                setattr(music, 'hasSinger', [])
            if not hasattr(music, 'hasGenre'):
                setattr(music, 'hasGenre', [])
            music.hasYear.append(year)
            music.hasSinger.append(singer_instance)
            music.hasGenre.append(genre_instance)
        onto.save(file=self.path)
        return music 
