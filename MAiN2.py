from modules.updates import Updates
import os
from flask import Flask, render_template, request, redirect, session
from modules.user import User
from modules.userlist import Userlist
from modules.complaint import Complaint
from modules.packgae import Package
from modules.transaction import Transaction
app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATA ----------------
user_list = Userlist()
complaints = []
packages = [
    Package("10 Mbps", 1500),
    Package("20 Mbps", 2500),
    Package("50 Mbps", 4000)
]

transactions = []

# demo accounts
user_list.add_user(User("1", "user1", "user@gmail.com", "111", "Home", "user123", "user"))
user_list.add_user(User("0", "admin", "admin@gmail.com", "000", "Office", "admin123", "manager"))
user_list.add_user(User("2", "admin", "admin@gmail.com", "000", "Office", "a", "sub_manager"))

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        role = request.form.get("role")  # safer
        password = request.form.get("password")

        if role == "user":
            username = request.form.get("username")
            for u in user_list.users:
                if u.role == "user" and u.username == username and u.password == password:
                    session["username"] = u.username
                    session["role"] = "user"
                    session["serial"] = u.serial_number
                    return redirect("/dashboard")

        elif role == "manager":
            manager_id = request.form.get("manager_id")
            for u in user_list.users:
                if u.role == "manager" and u.serial_number == manager_id and u.password == password:
                    session["username"] = u.username
                    session["role"] = "manager"
                    session["serial"] = u.serial_number
                    return redirect("/dashboard")

        elif role == "sub_manager":
            sub_manager_id = request.form.get("sub_manager_id")
            for u in user_list.users:
                if u.role == "sub_manager" and u.serial_number == sub_manager_id and u.password == password:
                    session["username"] = u.username
                    session["role"] = "sub_manager"
                    session["serial"] = u.serial_number
                    return redirect("/sub_dashboard")  # sub manager dashboard

        error = "Invalid login credentials"

    return render_template("login.html", error=error)


# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "role" not in session:
        return redirect("/")

    role = session["role"]

    if role == "manager":
        search_serial = request.args.get("search_serial", "")
        selected_sub_manager = request.args.get("sub_manager_filter", "")
        search_result_serial = None
        not_found = False

        # Add new user
        if request.method == "POST" and request.form.get("action") == "add_user":
            user = User(
                request.form["serial"],
                request.form["username"],
                request.form["email"],
                request.form["number"],
                request.form["address"],
                request.form["password"],
                "user"
            )
            user_list.add_user(user)
            return redirect("/dashboard")

        # Assign / Unassign Sub-Manager
        if request.method == "POST" and "assign_sub" in request.form:
            user_serial = request.form["user_serial"]
            sub_serial = request.form.get("sub_manager_serial")  # can be empty for unassign

            user = user_list.get_user(user_serial)
            if user:
                if sub_serial:
                    user.assigned_to = sub_serial
                else:
                    user.assigned_to = None  # unassign
            return redirect("/dashboard")

        # Filter users by selected sub-manager
        if selected_sub_manager:
            filtered_users = [
                u for u in user_list.users 
                if u.role == "user" and u.assigned_to == selected_sub_manager
            ]
        else:
            filtered_users = [u for u in user_list.users if u.role == "user"]

        # Counters (filtered)
        total_users = len(filtered_users)
        total_sub_managers = len([u for u in user_list.users if u.role == "sub_manager"])
        filtered_serials = [u.serial_number for u in filtered_users]

        total_transactions = len([t for t in transactions if str(t.user_serial) in filtered_serials])
        total_income = sum(t.price for t in transactions if str(t.user_serial) in filtered_serials and t.status == "Paid")
        remaining_balance = sum(t.price for t in transactions if str(t.user_serial) in filtered_serials and t.status != "Paid")
        total_complaints = len([c for c in complaints if str(c.serial) in filtered_serials])
        resolved_complaints = len([c for c in complaints if str(c.serial) in filtered_serials and c.status == "Resolved"])

        # Search
        if search_serial:
            user = user_list.get_user(search_serial)
            if user:
                search_result_serial = user.serial_number
            else:
                not_found = True

        return render_template(
            "dashboard_manager.html",
            users=filtered_users,
            sub_managers=[u for u in user_list.users if u.role=="sub_manager"],

            search_result_serial=search_result_serial,
            not_found=not_found,
            search_serial=search_serial,
            selected_sub_manager=selected_sub_manager,

            # 👇 counters
            total_users=total_users,
            total_sub_managers=total_sub_managers,
            total_transactions=total_transactions,
            total_income=total_income,
            remaining_balance=remaining_balance,
            total_complaints=total_complaints,
            resolved_complaints=resolved_complaints
        )

    # User dashboard
    else:
        user = user_list.get_user(session["serial"])
        system_status = "online"

        user_packages = [t for t in transactions if t.user_serial == user.serial_number and t.assigned]

        return render_template(
            "dashboard_user.html",
            user=user,
            packages=user_packages,
            system_status=system_status
        )
