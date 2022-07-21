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
            "width": 130
        },
        {
            "label": _("التاريخ"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("الحالة"),
            "fieldname": "docstatus",
            "fieldtype": "Data",
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
            "width": 90
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
            "label": _("Version"),
            "fieldname": "document_version",
            "fieldtype": "Data",
            "width": 90
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
					`tabSales Invoice`.docstatus as docstatus,
					`tabSales Invoice`.posting_date as posting_date,
					`tabSales Invoice`.customer as customer,
					`tabSales Invoice`.customer_group as customer_group,
					`tabSales Invoice`.territory as territory,
					`tabSales Invoice`.grand_total as grand_total,
					`tabSales Invoice`.total as total,
					`tabSales Invoice`.total_taxes_and_charges as total_taxes_and_charges,
					`tabSales Invoice`.discount_amount as discount_amount,
					`tabSales Invoice`.grand_total as grand_total,
					`tabSales Invoice`.document_version as document_version,
					`tabSales Invoice`.uuid as uuid,
					`tabSales Invoice`.eta_status as eta_status


				FROM
					`tabSales Invoice`
				WHERE
					`tabSales Invoice`.uuid != ""
					and `tabSales Invoice`.e_invoice = 1
					{conditions}

				ORDER BY `tabSales Invoice`.posting_date desc
				 """.format(conditions=conditions), filters, as_dict=1)

    if item_results:
        docstatus = ""
        for item_dict in item_results:
            if item_dict.docstatus == 0:
                docstatus = "Draft"
            if item_dict.docstatus == 1:
                docstatus = "Submitted"
            if item_dict.docstatus == 2:
                docstatus = "Cancelled"
            data = {
                'name': item_dict.name,
                'posting_date': item_dict.posting_date,
                'docstatus': docstatus,
                'customer': item_dict.customer,
                'customer_group': item_dict.customer_group,
                'territory': item_dict.territory,
                'grand_total': item_dict.grand_total,
                'total': item_dict.total,
                'total_taxes_and_charges': item_dict.total_taxes_and_charges,
                'discount_amount': item_dict.discount_amount,
                'document_version': item_dict.document_version,
                'eta_status': item_dict.eta_status,
                'uuid': item_dict.uuid,
            }
            result.append(data)
    return result
