from infrastructure.ontology_repository import OntologyRepository

class OntologyService:
    def __init__(self, ontology_path: str):
        self.repo = OntologyRepository(ontology_path)
        self.ontology = None

    def load_ontology(self):
        self.ontology = self.repo.load()
        return self.ontology

    def register_user(self, userName: str, birthYear: str, email: str):
        return self.repo.add_user(userName, int(birthYear), email)

    def add_music(self, title: str, year: str, singer: str, genre: str):
        return self.repo.add_music(title, year, singer, genre)

    def get_user(self, userName: str, email: str):
        return self.repo.get_user(userName, email)

    def list_musics(self, limit=10, search='', order_by='title', order_dir='asc', user_name=None):
        return self.repo.list_musics(limit=limit, search=search, order_by=order_by, order_dir=order_dir, user_name=user_name)

    def add_rating(self, userName: str, music_title: str, genre_name: str, stars: int):
        return self.repo.add_rating(userName, music_title, genre_name, stars)

    def get_user_rating(self, userName: str, music_title: str):
        return self.repo.get_user_rating(userName, music_title)

    def list_recommended_musics(self, user_name, limit=10):
        return self.repo.list_recommended_musics(user_name, limit)


