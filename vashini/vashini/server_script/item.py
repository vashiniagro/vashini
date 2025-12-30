import re
import frappe

@frappe.whitelist()
def get_naming_series(item_group):
    # abbr = frappe.db.get_value("Item Group",{"name":item_group},["custom_abbr"])
    abbr = frappe.db.get_value("Item Group", {"name": item_group}, ["custom_abbr"])

    if abbr:
        abbrseries = abbr + "-" + "####"   # <-- Not used but fine

    # Get last item in this group
    data = frappe.get_all(
        "Item",
        filters={"item_group": item_group, "name": ["like", (abbr or '') + "%"]},
        fields=["name"],
        order_by="name desc",
        limit=1
    )

    if data:
        # Match FGD-0001 or FGD-001, etc.
        match = re.match(r"([A-Z]+-?)(\d+)$", data[0]["name"])
        if match:
            prefix = match.group(1)                  # e.g., "FGD-"
            num_part = match.group(2)                # e.g., "0001"
            new_number = str(int(num_part) + 1).zfill(len(num_part))  
            serial = prefix + new_number             # keeps original digit count
        else:
            serial = f"{abbr}-0001"
    else:
        serial = f"{abbr}-0001"

    return serial
