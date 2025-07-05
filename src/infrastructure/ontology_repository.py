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
        
        print(f"Debug: list_musics called with limit={limit}, search='{search}', order_by='{order_by}'")
        print(f"Debug: onto is {self.onto}")
        
        musics = []
        music_instances = set()  # Use set to avoid duplicates
        
        if self.onto and hasattr(self.onto, 'Music') and self.onto.Music is not None:
            try:
                instances = list(self.onto.Music.instances())
                print(f"Debug: Found {len(instances)} music instances via Music.instances()")
                music_instances.update(instances)
            except Exception as e:
                print(f"Error with Music.instances(): {e}")
        
        if self.onto:
            try:
                all_individuals = list(self.onto.individuals())
                print(f"Debug: Found {len(all_individuals)} total individuals")
                for individual in all_individuals:
                    if hasattr(individual, '__class__') and hasattr(individual.__class__, '__name__'):
                        if individual.__class__.__name__ == 'Music':
                            music_instances.add(individual)
            except Exception as e:
                print(f"Error searching individuals: {e}")
        
        if self.onto:
            try:
                music_search = self.onto.search(iri="*Music*")
                print(f"Debug: Found {len(music_search)} individuals with 'Music' in IRI")
                for item in music_search:
                    # Check if this item has music-like properties
                    if hasattr(item, 'title') or hasattr(item, 'hasYear') or hasattr(item, 'year'):
                        music_instances.add(item)
                        print(f"Debug: Found potential music: {item}")
                    # Also check if the item's class name is 'Music'
                    elif hasattr(item, '__class__') and hasattr(item.__class__, '__name__') and item.__class__.__name__ == 'Music':
                        music_instances.add(item)
                        print(f"Debug: Found music by class name: {item}")
                    # If the item has a title property, consider it music
                    elif hasattr(item, 'title') and item.title:
                        music_instances.add(item)
                        print(f"Debug: Found music by title property: {item}")
            except Exception as e:
                print(f"Error searching by IRI: {e}")
        
        # Also try to find music by searching for individuals with title property
        if self.onto:
            try:
                all_individuals = list(self.onto.individuals())
                for individual in all_individuals:
                    if hasattr(individual, 'title') and individual.title and len(individual.title) > 0:
                        music_instances.add(individual)
            except Exception as e:
                print(f"Error searching by title: {e}")
        
        print(f"Debug: Total music instances found: {len(music_instances)}")
        
        # Process the found music instances
        for music in music_instances:
            
            title = None
            if hasattr(music, 'title') and music.title:
                title = music.title[0]
            elif hasattr(music, 'hasTitle') and music.hasTitle:
                title = music.hasTitle[0]
            
            if title:
                singer_name = ""
                
                if hasattr(music, 'hasSinger') and music.hasSinger:
                    singer = music.hasSinger[0]
                    if hasattr(singer, 'singerName') and singer.singerName:
                        singer_name = singer.singerName[0]
                    elif hasattr(singer, 'displayName') and singer.displayName:
                        singer_name = singer.displayName[0]
                    else:
                        singer_name = singer.name
                
                genre_name = ""
                if hasattr(music, 'hasGenre') and music.hasGenre:
                    genre = music.hasGenre[0]
                    if hasattr(genre, 'displayName') and genre.displayName:
                        genre_name = genre.displayName[0]
                    else:
                        genre_name = genre.name
                
                year = ""
                if hasattr(music, 'hasYear') and music.hasYear:
                    year = music.hasYear[0]
                elif hasattr(music, 'year') and music.year:
                    year = music.year[0]
                
                music_dict = {
                    'title': title,
                    'year': year,
                    'singer': singer_name,
                    'genre': genre_name
                }
                musics.append(music_dict)
        
        if search:
            search_lower = search.lower()
            musics = [m for m in musics if search_lower in m['title'].lower()]
        
        reverse = order_dir == 'desc'
        musics = sorted(musics, key=lambda m: str(m.get(order_by, '')).lower(), reverse=reverse)
        result = musics[:limit]
        return result

    def add_rating(self, userName: str, music_title: str, stars: int):
        if self.onto is None:
            self.onto = self.load()
        if self.onto is not None:
            self.ensure_classes()
        
        user = None
        music = None
        if self.onto:
            user = self.onto.search_one(iri="*#" + userName)
            # Try different ways to find the music
            music = self.onto.search_one(iri="*#" + music_title.replace(" ", "_"))
            if not music:
                # Try searching by title property
                all_individuals = list(self.onto.individuals())
                for individual in all_individuals:
                    if hasattr(individual, 'title') and individual.title and individual.title[0] == music_title:
                        music = individual
                        break
        
        if not user:
            raise Exception(f'Usuário {userName} não encontrado')
        if not music:
            raise Exception(f'Música {music_title} não encontrada')
        
        # Create a unique rating name
        rating_name = f"{userName}_{music_title.replace(' ', '_')}_rating"
        
        # Check if rating already exists
        existing_rating = None
        if hasattr(user, 'hasRated') and user.hasRated:
            for r in user.hasRated:
                if hasattr(r, 'ratedMusic') and r.ratedMusic and r.ratedMusic[0] == music:
                    existing_rating = r
                    break
        
        if existing_rating:
            # Update existing rating
            existing_rating.hasStars = [stars]
            self.save()
            return existing_rating
        
        # Create new rating
        if self.onto and hasattr(self.onto, 'Rating') and self.onto.Rating is not None:
            try:
                with self.onto:
                    rating = self.onto.Rating(rating_name)
                    rating.hasStars = [stars]
                    rating.ratedMusic = [music]
                    
                    # Add rating to user
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
            # Try different ways to find the music
            music = self.onto.search_one(iri="*#" + music_title.replace(" ", "_"))
            if not music:
                # Try searching by title property
                all_individuals = list(self.onto.individuals())
                for individual in all_individuals:
                    if hasattr(individual, 'title') and individual.title and individual.title[0] == music_title:
                        music = individual
                        break
        
        print(f"Debug: get_user_rating - userName: {userName}, music_title: {music_title}")
        print(f"Debug: get_user_rating - user found: {user is not None}")
        print(f"Debug: get_user_rating - music found: {music is not None}")
        
        if not user or not music:
            print(f"Debug: get_user_rating - returning None (user or music not found)")
            return None
        
        if hasattr(user, 'hasRated') and user.hasRated:
            print(f"Debug: get_user_rating - user has {len(user.hasRated)} ratings")
            for rating in user.hasRated:
                if hasattr(rating, 'ratedMusic') and rating.ratedMusic:
                    rated_music = rating.ratedMusic[0]
                    print(f"Debug: get_user_rating - checking rating for music: {rated_music.name if rated_music else 'None'}")
                    # Compare by name or title
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
                                print(f"Debug: get_user_rating - found rating: {rating.hasStars[0]}")
                                return rating.hasStars[0]
        else:
            print(f"Debug: get_user_rating - user has no ratings")
        
        print(f"Debug: get_user_rating - returning None (no rating found)")
        return None

    def list_recommended_musics(self, user_name):
        if self.onto is None:
            self.onto = self.load()
        if self.onto is not None:
            self.ensure_classes()
        
        user = None
        if self.onto:
            user = self.onto.search_one(iri="*#" + user_name)
        
        musics = []
        if user and hasattr(user, 'recommendMusic'):
            for m in getattr(user, 'recommendMusic', []):
                if hasattr(m, 'title') and m.title:
                    singer_name = ""
                    if hasattr(m, 'hasSinger') and m.hasSinger:
                        singer = m.hasSinger[0]
                        if hasattr(singer, 'displayName') and singer.displayName:
                            singer_name = singer.displayName[0]
                        else:
                            singer_name = singer.name
                    
                    genre_name = ""
                    if hasattr(m, 'hasGenre') and m.hasGenre:
                        genre = m.hasGenre[0]
                        if hasattr(genre, 'displayName') and genre.displayName:
                            genre_name = genre.displayName[0]
                        else:
                            genre_name = genre.name
                    
                    music_dict = {
                        'title': m.title[0] if m.title else '',
                        'year': m.year[0] if hasattr(m, 'year') and m.year else '',
                        'singer': singer_name,
                        'genre': genre_name
                    }
                    musics.append(music_dict)
        return musics
