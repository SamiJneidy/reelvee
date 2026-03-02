from typing import Optional

class AuthRepository:
    def __init__(self, session=None):
        self.session = session
