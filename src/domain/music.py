class Music:
    def __init__(self, title: str, hasYear: str, hasSinger: 'Singer', hasGenre: 'Genre'):
        self.title = title  # Título da música
        self.hasYear = hasYear  # Ano de lançamento
        self.hasSinger = hasSinger  # hasSinger: Music -> Singer
        self.hasGenre = hasGenre  # hasGenre: Music -> Genre
