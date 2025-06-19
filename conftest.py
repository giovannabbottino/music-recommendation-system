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
        class Rating(Thing): pass
        class hasRating(DataProperty):
            domain = [Rating]
            range = [int]
            is_functional = True
        class ratedBy(ObjectProperty):
            domain = [Rating]
            range = [User]
            is_functional = True
        class hasGenre(ObjectProperty):
            domain = [Rating]
            range = [Genre]
            is_functional = True
        class hasPreference(ObjectProperty):
            domain = [User]
            range = [Genre]
            is_functional = True
    
    onto.save(file=temp_ontology_file)
    return onto, temp_ontology_file 
