from __future__ import unicode_literals
import frappe
from frappe import auth
import datetime
import json, ast
from frappe import utils
from frappe.utils import add_to_date
import json, ast, requests
from datetime import datetime, timedelta
from ecs_einvoice.ecs_einvoice.sales_invoice.sales_invoice import send_invoice, cancel_invoice, get_invoice
from time import sleep


################ Quotation

@frappe.whitelist()
def quot_onload(doc, method=None):
    pass


@frappe.whitelist()
def quot_before_insert(doc, method=None):
    pass


@frappe.whitelist()
def quot_after_insert(doc, method=None):
    pass


@frappe.whitelist()
def quot_before_validate(doc, method=None):
    pass


@frappe.whitelist()
def quot_validate(doc, method=None):
    pass


@frappe.whitelist()
def quot_on_submit(doc, method=None):
    pass


@frappe.whitelist()
def quot_on_cancel(doc, method=None):
    pass


@frappe.whitelist()
def quot_on_update_after_submit(doc, method=None):
    pass


@frappe.whitelist()
def quot_before_save(doc, method=None):
    pass


@frappe.whitelist()
def quot_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def quot_on_update(doc, method=None):
    pass


################ Sales Order


@frappe.whitelist()
def so_onload(doc, method=None):
    pass


@frappe.whitelist()
def so_before_insert(doc, method=None):
    pass


@frappe.whitelist()
def so_after_insert(doc, method=None):
    pass


@frappe.whitelist()
def so_before_validate(doc, method=None):
    pass


@frappe.whitelist()
def so_validate(doc, method=None):
    pass


@frappe.whitelist()
def so_on_submit(doc, method=None):
    pass


@frappe.whitelist()
def so_on_cancel(doc, method=None):
    pass


@frappe.whitelist()
def so_on_update_after_submit(doc, method=None):
    pass


@frappe.whitelist()
def so_before_save(doc, method=None):
    pass


@frappe.whitelist()
def so_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def so_on_update(doc, method=None):
    pass


################ Delivery Note

@frappe.whitelist()
def dn_onload(doc, method=None):
    pass


@frappe.whitelist()
def dn_before_insert(doc, method=None):
    pass


@frappe.whitelist()
def dn_after_insert(doc, method=None):
    pass


@frappe.whitelist()
def dn_before_validate(doc, method=None):
    pass


@frappe.whitelist()
def dn_validate(doc, method=None):
    pass


@frappe.whitelist()
def dn_on_submit(doc, method=None):
    pass


@frappe.whitelist()
def dn_on_cancel(doc, method=None):
    pass


@frappe.whitelist()
def dn_on_update_after_submit(doc, method=None):
    pass


@frappe.whitelist()
def dn_before_save(doc, method=None):
    pass


@frappe.whitelist()
def dn_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def dn_on_update(doc, method=None):
    pass


################ Sales Invoice

@frappe.whitelist()
def siv_onload(doc, method=None):
    pass

@frappe.whitelist()
def siv_before_insert(doc, method=None):
    enable = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'enable')
    signature_type = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'signature_type')
    doc.e_invoice = enable
    doc.signature_type = signature_type
    doc.against_uuid = ""
    doc.sign = 0
    doc.e_signed = 0
    doc.signature = ""
    doc.uuid = ""
    doc.eta_status = ""
    doc.submission_uuid = ""
    doc.long_id = ""
    doc.eta_link = ""
    doc.eta_invoice_link = ""

@frappe.whitelist()
def siv_after_insert(doc, method=None):
    pass
@frappe.whitelist()
def siv_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def siv_validate(doc, method=None):
    for x in doc.items:
        x.tax_code = frappe.db.get_value("Item Tax Template", x.item_tax_template, "tax_code")
        x.tax_subtype_code = frappe.db.get_value("Item Tax Template", x.item_tax_template, "tax_subtype_code")
    enable = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'enable')
    signature_type = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'signature_type')
    doc.e_invoice = enable
    doc.signature_type = signature_type

