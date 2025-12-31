from datetime import datetime

class Updates:
    def __init__(self, receiver_serial, receiver_name, sender_serial, sender_name, comment, is_from_manager=False):
        self.receiver_serial = receiver_serial
        self.receiver_name = receiver_name
        self.sender_serial = sender_serial
        self.sender_name = sender_name
        self.comment = comment
        self.timestamp = datetime.now()
        self.is_from_manager = is_from_manager


    def get_updates(self, comment):
        self.comment = comment
        self.timestamp = datetime.now()
