import os

class UserUtils:
    """
    Utility class to get user-related info like OS login name.
    """

    @staticmethod
    def get_os_user():
        """
        Get the current operating system login username.
        """
        return os.environ.get("USERNAME") or os.environ.get("USER") or "UnknownUser"
