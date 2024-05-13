class UserModel:
    def __init__(self, username, password, email):
        self.email = email
        self.username = username
        self.password = password

    def __str__(self):
        return f"UserModel(username={self.username}, password={self.password})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "email": self.email,
        }

    @staticmethod
    def from_dict(data):
        return UserModel(
            username=data.get("username"),
            password=data.get("password"),
            email=data.get("email"),
        )
