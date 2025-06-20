import pytest
from src.infrastructure.ontology_repository import OntologyRepository

class TestFavoriteSingerRule:
    def test_apply_favorite_singer_rule_success(self, singer_data):
        """Test if the singer is marked as favorite when a user rates a song with 5 stars."""
        onto, temp_file, user, singer, music1, _ = singer_data
        rating = onto.Rating("rating1")
        rating.hasRating.append(5)
        rating.ratedBy.append(user)
        rating.ratesMusic.append(music1)
        onto.save(file=temp_file)
        repo = OntologyRepository(temp_file)
        onto_loaded = repo.load()
        repo.apply_favorite_singer_rule()
        user_instance = next(i for i in onto_loaded.individuals() if i.name == "test_user")
        singer_instance = next(i for i in onto_loaded.individuals() if i.name == "queen")
        assert hasattr(user_instance, 'favoriteSinger')
        assert singer_instance in user_instance.favoriteSinger

    def test_apply_singer_recommendation_rule_success(self, singer_data):
        """Test if songs by a favorite singer are recommended to the user."""
        onto, temp_file, user, singer, music1, music2 = singer_data
        user.favoriteSinger.append(singer)
        onto.save(file=temp_file)
        repo = OntologyRepository(temp_file)
        onto_loaded = repo.load()
        repo.apply_singer_recommendation_rule()
        user_instance = next(i for i in onto_loaded.individuals() if i.name == "test_user")
        music_names = [m.name for m in getattr(user_instance, 'recommendMusic', [])]
        assert "bohemian_rhapsody" in music_names
        assert "another_one_bites_the_dust" in music_names 
