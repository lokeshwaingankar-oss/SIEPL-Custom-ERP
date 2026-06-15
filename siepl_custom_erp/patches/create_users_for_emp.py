import frappe
from frappe.utils import now_datetime
import random

def setup_employee_user_permissions():
    active_employees = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["name", "employee_name", "company_email", "personal_email", 
                "user_id", "company", "department", "designation"]
    )
    
    for employee in active_employees:
        try:
            user_id = get_or_create_user(employee)
            
            if user_id:
                if not employee.get("user_id"):
                    frappe.db.set_value("Employee", employee["name"], "user_id", user_id)
                
                create_user_permission(user_id, employee["name"])
        except Exception as e:
            frappe.log_error(
                message=frappe.get_traceback(),
                title=f"Error setting up user for employee {employee['name']}"
            )
    
    frappe.db.commit()


def get_or_create_user(employee):
    if employee.get("user_id"):
        if frappe.db.exists("User", employee["user_id"]):
            return employee["user_id"]
    random_number = random.randint(100, 999)
    emp_name = employee.get('employee_name').replace(' ', '_')
    email = "{0}{1}@hothurindia.com".format(emp_name,random_number)
    if frappe.db.exists("User", email):
        return email
    
    user = frappe.new_doc("User")
    user.email          = email
    user.first_name     = employee.get("employee_name")
    user.enabled        = 1
    user.user_type      = "System User"
    user.send_welcome_email = 0   # Set to 1 if you want welcome email sent
    user.append("roles", {
        "role": "Employee"
    })
    user.new_password = f"{employee.get('employee_name')}{786}!@#"
    user.save(ignore_permissions=True)
    
    return user.name


def create_user_permission(user_id, employee_name):
    existing_permission = frappe.db.exists(
        "User Permission",
        {
            "user": user_id,
            "allow": "Employee",
            "for_value": employee_name
        }
    )
    
    if existing_permission:
        return existing_permission
    
    # Create new user permission
    permission = frappe.new_doc("User Permission")
    permission.user       = user_id
    permission.allow      = "Employee"
    permission.for_value  = employee_name
    permission.apply_to_all_doctypes = 1 
    permission.save(ignore_permissions=True)
    
    return permission.name