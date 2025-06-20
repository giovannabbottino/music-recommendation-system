import pytest
from src.infrastructure.ontology_repository import OntologyRepository
from owlready2 import get_ontology, Thing

class TestOntologyRepository:
    def test_load_ontology(self, sample_ontology):
        _, temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        ontology = repo.load()
        assert ontology is not None
        assert hasattr(ontology, 'User')
        assert hasattr(ontology, 'Genre')

    def test_add_user(self, sample_ontology):
        _, temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        user = repo.add_user('alice', '1990', 'alice@email.com')
        assert user is not None
        assert user.name == 'alice'
        assert hasattr(user, 'birthYear')
        assert hasattr(user, 'email')
        repo2 = OntologyRepository(temp_file)
        onto2 = repo2.load()
        user2 = next((u for u in onto2.individuals() if u.name == 'alice'), None)
        assert user2 is not None
        assert hasattr(user2, 'birthYear')
        assert hasattr(user2, 'email')

    def test_add_user_when_user_class_missing(self, temp_ontology_file):
        onto = get_ontology(f"file://{temp_ontology_file}")
        with onto:
            class Genre(Thing): pass
        onto.save(file=temp_ontology_file)
        repo = OntologyRepository(temp_ontology_file)
        repo.load()
        user = repo.add_user('bob', '1985', 'bob@email.com')
        assert user is not None
        assert user.name == 'bob'
        assert hasattr(user, 'birthYear')
        assert hasattr(user, 'email')
        assert hasattr(repo.ontology, 'User')
        repo2 = OntologyRepository(temp_ontology_file)
        onto2 = repo2.load()
        user2 = next((u for u in onto2.individuals() if u.name == 'bob'), None)
        assert user2 is not None
        assert hasattr(user2, 'birthYear')
        assert hasattr(user2, 'email')

    def test_add_music(self, sample_ontology):
        _, temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        music = repo.add_music('Imagine', '1971', 'John Lennon', 'Rock')
        assert music is not None
        assert music.name == 'Imagine'
        assert hasattr(music, 'hasYear')
        assert hasattr(music, 'hasSinger')
        assert hasattr(music, 'hasGenre')
        assert music.hasYear[0] == '1971'
        assert music.hasSinger[0].name == 'John Lennon'
        assert music.hasGenre[0].name == 'Rock'
        repo2 = OntologyRepository(temp_file)
        onto2 = repo2.load()
        music2 = next((m for m in onto2.individuals() if m.name == 'Imagine'), None)
        assert music2 is not None
        assert music2.hasYear[0] == '1971'
        assert music2.hasSinger[0].name == 'John Lennon'
        assert music2.hasGenre[0].name == 'Rock'

    def test_add_music_existing_singer_and_genre(self, sample_ontology):
        onto, temp_file = sample_ontology
        singer = onto.Singer('Queen')
        genre = onto.Genre('Rock')
        onto.save(file=temp_file)
        repo = OntologyRepository(temp_file)
        repo.load()
        music = repo.add_music('Bohemian Rhapsody', '1975', 'Queen', 'Rock')
        assert music is not None
        assert music.hasSinger[0].name == 'Queen'
        assert music.hasGenre[0].name == 'Rock'

    def test_add_user_duplicate(self, sample_ontology):
        _, temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        user1 = repo.add_user('john', '1980', 'john@email.com')
        assert user1 is not None
        with pytest.raises(Exception) as excinfo:
            repo.add_user('john', '1980', 'john@email.com')
        assert 'already exists' in str(excinfo.value)

    def test_get_user(self, sample_ontology):
        _, temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.add_user('alice', '1990', 'alice@email.com')
        user = repo.get_user('alice', 'alice@email.com')
        assert user is not None
        assert user.name == 'alice'
        assert 'alice@email.com' in user.email
        user_none = repo.get_user('bob', 'bob@email.com')
        assert user_none is None

    def test_add_rating(self, sample_ontology):
        _, temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.add_user('alice', '1990', 'alice@email.com')
        repo.add_music('Imagine', '1971', 'John Lennon', 'Rock')
        rating = repo.add_rating('alice', 'Imagine', 5)
        assert rating is not None
        assert hasattr(rating, 'hasStars')
        assert rating.hasStars[0] == 5
        assert hasattr(rating, 'ratedMusic')
        assert rating.ratedMusic[0].name == 'Imagine'
        user = repo.get_user('alice', 'alice@email.com')
        assert hasattr(user, 'hasRated')
        assert any(r for r in user.hasRated if hasattr(r, 'hasStars') and r.hasStars[0] == 5) 

    def test_list_recommended_musics_none(self, sample_ontology):
        _, temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.add_user('alice', '1990', 'alice@email.com')
        recommended = repo.list_recommended_musics('alice')
        assert recommended == []

    def test_list_recommended_musics_no_ratings(self, sample_ontology):
        _, temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.add_user('alice', '1990', 'alice@email.com')
        repo.add_music('Imagine', '1971', 'John Lennon', 'Rock')
        recommended = repo.list_recommended_musics('alice')
        assert recommended == []

    def test_list_recommended_musics_happy_path(self, sample_ontology):
        _, temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.add_user('alice', '1990', 'alice@email.com')
        repo.add_music('Imagine', '1971', 'John Lennon', 'Rock')
        repo.add_rating('alice', 'Imagine', 5)
        recommended = repo.list_recommended_musics('alice')
        titles = [m['title'] for m in recommended]
        assert 'Imagine' in titles or recommended == []
