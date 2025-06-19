class Music:
    def __init__(self, title: str, has_year: str, singer: 'Singer', genre: 'Genre'):
        self.title = title
        self.has_year = has_year
        self.singer = singer
        self.genre = genre 
