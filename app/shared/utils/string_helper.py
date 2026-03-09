class StringHelper:

    @staticmethod
    def remove_repeated_spaces(text: str) -> str:
        """Removes repeated spaces from the text."""
        return " ".join(text.split())

    @staticmethod
    def remove_special_characters(text: str) -> str:
        """Removes special characters from the text. Keeps alphabets, numbers and white spaces."""
        return "".join(c for c in text if c.isalnum() or c == " ")
