import pytest
import os
from src.infrastructure.ontology_repository import OntologyRepository
from owlready2 import Thing
import shutil

@pytest.fixture
def sample_ontology():
    """Fixture to use the data-test-copy.rdf file for all tests."""
    original_file = os.path.join(os.path.dirname(__file__), '../../../data/data-test.rdf')
    test_file = os.path.join(os.path.dirname(__file__), '../../../data/data-test-copy.rdf')
    
    if not os.path.exists(original_file):
        pytest.skip(f"Arquivo original não encontrado: {original_file}")
    
    if not os.path.exists(test_file) or os.path.getmtime(test_file) < os.path.getmtime(original_file):
        try:
            shutil.copy2(original_file, test_file)
        except Exception as e:
            pytest.skip(f"Erro ao copiar arquivo de teste: {e}")
    
    yield test_file

def test_load_and_ensure_classes(sample_ontology):
    """Test loading ontology and ensuring classes are created."""
    repo = OntologyRepository(sample_ontology)
    onto = repo.load()
    assert onto is not None
    assert hasattr(onto, 'User')
    assert hasattr(onto, 'Music')
    assert hasattr(onto, 'Genre')
    assert hasattr(onto, 'Singer')
    assert hasattr(onto, 'Rating')

def test_add_user(sample_ontology):
    """Test adding a new user."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    user = repo.add_user('testuser', 1990, 'test@example.com')
    assert user is not None
    assert user.userName[0] == 'testuser'
    assert user.birthYear[0] == 1990
    assert user.email[0] == 'test@example.com'
    
    user2 = repo.add_user('testuser', 1995, 'new@example.com')
    assert user2 is not None
    assert user2.birthYear[0] == 1995
    assert user2.email[0] == 'new@example.com'

def test_add_music(sample_ontology):
    """Test adding music with singer and genre."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    music = repo.add_music('Bohemian Rhapsody', '1975', 'Queen', 'Rock')
    assert music is not None
    assert music.title[0] == 'Bohemian Rhapsody'
    assert music.hasYear[0] == '1975'
    assert music.hasSinger[0].singerName[0] == 'Queen'
    assert music.hasGenre[0].genreName[0] == 'Rock'
    
    music2 = repo.add_music('Bohemian Rhapsody', '1976', 'Queen', 'Progressive Rock')
    assert music2.hasYear[0] == '1976'
    assert music2.hasGenre[0].genreName[0] == 'Progressive Rock'

def test_add_rating(sample_ontology):
    """Test adding a rating."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    repo.add_user('testuser', 1990, 'test@example.com')
    repo.add_music('Test Song', '2020', 'Test Singer', 'Test Genre')
    
    result = repo.add_rating('testuser', 'Test Song', 'Test Genre', 5)
    assert result is True
    
    result2 = repo.add_rating('testuser', 'Test Song', 'Test Genre', 4)
    assert result2 is True

def test_add_rating_with_nonexistent_entities(sample_ontology):
    """Test adding rating with non-existent entities should raise exception."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    with pytest.raises(Exception, match="User, music, or genre not found."):
        repo.add_rating('nonexistent', 'nonexistent', 'nonexistent', 5)

def test_get_user(sample_ontology):
    """Test getting user by name and email."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    repo.add_user('testuser', 1990, 'test@example.com')
    
    user = repo.get_user('testuser')
    assert user is not None
    assert user.userName[0] == 'testuser'
    
    user2 = repo.get_user('testuser', 'test@example.com')
    assert user2 is not None
    assert user2.email[0] == 'test@example.com'
    
    user3 = repo.get_user('testuser', 'wrong@example.com')
    assert user3 is None
    
    user4 = repo.get_user('nonexistent')
    assert user4 is None

def test_get_user_rating(sample_ontology):
    """Test getting user rating for a specific music."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    repo.add_user('testuser', 1990, 'test@example.com')
    repo.add_music('Test Song', '2020', 'Test Singer', 'Test Genre')
    repo.add_rating('testuser', 'Test Song', 'Test Genre', 5)
    
    rating = repo.get_user_rating('testuser', 'Test Song')
    assert rating == 5
    
    rating2 = repo.get_user_rating('nonexistent', 'Test Song')
    assert rating2 is None
    
    rating3 = repo.get_user_rating('testuser', 'nonexistent')
    assert rating3 is None

