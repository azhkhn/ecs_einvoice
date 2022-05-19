# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    columns = get_columns()
    data = get_data(filters, columns)
    return columns, data


def get_columns():
    return [
        {
            "label": _("الفاتورة"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 170
        },
        {
            "label": _("التاريخ"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("اسم العميل"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 120
        },
        {
            "label": _("مجموعة العميل"),
            "fieldname": "customer_group",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("المنطقة"),
            "fieldname": "territory",
            "fieldtype": "Data",
            "width": 80
        },
        {
            "label": _("الاجمالي"),
            "fieldname": "total",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("اجمالي قيمة الضريبة"),
            "fieldname": "total_taxes_and_charges",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("قيمة الخصم"),
            "fieldname": "discount_amount",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("اجمالي المبلغ"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 100
        },

        {
            "label": _("UUID"),
            "fieldname": "uuid",
            "fieldtype": "Data",
            "width": 130
        },
        {
            "label": _("ETA Status"),
            "fieldname": "eta_status",
            "fieldtype": "Data",
            "width": 130
        },
		{
			"label": _("Item"),
			"fieldname": "item_code",
			"fieldtype": "Link",
            "options": "Item",
			"width": 130
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 130
		},
		{
			"label": _("ETA Item Type"),
			"fieldname": "eta_item_type",
			"fieldtype": "Data",
			"width": 130
		},
		{
			"label": _("ETA Item Code"),
			"fieldname": "eta_item_code",
			"fieldtype": "Data",
			"width": 130
		},
		{
			"label": _("Quantity"),
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 80
		},
		{
			"label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Data",
			"width": 80
		},
		{
			"label": _("Rate"),
			"fieldname": "rate",
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"label": _("Discount Amount"),
			"fieldname": "discount_amount",
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"label": _("Item Tax Template"),
			"fieldname": "item_tax_template",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Tax Code"),
			"fieldname": "tax_code",
			"fieldtype": "Data",
			"width": 90
		},
		{
			"label": _("Tax Subtype Code"),
			"fieldname": "tax_subtype_code",
			"fieldtype": "Data",
			"width": 150
		},
	]



def get_data(filters, columns):
    item_price_qty_data = []
    item_price_qty_data = get_item_price_qty_data(filters)
    return item_price_qty_data


def get_item_price_qty_data(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += " and `tabSales Invoice`.posting_date>=%(from_date)s"
    if filters.get("to_date"):
        conditions += " and `tabSales Invoice`.posting_date<=%(to_date)s"
    if filters.get("customer"):
        conditions += " and `tabSales Invoice`.customer=%(customer)s"
    if filters.get("customer_group"):
        conditions += " and `tabCustomer`.customer_group=%(customer_group)s"
    if filters.get("territory"):
        conditions += " and `tabSales Invoice`.territory=%(territory)s"
    if filters.get("e_invoice"):
        conditions += " and `tabSales Invoice`.e_invoice=%(e_invoice)s"

    result = []
    item_results = frappe.db.sql("""
				SELECT 
					`tabSales Invoice`.name as name,
					`tabSales Invoice`.e_invoice as e_invoice,
					`tabSales Invoice`.posting_date as posting_date,
					`tabSales Invoice`.customer as customer,
					`tabSales Invoice`.customer_group as customer_group,
					`tabSales Invoice`.territory as territory,
					`tabSales Invoice`.grand_total as grand_total,
					`tabSales Invoice`.total as total,
					`tabSales Invoice`.total_taxes_and_charges as total_taxes_and_charges,
					`tabSales Invoice`.discount_amount as discount_amount,
					`tabSales Invoice`.grand_total as grand_total,
					`tabSales Invoice`.uuid as uuid,
					`tabSales Invoice`.eta_status as eta_status,
					`tabSales Invoice Item`.item_code as item_code,
					`tabSales Invoice Item`.item_name as item_name,
					`tabSales Invoice Item`.eta_item_type as eta_item_type,
					`tabSales Invoice Item`.eta_item_code as eta_item_code,
					`tabSales Invoice Item`.qty as qty,
					`tabSales Invoice Item`.uom as uom,
					`tabSales Invoice Item`.rate as rate,
					`tabSales Invoice Item`.amount as amount,
					`tabSales Invoice Item`.item_tax_template as item_tax_template,
					`tabSales Invoice Item`.tax_code as tax_code,
					`tabSales Invoice Item`.tax_subtype_code as tax_subtype_code,
					`tabSales Invoice Item`.discount_amount as discount_amount

				FROM
					`tabSales Invoice` join `tabSales Invoice Item` on `tabSales Invoice`.name =`tabSales Invoice Item`.parent
				WHERE
					`tabSales Invoice`.docstatus = 1
					and `tabSales Invoice`.e_invoice = 1
					{conditions}

				ORDER BY `tabSales Invoice`.posting_date desc
				 """.format(conditions=conditions), filters, as_dict=1)

    if item_results:
        for item_dict in item_results:
            data = {
                'name': item_dict.name,
                'posting_date': item_dict.posting_date,
                'customer': item_dict.customer,
                'customer_group': item_dict.customer_group,
                'territory': item_dict.territory,
                'grand_total': item_dict.grand_total,
                'total': item_dict.total,
                'total_taxes_and_charges': item_dict.total_taxes_and_charges,
                'discount_amount': item_dict.discount_amount,
                'eta_status': item_dict.eta_status,
                'uuid': item_dict.uuid,
                'item_code': item_dict.item_code,
                'item_name': item_dict.item_name,
                'eta_item_type': item_dict.eta_item_type,
                'eta_item_code': item_dict.eta_item_code,
                'qty': item_dict.qty,
                'uom': item_dict.uom,
                'rate': item_dict.rate,
                'amount': item_dict.amount,
                'item_tax_template': item_dict.item_tax_template,
                'tax_code': item_dict.tax_code,
                'tax_subtype_code': item_dict.tax_subtype_code,
                'discount_amount': item_dict.discount_amount,
            }
            result.append(data)
    return result
