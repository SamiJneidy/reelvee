from app.shared.exceptions.files import InvalidFilenameException

class FileHelper:
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Validate filename and return name and extension"""
        try:
            if filename.count(".") != 1:
                raise InvalidFilenameException(detail="Filename must have exactly one extension")
            name, extension = filename.split(".")
            if extension == "":
                raise InvalidFilenameException(detail="Filename must have an extension")
            return name, extension
        except Exception:
            raise InvalidFilenameException()

    @staticmethod
    def get_extension(filename: str) -> str:
        """Get extension from filename"""
        return FileHelper.validate_filename(filename)[1]
    
    @staticmethod
    def get_name(filename: str) -> str:
        """Get name from filename"""
        return FileHelper.validate_filename(filename)[0]
