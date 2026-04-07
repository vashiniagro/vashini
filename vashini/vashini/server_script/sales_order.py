import frappe
import re
from frappe.utils import getdate
from erpnext.accounts.utils import get_fiscal_year
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_inter_company_transaction


# def set_proforma_invoice_no(self, method):
#     if not self.company or self.custom_performa_invoice_no:
#         return

#     # 🏢 Company Abbreviation
#     abbr = frappe.db.get_value("Company", self.company, "abbr")
#     if not abbr:
#         frappe.throw(f"Abbreviation not set for Company {self.company}")

#     # 📅 Date
#     posting_date = self.transaction_date or getdate()

#     # ✅ COMPANY-AWARE fiscal year lookup
#     fiscal_year_name = get_fiscal_year(
#         posting_date,
#         company=self.company
#     )[0]

#     fy_doc = frappe.get_doc("Fiscal Year", fiscal_year_name)

#     # ✅ Correct FY short format → 25-26
#     fy_start = fy_doc.year_start_date.year
#     fy_end = fy_doc.year_end_date.year

#     fy_short = f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"

#     prefix = f"{abbr}/PI{fy_short}/"

#     existing = frappe.db.sql(
#         """
#         SELECT custom_performa_invoice_no
#         FROM `tabSales Order`
#         WHERE company = %s
#           AND custom_performa_invoice_no LIKE %s
#         """,
#         (self.company, prefix + "%"),
#         as_dict=True
#     )

#     used_numbers = set()

#     for row in existing:
#         val = row.custom_performa_invoice_no
#         if not val:
#             continue

#         match = re.search(rf"^{re.escape(prefix)}(\d+)$", val)
#         if match:
#             used_numbers.add(int(match.group(1)))

#     next_no = 1
#     while next_no in used_numbers:
#         next_no += 1

#     self.custom_performa_invoice_no = f"{prefix}{str(next_no).zfill(3)}"

def proforma_no_cancel(self,method):
    self.custom_performa_invoice_no = ""
# Trigger: on_submit

def auto_create_po(self,method):
    if self.is_internal_customer and not self.inter_company_order_reference:
        try:
            po = make_inter_company_transaction("Sales Order", self.name)

            if po and po.docstatus == 0:
                po.flags.ignore_mandatory = True
                po.save(ignore_permissions=True)

            frappe.msgprint(f"Inter Company PO {po.name} created in Draft")

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Auto Inter Company PO Error")

