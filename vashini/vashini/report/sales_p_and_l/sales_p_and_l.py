from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import formatdate
from datetime import datetime
from dateutil.relativedelta import relativedelta

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns(filters)
    data = get_data(filters)
    dataa = []

    # Step 1: Group data by custom_sales_invoice_reference
    from collections import defaultdict
    grouped_data = defaultdict(list)

    for row in data:
        key = row.custom_sales_invoice_reference or "No Reference"
        grouped_data[key].append(row)

    # Step 2: Process each group
    for custom_ref, rows in grouped_data.items():
        tot_amount = 0

        for i in rows:
            customer = frappe.db.get_value("Sales Invoice", i.custom_sales_invoice_reference, "customer_name") or 0
            dataa.append({
                "name": i.name,
                "supplier": i.supplier_name,
                "posting_date": i.posting_date,
                "bill_no": i.bill_no,
                "customer":customer,
                "bill_date": i.bill_date,
                "item_name":i.item_name,
                "expense_account": i.expense_account,
                "amount": i.amount,
                "custom_sales_invoice_reference": i.custom_sales_invoice_reference
            })
            tot_amount += i.amount or 0

        # Add total row for this Sales Invoice group
        dataa.append({
            "name": "",
            "supplier": "",
            "posting_date": "",
            "customer":"",
            "custom_sales_invoice_reference": "TOTAL Purchase Value",
            "bill_no": "",
            "bill_date": "",
            "expense_account": "",
            "amount": tot_amount
        })

        # Add Sales Invoice comparison row
        if custom_ref != "No Reference":
            stock =frappe.db.get_value("Stock Entry",{"custom_sales_invoice": custom_ref,"stock_entry_type": "Repack"}, "name")
            val = frappe.db.get_value(
                "Stock Entry",
                {
                    "custom_sales_invoice": custom_ref,
                    "stock_entry_type": "Repack"
                },
                "total_outgoing_value"
            ) or 0

            dataa.append({
                "name": stock,
                "supplier": "",
                "posting_date": "",
                "customer": customer,
                "custom_sales_invoice_reference": "Total Coconut Value",
                "bill_no": "",
                "bill_date": "",
                "expense_account": "",
                "amount": val
            })
            sales_total = frappe.db.get_value("Sales Invoice", custom_ref, "base_total") or 0
            customer = frappe.db.get_value("Sales Invoice", custom_ref, "customer_name") or 0
            dataa.append({
                "name": "",
                "supplier": "",
                "posting_date": "",
                "customer":customer,
                "custom_sales_invoice_reference": f" Total Sales Value",
                "bill_no": "",
                "bill_date": "",
                "expense_account": "",
                "amount": sales_total
            })
            dataa.append({
                "name": "",
                "supplier": "",
                "posting_date": "",
                "customer":customer,
                "custom_sales_invoice_reference": f"Gross Profit",
                "bill_no": "",
                "bill_date": "",
                "expense_account": "",
                "amount": sales_total - tot_amount - val
            })

    return columns, dataa



def get_columns(filters):
    return [
    	{'label': _('Sales Invoice Reference'), 'fieldtype': 'Data', 'fieldname': 'custom_sales_invoice_reference', 'width': 150},
    	{'label': _('Customer'), 'fieldtype': 'Data', 'fieldname': 'customer', 'width': 150},
        {'label': _('Purchase Invoice'), 'fieldtype': 'Data', 'fieldname': 'name', 'width': 150},
        {'label': _('Supplier'), 'fieldtype': 'Data', 'fieldname': 'supplier', 'width': 150},
        {'label': _('Date'), 'fieldtype': 'Date', 'fieldname': 'posting_date', 'width': 150},   
        {'label': _('Supplier Invoice No'), 'fieldtype': 'Data', 'fieldname': 'bill_no', 'width': 150},
        {'label': _('Supplier Invoice Date'), 'fieldtype': 'Date', 'fieldname': 'bill_date', 'width': 150},
        {'label': _('Item Name'), 'fieldtype': 'Data', 'fieldname': 'item_name', 'width': 250},
        {'label': _('Account'), 'fieldtype': 'Link', 'fieldname': 'expense_account', 'width': 200, 'options': 'Account'},
        {'label': _('Amount'), 'fieldtype': 'Currency', 'fieldname': 'amount', 'width': 150}
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
            pi.custom_sales_invoice_reference
        FROM
            `tabPurchase Invoice` pi
        LEFT JOIN
            `tabPurchase Invoice Item` pii ON pi.name = pii.parent
        WHERE
            pi.docstatus = 1 {conditions}
    """, filters, as_dict=True)

def get_conditions(filters):
    conditions = ""
    if filters.get("sales_invoice"):
        conditions += f" AND pi.custom_sales_invoice_reference = %(sales_invoice)s"
    return conditions
