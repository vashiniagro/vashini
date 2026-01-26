import frappe
import re
from frappe.utils import getdate
from erpnext.accounts.utils import get_fiscal_year


def set_proforma_invoice_no(self, method):
    if not self.company or self.custom_performa_invoice_no:
        return

    # 🏢 Company Abbreviation
    abbr = frappe.db.get_value("Company", self.company, "abbr")
    if not abbr:
        frappe.throw(f"Abbreviation not set for Company {self.company}")

    # 📅 Date
    posting_date = self.transaction_date or getdate()

    # ✅ COMPANY-AWARE fiscal year lookup
    fiscal_year_name = get_fiscal_year(
        posting_date,
        company=self.company
    )[0]

    fy_doc = frappe.get_doc("Fiscal Year", fiscal_year_name)

    # ✅ Correct FY short format → 25-26
    fy_start = fy_doc.year_start_date.year
    fy_end = fy_doc.year_end_date.year

    fy_short = f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"

    prefix = f"{abbr}/PI{fy_short}/"

    existing = frappe.db.sql(
        """
        SELECT custom_performa_invoice_no
        FROM `tabSales Order`
        WHERE company = %s
          AND custom_performa_invoice_no LIKE %s
        """,
        (self.company, prefix + "%"),
        as_dict=True
    )

    used_numbers = set()

    for row in existing:
        val = row.custom_performa_invoice_no
        if not val:
            continue

        match = re.search(rf"^{re.escape(prefix)}(\d+)$", val)
        if match:
            used_numbers.add(int(match.group(1)))

    next_no = 1
    while next_no in used_numbers:
        next_no += 1

    self.custom_performa_invoice_no = f"{prefix}{str(next_no).zfill(3)}"
