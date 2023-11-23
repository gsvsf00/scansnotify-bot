from .Scan import Scan

class TelegramUser:
    def __init__(self, user_id, username=None, first_name=None, last_name=None):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.is_bot = None
        self.language_code = None
        self.scans = []

    def get_full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def add_scan(self, name, source):
        scan = Scan(name, source)
        self.scans.append(scan)

    def list_scans(self):
        return [f"{scan.name} from {scan.source}" for scan in self.scans]

    def __str__(self):
        return f"User {self.user_id} ({self.get_full_name()})"

    def update_user_info(self, user_info):
        # Update user information based on the provided dictionary
        self.user_id = user_info.get('user_id', self.user_id)
        self.username = user_info.get('username', self.username)
        self.first_name = user_info.get('first_name', self.first_name)
        self.last_name = user_info.get('last_name', self.last_name)
        self.is_bot = user_info.get('is_bot', self.is_bot)
        self.language_code = user_info.get('language_code', self.language_code)
        # Add any other attributes you want to update
