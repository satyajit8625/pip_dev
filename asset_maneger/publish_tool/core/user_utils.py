import os
import getpass

class UserUtils:
    """
    Utility class to get user-related info like OS login name.

    Example:
        username = UserUtils.get_os_user()
    """

    @staticmethod
    def get_os_user() -> str:
        """
        Get the current operating system login username.

        Returns:
            str: The OS login username, or 'UnknownUser' if not found.
        """
        return (
            os.environ.get("USERNAME")
            or os.environ.get("USER")
            or getpass.getuser()
            or "UnknownUser"
        )
