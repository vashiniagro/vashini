// Copyright (c) 2025, Nxweb and contributors
// For license information, please see license.txt

frappe.query_reports["Sales P And L"] = {
	"filters": [
		{
			"fieldname":"sales_invoice",
			"label":__("Sales Invoice"),
			"fieldtype":"Link",
			"width": "80",
			"options":"Sales Invoice"
		},
	]
};
