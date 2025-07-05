import pytest
import os
from src.infrastructure.ontology_repository import OntologyRepository
from owlready2 import get_ontology, Thing

class TestOntologyRepository:
    def test_load_ontology(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        ontology = repo.load()
        assert ontology is not None
        assert hasattr(ontology, 'User')
        assert hasattr(ontology, 'Genre')

    def test_add_user(self, sample_ontology):
        temp_file = sample_ontology
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
        assert hasattr(repo.onto, 'User')
        repo2 = OntologyRepository(temp_ontology_file)
        onto2 = repo2.load()
        user2 = next((u for u in onto2.individuals() if u.name == 'bob'), None)
        assert user2 is not None
        assert hasattr(user2, 'birthYear')
        assert hasattr(user2, 'email')

    def test_add_music(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        music = repo.add_music('Imagine', '1971', 'John Lennon', 'Rock')
        assert music is not None
        assert music.name == 'Imagine'
        assert hasattr(music, 'title')
        assert hasattr(music, 'hasSinger')
        assert hasattr(music, 'hasGenre')
        assert music.title[0] == 'Imagine'
        # Check displayName property for singer
        if hasattr(music.hasSinger[0], 'displayName') and music.hasSinger[0].displayName:
            assert music.hasSinger[0].displayName[0] == 'John Lennon'
        else:
            assert music.hasSinger[0].name == 'John_Lennon'
        # Check displayName property for genre
        if hasattr(music.hasGenre[0], 'displayName') and music.hasGenre[0].displayName:
            assert music.hasGenre[0].displayName[0] == 'Rock'
        else:
            assert music.hasGenre[0].name == 'Rock'
        repo2 = OntologyRepository(temp_file)
        onto2 = repo2.load()
        music2 = next((m for m in onto2.individuals() if m.name == 'Imagine'), None)
        assert music2 is not None
        assert music2.title[0] == 'Imagine'

    def test_add_music_existing_singer_and_genre(self, sample_ontology):
        temp_file = sample_ontology
        # Create a temporary ontology to add existing singer and genre
        import tempfile
        import uuid
        with tempfile.NamedTemporaryFile(suffix='.owl', delete=False) as tmp:
            temp_path = tmp.name
        try:
            unique_iri = f"http://example.org/music_{uuid.uuid4()}#"
            onto = get_ontology(unique_iri)
            with onto:
                class User(Thing): pass
                class Music(Thing): pass
                class Genre(Thing): pass
                class Singer(Thing): pass
                class Rating(Thing): pass
            singer = onto.Singer('Queen')
            singer.displayName = ['Queen']
            genre = onto.Genre('Rock')
            genre.displayName = ['Rock']
            onto.save(file=temp_path)
            
            repo = OntologyRepository(temp_path)
            repo.load()
            music = repo.add_music('Bohemian Rhapsody', '1975', 'Queen', 'Rock')
            assert music is not None
            # Check displayName property for singer
            if hasattr(music.hasSinger[0], 'displayName') and music.hasSinger[0].displayName:
                assert music.hasSinger[0].displayName[0] == 'Queen'
            else:
                assert music.hasSinger[0].name == 'Queen'
            # Check displayName property for genre
            if hasattr(music.hasGenre[0], 'displayName') and music.hasGenre[0].displayName:
                assert music.hasGenre[0].displayName[0] == 'Rock'
            else:
                assert music.hasGenre[0].name == 'Rock'
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_add_user_duplicate(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        user1 = repo.add_user('john', '1980', 'john@email.com')
        assert user1 is not None
        # Agora o comportamento é retornar o usuário existente em vez de lançar exceção
        user2 = repo.add_user('john', '1980', 'john@email.com')
        assert user2 is not None
        assert user2 == user1  # Deve ser o mesmo objeto

    def test_get_user(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.add_user('alice', '1990', 'alice@email.com')
        user = repo.get_user('alice', 'alice@email.com')
        assert user is not None
        assert user.name == 'alice'
        assert 'alice@email.com' in user.email
        user_none = repo.get_user('non-existent', 'bob@email.com')
        assert user_none is None

    def test_add_rating(self, sample_ontology):
        temp_file = sample_ontology
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
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.add_user('alice', '1990', 'alice@email.com')
        recommended = repo.list_recommended_musics('alice')
        assert recommended == []

    def test_list_recommended_musics_no_ratings(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.add_user('alice', '1990', 'alice@email.com')
        repo.add_music('Imagine', '1971', 'John Lennon', 'Rock')
        recommended = repo.list_recommended_musics('alice')
        assert recommended == []

    def test_list_musics_empty(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        musics = repo.list_musics()
        assert musics == []

    def test_list_musics_with_data(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Add some test music
        music1 = repo.add_music('Test Song 1', '2020', 'Test Artist 1', 'Rock')
        music2 = repo.add_music('Test Song 2', '2021', 'Test Artist 2', 'Pop')
        
        musics = repo.list_musics()
        assert len(musics) == 2
        assert any(m['title'] == 'Test Song 1' for m in musics)
        assert any(m['title'] == 'Test Song 2' for m in musics)

    def test_list_musics_with_limit(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Add multiple test music
        for i in range(5):
            repo.add_music(f'Test Song {i}', f'202{i}', f'Test Artist {i}', 'Rock')
        
        musics = repo.list_musics(limit=3)
        assert len(musics) == 3

    def test_list_musics_with_search(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Add test music
        repo.add_music('Rock Song', '2020', 'Rock Artist', 'Rock')
        repo.add_music('Pop Song', '2021', 'Pop Artist', 'Pop')
        repo.add_music('Jazz Song', '2022', 'Jazz Artist', 'Jazz')
        
        # Search for rock songs
        musics = repo.list_musics(search='rock')
        assert len(musics) == 1
        assert musics[0]['title'] == 'Rock Song'

    def test_list_musics_with_order_by_title(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Add test music in reverse order
        repo.add_music('Zebra Song', '2020', 'Artist Z', 'Rock')
        repo.add_music('Alpha Song', '2021', 'Artist A', 'Pop')
        
        musics = repo.list_musics(order_by='title', order_dir='asc')
        assert len(musics) == 2
        assert musics[0]['title'] == 'Alpha Song'
        assert musics[1]['title'] == 'Zebra Song'

    def test_list_musics_with_order_by_year(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Add test music
        repo.add_music('Old Song', '2020', 'Old Artist', 'Rock')
        repo.add_music('New Song', '2023', 'New Artist', 'Pop')
        
        musics = repo.list_musics(order_by='year', order_dir='desc')
        assert len(musics) == 2
        assert musics[0]['year'] == '2023'
        assert musics[1]['year'] == '2020'

    def test_list_musics_with_order_by_singer(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Add test music
        repo.add_music('Song 1', '2020', 'Zebra Artist', 'Rock')
        repo.add_music('Song 2', '2021', 'Alpha Artist', 'Pop')
        
        musics = repo.list_musics(order_by='singer', order_dir='asc')
        assert len(musics) == 2
        assert musics[0]['singer'] == 'Alpha Artist'
        assert musics[1]['singer'] == 'Zebra Artist'

    def test_list_musics_with_order_by_genre(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Add test music
        repo.add_music('Song 1', '2020', 'Artist 1', 'Zebra Genre')
        repo.add_music('Song 2', '2021', 'Artist 2', 'Alpha Genre')
        
        print(f"Debug: Testing genre ordering")
        musics = repo.list_musics(order_by='genre', order_dir='asc')
        print(f"Debug: Found {len(musics)} musics: {musics}")
        assert len(musics) == 2
        assert musics[0]['genre'] == 'Alpha Genre'
        assert musics[1]['genre'] == 'Zebra Genre'

    def test_list_musics_with_user_name_parameter(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Add test music
        repo.add_music('Test Song', '2020', 'Test Artist', 'Rock')
        
        # Test that user_name parameter doesn't break the function
        musics = repo.list_musics(user_name='testuser')
        assert len(musics) == 1
        assert musics[0]['title'] == 'Test Song'

    def test_list_musics_music_structure(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Add test music
        repo.add_music('Test Song', '2020', 'Test Artist', 'Rock')
        
        print(f"Debug: Testing music structure")
        musics = repo.list_musics()
        print(f"Debug: Found {len(musics)} musics: {musics}")
        assert len(musics) == 1
        
        music = musics[0]
        assert 'title' in music
        assert 'year' in music
        assert 'singer' in music
        assert 'genre' in music
        
        assert music['title'] == 'Test Song'
        assert music['year'] == '2020'
        assert music['singer'] == 'Test Artist'
        assert music['genre'] == 'Rock'
