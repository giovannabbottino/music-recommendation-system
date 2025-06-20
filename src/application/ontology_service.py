from infrastructure.ontology_repository import OntologyRepository

class OntologyService:
    def __init__(self, ontology_path: str):
        self.repo = OntologyRepository(ontology_path)
        self.ontology = None

    def load_ontology(self):
        self.ontology = self.repo.load()
        print(f"Ontologia carregada com {len(list(self.ontology.classes()))} classes.")
        return self.ontology 

    def register_user(self, userName: str, birthYear: str, email: str):
        return self.repo.add_user(userName, birthYear, email)

    def add_music(self, title: str, year: str, singer: str, genre: str):
        return self.repo.add_music(title, year, singer, genre)

    def get_user(self, userName: str, email: str):
        return self.repo.get_user(userName, email)

    def list_musics(self):
        return self.repo.list_musics()

    def add_rating(self, userName: str, music_title: str, stars: int):
        return self.repo.add_rating(userName, music_title, stars)
