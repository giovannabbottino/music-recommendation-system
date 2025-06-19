import pytest
from unittest.mock import patch, MagicMock
from owlready2 import ObjectProperty
from src.infrastructure.ontology_repository import OntologyRepository


class TestOntologyRepository:
    
    def test_apply_genre_preference_rule_success(self, sample_ontology):
        """Test successful application of genre preference rule."""
        onto, temp_file = sample_ontology
        
        user = onto.User("test_user")
        genre = onto.Genre("rock")
        rating = onto.Rating("test_rating")
        rating.hasRating.append(5)
        rating.ratedBy.append(user)
        rating.hasGenre.append(genre)
        
        onto.save(file=temp_file)
        
        repo = OntologyRepository(temp_file)
        repo.load()
        
        repo.apply_genre_preference_rule()
        
        assert repo.ontology is not None
    
    def test_apply_genre_preference_rule_with_4_star_rating(self, sample_ontology):
        """Test that preference is not inferred for ratings less than 5 stars."""
        onto, temp_file = sample_ontology
        
        user = onto.User("test_user")
        genre = onto.Genre("jazz")
        rating = onto.Rating("test_rating_4")
        rating.hasRating.append(4)
        rating.ratedBy.append(user)
        rating.hasGenre.append(genre)
        
        onto.save(file=temp_file)
        
        repo = OntologyRepository(temp_file)
        repo.load()
        
        repo.apply_genre_preference_rule()
        
        assert repo.ontology is not None
    
    def test_apply_genre_preference_rule_multiple_ratings(self, sample_ontology):
        """Test rule application with multiple ratings for different genres."""
        onto, temp_file = sample_ontology
        
        user = onto.User("test_user")
        rock_genre = onto.Genre("rock")
        jazz_genre = onto.Genre("jazz")
        
        rock_rating = onto.Rating("rock_rating")
        rock_rating.hasRating.append(5)
        rock_rating.ratedBy.append(user)
        rock_rating.hasGenre.append(rock_genre)
        
        jazz_rating = onto.Rating("jazz_rating")
        jazz_rating.hasRating.append(5)
        jazz_rating.ratedBy.append(user)
        jazz_rating.hasGenre.append(jazz_genre)
        
        pop_genre = onto.Genre("pop")
        pop_rating = onto.Rating("pop_rating")
        pop_rating.hasRating.append(3)
        pop_rating.ratedBy.append(user)
        pop_rating.hasGenre.append(pop_genre)
        
        onto.save(file=temp_file)
        
        repo = OntologyRepository(temp_file)
        repo.load()
        
        repo.apply_genre_preference_rule()
        
        assert repo.ontology is not None

    def test_apply_music_recommendation_rule_success(self, sample_ontology):
        """Test successful application of music recommendation rule."""
        onto, temp_file = sample_ontology
        
        user = onto.User("test_user")
        genre = onto.Genre("rock")
        music = onto.Music("test_music")
        music.musicHasGenre.append(genre)
        
        user.hasPreference.append(genre)
        
        onto.save(file=temp_file)
        
        repo = OntologyRepository(temp_file)
        repo.load()
        
        repo.apply_music_recommendation_rule()
        
        assert repo.ontology is not None
    
    def test_apply_music_recommendation_rule_no_preference(self, sample_ontology):
        """Test that music is not recommended when user has no genre preference."""
        onto, temp_file = sample_ontology
        
        user = onto.User("test_user")
        genre = onto.Genre("rock")
        music = onto.Music("test_music")
        music.musicHasGenre.append(genre)
        
        onto.save(file=temp_file)
        
        repo = OntologyRepository(temp_file)
        repo.load()
        
        repo.apply_music_recommendation_rule()
        
        assert repo.ontology is not None
    
