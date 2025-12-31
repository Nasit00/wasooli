class Transaction:
    _id = 1

    def __init__(self, user_serial, username, package_name, price):
        self.id = Transaction._id
        Transaction._id += 1

        self.user_serial = user_serial
        self.username = username
        self.package_name = package_name
        self.price = price

        self.status = "Pending"
        self.receipt = None
        self.assigned = False   # ✅ VERY IMPORTANT

    def confirm_payment(self, receipt):
        self.receipt = receipt
        self.status = "Paid"
