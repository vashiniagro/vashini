// Copyright (c) 2026, Nxweb and contributors
// For license information, please see license.txt

frappe.query_reports["Sales P And L Test"] = {
	"filters": [
		{
			"fieldname":"sales_invoice",
			"label":__("Sales Invoice"),
			"fieldtype":"Link",
			"options":"Sales Invoice"
		},
		{
			"fieldname":"sales_person",
			"label":__("Sales Person"),
			"fieldtype":"Link",
			"options":"Sales Person"
		},
		{
			"fieldname":"customer",
			"label":__("Customer"),
			"fieldtype":"Link",
			"options":"Customer"
		}
	]
};
