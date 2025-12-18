# Copyright (c) 2025, Samtech and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def sync_user_permissions(doc, method=None):
    if not doc.custom_user:
        return
    existing_perms = frappe.get_all(
        "User Permission",
        filters={
            "user": doc.custom_user,
            "allow": "Territory"
        },
        pluck="for_value"
    )
    existing_perms = set(existing_perms)

    for row in doc.custom_terrorities:
        print()
        print()
        print("existing_perms : ", existing_perms)
        print("row.territory : ", row.territory)
        print()
        print()
        if row.territory not in existing_perms:
            print()
            existing_perms.add(row.territory)
            print("row.territory existed : ", row.territory)
            print()
            frappe.get_doc({
                "doctype": "User Permission",
                "user": doc.custom_user,
                "allow": "Territory",
                "for_value": row.territory,
                "apply_to_all_doctypes": 1
            }).insert(ignore_permissions=True)

    return


# ============================================
# SYNC FROM ITEM TO SALES PERSON
# ============================================

def sync_from_item_to_sales_person(doc, method=None):
	"""
	Called when Item is saved.
	Syncs Sales Person Item child table to Target Detail Item in Sales Person.
	"""

	# Prevent infinite loop
	if frappe.flags.in_sync:
		return
	
	frappe.flags.in_sync = True

	try:
		for row in doc.get("custom_sales_person_details"):
			sales_person_doc = frappe.get_doc("Sales Person", row.sales_person)

			isExist=False
			for item in sales_person_doc.custom_targets_items:
				if item.item == doc.name:
					item.fiscal_year = row.fiscal_year
					item.target_qty = row.target_qty
					item.target_amount = row.target_amount
					item.distribution_id = row.distribution_id
					isExist=True
					break
			if not isExist:
				new_item = {"item": doc.name, "fiscal_year": row.fiscal_year, "target_qty": row.target_qty, "target_amount": row.target_amount, "distribution_id": row.distribution_id}
				sales_person_doc.append("custom_targets_items", new_item)
			sales_person_doc.save()
	except Exception as e:
		frappe.msgprint(f"{e}")
	finally:
		frappe.flags.in_sync = False

# ============================================
# SYNC FROM SALES PERSON TO ITEM
# ============================================

def sync_from_sales_person_to_item(doc, method=None):
	"""
	Called when Sales Person is saved.
	Syncs Target Detail Item child table to Sales Person Item in Item.
	"""

	if frappe.flags.in_sync:
		return
	
	frappe.flags.in_sync = True

	try:
		for row in doc.get("custom_targets_items"):
			item_doc = frappe.get_doc("Item", row.item)

			isExist=False
			for sales_person in item_doc.custom_sales_person_details:
				if sales_person.sales_person == doc.name:
					sales_person.fiscal_year = row.fiscal_year
					sales_person.target_qty = row.target_qty
					sales_person.target_amount = row.target_amount
					sales_person.distribution_id = row.distribution_id
					isExist=True
					break
			if not isExist:
				new_sales_person = {"sales_person": doc.name, "fiscal_year": row.fiscal_year, "target_qty": row.target_qty, "target_amount": row.target_amount, "distribution_id": row.distribution_id}
				item_doc.append("custom_sales_person_details", new_sales_person)
			item_doc.save()
	except Exception as e:
		frappe.msgprint(f"{e}")
	finally:
		frappe.flags.in_sync = False



