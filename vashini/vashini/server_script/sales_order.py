import frappe
import re
from frappe.utils import getdate
from erpnext.accounts.utils import get_fiscal_year

def set_proforma_invoice_no(self, method):
    if not self.company or self.custom_performa_invoice_no:
        return

    abbr = frappe.db.get_value("Company", self.company, "abbr")
    if not abbr:
        frappe.throw(f"Abbreviation not set for Company {self.company}")

    posting_date = self.transaction_date or getdate()
    fiscal_year = get_fiscal_year(posting_date)[0] 

    fy_start, fy_end = fiscal_year.split("-")
    fy_short = f"{fy_start[-2:]}-{fy_end[-2:]}"

    prefix = f"{abbr}/PI{fy_short}/"

    existing = frappe.db.sql("""
        SELECT custom_performa_invoice_no
        FROM `tabSales Order`
        WHERE company = %s
          AND custom_performa_invoice_no LIKE %s
    """, (self.company, prefix + "%"), as_dict=True)

    used_numbers = set()

    for row in existing:
        if row.custom_performa_invoice_no:
            match = re.search(rf"{prefix}(\d+)", row.custom_performa_invoice_no)
            if match:
                used_numbers.add(int(match.group(1)))

    next_no = 1
    while next_no in used_numbers:
        next_no += 1

    self.custom_performa_invoice_no = f"{prefix}{str(next_no).zfill(3)}"






# import frappe
# from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_inter_company_transaction

# def make_inter_company_po(self, method):
#     if self.is_internal_customer == 1 and not self.inter_company_order_reference:
#         # Create the inter-company Purchase Order
#         po = make_inter_company_transaction("Sales Order", self.name)
#         po.insert()
#         po.submit()

#         # Optional: Update reference field if needed
#         # self.db_set('inter_company_order_reference', po.name)

#         frappe.msgprint(f"Inter Company Purchase Order {po.name} has been created.")
