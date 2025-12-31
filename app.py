from userlist import Userlist
from user import User
class App:
    def __init__(self):
        self.user_list = Userlist()
    def run(self):
        print("Welcome to the User Management App")
        while True:
            print("\nOptions:")
            print("1. Add User")
            print("2. Remove User")
            print("3. Get User Info")
            print("4. List All Users")
            print("5. Update User Info")
            print("6. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                serial_number = input("Enter Serial Number: ")
                username = input("Enter Username: ")
                email = input("Enter Email: ")
                number = input("Enter Number: ")
                address = input("Enter Address: ")
                user = User(serial_number, username, email, number, address)
                self.user_list.add_user(user)
                print("User added successfully.")
            elif choice == '2':
                serial_number = input("Enter Serial Number of the user to remove: ")
                self.user_list.remove_user(serial_number)
                print("User removed successfully.")
            elif choice == '3':
                serial_number = input("Enter Serial Number of the user to get info: ")
                user = self.user_list.get_user(serial_number)
                if user:
                    print(user.get_info())
                else:
                    print("User not found.")
            elif choice == '4':
                users = self.user_list.list_users()
                for user_info in users:
                    print(user_info)
            elif choice == "5":
                    serial_number = input("Enter Serial Number of the user to update: ")
                    user = self.user_list.get_user(serial_number)
                    if user:
                        print("What do you want to update?")
                        print("1. Email")
                        print("2. Address")
                        print("3. Number")
                        update_choice = input("Enter your choice: ")
                        if update_choice == '1':
                            new_email = input("Enter new email: ")
                            user.update_email(new_email)
                            print("Email updated successfully.")
                        elif update_choice == '2':
                            new_address = input("Enter new address: ")
                            user.update_address(new_address)
                            print("Address updated successfully.")
                        elif update_choice == '3':
                            new_number = input("Enter new number: ")
                            user.update_number(new_number)
                            print("Number updated successfully.")
                        else:
                            print("Invalid choice.")
                    else:
                        print("User not found.")
            elif choice == '6':
                print("Exiting the app. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")