# ---------------- ASSIGN USERS TO SUB-MANAGER ----------------
@app.route("/assign_users", methods=["POST"])
def assign_users():
    if session.get("role") != "manager":
        return redirect("/dashboard")

    user_serial = request.form["user_serial"]
    sub_serial = request.form["sub_manager"]

    user = user_list.get_user(user_serial)
    if user:
        user.assigned_to = sub_serial

    return redirect("/dashboard")
# ---------------- SUB DASHBOARD ----------------
# ---------------- SUB DASHBOARD ----------------
@app.route("/sub_dashboard")
def sub_dashboard():
    if session.get("role") != "sub_manager":
        return redirect("/dashboard")

    sub_manager = user_list.get_user(session["serial"])

    # Users assigned to this sub-manager
    assigned_users = [
        u for u in user_list.users
        if str(u.assigned_to) == str(sub_manager.serial_number)
    ]
    assigned_serials = [str(u.serial_number) for u in assigned_users]

    # Transactions of assigned users
    assigned_transactions = [
        t for t in transactions if str(t.user_serial) in assigned_serials
    ]
    collected_income = sum(t.price for t in assigned_transactions if t.status == "Paid")
    remaining_balance = sum(t.price for t in assigned_transactions if t.status != "Paid")

    # Complaints of assigned users
    assigned_complaints = [c for c in complaints if str(c.serial) in assigned_serials]
    resolved_complaints = len([c for c in assigned_complaints if c.status == "Resolved"])

    return render_template(
        "dashboard_sub_manager.html",
        sub_manager=sub_manager,
        users=assigned_users,
        transactions=assigned_transactions,
        complaints=assigned_complaints,

        # Counters
        total_assigned_users=len(assigned_users),
        total_income=collected_income,
        remaining_balance=remaining_balance,
        total_complaints=len(assigned_complaints),
        resolved_complaints=resolved_complaints
    )

# ---------------- UPDATES SUB-MANAGER ----------------
@app.route("/updates_sub_manager", methods=["GET", "POST"])
def updates_sub_manager():
    if session.get("role") != "sub_manager":
        return redirect("/dashboard")

    sub_manager = user_list.get_user(session["serial"])

    # Users assigned to this sub-manager
    assigned_users = [
        u for u in user_list.users
        if str(u.assigned_to) == str(sub_manager.serial_number)
    ]
    assigned_user_serials = [str(u.serial_number) for u in assigned_users]

    if request.method == "POST":
        receiver_serial = request.form["user_serial"]
        comment = request.form["comment"]

        u = Updates(
            receiver_serial=receiver_serial,
            receiver_name=user_list.get_user(receiver_serial).username,
            sender_serial=sub_manager.serial_number,
            sender_name=sub_manager.username,
            comment=comment,
            is_from_manager=False
        )
        updates_list.append(u)
        return redirect("/updates_sub_manager")

    # Updates from manager to this sub-manager
    manager_updates = [
        u for u in updates_list
        if str(u.receiver_serial) == str(sub_manager.serial_number) and u.is_from_manager
    ]

    # Sub-manager's own updates to assigned users
    sub_updates = [
        u for u in updates_list
        if str(u.receiver_serial) in assigned_user_serials and not u.is_from_manager
    ]

    return render_template(
        "update_sub_manager.html",
        assigned_users=assigned_users,
        manager_updates=manager_updates,
        updates=sub_updates
    )



