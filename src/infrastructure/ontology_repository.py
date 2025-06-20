from owlready2 import get_ontology, Imp, sync_reasoner_pellet, ObjectProperty, DataProperty, Thing
from .rule_repository import RuleRepository

class OntologyRepository:
    def __init__(self, path: str):
        self.path = path
        self.ontology = None

    def load(self):
        self.ontology = get_ontology(self.path).load()
        onto = self.ontology
        with onto:
            if not hasattr(onto, 'hasStars'):
                class hasStars(onto.DataProperty):
                    domain = [onto.Rating]
                    range = [int]
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
            existing_user = next((u for u in onto.individuals() if u.__class__.__name__ == 'User' and u.name == userName and hasattr(u, 'email') and email in u.email and hasattr(u, 'birthYear') and birthYear in u.birthYear), None)
            if existing_user:
                raise Exception('A user with the same name, email, and birth year already exists.')
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

    def get_user(self, userName: str, email: str):
        if self.ontology is None:
            self.ontology = self.load()
        onto = self.ontology
        user = next((u for u in onto.individuals() if u.__class__.__name__ == 'User' and u.name == userName and hasattr(u, 'email') and email in u.email), None)
        return user 

    def list_musics(self, limit=10, search='', order_by='title', order_dir='asc', user_name=None):
        if self.ontology is None:
            self.ontology = self.load()
        onto = self.ontology
        user_ratings = {}
        if order_by == 'user_rating' and user_name:
            user = next((u for u in onto.individuals() if u.__class__.__name__ == 'User' and u.name == user_name), None)
            if user:
                for r in getattr(user, 'hasRated', []):
                    if hasattr(r, 'ratedMusic') and hasattr(r, 'hasStars') and r.hasStars:
                        for m in r.ratedMusic:
                            user_ratings[m.name] = r.hasStars[0]
        musics = []
        for m in onto.individuals():
            if m.__class__.__name__ == 'Music':
                music_dict = {
                    'title': m.name,
                    'year': m.hasYear[0] if hasattr(m, 'hasYear') and m.hasYear else '',
                    'singer': m.hasSinger[0].name if hasattr(m, 'hasSinger') and m.hasSinger else '',
                    'genre': m.hasGenre[0].name if hasattr(m, 'hasGenre') and m.hasGenre else ''
                }
                if order_by == 'user_rating' and user_name:
                    music_dict['user_rating'] = user_ratings.get(m.name)
                musics.append(music_dict)
        if search:
            search_lower = search.lower()
            musics = [m for m in musics if any(search_lower in str(v).lower() for v in m.values())]
        reverse = order_dir == 'desc'
        if order_by == 'user_rating' and user_name:
            musics = sorted(musics, key=lambda m: (m.get('user_rating') is None, m.get('user_rating')), reverse=reverse)
        else:
            musics = sorted(musics, key=lambda m: str(m.get(order_by, '')).lower(), reverse=reverse)
        return musics[:limit]

    def add_rating(self, userName: str, music_title: str, stars: int):
        if self.ontology is None:
            self.ontology = self.load()
        onto = self.ontology
        user = next((u for u in onto.individuals() if u.__class__.__name__ == 'User' and u.name == userName), None)
        music = next((m for m in onto.individuals() if m.__class__.__name__ == 'Music' and m.name == music_title), None)
        if not user or not music:
            raise Exception('Usuário ou música não encontrados')
        with onto:
            if not hasattr(onto, 'Rating') or onto.Rating is None or not callable(onto.Rating):
                class Rating(Thing): pass
                setattr(onto, 'Rating', Rating)
            rating = onto.Rating(f"{userName}_{music_title}_rating")
            if not hasattr(onto, 'hasStars'):
                class hasStars(onto.DataProperty):
                    domain = [onto.Rating]
                    range = [int]
            if not hasattr(onto, 'ratedMusic'):
                class ratedMusic(onto.ObjectProperty):
                    domain = [onto.Rating]
                    range = [onto.Music]
            if not hasattr(onto, 'hasRated'):
                class hasRated(onto.ObjectProperty):
                    domain = [onto.User]
                    range = [onto.Rating]
            rating.hasStars = [stars]
            rating.ratedMusic = [music]
            user.hasRated.append(rating)
        onto.save(file=self.path)
        return rating 

    def get_user_rating(self, userName: str, music_title: str):
        if self.ontology is None:
            self.ontology = self.load()
        onto = self.ontology
        user = next((u for u in onto.individuals() if u.__class__.__name__ == 'User' and u.name == userName), None)
        music = next((m for m in onto.individuals() if m.__class__.__name__ == 'Music' and m.name == music_title), None)
        if not user or not music:
            return None
        for r in getattr(user, 'hasRated', []):
            if hasattr(r, 'ratedMusic') and music in getattr(r, 'ratedMusic', []):
                if hasattr(r, 'hasStars') and r.hasStars:
                    return r.hasStars[0]
        return None

    def list_recommended_musics(self, user_name):
        if self.ontology is None:
            self.ontology = self.load()
        try:
            rule_repo = RuleRepository(self.path)
            for attr in dir(rule_repo):
                if attr.startswith('apply_') and attr.endswith('_rule') and callable(getattr(rule_repo, attr)):
                    getattr(rule_repo, attr)()
        except Exception:
            pass
        onto = self.ontology
        user = next((u for u in onto.individuals() if u.__class__.__name__ == 'User' and u.name == user_name), None)
        musics = []
        if user and hasattr(user, 'recommendMusic'):
            for m in getattr(user, 'recommendMusic', []):
                musics.append({
                    'title': m.name,
                    'year': m.hasYear[0] if hasattr(m, 'hasYear') and m.hasYear else '',
                    'singer': m.hasSinger[0].name if hasattr(m, 'hasSinger') and m.hasSinger else '',
                    'genre': m.hasGenre[0].name if hasattr(m, 'hasGenre') and m.hasGenre else ''
                })
        return musics