@frappe.whitelist()
def siv_on_submit(doc, method=None):
    enable = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'enable')
    if enable == 1:
        posting_date = doc.posting_date
        allowed_days = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'allowed_days')
        if posting_date < add_to_date(utils.today(), days=-(allowed_days), as_string=True):
            frappe.throw(
                "You are allowed only to submit past dated invoices for {0} days before today".format(allowed_days))
    '''
    linking_with_eta = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'linking_with_eta')
    enable = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'enable')
    if linking_with_eta == "Automatically" and enable == 1:
        name = doc.name
        send_invoice(name)
        sleep(1)
        get_invoice(name)
        doc.reload()
    

    user = frappe.session.user
    lang = frappe.db.get_value("User", {'name': user}, "language")
    if doc.eta_status != "Invalid":
        if lang == "ar":
            frappe.msgprint(" تم ترحيل الفاتورة إلى نظام مصلحة الضرائب بنجاح ")
        else:
            frappe.msgprint(" Invoice Has Been Submitted Successfully To ETA ")

    if doc.eta_status == "Invalid":
        if lang == "ar":
            frappe.msgprint(" حدث خطأ في ترحيل الفاتورة إلى نظام مصلحة الضرائب ")
        else:
            frappe.msgprint(" There Is A Problem In Submitting The Invoice To ETA ")
    '''

@frappe.whitelist()
def siv_on_cancel(doc, method=None):
    pass
    '''
    linking_with_eta = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'linking_with_eta')
    enable = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'enable')
    if linking_with_eta == "Automatically" and enable == 1:
        name = doc.name
        cancel_invoice(name)
    '''


@frappe.whitelist()
def siv_on_update_after_submit(doc, method=None):
    '''
    linking_with_eta = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'linking_with_eta')
    if linking_with_eta == "Manually" and doc.send_to_eta_1 == 1:
        name = doc.name
        send_invoice(name)
        sleep(1)
        get_invoice(name)
        doc.reload()
    '''
    pass


@frappe.whitelist()
def siv_before_save(doc, method=None):
    pass


@frappe.whitelist()
def siv_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def siv_on_update(doc, method=None):
    pass


################ Payment Entry

@frappe.whitelist()
def pe_onload(doc, method=None):
    pass


@frappe.whitelist()
def pe_before_insert(doc, method=None):
    pass


@frappe.whitelist()
def pe_after_insert(doc, method=None):
    pass


def pe_before_validate(doc, method=None):
    pass


@frappe.whitelist()
def pe_validate(doc, method=None):
    pass


@frappe.whitelist()
def pe_on_submit(doc, method=None):
    pass


@frappe.whitelist()
def pe_on_cancel(doc, method=None):
    pass


@frappe.whitelist()
def pe_on_update_after_submit(doc, method=None):
    pass


@frappe.whitelist()
def pe_before_save(doc, method=None):
    pass


@frappe.whitelist()
def pe_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def pe_on_update(doc, method=None):
    pass


################ Material Request

@frappe.whitelist()
def mr_onload(doc, method=None):
    pass


@frappe.whitelist()
def mr_before_insert(doc, method=None):
    pass


@frappe.whitelist()
def mr_after_insert(doc, method=None):
    pass


@frappe.whitelist()
def mr_before_validate(doc, method=None):
    pass


@frappe.whitelist()
def pe_after_insert(doc, method=None):
    pass


@frappe.whitelist()
def mr_validate(doc, method=None):
    pass


@frappe.whitelist()
def mr_on_submit(doc, method=None):
    pass


@frappe.whitelist()
def mr_on_cancel(doc, method=None):
    pass


@frappe.whitelist()
def mr_on_update_after_submit(doc, method=None):
    pass


@frappe.whitelist()
def mr_before_save(doc, method=None):
    pass


@frappe.whitelist()
def mr_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def mr_on_update(doc, method=None):
    pass


################ Purchase Order

@frappe.whitelist()
def po_onload(doc, method=None):
    pass


@frappe.whitelist()
def po_before_insert(doc, method=None):
    pass


@frappe.whitelist()
def po_after_insert(doc, method=None):
    pass


@frappe.whitelist()
def po_before_validate(doc, method=None):
    pass


@frappe.whitelist()
def po_validate(doc, method=None):
    pass


@frappe.whitelist()
def po_on_submit(doc, method=None):
    pass


@frappe.whitelist()
def po_on_cancel(doc, method=None):
    pass


