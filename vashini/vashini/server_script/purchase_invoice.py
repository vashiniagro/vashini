import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_inter_company_purchase_invoice as original_make_icpi

@frappe.whitelist()
def make_inter_company_purchase_invoice(source_name, target_doc=None):
    # Run ERPNext's original mapping
    doc = original_make_icpi(source_name, target_doc)

    # Get the Sales Invoice
    sales_invoice = frappe.get_doc("Sales Invoice", source_name)

    # Ensure Supplier = Sales Invoice's Company (Supplier record must exist)
    if frappe.db.exists("Supplier", sales_invoice.company):
        doc.supplier = sales_invoice.company

    # Clear contact fields
    doc.contact_person = None
    doc.contact_display = None
    doc.contact_mobile = None
    doc.contact_email = None
    
    return doc
