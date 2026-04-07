from __future__ import unicode_literals
import frappe
from frappe import _
from collections import defaultdict


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    dataa = []

    grouped_data = defaultdict(list)

    # Group by Sales Invoice Reference
    for row in data:
        key = row.custom_sales_invoice_reference or "No Reference"
        grouped_data[key].append(row)

    # Process each group
    for custom_ref, rows in grouped_data.items():
        tot_amount = 0

        for i in rows:
            dataa.append({
                "custom_sales_invoice_reference": i.custom_sales_invoice_reference,
                "customer": i.customer_name,
                "sales_person": i.sales_person,
                "name": i.name,
                "supplier": i.supplier_name,
                "posting_date": i.posting_date,
                "bill_no": i.bill_no,
                "bill_date": i.bill_date,
                "item_name": i.item_name,
                "expense_account": i.expense_account,
                "amount": i.amount,
                "total_amount": ""
            })

            tot_amount += i.amount or 0

        # Total Purchase Value
        dataa.append({
            "custom_sales_invoice_reference": "TOTAL Purchase Value",
            "customer": "",
            "sales_person": "",
            "name": "",
            "supplier": "",
            "posting_date": "",
            "bill_no": "",
            "bill_date": "",
            "item_name": "",
            "expense_account": "",
            "amount": tot_amount,
            "total_amount": ""
        })

        if custom_ref != "No Reference":

            # Stock Entry Value
            stock = frappe.db.get_value(
                "Stock Entry",
                {
                    "custom_sales_invoice": custom_ref,
                    "stock_entry_type": "Repack"
                },
                "name"
            )

            val = frappe.db.get_value(
                "Stock Entry",
                {
                    "custom_sales_invoice": custom_ref,
                    "stock_entry_type": "Repack"
                },
                "total_outgoing_value"
            ) or 0

            dataa.append({
                "custom_sales_invoice_reference": "Total Coconut Value",
                "customer": "",
                "sales_person": "",
                "name": stock,
                "supplier": "",
                "posting_date": "",
                "bill_no": "",
                "bill_date": "",
                "item_name": "",
                "expense_account": "",
                "amount": val,
                "total_amount": ""
            })

            # Sales Total
            sales_total = frappe.db.get_value(
                "Sales Invoice", custom_ref, "base_total"
            ) or 0

            customer = rows[0].customer_name if rows else ""

            dataa.append({
                "custom_sales_invoice_reference": "Total Sales Value",
                "customer": customer,
                "sales_person": "",
                "name": "",
                "supplier": "",
                "posting_date": "",
                "bill_no": "",
                "bill_date": "",
                "item_name": "",
                "expense_account": "",
                "amount": sales_total,
                "total_amount": ""
            })

            # 🔥 Gross Profit (VALUE ONLY IN TOTAL AMOUNT)
            gross_profit = sales_total - tot_amount - val

            dataa.append({
                "custom_sales_invoice_reference": "Gross Profit",
                "customer": customer,
                "sales_person": "",
                "name": "",
                "supplier": "",
                "posting_date": "",
                "bill_no": "",
                "bill_date": "",
                "item_name": "",
                "expense_account": "",
                "amount": "",                 # EMPTY
                "total_amount": gross_profit  # VALUE HERE
            })

    return columns, dataa


def get_columns():
    return [
        {'label': _('Sales Invoice Reference'), 'fieldname': 'custom_sales_invoice_reference', 'fieldtype': 'Data', 'width': 180},
        {'label': _('Customer'), 'fieldname': 'customer', 'fieldtype': 'Data', 'width': 150},
        {'label': _('Sales Person'), 'fieldname': 'sales_person', 'fieldtype': 'Link', 'options': 'Sales Person', 'width': 150},
        {'label': _('Purchase Invoice'), 'fieldname': 'name', 'fieldtype': 'Data', 'width': 150},
        {'label': _('Supplier'), 'fieldname': 'supplier', 'fieldtype': 'Data', 'width': 150},
        {'label': _('Date'), 'fieldname': 'posting_date', 'fieldtype': 'Date', 'width': 120},
        {'label': _('Supplier Invoice No'), 'fieldname': 'bill_no', 'fieldtype': 'Data', 'width': 150},
        {'label': _('Supplier Invoice Date'), 'fieldname': 'bill_date', 'fieldtype': 'Date', 'width': 120},
        {'label': _('Item Name'), 'fieldname': 'item_name', 'fieldtype': 'Data', 'width': 200},
        {'label': _('Account'), 'fieldname': 'expense_account', 'fieldtype': 'Link', 'options': 'Account', 'width': 200},
        {'label': _('Amount'), 'fieldname': 'amount', 'fieldtype': 'Currency', 'width': 150},
        {'label': _('Total Amount'), 'fieldname': 'total_amount', 'fieldtype': 'Currency', 'width': 150}
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    return frappe.db.sql(f"""
        SELECT
            pi.name,
            pi.supplier_name,
            pii.item_name,
            pi.posting_date,
            pi.bill_no,
            pi.bill_date,
            pii.expense_account,
            pii.amount,
            pi.custom_sales_invoice_reference,

            si.customer,
            si.customer_name,

            st.sales_person

        FROM
            `tabPurchase Invoice` pi

        LEFT JOIN
            `tabPurchase Invoice Item` pii ON pi.name = pii.parent

        LEFT JOIN
            `tabSales Invoice` si 
            ON si.name = pi.custom_sales_invoice_reference

        LEFT JOIN
            `tabSales Team` st 
            ON st.parent = pi.custom_sales_invoice_reference
            AND st.parenttype = 'Sales Invoice'
            AND st.allocated_percentage = (
                SELECT MAX(st2.allocated_percentage)
                FROM `tabSales Team` st2
                WHERE st2.parent = pi.custom_sales_invoice_reference
                AND st2.parenttype = 'Sales Invoice'
            )

        WHERE
            pi.docstatus = 1 {conditions}
    """, filters, as_dict=True)


def get_conditions(filters):
    conditions = ""

    if filters.get("sales_invoice"):
        conditions += " AND pi.custom_sales_invoice_reference = %(sales_invoice)s"

    if filters.get("sales_person"):
        conditions += """
            AND EXISTS (
                SELECT 1 FROM `tabSales Team` st
                WHERE st.parent = pi.custom_sales_invoice_reference
                AND st.parenttype = 'Sales Invoice'
                AND st.sales_person = %(sales_person)s
            )
        """

    if filters.get("customer"):
        conditions += " AND si.customer = %(customer)s"

    return conditions