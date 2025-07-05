import os
import sys
import pytest
import tempfile
from owlready2 import get_ontology, Thing
from uuid import uuid4

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
def sample_ontology():
    """Fixture to create a sample ontology with basic structure and unique IRI."""
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
        onto.save(file=temp_path)
        yield temp_path
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@pytest.fixture
def genre_data():
    """Fixture to create a user and three genres for genre-related tests."""
    
    with tempfile.NamedTemporaryFile(suffix='.owl', delete=False) as tmp:
        temp_path = tmp.name
    
    try:
        onto = get_ontology(temp_path)
        
        with onto:
            class User(Thing): pass
            class Music(Thing): pass
            class Genre(Thing): pass
            class Singer(Thing): pass
            class Rating(Thing): pass

        user = onto.User("test_user")
        user.birthYear = ["1990"]
        user.email = ["test@email.com"]
        
        rock_genre = onto.Genre("Rock")
        rock_genre.name = ["Rock"]
        
        jazz_genre = onto.Genre("Jazz")
        jazz_genre.name = ["Jazz"]
        
        pop_genre = onto.Genre("Pop")
        pop_genre.name = ["Pop"]
        
        onto.save(file=temp_path)
        yield onto, temp_path, user, rock_genre, jazz_genre, pop_genre
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@pytest.fixture
def singer_data():
    """Fixture to create a user, a singer, and two songs for singer-related tests."""
    
    with tempfile.NamedTemporaryFile(suffix='.owl', delete=False) as tmp:
        temp_path = tmp.name
    
    try:
        onto = get_ontology(temp_path)
        
        with onto:
            class User(Thing): pass
            class Music(Thing): pass
            class Genre(Thing): pass
            class Singer(Thing): pass
            class Rating(Thing): pass
        
        user = onto.User("test_user")
        user.birthYear = ["1990"]
        user.email = ["test@email.com"]
        
        singer = onto.Singer("queen")
        singer.name = ["Queen"]
        
        music1 = onto.Music("bohemian_rhapsody")
        music1.title = ["Bohemian Rhapsody"]
        music1.hasSinger = [singer]
        
        music2 = onto.Music("another_one_bites_the_dust")
        music2.title = ["Another One Bites the Dust"]
        music2.hasSinger = [singer]
        
        onto.save(file=temp_path)
        yield onto, temp_path, user, singer, music1, music2
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