def test_get_user_genre_preferences(sample_ontology):
    """Test getting user genre preferences based on high ratings."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    repo.add_user('testuser', 1990, 'test@example.com')
    repo.add_music('Rock Song', '2020', 'Rock Singer', 'Rock')
    repo.add_music('Pop Song', '2020', 'Pop Singer', 'Pop')
    repo.add_music('Jazz Song', '2020', 'Jazz Singer', 'Jazz')
    
    repo.add_rating('testuser', 'Rock Song', 'Rock', 5)
    repo.add_rating('testuser', 'Pop Song', 'Pop', 3) 
    repo.add_rating('testuser', 'Jazz Song', 'Jazz', 4) 
    
    preferences = repo.get_user_genre_preferences('testuser')
    assert 'Rock' in preferences
    assert 'Jazz' in preferences
    assert 'Pop' not in preferences 
    
    preferences2 = repo.get_user_genre_preferences('nonexistent')
    assert preferences2 == []

def test_add_genre_preference(sample_ontology):
    """Test adding genre preference for user."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    repo.add_user('testuser', 1990, 'test@example.com')
    repo.add_music('Test Song', '2020', 'Test Singer', 'Rock')
    
    result = repo.add_genre_preference('testuser', 'Rock')
    assert result is True
    
    with pytest.raises(Exception, match="User or genre not found."):
        repo.add_genre_preference('nonexistent', 'Rock')
    
    with pytest.raises(Exception, match="User or genre not found."):
        repo.add_genre_preference('testuser', 'nonexistent')

def test_get_user_preferences(sample_ontology):
    """Test getting user preferences."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    repo.add_user('testuser', 1990, 'test@example.com')
    repo.add_music('Test Song', '2020', 'Test Singer', 'Rock')
    
    repo.add_genre_preference('testuser', 'Rock')
    
    preferences = repo.get_user_preferences('testuser')
    assert 'Rock' in preferences
    
    preferences2 = repo.get_user_preferences('nonexistent')
    assert preferences2 == []

def test_list_recommended_musics(sample_ontology):
    """Test listing recommended musics based on user preferences."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    repo.add_user('testuser', 1990, 'test@example.com')
    repo.add_music('Rock Song 1', '2020', 'Rock Singer 1', 'Rock')
    repo.add_music('Rock Song 2', '2020', 'Rock Singer 2', 'Rock')
    repo.add_music('Pop Song', '2020', 'Pop Singer', 'Pop')
    
    repo.add_rating('testuser', 'Rock Song 1', 'Rock', 5)
    
    recommendations = repo.list_recommended_musics('testuser', limit=5)
    assert len(recommendations) > 0
    
    rock_titles = [rec['title'] for rec in recommendations if rec['genre'] == 'Rock']
    assert len(rock_titles) > 0
    
    pop_titles = [rec['title'] for rec in recommendations if rec['genre'] == 'Pop']
    assert len(pop_titles) == 0
    
    recommendations2 = repo.list_recommended_musics('nonexistent')
    assert recommendations2 == []

def test_save_functionality(sample_ontology):
    """Test that save functionality works correctly."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    repo.add_user('testuser', 1990, 'test@example.com')
    repo.add_music('Test Song', '2020', 'Test Singer', 'Rock')
    
    repo2 = OntologyRepository(sample_ontology)
    repo2.load()
    
    user = repo2.get_user('testuser')
    assert user is not None
    assert user.userName[0] == 'testuser'

def test_error_handling():
    """Test error handling when ontology file doesn't exist."""
    repo = OntologyRepository('nonexistent_file.rdf')
    onto = repo.load()
    assert onto is not None
    assert hasattr(onto, 'User')
    assert hasattr(onto, 'Music') 