@frappe.whitelist()
def po_on_update_after_submit(doc, method=None):
    pass


@frappe.whitelist()
def po_before_save(doc, method=None):
    pass


@frappe.whitelist()
def po_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def po_on_update(doc, method=None):
    pass


################ Purchase Receipt

@frappe.whitelist()
def pr_onload(doc, method=None):
    pass


@frappe.whitelist()
def pr_before_insert(doc, method=None):
    pass


@frappe.whitelist()
def pr_after_insert(doc, method=None):
    pass


@frappe.whitelist()
def pr_before_validate(doc, method=None):
    pass


@frappe.whitelist()
def pr_validate(doc, method=None):
    pass


@frappe.whitelist()
def pr_on_submit(doc, method=None):
    pass


@frappe.whitelist()
def pr_on_cancel(doc, method=None):
    pass


@frappe.whitelist()
def pr_on_update_after_submit(doc, method=None):
    pass


@frappe.whitelist()
def pr_before_save(doc, method=None):
    pass


@frappe.whitelist()
def pr_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def pr_on_update(doc, method=None):
    pass


################ Purchase Invoice

@frappe.whitelist()
def piv_onload(doc, method=None):
    pass


@frappe.whitelist()
def piv_before_insert(doc, method=None):
    pass


@frappe.whitelist()
def piv_after_insert(doc, method=None):
    pass


@frappe.whitelist()
def piv_before_validate(doc, method=None):
    pass


@frappe.whitelist()
def piv_validate(doc, method=None):
    pass


@frappe.whitelist()
def piv_on_submit(doc, method=None):
    pass


@frappe.whitelist()
def piv_on_cancel(doc, method=None):
    pass


@frappe.whitelist()
def piv_on_update_after_submit(doc, method=None):
    pass


@frappe.whitelist()
def piv_before_save(doc, method=None):
    pass


@frappe.whitelist()
def piv_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def piv_on_update(doc, method=None):
    pass


################ Employee Advance

@frappe.whitelist()
def emad_onload(doc, method=None):
    pass


@frappe.whitelist()
def emad_before_insert(doc, method=None):
    pass


@frappe.whitelist()
def emad_after_insert(doc, method=None):
    pass


@frappe.whitelist()
def emad_before_validate(doc, method=None):
    pass


@frappe.whitelist()
def emad_validate(doc, method=None):
    pass


@frappe.whitelist()
def emad_on_submit(doc, method=None):
    pass


@frappe.whitelist()
def emad_on_cancel(doc, method=None):
    pass


@frappe.whitelist()
def emad_on_update_after_submit(doc, method=None):
    pass


@frappe.whitelist()
def emad_before_save(doc, method=None):
    pass


@frappe.whitelist()
def emad_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def emad_on_update(doc, method=None):
    pass


################ Expense Claim

@frappe.whitelist()
def excl_onload(doc, method=None):
    pass


@frappe.whitelist()
def excl_before_insert(doc, method=None):
    pass


@frappe.whitelist()
def excl_after_insert(doc, method=None):
    pass


@frappe.whitelist()
def excl_before_validate(doc, method=None):
    pass


@frappe.whitelist()
def excl_validate(doc, method=None):
    pass


@frappe.whitelist()
def excl_on_submit(doc, method=None):
    pass


@frappe.whitelist()
def excl_on_cancel(doc, method=None):
    pass


@frappe.whitelist()
def excl_on_update_after_submit(doc, method=None):
    pass


@frappe.whitelist()
def excl_before_save(doc, method=None):
    pass


@frappe.whitelist()
def excl_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def excl_on_update(doc, method=None):
    pass


################ Stock Entry

@frappe.whitelist()
def ste_onload(doc, method=None):
    pass


@frappe.whitelist()
def ste_before_insert(doc, method=None):
    pass


@frappe.whitelist()
def ste_after_insert(doc, method=None):
    pass


@frappe.whitelist()
def ste_before_validate(doc, method=None):
    pass


@frappe.whitelist()
def ste_validate(doc, method=None):
    pass


@frappe.whitelist()
def ste_on_submit(doc, method=None):
    pass


@frappe.whitelist()
def ste_on_cancel(doc, method=None):
    pass


