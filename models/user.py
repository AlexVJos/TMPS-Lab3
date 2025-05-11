class User:
    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role

    def __str__(self) -> str:
        return f"User: {self.username} ({self.role})"
