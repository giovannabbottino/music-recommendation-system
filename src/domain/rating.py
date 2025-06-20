class Rating:
    def __init__(self, hasStars: int, ratedMusic: 'Music'):
        if not (1 <= hasStars <= 5):
            raise ValueError('hasStars must be between 1 and 5')
        self.hasStars = hasStars  # Nota atribuída (de 1 a 5)
        self.ratedMusic = ratedMusic  # ratedMusic: Rating -> Music