@frappe.whitelist()
def ste_on_update_after_submit(doc, method=None):
    pass


@frappe.whitelist()
def ste_before_save(doc, method=None):
    pass


@frappe.whitelist()
def ste_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def ste_on_update(doc, method=None):
    pass


################ Blanket Order

@frappe.whitelist()
def blank_onload(doc, method=None):
    pass


@frappe.whitelist()
def blank_before_insert(doc, method=None):
    pass


@frappe.whitelist()
def blank_after_insert(doc, method=None):
    pass


@frappe.whitelist()
def blank_before_validate(doc, method=None):
    pass


@frappe.whitelist()
def blank_validate(doc, method=None):
    pass


@frappe.whitelist()
def blank_on_submit(doc, method=None):
    pass


@frappe.whitelist()
def blank_on_cancel(doc, method=None):
    pass


@frappe.whitelist()
def blank_on_update_after_submit(doc, method=None):
    pass


@frappe.whitelist()
def blank_before_save(doc, method=None):
    pass


@frappe.whitelist()
def blank_before_cancel(doc, method=None):
    pass


@frappe.whitelist()
def blank_on_update(doc, method=None):
    pass


################ Item

@frappe.whitelist()
def item_onload(doc, method=None):
    pass


@frappe.whitelist()
def item_before_insert(doc, method=None):
    doc.eta_item = ""
    doc.eta_item_code = ""
    doc.eta_item_type = ""

@frappe.whitelist()
def item_after_insert(doc, method=None):
    pass

@frappe.whitelist()
def item_before_validate(doc, method=None):
    pass

@frappe.whitelist()
def item_validate(doc, method=None):
    pass

@frappe.whitelist()
def item_before_save(doc, method=None):
    pass

@frappe.whitelist()
def item_on_update(doc, method=None):
    generated_access_token = frappe.db.get_value('EInvoice Settings', {'company': doc.company},
                                                 'generated_access_token')
    tax_id = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'tax_id')
    category_code = frappe.db.get_value('EInvoice Settings', {'company': doc.company}, 'category_code')

    if not tax_id:
        frappe.throw(" Please Add The Tax ID In The E-Invoice Settings For Company " + str(doc.company))

    if not category_code:
        frappe.throw(" Please Add The Category Code In The E-Invoice Settings For Company " + str(doc.company))

    if doc.eta_item and not doc.eta_item_type:
        frappe.throw(" Please Select ETA Item Type For Item " + str(doc.name))

    if doc.eta_item and not doc.eta_item_code:
        data = {}
        items = [
            {
                "codeType": doc.eta_item_type,
                "parentCode": category_code,
                "itemCode": "EG-" + str(tax_id) + "-" + str(doc.item_code.replace('-', '')),
                "codeName": doc.item_name,
                "codeNameAr": doc.item_name,
                "activeFrom": "2022-01-01T00:00:00.000",
                "description": doc.description,
                "descriptionAr": doc.description,
                "requestReason": "Request reason text"
            }
        ]
        data["items"] = items
        headers = {'content-type': 'application/json;charset=utf-8',
                   "Authorization": "Bearer " + generated_access_token,
                   "Content-Length": "376"
                   }
        response = requests.post(url="https://api.preprod.invoicing.eta.gov.eg/api/v1.0/codetypes/requests/codes",
                                 data=json.dumps(data), headers=headers)
        frappe.msgprint(json.dumps(data))
        frappe.msgprint(response.content)
        returned_data = response.json()
        doc.eta_item_code = returned_data['passedItems'][0]['itemCode']
        doc.save()
        doc.reload()


@frappe.whitelist()
def get_item_status(name):
    item = frappe.get_doc("Item", name)

    generated_access_token = frappe.db.get_value('EInvoice Settings', {'company': item.company}, 'generated_access_token')

    headers = {'content-type': 'application/json;charset=utf-8',
               "Authorization": "Bearer " + generated_access_token,
               "Content-Length": "376"
               }

    url = "https://api.preprod.invoicing.eta.gov.eg/api/v1.0/codetypes/requests/my?ItemCode=" + str(item.eta_item_code)

    response = requests.get(url=url, headers=headers)
    frappe.msgprint(response.content)

