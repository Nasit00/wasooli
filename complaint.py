from datetime import datetime

class Complaint:
    def __init__(self, cid, serial, username, message):
        self.id = cid
        self.serial = serial
        self.username = username
        self.message = message
        self.status = "Pending"
        self.reply = ""
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
