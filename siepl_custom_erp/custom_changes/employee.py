import frappe
import random
from frappe.utils.password import update_password


def generate_password(first_name):
    password = f"{first_name.lower()}{786}!@#"
    return password


def generate_email(emp_name):
    random_number = random.randint(100, 999)
    email = "{0}{1}@hothurindia.com".format(emp_name.lower().replace(" ", "_"), random_number)
    return email


def create_user_and_permission(doc, method=None):
    frappe.msgprint("called")
    try:
        emp_name  = doc.first_name
        email     = doc.company_email or doc.personal_email

        if not email:
            email = generate_email(emp_name)

        if frappe.db.exists("User", email):
            frappe.msgprint(f"User already exists for {email}")
            return

        first_name  = doc.first_name
        clean_name  = ''.join(c for c in first_name if c.isalpha())
        password    = generate_password(clean_name)

        user_doc = frappe.get_doc({
            "doctype"          : "User",
            "email"            : email,
            "first_name"       : doc.first_name  or "",
            "last_name"        : doc.last_name   or "",
            "enabled"          : 1,
            "user_type"        : "System User",
            "new_password"     : password,
            "send_welcome_email": 0,
        })

        user_doc.append("roles", {
            "doctype": "Has Role",
            "role"   : "Employee"
        })
        user_doc.save(ignore_permissions=True)

        update_password(email, password)

        frappe.db.set_value("Employee", doc.name, "user_id", email)

        
        if not frappe.db.exists("User Permission", {
            "user"      : email,
            "allow"     : "Employee",
            "for_value" : doc.name
        }):
            perm_doc = frappe.get_doc({
                "doctype"              : "User Permission",
                "user"                 : email,
                "allow"                : "Employee",
                "for_value"            : doc.name,
                "apply_to_all_doctypes": 1,
            })
            perm_doc.save(ignore_permissions=True)

        frappe.db.commit()

        frappe.msgprint(
            f"✅ User Created: {email} | Password: {password}",
            alert=True
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create User on Employee Insert Failed")
        frappe.throw(f"Error creating user: {str(e)}")