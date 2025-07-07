from owlready2 import get_ontology, Thing, DataProperty, ObjectProperty

class OntologyRepository:
    def __init__(self, path: str):
        self.path = path
        self.onto = None

    def load(self):
        try:
            self.onto = get_ontology(self.path).load()
        except:
            self.onto = get_ontology(self.path)
        self.ensure_classes()
        return self.onto

    def save(self):
        if self.onto:
            self.onto.save(file=self.path)

    def ensure_classes(self):
        if not self.onto:
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
        user = self.onto.search_one(userName=name)
        if user:
            user.birthYear = [year]
            user.email = [mail]
        else:
            with self.onto:
                user = self.onto.User(name.replace(" ", "_"))
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
        singer_ind = self.onto.search_one(singerName=singer)
        if not singer_ind:
            with self.onto:
                singer_ind = self.onto.Singer(singer.replace(" ", "_"))
                singer_ind.singerName = [singer]
        genre_ind = self.onto.search_one(genreName=genre)
        if not genre_ind:
            with self.onto:
                genre_ind = self.onto.Genre(genre.replace(" ", "_"))
                genre_ind.genreName = [genre]
        music = self.onto.search_one(title=title)
        if music:
            music.hasYear = [year]
            music.hasSinger = [singer_ind]
            music.hasGenre = [genre_ind]
        else:
            with self.onto:
                music = self.onto.Music(title.replace(" ", "_"))
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
        user = self.onto.search_one(userName=user_name)
        music = self.onto.search_one(title=music_title)
        genre = self.onto.search_one(genreName=genre_name)
        if not user or not music or not genre:
            raise Exception("User, music, or genre not found.")
        existing = None
        for r in self.onto.Rating.instances():
            if (user in r.givenBy) and (music in r.ratesSong):
                existing = r
                break
        if existing:
            existing.stars = [star_value]
        else:
            with self.onto:
                rating = self.onto.Rating(f"{user_name}_{music_title}_rating".replace(" ", "_"))
                rating.givenBy = [user]
                rating.ratesSong = [music]
                rating.ratesGenre = [genre]
                rating.stars = [star_value]
        self.save()
        return True

    def get_user(self, name: str, email: str = None):
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
        user = self.onto.search_one(userName=user_name)
        music = self.onto.search_one(title=music_title)
        if not user or not music:
            return None
        for rating in self.onto.Rating.instances():
            if (user in rating.givenBy) and (music in rating.ratesSong):
                if hasattr(rating, 'stars') and rating.stars:
                    return rating.stars[0]
        return None

    def get_user_genre_preferences(self, user_name: str):
        if not self.onto:
            self.load()
        if not self.onto:
            raise Exception("Ontology not loaded")
        user = self.onto.search_one(userName=user_name)
        if not user:
            return []
        
        preferences = set()
        for rating in self.onto.Rating.instances():
            if (user in rating.givenBy) and hasattr(rating, 'stars') and rating.stars and rating.stars[0] >= 4:
                if hasattr(rating, 'ratesGenre') and rating.ratesGenre:
                    genre = rating.ratesGenre[0]
                    if hasattr(genre, 'genreName') and genre.genreName:
                        preferences.add(genre.genreName[0])
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
        preferences = self.get_user_genre_preferences(user_name)
        if not preferences:
            return []

        recommendations = []
        for music in self.onto.Music.instances():
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
        return recommendations

    def list_musics(self, limit=10, search='', order_by='title', order_dir='asc', user_name=None):
        if not self.onto:
            self.load()
        if not self.onto:
            raise Exception("Ontology not loaded")
        self.ensure_classes()

        musics = list(self.onto.Music.instances())

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
                user = self.onto.search_one(userName=user_name)
                if user:
                    for rating in self.onto.Rating.instances():
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
