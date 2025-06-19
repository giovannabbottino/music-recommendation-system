class Rating:
    def __init__(self, stars: int, user: 'User', music: 'Music', genre: 'Genre'):
        if not (1 <= stars <= 5):
            raise ValueError('Stars must be between 1 and 5')
        self.stars = stars
        self.user = user
        self.music = music
        self.genre = genre 
