from modules.user import User
class Userlist(User):
    def __init__(self):
        self.users=[]
    def add_user(self, user):
        self.users.append(user)
    def remove_user(self, serial_number):
        self.users = [user for user in self.users if user.serial_number != serial_number]
    def get_user(self, serial_number):
        for user in self.users:
            if user.serial_number == serial_number:
                return user
        return None
    def list_users(self):
        return [user.get_info() for user in self.users]
    