def test_test_data_file_exists(sample_ontology):
    """Test that the test data file exists and has content."""
    assert os.path.exists(sample_ontology)
    
    file_size = os.path.getsize(sample_ontology)
    assert file_size > 0, f"Arquivo de teste está vazio: {sample_ontology}"


def test_list_musics_with_real_data(sample_ontology):
    """Test list_musics with real data from data-test.rdf."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    musics = repo.list_musics(limit=10)
    
    if len(musics) > 0:
        assert all(isinstance(m, dict) for m in musics)
        assert all('title' in m for m in musics)
        assert all('year' in m for m in musics)
        assert all('genre' in m for m in musics)
        assert all('singer' in m for m in musics)
        assert all('already_rated' in m for m in musics)

def test_search_with_real_data(sample_ontology):
    """Test search functionality with real data."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    musics = repo.list_musics(search='rock', limit=5)
    
    if len(musics) > 0:
        for music in musics:
            assert 'rock' in music['title'].lower()

def test_ordering_with_real_data(sample_ontology):
    """Test ordering functionality with real data."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    musics = repo.list_musics(order_by='title', order_dir='asc', limit=5)
    if len(musics) > 1:
        titles = [m['title'] for m in musics]
        assert titles == sorted(titles)

def test_analyze_test_data_structure(sample_ontology):
    """Test to analyze the structure of the test data file."""
    repo = OntologyRepository(sample_ontology)
    onto = repo.load()
    
    assert onto is not None
    
    classes = [cls for cls in onto.classes()]
    
    for cls_name in ['User', 'Music', 'Genre', 'Singer', 'Rating']:
        if hasattr(onto, cls_name):
            instances = list(getattr(onto, cls_name).instances())
    
    music_by_title = onto.search_one(title="*")
    
    if hasattr(onto, 'Music'):
        music_instances = list(onto.Music.instances())
    
    all_with_title = onto.search(title="*")
    
    all_entities = list(onto.individuals())

def test_analyze_music_properties(sample_ontology):
    """Test to analyze music properties in the test data file."""
    repo = OntologyRepository(sample_ontology)
    onto = repo.load()
    
    music_instances = list(onto.Music.instances())
    
    if len(music_instances) > 0:
        for i, music in enumerate(music_instances[:5]):
            properties = [prop for prop in dir(music) if not prop.startswith('_')]
            
            for prop in ['title', 'hasYear', 'hasSinger', 'hasGenre']:
                if hasattr(music, prop):
                    value = getattr(music, prop)
    
    all_entities = list(onto.individuals())
    
    music_like_entities = []
    for entity in all_entities[:100]: 
        if hasattr(entity, 'title') or hasattr(entity, 'hasYear') or hasattr(entity, 'hasSinger') or hasattr(entity, 'hasGenre'):
            music_like_entities.append(entity)
    

def test_add_test_data_to_file(sample_ontology):
    """Test to add test data to the copied file."""
    repo = OntologyRepository(sample_ontology)
    repo.load()
    
    try:
        user = repo.add_user('testuser', 1990, 'test@example.com')
        
        musics = [
            ('Bohemian Rhapsody', '1975', 'Queen', 'Rock'),
            ('Hotel California', '1976', 'Eagles', 'Rock'),
            ('Imagine', '1971', 'John Lennon', 'Pop'),
            ('Stairway to Heaven', '1971', 'Led Zeppelin', 'Rock'),
            ('Yesterday', '1965', 'The Beatles', 'Pop')
        ]
        
        for title, year, singer, genre in musics:
            music = repo.add_music(title, year, singer, genre)
           
        all_musics = repo.list_musics(limit=10)
        
        assert len(all_musics) >= 5
        
    except Exception as e:
        print(f"❌ Erro ao adicionar dados de teste: {e}")
        raise
