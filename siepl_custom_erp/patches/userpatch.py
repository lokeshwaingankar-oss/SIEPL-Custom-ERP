import frappe


def generate_password():
    try:
        # Extract first name from email (part before @ )
        users = users = frappe.get_all(
            "User",
            filters={
                "enabled": 1,
                "name": ["not in", ["Administrator", "Guest"]]
            },
            fields=["name", "email", "first_name", "full_name"]
        )
        for row in users:
            password = f"{row.get('first_name')}{786}!@#"
            user_doc = frappe.get_doc("User",row.get('name'))
            user_doc.new_password = password
            user_doc.save(ignore_permissions=True)
            user_doc.append("roles", {
                "role": "Employee"
            })
            user_doc.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        print("................................",e)