# ---------------- EDIT USER ----------------
@app.route("/edit/<serial>", methods=["GET", "POST"])
def edit(serial):
    if session.get("role") != "manager":
        return redirect("/dashboard")

    user = user_list.get_user(serial)
    if not user:
        return redirect("/dashboard")

    search_serial = request.args.get("search_serial", "")

    if request.method == "POST":
        user.update_email(request.form["email"])
        user.update_number(request.form["number"])
        user.update_address(request.form["address"])
        return redirect(f"/dashboard?search_serial={search_serial}")

    return render_template("edit.html", u=user, search_serial=search_serial)

# ---------------- REMOVE USER ----------------
@app.route("/remove/<serial>")
def remove(serial):
    if session.get("role") != "manager":
        return redirect("/dashboard")
    search_serial = request.args.get("search_serial", "")
    user_list.remove_user(serial)
    return redirect(f"/dashboard?search_serial={search_serial}")

# ---------------- RESET SEARCH ----------------
@app.route("/reset_search")
def reset_search():
    if session.get("role") != "manager":
        return redirect("/dashboard")
    return redirect("/dashboard")

# ---------------- USER PROFILE ----------------
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if session.get("role") != "user":
        return redirect("/dashboard")

    user = user_list.get_user(session["serial"])
    if request.method == "POST":
        user.update_email(request.form["email"])
        user.update_number(request.form["number"])
        user.update_address(request.form["address"])
        return redirect("/dashboard")

    return render_template("edit.html", u=user)

# ---------------- TRANSACTIONS / UPDATES PLACEHOLDERS ----------------
@app.route("/transactions", methods=["GET", "POST"])
def transactions_page():
    if "role" not in session:
        return redirect("/")

    role = session["role"]

    # ================= USER =================
    if role == "user":
        user = user_list.get_user(session["serial"])
        if not user:
            return redirect("/dashboard")

        # BUY / PAY button
        if request.method == "POST":
            pkg_name = request.form.get("package")
            receipt = request.form.get("receipt")

            found = False
            for t in transactions:
                if str(t.user_serial) == str(user.serial_number) and t.package_name == pkg_name:
                    if receipt:
                        t.confirm_payment(receipt)
                    found = True
                    break

            if not found:
                for p in packages:
                    if p.name == pkg_name:
                        transactions.append(
                            Transaction(
                                user.serial_number,
                                user.username,
                                p.name,
                                p.price
                            )
                        )
                        break

            return redirect("/transactions")

        user_tx = [t for t in transactions if str(t.user_serial) == str(user.serial_number)]

        return render_template(
            "transactions_user.html",
            packages=packages,
            transactions=user_tx
        )

    # ================= MANAGER =================
    elif role == "manager":
        return redirect("/transactions_manager")

    # ================= SUB MANAGER =================
    elif role == "sub_manager":
    # Get serials of users assigned to this sub-manager
        assigned_serials = [str(u.serial_number) for u in user_list.users if str(u.assigned_to) == str(session["serial"])]

        # Transactions of assigned users
        sub_tx = [t for t in transactions if str(t.user_serial) in assigned_serials]

        # Handle POST (update status or assign package)
        if request.method == "POST":
            tid = int(request.form.get("transaction_id", 0))
            new_status = request.form.get("status")  # for status update

            for t in sub_tx:
                if t.id == tid:
                    # Update status
                    if new_status:
                        t.status = new_status
                    # Assign package if paid and not assigned
                    elif t.status == "Paid" and not t.assigned:
                        t.assigned = True
                    break
            return redirect("/transactions")

        return render_template(
            "transactions_sub_manager.html",
            transactions=sub_tx
        )




