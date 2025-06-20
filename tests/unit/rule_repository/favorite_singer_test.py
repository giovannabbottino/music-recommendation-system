import pytest
from src.infrastructure.rule_repository import RuleRepository

class TestFavoriteSingerRule:
    def test_apply_favorite_singer_rule_success(self, singer_data):
        """Test if the singer is marked as favorite when a user rates a song with 5 stars."""
        onto, temp_file, user, singer, music1, _ = singer_data
        rating = onto.Rating("rating1")
        rating.hasStars.append(5)
        rating.ratedMusic.append(music1)
        user.hasRated.append(rating)
        onto.save(file=temp_file)
        repo = RuleRepository(temp_file)
        onto_loaded = repo.load()
        repo.apply_favorite_singer_rule()
        user_instance = next(i for i in onto_loaded.individuals() if i.name == "test_user")
        singer_instance = next(i for i in onto_loaded.individuals() if i.name == "queen")
        assert hasattr(user_instance, 'hasPreference')
        assert singer_instance in user_instance.hasPreference

    def test_apply_singer_recommendation_rule_success(self, singer_data):
        """Test if songs by a favorite singer are recommended to the user."""
        onto, temp_file, user, singer, music1, music2 = singer_data
        user.hasPreference.append(singer)
        onto.save(file=temp_file)
        repo = RuleRepository(temp_file)
        onto_loaded = repo.load()
        repo.apply_singer_recommendation_rule()
        user_instance = next(i for i in onto_loaded.individuals() if i.name == "test_user")
        music_names = [m.name for m in getattr(user_instance, 'recommendMusic', [])]
        assert "bohemian_rhapsody" in music_names
        assert "another_one_bites_the_dust" in music_names 
