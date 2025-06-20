class User:
    def __init__(self, userName: str, birthYear: str, email: str):
        self.userName = userName  # Nome do usuário
        self.birthYear = birthYear  # Ano de nascimento (string para xsd:dateTime)
        self.email = email  # E-mail de contato
