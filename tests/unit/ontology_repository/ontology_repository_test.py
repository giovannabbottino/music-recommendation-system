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

    def test_get_user_rating_existing(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Setup: add user and music
        repo.add_user('bob', '1985', 'bob@email.com')
        repo.add_music('Bohemian Rhapsody', '1975', 'Queen', 'Rock')
        
        # Add rating
        repo.add_rating('bob', 'Bohemian Rhapsody', 4)
        
        # Get rating
        rating = repo.get_user_rating('bob', 'Bohemian Rhapsody')
        assert rating == 4

    def test_get_user_rating_nonexistent(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Setup: add user and music
        repo.add_user('charlie', '1995', 'charlie@email.com')
        repo.add_music('Hotel California', '1976', 'Eagles', 'Rock')
        
        # Try to get rating for music that hasn't been rated
        rating = repo.get_user_rating('charlie', 'Hotel California')
        assert rating is None

    def test_get_user_rating_nonexistent_user(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Add music without user
        repo.add_music('Stairway to Heaven', '1971', 'Led Zeppelin', 'Rock')
        
        # Try to get rating for nonexistent user
        rating = repo.get_user_rating('nonexistent_user', 'Stairway to Heaven')
        assert rating is None

    def test_get_user_rating_nonexistent_music(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Add user without music
        repo.add_user('david', '1980', 'david@email.com')
        
        # Try to get rating for nonexistent music
        rating = repo.get_user_rating('david', 'Nonexistent Song')
        assert rating is None

    def test_get_user_rating_update_existing(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Setup: add user and music
        repo.add_user('eve', '1990', 'eve@email.com')
        repo.add_music('Yesterday', '1965', 'The Beatles', 'Pop')
        
        # Add initial rating
        repo.add_rating('eve', 'Yesterday', 3)
        rating1 = repo.get_user_rating('eve', 'Yesterday')
        assert rating1 == 3
        
        # Update rating
        repo.add_rating('eve', 'Yesterday', 5)
        rating2 = repo.get_user_rating('eve', 'Yesterday')
        assert rating2 == 5

    def test_get_user_rating_multiple_users(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Setup: add multiple users and music
        repo.add_user('frank', '1985', 'frank@email.com')
        repo.add_user('grace', '1992', 'grace@email.com')
        repo.add_music('Wonderwall', '1995', 'Oasis', 'Rock')
        
        # Add ratings for different users
        repo.add_rating('frank', 'Wonderwall', 4)
        repo.add_rating('grace', 'Wonderwall', 2)
        
        # Get ratings
        frank_rating = repo.get_user_rating('frank', 'Wonderwall')
        grace_rating = repo.get_user_rating('grace', 'Wonderwall')
        
        assert frank_rating == 4
        assert grace_rating == 2

    def test_get_user_rating_multiple_musics(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Setup: add user and multiple musics
        repo.add_user('henry', '1988', 'henry@email.com')
        repo.add_music('Smells Like Teen Spirit', '1991', 'Nirvana', 'Grunge')
        repo.add_music('Sweet Child O Mine', '1987', 'Guns N Roses', 'Rock')
        
        # Add ratings for different musics
        repo.add_rating('henry', 'Smells Like Teen Spirit', 5)
        repo.add_rating('henry', 'Sweet Child O Mine', 3)
        
        # Get ratings
        nirvana_rating = repo.get_user_rating('henry', 'Smells Like Teen Spirit')
        gnr_rating = repo.get_user_rating('henry', 'Sweet Child O Mine')
        
        assert nirvana_rating == 5
        assert gnr_rating == 3

    def test_get_user_rating_with_spaces_in_title(self, sample_ontology):
        temp_file = sample_ontology
        repo = OntologyRepository(temp_file)
        repo.load()
        
        # Setup: add user and music with spaces in title
        repo.add_user('iris', '1993', 'iris@email.com')
        repo.add_music('Sweet Home Alabama', '1974', 'Lynyrd Skynyrd', 'Southern Rock')
        
        # Add rating
        repo.add_rating('iris', 'Sweet Home Alabama', 4)
        
        # Get rating
        rating = repo.get_user_rating('iris', 'Sweet Home Alabama')
        assert rating == 4 

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
