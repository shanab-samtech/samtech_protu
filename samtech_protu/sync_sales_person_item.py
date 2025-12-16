# Copyright (c) 2025, Samtech and contributors
# For license information, please see license.txt

import frappe
from frappe import _

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