@app.route("/transactions_manager", methods=["GET", "POST"])
def transactions_manager():
    if session.get("role") != "manager":
        return redirect("/dashboard")

    if request.method == "POST":

        # ---------- Add New Package ----------
        if "add_package" in request.form:
            name = request.form["new_pkg_name"]
            price = int(request.form["new_pkg_price"])
            if not any(p.name == name for p in packages):
                packages.append(Package(name, price))

        # ---------- Update Existing Package Price ----------
        elif "price_update" in request.form:
            name = request.form["pkg_name"]
            new_price = float(request.form["price"])
            for p in packages:
                if p.name == name:
                    p.price = new_price
                    break

        # ---------- Assign Package to User ----------
        elif "assign" in request.form:
            tid = int(request.form.get("transaction_id"))
            # Find transaction by id
            for t in transactions:
                if t.id == tid and t.status == "Paid" and not t.assigned:
                    t.assigned = True
                    break

        return redirect("/transactions_manager")  # avoid form resubmission

    return render_template(
        "transactions_manager.html",
        packages=packages,
        users=user_list.users,
        transactions=transactions
    )

@app.route("/update_transaction/<int:tid>", methods=["POST"])
def update_transaction(tid):
    if "role" not in session:
        return redirect("/")

    role = session["role"]
    user_serial = session.get("serial")
    new_status = request.form.get("status")

    for t in transactions:
        if t.id == tid:
            # Manager can update any transaction
            if role == "manager":
                if new_status == "Assigned":
                    t.assigned = True
                t.status = new_status
                return redirect("/transactions_manager")

            # Sub-manager can update only assigned users' transactions
            elif role == "sub_manager":
                assigned_serials = [u.serial_number for u in user_list.users if str(u.assigned_to) == str(user_serial)]
                if t.user_serial in assigned_serials:
                    if t.status == "Paid" and new_status == "Assigned":
                        t.assigned = True
                        t.status = "Assigned"
                    return redirect("/transactions")  # stay on sub-manager page
            break

    # fallback
    if role == "sub_manager":
        return redirect("/transactions")
    else:
        return redirect("/transactions_manager")




# ---------------- COMPLAINTS ----------------
@app.route("/complaints", methods=["GET", "POST"])
def complaints_page():
    if "role" not in session:
        return redirect("/")

    role = session["role"]

    # ========== USER ========== (add complaint)
    if role == "user":
        user = user_list.get_user(session["serial"])
        if request.method == "POST":
            complaints.append(
                Complaint(
                    len(complaints) + 1,
                    user.serial_number,
                    user.username,
                    request.form["message"]
                )
            )
            return redirect("/complaints")

        user_complaints = [c for c in complaints if str(c.serial) == str(session["serial"])]
        return render_template("complaints_user.html", complaints=user_complaints)

    # ========== SUB MANAGER ==========
    elif role == "sub_manager":
        assigned_serials = [
            str(u.serial_number)
            for u in user_list.users
            if str(u.assigned_to) == str(session["serial"])
        ]

        filtered_complaints = [c for c in complaints if str(c.serial) in assigned_serials]

        return render_template(
            "complaints_sub_manager.html",
            complaints=filtered_complaints
        )

    # ========== MANAGER ==========
    elif role == "manager":
        return render_template("complaints_manager.html", complaints=complaints)

    return redirect("/")

