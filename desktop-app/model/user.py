class User:
    def __init__(self, uid, username, display_name, email, created_at):
        self.uid = uid
        self.username = username
        self.email = email
        self.display_name = display_name
        self.created_at = created_at

    def get_uid(self):
        return self.uid

    def set_uid(self, uid):
        self.uid = uid

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def get_email(self):
        return self.email

    def set_email(self, email):
        self.email = email

    def get_display_name(self):
        return self.display_name

    def set_display_name(self, display_name):
        self.display_name = display_name

    def get_created_at(self):
        return self.created_at

    def set_created_at(self, created_at):
        self.created_at = created_at
