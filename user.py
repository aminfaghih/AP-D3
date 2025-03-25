class User:
    """Represents a user with a UUID, username, and password."""
    def __init__(self, uuid, username, password):
        self.uuid = uuid
        self.username = username
        self.password = password