# ---------------- UPDATE COMPLAINT STATUS ----------------
@app.route("/update_complaint/<int:cid>/<status>", methods=["POST"])
def update_complaint(cid, status):
    if "role" not in session:
        return redirect("/")

    role = session["role"]
    user_serial = session.get("serial")

    # Find complaint
    for c in complaints:
        if c.id == cid:
            # Manager can update any complaint
            if role == "manager":
                c.status = status
                return redirect("/complaints")
            # Sub-manager can update only assigned users' complaints
            elif role == "sub_manager":
                assigned_serials = [u.serial_number for u in user_list.users if u.assigned_to == user_serial]
                if c.serial in assigned_serials:
                    c.status = status
                    return redirect("/complaints")  # stay on sub-manager complaints page
            break

    # fallback
    if role == "sub_manager":
        return redirect("/sub_dashboard")
    else:
        return redirect("/dashboard")


# ---------------- RESOLVE COMPLAINT ----------------
# ---------------- RESOLVE COMPLAINT ----------------
@app.route("/resolve/<int:index>", methods=["POST"])
def resolve_complaint(index):
    if "role" not in session:
        return redirect("/")

    role = session["role"]
    user_serial = session.get("serial")

    if 0 <= index < len(complaints):
        c = complaints[index]
        reply = request.form.get("reply", "")

        # Manager can resolve any complaint
        if role == "manager":
            c.reply = reply
            c.status = "Resolved"
            return redirect("/complaints")

        # Sub-manager can resolve only assigned users' complaints
        elif role == "sub_manager":
            assigned_serials = [
                u.serial_number for u in user_list.users
                if str(u.assigned_to) == str(user_serial)
            ]
            if c.serial in assigned_serials:
                c.reply = reply
                c.status = "Resolved"
                return redirect("/complaints")  # stay on sub-manager page

    # fallback redirects
    if role == "sub_manager":
        return redirect("/sub_dashboard")
    else:
        return redirect("/dashboard")

updates_list = []  # global list to store updates
@app.route("/updates", methods=["GET", "POST"])
def updates():
    if "role" not in session:
        return redirect("/")

    role = session["role"]

    # -------- MANAGER --------
    if role == "manager":
        if request.method == "POST":
            receiver = user_list.get_user(request.form["user_serial"])
            comment = request.form["comment"]

            u = Updates(
                receiver_serial=receiver.serial_number,
                receiver_name=receiver.username,
                sender_serial=session["serial"],
                sender_name=session["username"],
                comment=comment,
                is_from_manager=True
            )
            updates_list.append(u)
            return redirect("/updates")

        # Manager sees all updates: sub-manager -> assigned users + manager's own updates
        return render_template(
            "updates_manager.html",
            users=user_list.users,  # all users + sub-managers
            updates=updates_list
        )

    # -------- SUB-MANAGER --------
    elif role == "sub_manager":
        # Only assigned users
        assigned_users = [u for u in user_list.users if str(u.assigned_to) == str(session['serial'])]

        if request.method == "POST":
            receiver = user_list.get_user(request.form["user_serial"])
            comment = request.form["comment"]

            u = Updates(
                receiver_serial=receiver.serial_number,
                receiver_name=receiver.username,
                sender_serial=session["serial"],
                sender_name=session["username"],
                comment=comment,
                is_from_manager=False
            )
            updates_list.append(u)
            return redirect("/updates")

        # Show updates for assigned users (both manager's and sub-manager's)
        filtered_updates = [
            u for u in updates_list
            if u.receiver_serial in [x.serial_number for x in assigned_users] or
               (u.receiver_serial == session['serial'] and u.is_from_manager)
        ]

        return render_template(
            "updates_sub_manager.html",
            users=assigned_users,             # dropdown to write update
            updates=filtered_updates          # show updates for assigned users + manager updates to sub-manager
        )

    # -------- USER --------
    else:
        # Only view updates given to the user
        user_updates = [u for u in updates_list if u.receiver_serial == session["serial"]]

        return render_template(
            "updates_user.html",
            updates=user_updates
        )

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

