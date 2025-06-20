class Music:
    def __init__(self, title: str, hasYear: str, hasSinger: 'Singer', hasGenre: 'Genre'):
        self.title = title  
        self.hasYear = hasYear  
        self.hasSinger = hasSinger  
        self.hasGenre = hasGenre 
