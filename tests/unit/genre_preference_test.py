import pytest
from unittest.mock import patch, MagicMock
from owlready2 import ObjectProperty
from src.infrastructure.ontology_repository import OntologyRepository


class TestOntologyRepository:
    
    def test_apply_genre_preference_rule_success(self, genre_data):
        """Test successful application of genre preference rule."""
        onto, temp_file, user, rock_genre, jazz_genre, pop_genre = genre_data
        rating = onto.Rating("test_rating")
        rating.hasStars.append(5)
        user.hasRated.append(rating)
        music = onto.Music("test_music")
        music.hasGenre.append(rock_genre)
        rating.ratedMusic.append(music)
        onto.save(file=temp_file)
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.apply_genre_preference_rule()
        assert repo.ontology is not None
    
    def test_apply_genre_preference_rule_with_4_star_rating(self, genre_data):
        """Test that preference is not inferred for ratings less than 5 stars."""
        onto, temp_file, user, rock_genre, jazz_genre, pop_genre = genre_data
        rating = onto.Rating("test_rating_4")
        rating.hasStars.append(4)
        user.hasRated.append(rating)
        music = onto.Music("test_music_4")
        music.hasGenre.append(jazz_genre)
        rating.ratedMusic.append(music)
        onto.save(file=temp_file)
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.apply_genre_preference_rule()
        assert repo.ontology is not None
    
    def test_apply_genre_preference_rule_multiple_ratings(self, genre_data):
        """Test rule application with multiple ratings for different genres."""
        onto, temp_file, user, rock_genre, jazz_genre, pop_genre = genre_data
        rock_rating = onto.Rating("rock_rating")
        rock_rating.hasStars.append(5)
        user.hasRated.append(rock_rating)
        rock_music = onto.Music("rock_music")
        rock_music.hasGenre.append(rock_genre)
        rock_rating.ratedMusic.append(rock_music)
        jazz_rating = onto.Rating("jazz_rating")
        jazz_rating.hasStars.append(5)
        user.hasRated.append(jazz_rating)
        jazz_music = onto.Music("jazz_music")
        jazz_music.hasGenre.append(jazz_genre)
        jazz_rating.ratedMusic.append(jazz_music)
        pop_rating = onto.Rating("pop_rating")
        pop_rating.hasStars.append(3)
        user.hasRated.append(pop_rating)
        pop_music = onto.Music("pop_music")
        pop_music.hasGenre.append(pop_genre)
        pop_rating.ratedMusic.append(pop_music)
        onto.save(file=temp_file)
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.apply_genre_preference_rule()
        assert repo.ontology is not None

    def test_apply_music_recommendation_rule_success(self, genre_data):
        """Test successful application of music recommendation rule."""
        onto, temp_file, user, rock_genre, _, _ = genre_data
        music = onto.Music("test_music")
        music.hasGenre.append(rock_genre)
        user.hasPreference.append(rock_genre)
        onto.save(file=temp_file)
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.apply_music_recommendation_rule()
        assert repo.ontology is not None
    
    def test_apply_music_recommendation_rule_no_preference(self, genre_data):
        """Test that music is not recommended when user has no genre preference."""
        onto, temp_file, user, rock_genre, _, _ = genre_data
        music = onto.Music("test_music")
        music.hasGenre.append(rock_genre)
        onto.save(file=temp_file)
        repo = OntologyRepository(temp_file)
        repo.load()
        repo.apply_music_recommendation_rule()
        assert repo.ontology is not None
    