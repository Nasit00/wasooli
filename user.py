class User:
    def __init__(self, serial, username, email, number, address, password, role):
        self.serial_number = serial
        self.username = username
        self.email = email
        self.number = number
        self.address = address
        self.password = password
        self.role = role

        # 🔥 NEW (for sub-manager system)
        self.assigned_to = None   # manager / sub-manager serial
        self.active_package = None

    def get_info(self):
        return {
            "serial_number": self.serial_number,
            "username": self.username,
            "email": self.email,
            "number": self.number,
            "address": self.address,
            "role": self.role
        }

    def update_email(self, email):
        self.email = email

    def update_number(self, number):
        self.number = number

    def update_address(self, address):
        self.address = address
