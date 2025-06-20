class Rating:
    def __init__(self, hasStars: int, ratedMusic: 'Music'):
        if not (1 <= hasStars <= 5):
            raise ValueError('hasStars must be between 1 and 5')
        self.hasStars = hasStars  
        self.ratedMusic = ratedMusic 
