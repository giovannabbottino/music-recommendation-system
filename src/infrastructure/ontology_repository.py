from owlready2 import get_ontology, Thing
from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

class OntologyRepository:
    def __init__(self, path: str):
        self.path = path
        self.onto = None
        self.ns = Namespace("http://example.org/music#")

    def ensure_classes(self):
        if self.onto is None:
            return
        onto = self.onto
        with onto:
            if not hasattr(onto, 'User') or onto.__dict__.get('User') is None:
                class User(Thing):
                    namespace = onto
            if not hasattr(onto, 'Music') or onto.__dict__.get('Music') is None:
                class Music(Thing):
                    namespace = onto
            if not hasattr(onto, 'Genre') or onto.__dict__.get('Genre') is None:
                class Genre(Thing):
                    namespace = onto
            if not hasattr(onto, 'Singer') or onto.__dict__.get('Singer') is None:
                class Singer(Thing):
                    namespace = onto
            if not hasattr(onto, 'Rating') or onto.__dict__.get('Rating') is None:
                class Rating(Thing):
                    namespace = onto

    def load(self):
        try:
            self.onto = get_ontology(self.path)
            self.onto.load()
        except Exception as e:
            print(f"Error loading ontology: {e}")
            self.onto = get_ontology(self.path)
        
        if self.onto is not None:
            self.ensure_classes()
        return self.onto

    def save(self):
        if self.onto:
            try:
                self.onto.save(file=self.path)
            except Exception as e:
                print(f"Error saving ontology: {e}")

    def add_user(self, userName: str, birthYear: str, email: str):
        if self.onto is None:
            self.onto = self.load()
        if self.onto is not None:
            self.ensure_classes()
        
        user = None
        if self.onto:
            user = self.onto.search_one(iri="*#" + userName)
        
        if user:
            user.birthYear = [birthYear]
            user.email = [email]
            self.save()
            return user
        
        if self.onto and hasattr(self.onto, 'User') and self.onto.User is not None:
            try:
                with self.onto:
                    user_class = self.onto.User
                    if user_class is None:
                        raise Exception('User class not found in ontology')
                    user = user_class(userName)
                    user.birthYear = [birthYear]
                    user.email = [email]
                self.save()
                return user
            except Exception as e:
                print(f"Error creating user: {e}")
                raise Exception(f'Failed to create user: {e}')
        
        raise Exception('Ontology not loaded or User class not available')

    def add_music(self, title: str, year: str, singer: str, genre: str):
        if self.onto is None:
            self.onto = self.load()
        if self.onto is not None:
            self.ensure_classes()
        
        music_name = title.replace(" ", "_")
        singer_name = singer.replace(" ", "_")
        genre_name = genre
        
        singer_obj = None
        if self.onto:
            singer_obj = self.onto.search_one(iri="*#" + singer_name)
        
        if not singer_obj and self.onto and hasattr(self.onto, 'Singer') and self.onto.Singer is not None:
            try:
                with self.onto:
                    singer_class = self.onto.Singer
                    if singer_class is None:
                        raise Exception('Singer class not found in ontology')
                    singer_obj = singer_class(singer_name)
                    singer_obj.displayName = [singer]
            except Exception as e:
                print(f"Error creating singer: {e}")
        
        genre_obj = None
        if self.onto:
            genre_obj = self.onto.search_one(iri="*#" + genre_name)
        
        if not genre_obj and self.onto and hasattr(self.onto, 'Genre') and self.onto.Genre is not None:
            try:
                with self.onto:
                    genre_class = self.onto.Genre
                    if genre_class is None:
                        raise Exception('Genre class not found in ontology')
                    genre_obj = genre_class(genre_name)
                    genre_obj.displayName = [genre]
            except Exception as e:
                print(f"Error creating genre: {e}")
        
        music = None
        if self.onto:
            music = self.onto.search_one(iri="*#" + music_name)
        
        if music:
            music.title = [title]
            music.year = [year]
            music.hasSinger = [singer_obj]
            music.hasGenre = [genre_obj]
            self.save()
            return music
        
        if self.onto and hasattr(self.onto, 'Music') and self.onto.Music is not None:
            try:
                with self.onto:
                    music_class = self.onto.Music
                    if music_class is None:
                        raise Exception('Music class not found in ontology')
                    music = music_class(music_name)
                    music.title = [title]
                    music.year = [year]
                    music.hasSinger = [singer_obj]
                    music.hasGenre = [genre_obj]
                self.save()
                return music
            except Exception as e:
                print(f"Error creating music: {e}")
                raise Exception(f'Failed to create music: {e}')
        
        raise Exception('Ontology not loaded or Music class not available')

    def get_user(self, userName: str, email: str):
        if self.onto is None:
            self.onto = self.load()
        if self.onto is not None:
            self.ensure_classes()
        
        user = None
        if self.onto:
            user = self.onto.search_one(iri="*#" + userName)
        
        if user and hasattr(user, 'email') and user.email and email in user.email:
            return user
        return None

    def list_musics(self, limit=10, search='', order_by='title', order_dir='asc', user_name=None):
        if self.onto is None:
            self.onto = self.load()
        if self.onto is not None:
            self.ensure_classes()
        
        musics = []
        music_instances = set()
        
        if self.onto and hasattr(self.onto, 'Music') and self.onto.Music is not None:
            try:
                instances = list(self.onto.Music.instances())
                music_instances.update(instances)
            except Exception as e:
                print(f"Error with Music.instances(): {e}")
        
        if self.onto:
            try:
                all_individuals = list(self.onto.individuals())
                for individual in all_individuals:
                    if hasattr(individual, '__class__') and hasattr(individual.__class__, '__name__'):
                        if individual.__class__.__name__ == 'Music':
                            music_instances.add(individual)
            except Exception as e:
                print(f"Error searching individuals: {e}")
        
        if self.onto:
            try:
                search_results = list(self.onto.search(iri="*"))
                for result in search_results:
                    if hasattr(result, '__class__') and hasattr(result.__class__, '__name__'):
                        if result.__class__.__name__ == 'Music':
                            music_instances.add(result)
            except Exception as e:
                print(f"Error with onto.search(): {e}")
        
        music_instances = list(music_instances)
        if order_by in ['title', 'year', 'singer']:
            def get_sort_key(music):
                if order_by == 'title':
                    return getattr(music, 'title', [''])[0] if hasattr(music, 'title') and music.title else ''
                elif order_by == 'year':
                    return getattr(music, 'year', [''])[0] if hasattr(music, 'year') and music.year else ''
                elif order_by == 'singer':
                    if hasattr(music, 'hasSinger') and music.hasSinger:
                        singer = music.hasSinger[0]
                        return getattr(singer, 'displayName', [''])[0] if hasattr(singer, 'displayName') and singer.displayName else ''
                    return ''
                return ''
            music_instances.sort(key=get_sort_key, reverse=(order_dir == 'desc'))
        
        count = 0
        for music in music_instances:
            if count >= limit:
                break
            title = getattr(music, 'title', [''])[0] if hasattr(music, 'title') and music.title else ''
            year = getattr(music, 'hasYear', [''])[0] if hasattr(music, 'hasYear') and music.hasYear else ''
            genre = ''
            if hasattr(music, 'hasGenre') and music.hasGenre:
                genre_obj = music.hasGenre[0]
                genre = getattr(genre_obj, 'name', '') if hasattr(genre_obj, 'name') else ''
            singer = ''
            if hasattr(music, 'hasSinger') and music.hasSinger:
                singer_obj = music.hasSinger[0]
                singer = getattr(singer_obj, 'singerName', [''])[0] if hasattr(singer_obj, 'singerName') and singer_obj.singerName else getattr(singer_obj, 'name', '')
            if search:
                if search.lower() not in title.lower():
                    continue
            already_rated = False
            if user_name:
                user = self.onto.search_one(iri="*#" + user_name)
                if user and hasattr(user, 'hasRated') and user.hasRated:
                    for rating in user.hasRated:
                        if hasattr(rating, 'ratedMusic') and rating.ratedMusic:
                            rated_music = rating.ratedMusic[0]
                            if rated_music == music:
                                already_rated = True
                                break
            musics.append({
                'title': title,
                'year': year,
                'genre': genre,
                'singer': singer,
                'already_rated': already_rated
            })
            count += 1
        return musics

    def add_rating(self, userName: str, music_title: str, stars: int):
        if self.onto is None:
            self.onto = self.load()
        if self.onto is not None:
            self.ensure_classes()
        
        user = None
        music = None
        if self.onto:
            user = self.onto.search_one(iri="*#" + userName)
            music = self.onto.search_one(iri="*#" + music_title.replace(" ", "_"))
            if not music:
                all_individuals = list(self.onto.individuals())
                for individual in all_individuals:
                    if hasattr(individual, 'title') and individual.title and individual.title[0] == music_title:
                        music = individual
                        break
        
        if not user:
            raise Exception(f'User {userName} not found')
        if not music:
            raise Exception(f'Music {music_title} not found')
        
        rating_name = f"{userName}_{music_title.replace(' ', '_')}_rating"
        
        existing_rating = None
        if hasattr(user, 'hasRated') and user.hasRated:
            for r in user.hasRated:
                if hasattr(r, 'ratedMusic') and r.ratedMusic and r.ratedMusic[0] == music:
                    existing_rating = r
                    break
        
        if existing_rating:
            existing_rating.hasStars = [stars]
            self.save()
            return existing_rating
        
        if self.onto and hasattr(self.onto, 'Rating') and self.onto.Rating is not None:
            try:
                with self.onto:
                    rating = self.onto.Rating(rating_name)
                    rating.hasStars = [stars]
                    rating.ratedMusic = [music]
                    
                    if not hasattr(user, 'hasRated'):
                        user.hasRated = []
                    user.hasRated.append(rating)
                
                self.save()
                return rating
            except Exception as e:
                raise Exception(f'Failed to create rating: {e}')
        
        raise Exception('Ontology not loaded or Rating class not available')

    def get_user_rating(self, userName: str, music_title: str):
        if self.onto is None:
            self.onto = self.load()
        if self.onto is not None:
            self.ensure_classes()
        
        user = None
        music = None
        if self.onto:
            user = self.onto.search_one(iri="*#" + userName)
            music = self.onto.search_one(iri="*#" + music_title.replace(" ", "_"))
            if not music:
                all_individuals = list(self.onto.individuals())
                for individual in all_individuals:
                    if hasattr(individual, 'title') and individual.title and individual.title[0] == music_title:
                        music = individual
                        break
        
        if not user or not music:
            return None
        
        if hasattr(user, 'hasRated') and user.hasRated:
            for rating in user.hasRated:
                if hasattr(rating, 'ratedMusic') and rating.ratedMusic:
                    rated_music = rating.ratedMusic[0]
                    if rated_music and music:
                        rated_music_title = None
                        if hasattr(rated_music, 'title') and rated_music.title:
                            rated_music_title = rated_music.title[0]
                        elif hasattr(rated_music, 'name'):
                            rated_music_title = rated_music.name
                        
                        music_title_compare = None
                        if hasattr(music, 'title') and music.title:
                            music_title_compare = music.title[0]
                        elif hasattr(music, 'name'):
                            music_title_compare = music.name
                        
                        if rated_music_title == music_title_compare:
                            if hasattr(rating, 'hasStars') and rating.hasStars:
                                return rating.hasStars[0]
        else:
            return None
        
        return None

    def get_user_genre_preferences(self, user_name: str):
        if self.onto is None:
            self.onto = self.load()
        if self.onto is not None:
            self.ensure_classes()
        
        user = None
        if self.onto:
            user = self.onto.search_one(iri="*#" + user_name)
        
        if not user:
            return []
        
        genre_ratings = {}
        
        if hasattr(user, 'hasRated') and user.hasRated:
            for rating in user.hasRated:
                if hasattr(rating, 'hasStars') and rating.hasStars:
                    stars_value = rating.hasStars[0]
                    if isinstance(stars_value, str):
                        try:
                            stars_value = int(stars_value)
                        except ValueError:
                            continue
                    
                    if stars_value >= 4:
                        if hasattr(rating, 'ratedMusic') and rating.ratedMusic:
                            music = rating.ratedMusic[0]
                            if hasattr(music, 'hasGenre') and music.hasGenre:
                                genre = music.hasGenre[0]
                                genre_name = ""
                                if hasattr(genre, 'displayName') and genre.displayName:
                                    genre_name = genre.displayName[0]
                                else:
                                    genre_name = genre.name
                                
                                if genre_name not in genre_ratings:
                                    genre_ratings[genre_name] = []
                                genre_ratings[genre_name].append(stars_value)
        else:
            return []
        
        preferences = []
        for genre, ratings in genre_ratings.items():
            if len(ratings) > 0: 
                preferences.append(genre)
        
        return preferences

    def add_genre_preference(self, user_name: str, genre_name: str):
        if self.onto is None:
            self.onto = self.load()
        if self.onto is not None:
            self.ensure_classes()
        
        user = None
        genre = None
        if self.onto:
            user = self.onto.search_one(iri="*#" + user_name)
            genre = self.onto.search_one(iri="*#" + genre_name)
        
        if not user:
            raise Exception(f'User {user_name} not found')
        if not genre:
            raise Exception(f'Genre {genre_name} not found')
        
        if hasattr(user, 'hasPreference'):
            if genre not in user.hasPreference:
                user.hasPreference.append(genre)
        else:
            user.hasPreference = [genre]
        
        self.save()
        return True

    def get_user_preferences(self, user_name: str):
        if self.onto is None:
            self.onto = self.load()
        if self.onto is not None:
            self.ensure_classes()
        
        user = None
        if self.onto:
            user = self.onto.search_one(iri="*#" + user_name)
        
        if not user or not hasattr(user, 'hasPreference'):
            return []
        
        preferences = []
        for genre in user.hasPreference:
            genre_name = ""
            if hasattr(genre, 'displayName') and genre.displayName:
                genre_name = genre.displayName[0]
            else:
                genre_name = genre.name
            preferences.append(genre_name)
        
        return preferences

    def list_recommended_musics(self, user_name, limit=10):
        if self.onto is None:
            self.onto = self.load()
        if self.onto is not None:
            self.ensure_classes()
        
        self.infer_genre_preferences(user_name)
        
        preferences = self.get_user_preferences(user_name)
        
        if not preferences:
            return []
        
        all_musics = []
        music_individuals = set()  
        
        try:
            all_individuals = list(self.onto.individuals())
            
            for individual in all_individuals:
                is_music = False
                
                if hasattr(individual, 'title') and individual.title:
                    is_music = True
                
                elif hasattr(individual, 'hasGenre') and individual.hasGenre:
                    is_music = True
                
                elif hasattr(individual, 'hasSinger') and individual.hasSinger:
                    is_music = True
                
                elif any(word in individual.name.lower() for word in ['song', 'music', 'track', 'album']):
                    is_music = True
                
                if is_music:
                    music_individuals.add(individual)
            
            for music in music_individuals:
                if len(all_musics) >= limit:
                    break
                
                genre_name = ""
                if hasattr(music, 'hasGenre') and music.hasGenre:
                    genre = music.hasGenre[0]
                    if hasattr(genre, 'displayName') and genre.displayName:
                        genre_name = genre.displayName[0]
                    else:
                        genre_name = genre.name
                
                if genre_name.lower() in [p.lower() for p in preferences]:
                    title = ""
                    if hasattr(music, 'title') and music.title:
                        title = music.title[0]
                    elif hasattr(music, 'name'):
                        title = music.name
                    
                    singer_name = ""
                    if hasattr(music, 'hasSinger') and music.hasSinger:
                        singer = music.hasSinger[0]
                        if hasattr(singer, 'displayName') and singer.displayName:
                            singer_name = singer.displayName[0]
                        else:
                            singer_name = singer.name
                    
                    year = ""
                    if hasattr(music, 'year') and music.year:
                        year = music.year[0]
                    elif hasattr(music, 'hasYear') and music.hasYear:
                        year = music.hasYear[0]
                    else:
                        year = "N/A" 
                    user_rating = self.get_user_rating(user_name, title)
                    
                    music_dict = {
                        'title': title,
                        'year': year,
                        'singer': singer_name,
                        'genre': genre_name,
                        'already_rated': user_rating is not None
                    }
                    all_musics.append(music_dict)
        except Exception as e:
            print(f"Error getting music instances: {e}")
        
        return all_musics

    def infer_genre_preferences(self, user_name: str):
        preferences = self.get_user_genre_preferences(user_name)
        
        user = None
        if self.onto:
            user = self.onto.search_one(iri="*#" + user_name)
        
        if not user:
            return
        
        for genre_name in preferences:
            genre = None
            if self.onto:
                genre = self.onto.search_one(iri="*#" + genre_name)
                if not genre:
                    all_individuals = list(self.onto.individuals())
                    for individual in all_individuals:
                        if hasattr(individual, '__class__') and hasattr(individual.__class__, '__name__'):
                            if individual.__class__.__name__ == 'Genre':
                                if hasattr(individual, 'displayName') and individual.displayName:
                                    if individual.displayName[0].lower() == genre_name.lower():
                                        genre = individual
                                        break
                                elif hasattr(individual, 'name') and individual.name.lower() == genre_name.lower():
                                    genre = individual
                                    break
            
            if genre:
                has_preference = False
                if hasattr(user, 'hasPreference'):
                    for pref in user.hasPreference:
                        if hasattr(pref, 'displayName') and pref.displayName and pref.displayName[0].lower() == genre_name.lower():
                            has_preference = True
                            break
                        elif hasattr(pref, 'name') and pref.name.lower() == genre_name.lower():
                            has_preference = True
                            break
                
                if not has_preference:
                    if hasattr(user, 'hasPreference'):
                        user.hasPreference.append(genre)
                    else:
                        user.hasPreference = [genre]
            else:
                print(f"Could not find genre '{genre_name}' in ontology")
        
        self.save()
