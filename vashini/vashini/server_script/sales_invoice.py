# import frappe
# from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_inter_company_transaction

# def make_inter_company_pi(self, method):
#     if self.is_internal_customer == 1:
#         # Create the inter-company Purchase Order
#         pi = make_inter_company_transaction("Sales Invoice", self.name)
#         pi.insert()

#         frappe.msgprint(f"Inter Company Purchase Invoice {pi.name} has been created.")
