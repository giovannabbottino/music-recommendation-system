from owlready2 import get_ontology, Thing, DataProperty, ObjectProperty
from typing import Optional

class OntologyRepository:
    def __init__(self, path: str):
        self.path = path
        self.onto = None

    def load(self):
        try:
            self.onto = get_ontology(self.path).load()
            print("Loaded!")
        except Exception as e:
            print("Error loading:", e)
            self.onto = get_ontology(self.path)
        return self.onto

    def save(self):
        if self.onto:
            self.onto.save(file=self.path)
    
    def _get_class(self, class_name):
        """Encontrar uma classe pelo nome"""
        if not self.onto:
            return None
        try:
            for cls in self.onto.classes():
                if class_name in cls.name:
                    return cls
        except Exception:
            pass
        return None

    def ensure_classes(self):
        if not self.onto:
            return
        
        if hasattr(self.onto, 'User') and hasattr(self.onto, 'Music') and hasattr(self.onto, 'Genre') and hasattr(self.onto, 'Singer') and hasattr(self.onto, 'Rating'):
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

    def add_user(self, name: str, year: int, mail: str):
        if not self.onto:
            self.load()
        if not self.onto:
            raise Exception("Ontology not loaded")
        
        user_class = self._get_class('User')
        if not user_class:
            # Try to ensure classes exist
            self.ensure_classes()
            user_class = self._get_class('User')
            if not user_class:
                raise Exception("User class not found in ontology")
            
        user = self.onto.search_one(userName=name)
        if user:
            user.birthYear = [year]
            user.email = [mail]
        else:
            with self.onto:
                user = user_class(name.replace(" ", "_"))
                user.userName = [name]
                user.birthYear = [year]
                user.email = [mail]
        self.save()
        return user

    def add_music(self, title: str, year: str, singer: str, genre: str):
        if not self.onto:
            self.load()
        if not self.onto:
            raise Exception("Ontology not loaded")
            
        singer_class = self._get_class('Singer')
        genre_class = self._get_class('Genre')
        music_class = self._get_class('Music')
        
        if not singer_class or not genre_class or not music_class:
            # Try to ensure classes exist
            self.ensure_classes()
            singer_class = self._get_class('Singer')
            genre_class = self._get_class('Genre')
            music_class = self._get_class('Music')
            if not singer_class or not genre_class or not music_class:
                raise Exception("Required classes not found in ontology")
            
        singer_ind = self.onto.search_one(singerName=singer)
        if not singer_ind:
            with self.onto:
                singer_ind = singer_class(singer.replace(" ", "_"))
                singer_ind.singerName = [singer]
        genre_ind = self.onto.search_one(genreName=genre)
        if not genre_ind:
            with self.onto:
                genre_ind = genre_class(genre.replace(" ", "_"))
                genre_ind.genreName = [genre]
        music = self.onto.search_one(title=title)
        if music:
            music.hasYear = [year]
            music.hasSinger = [singer_ind]
            music.hasGenre = [genre_ind]
        else:
            with self.onto:
                music = music_class(title.replace(" ", "_"))
                music.title = [title]
                music.hasYear = [year]
                music.hasSinger = [singer_ind]
                music.hasGenre = [genre_ind]
        self.save()
        return music

    def add_rating(self, user_name: str, music_title: str, genre_name: str, star_value: int):
        if not self.onto:
            self.load()
        if not self.onto:
            raise Exception("Ontology not loaded")
            
        rating_class = self._get_class('Rating')
        if not rating_class:
            # Try to ensure classes exist
            self.ensure_classes()
            rating_class = self._get_class('Rating')
            if not rating_class:
                raise Exception("Rating class not found in ontology")
            
        user = self.onto.search_one(userName=user_name)
        music = self.onto.search_one(title=music_title)
        genre = self.onto.search_one(genreName=genre_name)
        if not user or not music or not genre:
            raise Exception("User, music, or genre not found.")
        existing = None
        try:
            for r in rating_class.instances():
                if hasattr(r, 'givenBy') and hasattr(r, 'ratesSong'):
                    if (user in r.givenBy) and (music in r.ratesSong):
                        existing = r
                        break
        except AttributeError:
            # Properties don't exist, create new rating
            pass
        if existing:
            existing.stars = [star_value]
        else:
            with self.onto:
                rating = rating_class(f"{user_name}_{music_title}_rating".replace(" ", "_"))
                rating.givenBy = [user]
                rating.ratesSong = [music]
                rating.ratesGenre = [genre]
                rating.stars = [star_value]
        self.save()
        return True

    def get_user(self, name: str, email: Optional[str] = None):
        if not self.onto:
            self.load()
        if not self.onto:
            raise Exception("Ontology not loaded")
        user = self.onto.search_one(userName=name)
        if user:
            if email is None or (hasattr(user, 'email') and email in user.email):
                return user
        return None

    def get_user_rating(self, user_name: str, music_title: str):
        if not self.onto:
            self.load()
        if not self.onto:
            raise Exception("Ontology not loaded")
            
        rating_class = self._get_class('Rating')
        if not rating_class:
            return None
            
        user = self.onto.search_one(userName=user_name)
        music = self.onto.search_one(title=music_title)
        if not user or not music:
            return None
        try:
            for rating in rating_class.instances():
                if hasattr(rating, 'givenBy') and hasattr(rating, 'ratesSong'):
                    if (user in rating.givenBy) and (music in rating.ratesSong):
                        if hasattr(rating, 'stars') and rating.stars:
                            return rating.stars[0]
        except AttributeError:
            pass
        return None

    def get_user_genre_preferences(self, user_name: str):
        if not self.onto:
            self.load()
        if not self.onto:
            raise Exception("Ontology not loaded")
            
        rating_class = self._get_class('Rating')
        if not rating_class:
            return []
            
        user = self.onto.search_one(userName=user_name)
        if not user:
            return []
        
        preferences = set()
        try:
            for rating in rating_class.instances():
                if hasattr(rating, 'givenBy') and hasattr(rating, 'stars') and hasattr(rating, 'ratesGenre'):
                    if (user in rating.givenBy) and rating.stars and rating.stars[0] >= 4:
                        if rating.ratesGenre:
                            genre = rating.ratesGenre[0]
                            if hasattr(genre, 'genreName') and genre.genreName:
                                preferences.add(genre.genreName[0])
        except AttributeError:
            pass
        return list(preferences)

    def add_genre_preference(self, user_name: str, genre_name: str):
        if not self.onto:
            self.load()
        if not self.onto:
            raise Exception("Ontology not loaded")
        user = self.onto.search_one(userName=user_name)
        genre = self.onto.search_one(genreName=genre_name)
        if not user or not genre:
            raise Exception("User or genre not found.")
        if not hasattr(user, 'hasPreference') or genre not in user.hasPreference:
            if not hasattr(user, 'hasPreference'):
                user.hasPreference = []
            user.hasPreference.append(genre)
        self.save()
        return True

    def get_user_preferences(self, user_name: str):
        if not self.onto:
            self.load()
        if not self.onto:
            raise Exception("Ontology not loaded")
        user = self.onto.search_one(userName=user_name)
        if not user or not hasattr(user, 'hasPreference'):
            return []
        preferences = []
        for genre in user.hasPreference:
            if hasattr(genre, 'genreName') and genre.genreName:
                preferences.append(genre.genreName[0])
        return preferences

    def list_recommended_musics(self, user_name: str, limit: int = 10):
        if not self.onto:
            self.load()
        if not self.onto:
            raise Exception("Ontology not loaded")
            
        music_class = self._get_class('Music')
        if not music_class:
            return []
            
        preferences = self.get_user_genre_preferences(user_name)
        if not preferences:
            return []

        recommendations = []
        try:
            for music in music_class.instances():
                if hasattr(music, 'hasGenre') and music.hasGenre:
                    genre = music.hasGenre[0]
                    genre_name = getattr(genre, 'genreName', None)
                    if genre_name and genre_name[0] in preferences:
                        title = getattr(music, 'title', None)
                        year = getattr(music, 'hasYear', None)
                        singer_name = ""
                        if hasattr(music, 'hasSinger') and music.hasSinger:
                            singer = music.hasSinger[0]
                            singer_name = getattr(singer, 'singerName', "")
                            if singer_name:
                                singer_name = singer_name[0]
                        already_rated = self.get_user_rating(user_name, title[0]) is not None if title else False
                        recommendations.append({
                            "title": title[0] if title else None,
                            "year": year[0] if year else None,
                            "singer": singer_name,
                            "genre": genre_name[0] if genre_name else None,
                            "already_rated": already_rated
                        })
                        if len(recommendations) >= limit:
                            break
        except AttributeError:
            pass
        return recommendations

    def list_musics(self, limit=10, search='', order_by='title', order_dir='asc', user_name=None):
        if not self.onto:
            self.load()
        if not self.onto:
            raise Exception("Ontology not loaded")

        # Encontrar a classe Music correta
        music_class = self._get_class('Music')
        if not music_class:
            raise Exception("Music class not found in ontology")
            
        musics = list(music_class.instances())

        if search:
            musics = [
                m for m in musics
                if hasattr(m, 'title') and m.title and search.lower() in m.title[0].lower()
            ]

        def sort_key(music):
            if order_by == 'title' and hasattr(music, 'title') and music.title:
                return music.title[0]
            elif order_by == 'year' and hasattr(music, 'hasYear') and music.hasYear:
                return music.hasYear[0]
            elif order_by == 'singer' and hasattr(music, 'hasSinger') and music.hasSinger:
                singer = music.hasSinger[0]
                return getattr(singer, 'singerName', [""])[0] if hasattr(singer, 'singerName') and singer.singerName else ""
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
                if rating_class:
                    user = self.onto.search_one(userName=user_name)
                    if user:
                        try:
                            for rating in rating_class.instances():
                                if hasattr(rating, 'givenBy') and hasattr(rating, 'ratesSong'):
                                    if (user in rating.givenBy) and (music in rating.ratesSong):
                                        already_rated = True
                                        break
                        except AttributeError:
                            pass

            result.append({
                'title': title,
                'year': year,
                'genre': genre,
                'singer': singer,
                'already_rated': already_rated
            })

        return result
