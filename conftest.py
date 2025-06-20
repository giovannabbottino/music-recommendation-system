import os
import sys
import pytest
import tempfile
from owlready2 import get_ontology, Thing, DataProperty, ObjectProperty

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

@pytest.fixture
def temp_ontology_file():
    """Fixture to create a temporary ontology file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.owl', delete=False) as tmp:
        tmp_path = tmp.name
    
    yield tmp_path
    
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)

@pytest.fixture
def sample_ontology(temp_ontology_file):
    """Fixture to create a sample ontology with basic structure."""
    
    onto = get_ontology(f"file://{temp_ontology_file}")
    with onto:
        class User(Thing): pass
        class Genre(Thing): pass
        class Singer(Thing): pass
        class Music(Thing): pass
        class Rating(Thing): pass
        class hasStars(DataProperty):
            domain = [Rating]
            range = [int]
            is_functional = True
        class ratedMusic(ObjectProperty):
            domain = [Rating]
            range = [Music]
            is_functional = True
        class hasSinger(ObjectProperty):
            domain = [Music]
            range = [Singer]
            is_functional = True
        class hasGenre(ObjectProperty):
            domain = [Music]
            range = [Genre]
            is_functional = True
        class hasPreference(ObjectProperty):
            domain = [User]
            range = [Genre, Music, Singer]
            is_functional = False
        class hasRated(ObjectProperty):
            domain = [User]
            range = [Rating]
            is_functional = False
        class recommendMusic(ObjectProperty):
            domain = [User]
            range = [Music]
            is_functional = False
    
    onto.save(file=temp_ontology_file)
    return onto, temp_ontology_file 

@pytest.fixture
def genre_data(sample_ontology):
    """Fixture to create a user, three genres, and three ratings for genre-related tests."""
    onto, temp_file = sample_ontology
    user = onto.User("test_user")
    rock_genre = onto.Genre("rock")
    jazz_genre = onto.Genre("jazz")
    pop_genre = onto.Genre("pop")
    onto.save(file=temp_file)
    return onto, temp_file, user, rock_genre, jazz_genre, pop_genre 

@pytest.fixture
def singer_data(sample_ontology):
    """Fixture to create a user, a singer, and two songs for singer-related tests."""
    onto, temp_file = sample_ontology
    user = onto.User("test_user")
    singer = onto.Singer("queen")
    music1 = onto.Music("bohemian_rhapsody")
    music2 = onto.Music("another_one_bites_the_dust")
    music1.hasSinger.append(singer)
    music2.hasSinger.append(singer)
    onto.save(file=temp_file)
    return onto, temp_file, user, singer, music1, music2 
