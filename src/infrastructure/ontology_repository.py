import re
from typing import Optional
from owlready2 import *

def _safe_name(name: str):
    return re.sub(r'\W+', '_', name.strip())

class OntologyRepository:
    def __init__(self, path: str):
        self.path = path
        self.onto = None

    def load(self):
        try:
            self.onto = get_ontology(self.path).load()
            self.ensure_classes()
            print("Loaded!")
        except Exception as e:
            print("Error loading:", e)
            self.onto = get_ontology(self.path)
        return self.onto

    def save(self):
        if self.onto:
            self.onto.save(file=self.path)

    def _get_class(self, class_name):
        if not self.onto:
            return None
        for cls in self.onto.classes():
            if class_name == cls.name:
                return cls
        return None

    def ensure_classes(self):
        if not self.onto:
            return

        if hasattr(self.onto, 'User') and hasattr(self.onto, 'Music'):
            return

        with self.onto:
            class User(Thing): pass
            class Music(Thing): pass
            class Genre(Thing): pass
            class Singer(Thing): pass
            class Rating(Thing): pass

            class userName(DataProperty):
                domain = [User]
                range = [str]

            class birthYear(DataProperty):
                domain = [User]
                range = [int]

            class email(DataProperty):
                domain = [User]
                range = [str]

            class title(DataProperty):
                domain = [Music]
                range = [str]

            class hasYear(DataProperty):
                domain = [Music]
                range = [str]

            class singerName(DataProperty):
                domain = [Singer]
                range = [str]

            class genreName(DataProperty):
                domain = [Genre]
                range = [str]

            class stars(DataProperty):
                domain = [Rating]
                range = [int]

            class hasSinger(ObjectProperty):
                domain = [Music]
                range = [Singer]

            class hasGenre(ObjectProperty):
                domain = [Music]
                range = [Genre]

            class givenBy(ObjectProperty):
                domain = [Rating]
                range = [User]

            class ratesSong(ObjectProperty):
                domain = [Rating]
                range = [Music]

            class ratesGenre(ObjectProperty):
                domain = [Rating]
                range = [Genre]

            class hasPreference(ObjectProperty):
                domain = [User]
                range = [Genre]

            class RecommendedMusic(ObjectProperty):
                domain = [User]
                range = [Music]

            # Regras SWRL
            rule1a = Imp()
            rule1a.set_as_rule("""
                Rating(?r), stars(?r, 4), givenBy(?r, ?u), ratesGenre(?r, ?g)
                -> hasPreference(?u, ?g)
            """)
            rule1b = Imp()
            rule1b.set_as_rule("""
                Rating(?r), stars(?r, 5), givenBy(?r, ?u), ratesGenre(?r, ?g)
                -> hasPreference(?u, ?g)
            """)
            rule2 = Imp()
            rule2.set_as_rule("""
                User(?u), hasPreference(?u, ?g), Music(?m), hasGenre(?m, ?g)
                -> RecommendedMusic(?u, ?m)
            """)
            rule3a = Imp()
            rule3a.set_as_rule("""
                hasPreference(?u1, ?g), hasPreference(?u2, ?g), Rating(?r), givenBy(?r, ?u2),
                stars(?r, 4), ratesSong(?r, ?m)
                -> RecommendedMusic(?u1, ?m)
            """)
            rule3b = Imp()
            rule3b.set_as_rule("""
                hasPreference(?u1, ?g), hasPreference(?u2, ?g), Rating(?r), givenBy(?r, ?u2),
                stars(?r, 5), ratesSong(?r, ?m)
                -> RecommendedMusic(?u1, ?m)
            """)

    def add_user(self, name: str, year: int, mail: str):
        self.load()
        user_class = self._get_class('User')
        user = self.onto.search_one(userName=name)
        if user:
            user.birthYear = [year]
            user.email = [mail]
        else:
            with self.onto:
                user = user_class(_safe_name(name))
                user.userName = [name]
                user.birthYear = [year]
                user.email = [mail]
        self.save()
        return user

    def add_music(self, title: str, year: str, singer: str, genre: str):
        self.load()
        music_class = self._get_class('Music')
        singer_class = self._get_class('Singer')
        genre_class = self._get_class('Genre')

        singer_ind = self.onto.search_one(singerName=singer)
        if not singer_ind:
            with self.onto:
                singer_ind = singer_class(_safe_name(singer))
                singer_ind.singerName = [singer]

        genre_ind = self.onto.search_one(genreName=genre)
        if not genre_ind:
            with self.onto:
                genre_ind = genre_class(_safe_name(genre))
                genre_ind.genreName = [genre]

        music = self.onto.search_one(title=title)
        if music:
            music.hasYear = [year]
            music.hasSinger = [singer_ind]
            music.hasGenre = [genre_ind]
        else:
            with self.onto:
                music = music_class(_safe_name(title))
                music.title = [title]
                music.hasYear = [year]
                music.hasSinger = [singer_ind]
                music.hasGenre = [genre_ind]
        self.save()
        return music

    def add_rating(self, user_name: str, music_title: str, genre_name: str, star_value: int):
        self.load()
        rating_class = self._get_class('Rating')
        user = self.onto.search_one(userName=user_name)
        music = self.onto.search_one(title=music_title)
        genre = music.hasGenre[0] if music and hasattr(music, 'hasGenre') and music.hasGenre else None

        if not user or not music or not genre:
            raise Exception("User, music, or genre not found.")

        existing = None
        for r in rating_class.instances():
            if hasattr(r, 'givenBy') and hasattr(r, 'ratesSong'):
                if (user in r.givenBy) and (music in r.ratesSong):
                    existing = r
                    break
        if existing:
            existing.stars = [star_value]
        else:
            with self.onto:
                rating = rating_class(_safe_name(f"{user_name}_{music_title}_rating"))
                rating.givenBy = [user]
                rating.ratesSong = [music]
                rating.ratesGenre = [genre]
                rating.stars = [star_value]
        sync_reasoner_pellet([self.onto], infer_property_values=True, infer_data_property_values=True)
        self.save()
        return True

    def list_recommended_musics(self, user_name: str, limit: int = 10):
        from owlready2 import sync_reasoner_pellet
        self.load()
        sync_reasoner_pellet([self.onto], infer_property_values=True, infer_data_property_values=True)

        user = self.onto.search_one(userName=user_name)
        if not user or not hasattr(user, 'RecommendedMusic'):
            return []

        musics = list(user.RecommendedMusic)
        recommendations = []
        for music in musics[:limit]:
            title = music.title[0] if hasattr(music, 'title') and music.title else ""
            year = music.hasYear[0] if hasattr(music, 'hasYear') and music.hasYear else ""
            genre = music.hasGenre[0].genreName[0] if hasattr(music, 'hasGenre') and music.hasGenre and hasattr(music.hasGenre[0], 'genreName') else ""
            singer = music.hasSinger[0].singerName[0] if hasattr(music, 'hasSinger') and music.hasSinger and hasattr(music.hasSinger[0], 'singerName') else ""
            recommendations.append({
                "title": title,
                "year": year,
                "genre": genre,
                "singer": singer
            })
        return recommendations

    def get_user(self, name: str, email: Optional[str] = None):
        self.load()
        user = self.onto.search_one(userName=name)
        if user:
            if email is None or (hasattr(user, 'email') and email in user.email):
                return user
        return None

    def get_user_rating(self, user_name: str, music_title: str):
        self.load()
        rating_class = self._get_class('Rating')
        user = self.onto.search_one(userName=user_name)
        music = self.onto.search_one(title=music_title)
        if not user or not music:
            return None
        for rating in rating_class.instances():
            if hasattr(rating, 'givenBy') and hasattr(rating, 'ratesSong'):
                if (user in rating.givenBy) and (music in rating.ratesSong):
                    if hasattr(rating, 'stars') and rating.stars:
                        return rating.stars[0]
        return None

    def get_user_preferences(self, user_name: str):
        self.load()
        user = self.onto.search_one(userName=user_name)
        if not user or not hasattr(user, 'hasPreference'):
            return []
        preferences = []
        for genre in user.hasPreference:
            if hasattr(genre, 'genreName') and genre.genreName:
                preferences.append(genre.genreName[0])
        return preferences
    
    def get_user_preferences(self, user_name: str):
        self.load()
        user = self.onto.search_one(userName=user_name)
        if not user or not hasattr(user, 'hasPreference'):
            return []
        return [g.genreName[0] for g in user.hasPreference if hasattr(g, 'genreName') and g.genreName]


    def list_musics(self, limit=10, search='', order_by='title', order_dir='asc', user_name=None):
        self.load()
        music_class = self._get_class('Music')
        musics = list(music_class.instances())

        if search:
            musics = [
                m for m in musics
                if hasattr(m, 'title') and m.title and search.lower() in m.title[0].lower()
            ]

        def sort_key(music):
            if order_by == 'title':
                return music.title[0] if hasattr(music, 'title') and music.title else ""
            elif order_by == 'year':
                return music.hasYear[0] if hasattr(music, 'hasYear') and music.hasYear else ""
            elif order_by == 'singer':
                return (music.hasSinger[0].singerName[0]
                        if hasattr(music, 'hasSinger') and music.hasSinger and hasattr(music.hasSinger[0], 'singerName') and music.hasSinger[0].singerName else "")
            return ""

        musics.sort(key=sort_key, reverse=(order_dir == 'desc'))

        result = []
        for music in musics[:limit]:
            title = music.title[0] if hasattr(music, 'title') and music.title else ""
            year = music.hasYear[0] if hasattr(music, 'hasYear') and music.hasYear else ""
            genre = music.hasGenre[0].genreName[0] if hasattr(music, 'hasGenre') and music.hasGenre and hasattr(music.hasGenre[0], 'genreName') and music.hasGenre[0].genreName else ""
            singer = music.hasSinger[0].singerName[0] if hasattr(music, 'hasSinger') and music.hasSinger and hasattr(music.hasSinger[0], 'singerName') and music.hasSinger[0].singerName else ""

            already_rated = False
            if user_name:
                rating_class = self._get_class('Rating')
                user = self.onto.search_one(userName=user_name)
                if rating_class and user:
                    for rating in rating_class.instances():
                        if hasattr(rating, 'givenBy') and hasattr(rating, 'ratesSong'):
                            if (user in rating.givenBy) and (music in rating.ratesSong):
                                already_rated = True
                                break

            result.append({
                'title': title,
                'year': year,
                'genre': genre,
                'singer': singer,
                'already_rated': already_rated
            })

        return result
