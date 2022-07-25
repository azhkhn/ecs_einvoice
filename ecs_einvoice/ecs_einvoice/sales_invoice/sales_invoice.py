from __future__ import unicode_literals
from re import A
import frappe
from frappe import auth
import datetime
import json, ast, requests, sys
from frappe.utils import money_in_words
import urllib.request
from datetime import datetime, timedelta
from json import dumps
import pytz
from frappe.utils import add_to_date
from time import sleep
import pickle



@frappe.whitelist()
def send_invoice(name):
    invoice = frappe.get_doc("Sales Invoice", name)
    enable = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'enable')
    generated_access_token = frappe.db.get_value('EInvoice Settings', {'company': invoice.company},
                                                        'generated_access_token')
    client_id = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'client_id')
    client_secret = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'client_secret')
    environment = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'environment')
    api_base_url = ""
    if environment == "Pre-Production":
        api_base_url = "https://api.preprod.invoicing.eta.gov.eg/api/v1/documentsubmissions"
    if environment == "Production":
        api_base_url = "https://api.invoicing.eta.gov.eg/api/v1/documentsubmissions"
    document_version = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'document_version')
    activity_code = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'activity_code')
    company_type = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'company_type')
    company = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'company_name')
    tax_id = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'tax_id')
    branch_id = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'branch_id')
    country = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'country')
    governate = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'governate')
    region_city = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'region_city')
    street = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'street')
    building_number = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'building_number')
    postal_code = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'postal_code')
    floor = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'floor')
    room = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'room')
    landmark = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'landmark')
    additional_info = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'additional_info')

    if enable == 1 and document_version == "v0.9":
        data = {}
        documents = []
        references = []
        temp = {}

        ## Enviroment
        temp["documentTypeVersion"] = "0.9"

        ## Document Type Invoice, Credit Note, Debit Note
        invoice = frappe.get_doc("Sales Invoice", name)
        if invoice.is_return == 0 and invoice.is_debit_note == 0:
            temp["documentType"] = "I"

        elif invoice.is_return == 1:
            temp["documentType"] = "C"
            references.append(str(invoice.against_uuid))
            temp["references"] = references

        elif invoice.is_debit_note == 1:
            temp["documentType"] = "D"
            references.append(str(invoice.against_uuid))
            temp["references"] = references


        ## activity Code
        temp["taxpayerActivityCode"] = activity_code

        # Invoice Data
        temp["internalID"] = name
        temp["dateTimeIssued"] = str(add_to_date(invoice.posting_date, days=0)) + "T00:00:01Z"
        temp["purchaseOrderReference"] = invoice.po_no
        temp["purchaseOrderDescription"] = str(invoice.po_date)
        temp["proformaInvoiceNumber"] = ""

        temp["issuer"] = {
            "address": {
                "branchID": branch_id,
                "country": country,
                "governate": governate,
                "regionCity": region_city,
                "street": street,
                "buildingNumber": building_number,
                "postalCode": postal_code,
                "floor": floor,
                "room": room,
                "landmark": landmark,
                "additionalInformation": additional_info
            },
            "type": company_type,
            "id": tax_id,
            "name": company
        }

        customer = frappe.get_doc("Customer", invoice.customer)
        if customer.customer_type == "Company":
            c_address = frappe.get_doc("Address", invoice.customer_address)
            customer_type = "B"
            temp["receiver"] = {
                "address": {
                    "country": c_address.county,
                    "governate": c_address.state,
                    "regionCity": c_address.city,
                    "street": c_address.address_line1,
                    "buildingNumber": c_address.building_number,
                    "postalCode": c_address.pincode,
                    "floor": c_address.floor,
                    "room": c_address.room,
                    "landmark": c_address.landmark,
                    "additionalInformation": c_address.additional_info
                },
                "type": customer_type,
                "id": customer.tax_id,
                "name": customer.customer_name
            }
        else:
            customer_type = "P"
            temp["receiver"] = {
                "address": {
                    "country": "",
                    "governate": "",
                    "regionCity": "",
                    "street": "",
                    "buildingNumber": "",
                    "postalCode": "",
                    "floor": "",
                    "room": "",
                    "landmark": "",
                    "additionalInformation": ""
                },
                "type": customer_type,
                "id": "",
                "name": customer.customer_name
            }

        invoiceLines = []
        for x in invoice.items:
            item_tax_rate = frappe.db.sql(
                """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                    parent=x.item_tax_template), as_dict=0)
            salesTotal = x.rate #+ x.discount_amount
            invoiceLines.append({
                "description": x.item_name,
                "itemType": x.eta_item_type,
                "itemCode": x.eta_item_code,
                "unitType": "EA",
                "quantity": x.qty,
                "internalCode": x.item_code,

                "salesTotal": round((salesTotal * x.qty), 5),
                "total": round(((x.rate + (x.rate * item_tax_rate[0][0] / 100)) * x.qty), 5),
                "valueDifference": 0.00,
                "totalTaxableFees": 0,
                "netTotal": round(x.amount, 5),
                "itemsDiscount": 0,#round((x.discount_amount * x.qty), 5),
                "unitValue": {
                    "currencySold": invoice.currency,
                    "amountEGP": round(salesTotal, 5)
                },
                "discount": {
                    "rate": 0,#round(x.discount_percentage, 5),
                    "amount": 0#round((x.discount_amount * x.qty), 5)
                },
                "taxableItems": [
                    {
                        "taxType": x.tax_code,
                        "amount": round((x.amount * item_tax_rate[0][0] / 100), 5),
                        "subType": x.tax_subtype_code,
                        "rate": item_tax_rate[0][0]
                    },
                ]
            })

        temp["invoiceLines"] = invoiceLines

        total_taxes = 0
        for y in invoice.items:
            item_tax_rate = frappe.db.sql(
                """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                    parent=y.item_tax_template), as_dict=0)
            total_taxes += round((y.amount * item_tax_rate[0][0] / 100), 5)

        ss = []

        tax_type = frappe.db.sql(
            """ select distinct tax_code, item_tax_template from `tabSales Invoice Item` where parent = '{parent}' """.format(
                parent=invoice.name), as_dict=1)

        for w in tax_type:
            tax = frappe.db.sql(
                """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                    parent=w.item_tax_template), as_dict=0)
            sum_tax = frappe.db.sql(
            """ select sum(amount) from `tabSales Invoice Item` where parent = '{parent}' and tax_code = '{tax_code}' """.format(
                parent=invoice.name, tax_code=w.tax_code), as_dict=0)

            new_tax = tax[0][0] * sum_tax[0][0] / 100
            ss.append({
                "taxType": w.tax_code,
                "amount": round(new_tax, 5)
            })

        temp["taxTotals"] = ss
        total_discount = 0
        net_amount = 0
        for z in invoice.items:
            total_discount += (z.discount_amount * z.qty)
            net_amount += round(z.amount, 5)

        temp["netAmount"] = round(net_amount, 5)
        temp["totalAmount"] = round(invoice.grand_total, 5)
        temp["totalDiscountAmount"] = 0#round(total_discount, 5)

        temp["extraDiscountAmount"] = round(invoice.discount_amount, 5)
        temp["totalItemsDiscountAmount"] = 0#round(total_discount, 5)

        new_total = 0
        for v in invoice.items:
            new_total += (v.qty * v.rate) #+ (v.qty * v.discount_amount)

        temp["totalSalesAmount"] = round(new_total, 5)

        if invoice.is_return == 1:
            invoiceLines = []
            for x in invoice.items:
                item_tax_rate = frappe.db.sql(
                    """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                        parent=x.item_tax_template), as_dict=0)
                salesTotal = x.rate #+ x.discount_amount
                invoiceLines.append({
                    "description": x.item_name,
                    "itemType": x.eta_item_type,
                    "itemCode": x.eta_item_code,
                    "unitType": "EA",
                    "quantity": x.qty * -1,
                    "internalCode": x.item_code,

                    "salesTotal": round((salesTotal * x.qty * -1), 5),
                    "total": round(((x.rate + (x.rate * item_tax_rate[0][0] / 100)) * x.qty * -1), 5),
                    "valueDifference": 0.00,
                    "totalTaxableFees": 0,
                    "netTotal": round(x.amount * -1, 5),
                    "itemsDiscount": 0,#round((x.discount_amount * x.qty), 5),
                    "unitValue": {
                        "currencySold": invoice.currency,
                        "amountEGP": round(salesTotal, 5)
                    },
                    "discount": {
                        "rate": 0, #round(x.discount_percentage, 5),
                        "amount": 0 #round((x.discount_amount * x.qty * -1), 5)
                    },
                    "taxableItems": [
                        {
                            "taxType": x.tax_code,
                            "amount": round((x.amount * -1 * item_tax_rate[0][0] / 100), 5),
                            "subType": x.tax_subtype_code,
                            "rate": item_tax_rate[0][0]
                        },
                    ]
                })

            temp["invoiceLines"] = invoiceLines

            total_taxes = 0
            for y in invoice.items:
                item_tax_rate = frappe.db.sql(
                    """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                        parent=y.item_tax_template), as_dict=0)
                total_taxes += round((y.amount * -1 * item_tax_rate[0][0] / 100), 5)

            ss = []

            tax_type = frappe.db.sql(
                """ select distinct tax_code, item_tax_template from `tabSales Invoice Item` where parent = '{parent}' """.format(
                    parent=invoice.name), as_dict=1)

            for w in tax_type:
                tax = frappe.db.sql(
                    """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                        parent=w.item_tax_template), as_dict=0)
                sum_tax = frappe.db.sql(
                """ select sum(amount) from `tabSales Invoice Item` where parent = '{parent}' and tax_code = '{tax_code}' """.format(
                    parent=invoice.name, tax_code=w.tax_code), as_dict=0)

                new_tax = -1 * tax[0][0] * sum_tax[0][0] / 100
                ss.append({
                    "taxType": w.tax_code,
                    "amount": round(new_tax, 5)
                })

            temp["taxTotals"] = ss
            total_discount = 0
            net_amount = 0
            for z in invoice.items:
                total_discount += (z.discount_amount * z.qty * -1)
                net_amount += round(z.amount * -1, 5)

            temp["netAmount"] = round(net_amount, 5)
            temp["totalAmount"] = round(invoice.grand_total * -1, 5)
            temp["totalDiscountAmount"] = 0 #round(total_discount, 5)

            temp["extraDiscountAmount"] = round(invoice.discount_amount * -1, 5)
            temp["totalItemsDiscountAmount"] = 0#round(total_discount, 5)

            new_total = 0
            for v in invoice.items:
                new_total += (v.qty * v.rate) #+ (v.qty * v.discount_amount)

            temp["totalSalesAmount"] = round(new_total * -1, 5)

        # Append temp dict into document list then assign document to data
        documents.append(temp)

        data['documents'] = documents
        headers = {'content-type': 'application/json;charset=utf-8',
                   "Authorization": "Bearer " + generated_access_token,
                   "Content-Length": "376"
                   }
        response = requests.post(api_base_url, data=json.dumps(data), headers=headers)
        sleep(4)
        frappe.msgprint(json.dumps(data))
        frappe.msgprint(response.content)
        returned_data = response.json()
        uuid_no = returned_data['acceptedDocuments'][0]['uuid']
        invoice.uuid = uuid_no
        invoice.save()
        get_invoice(name)

@frappe.whitelist(allow_guest=True)
def get_invoice(name):
    invoice = frappe.get_doc("Sales Invoice", name)
    generated_access_token = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'generated_access_token')
    environment = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'environment')
    api_document_url = ""
    if environment == "Pre-Production":
        api_document_url = "https://api.preprod.invoicing.eta.gov.eg/api/v1/documents/"
    if environment == "Production":
        api_document_url = "https://api.invoicing.eta.gov.eg/api/v1/documents/"
    headers = {'content-type': 'application/json',
                "Authorization": "Bearer " + generated_access_token,

                "Accept": "application/json"
                }

    url = api_document_url + invoice.uuid + "/raw"
    response = requests.get(url, params={"documentUUID": invoice.uuid}, headers=headers)
    sleep(3)
    returned_data = response.json()
    invoice.eta_status = returned_data['validationResults']['status']
    invoice.submission_uuid = returned_data['submissionUUID']
    invoice.long_id = returned_data['longId']
    if environment == "Pre-Production":
        invoice.eta_invoice_link = "https://preprod.invoicing.eta.gov.eg/print/documents/" + invoice.uuid + "/share/" + invoice.long_id
        invoice.eta_link = "https://preprod.invoicing.eta.gov.eg/documents/" + invoice.uuid + "/share/" + invoice.long_id
    if environment == "Production":
        invoice.eta_invoice_link = "https://invoicing.eta.gov.eg/print/documents/" + invoice.uuid + "/share/" + invoice.long_id
        invoice.eta_link = "https://invoicing.eta.gov.eg/documents/" + invoice.uuid + "/share/" + invoice.long_id
    invoice.save()
    user = frappe.session.user
    lang = frappe.db.get_value("User", {'name': user}, "language")
    if invoice.eta_status == "Valid":
        new_comment = frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": "Sales Invoice",
            "reference_name": invoice.name,
            "content": " تم ترحيل الفاتورة إلى نظام مصلحة الضرائب بنجاح ",
        })
        new_comment.insert(ignore_permissions=True)
        if lang == "ar":
            frappe.msgprint(" تم ترحيل الفاتورة إلى نظام مصلحة الضرائب بنجاح ")
        else:
            frappe.msgprint(" Invoice Has Been Submitted Successfully To ETA ")

    if invoice.eta_status == "Invalid":
        new_comment = frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": "Sales Invoice",
            "reference_name": invoice.name,
            "content": " حدث خطأ في ترحيل الفاتورة إلى نظام مصلحة الضرائب ",
        })
        new_comment.insert(ignore_permissions=True)
        if lang == "ar":
            frappe.msgprint(" حدث خطأ في ترحيل الفاتورة إلى نظام مصلحة الضرائب ")
        else:
            frappe.msgprint(" There Is A Problem In Submitting The Invoice To ETA ")

@frappe.whitelist(allow_guest=True)
def cancel_invoice(name):
    invoice = frappe.get_doc("Sales Invoice", name)
    generated_access_token = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'generated_access_token')
    environment = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'environment')
    url = ""
    if environment == "Pre-Production":
        url = "https://api.preprod.invoicing.eta.gov.eg/api/v1.0/documents/state/"+invoice.uuid+"/state"
    if environment == "Production":
        url = "https://api.invoicing.eta.gov.eg/api/v1.0/documents/state/"+invoice.uuid+"/state"
    new_comment = frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Comment",
        "reference_doctype": "Sales Invoice",
        "reference_name": invoice.name,
        "content": "تم إرسال طلب إلغاء الفاتورة إلى نظام مصلحة الضرائب بنجاح",
    })
    new_comment.insert(ignore_permissions=True)
    headers = {'content-type': 'application/json',
            "Authorization": "Bearer " + generated_access_token,

            "Accept": "*/*"
            }
    response = requests.put(url, json={"status":"cancelled","reason":"some reason for cancelled document"},params={"documentUUID": invoice.uuid}, headers=headers)
    user = frappe.session.user
    lang = frappe.db.get_value("User", {'name': user}, "language")
    if response.content:
        if lang == "ar":
            frappe.msgprint(" تم إرسال طلب إلغاء الفاتورة إلى نظام مصلحة الضرائب بنجاح ")
        else:
            frappe.msgprint(" Cancellation Request Has Been Sent Successfully To ETA ")

@frappe.whitelist(allow_guest=True)
def update_uuid_status():
    invoices = frappe.db.sql(""" select name as name from `tabSales Invoice` where e_invoice = 1 and docstatus = 1 and uuid is not null and eta_status != "Valid" """,as_dict=1)
    for x in invoices:
        name = x.name
        get_invoice(name)

@frappe.whitelist()
def list_invoices_for_signature():
    invoices = frappe.db.sql(
        """ select name, customer_name, posting_date, grand_total, discount_amount, owner
         from `tabSales Invoice`
         where docstatus = 1
         and document_version = "v1.0"
         and e_signed = 0 
         and e_invoice = 1
         order by name desc
          """, as_dict=1)

    results = {}
    invoice = []
    results["status"] = ""
    results["message"] = ""

    for x in invoices:
        invoice_data = {
            "ID": x.name,
            "DocumentNumber": x.name,
            "DocumentDate": str(x.posting_date),
            "InvoiceTotal": x.grand_total + x.discount_amount,
            "TotalAfterDiscount": x.grand_total,
            "LastUpdateBy": x.owner,
            "CustomerID_Text": x.customer_name,
        }
        invoice.append(invoice_data)
        results["data"] = invoice

    if results:
        return results

    else:
        return "No Invoices Found"

@frappe.whitelist()
def get_invoice_details(**kwargs):
    invoice = frappe.get_doc("Sales Invoice", kwargs['name'])
    activity_code = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'activity_code')
    company_type = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'company_type')
    company = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'company_name')
    tax_id = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'tax_id')
    branch_id = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'branch_id')
    country = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'country')
    governate = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'governate')
    region_city = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'region_city')
    street = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'street')
    building_number = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'building_number')
    postal_code = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'postal_code')
    floor = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'floor')
    room = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'room')
    landmark = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'landmark')
    additional_info = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'additional_info')

    data = {}
    documents = []
    references = []
    temp = {}

    temp["issuer"] = {
        "address": {
            "branchID": branch_id,
            "country": country,
            "governate": governate,
            "regionCity": region_city,
            "street": street,
            "buildingNumber": building_number,
            "postalCode": postal_code,
            "floor": floor,
            "room": room,
            "landmark": landmark,
            "additionalInformation": additional_info
        },
        "type": company_type,
        "id": tax_id,
        "name": company
    }
    customer = frappe.get_doc("Customer", invoice.customer)
    if customer.customer_type == "Company":
        c_address = frappe.get_doc("Address", invoice.customer_address)
        customer_type = "B"
        temp["receiver"] = {
            "address": {
                "country": c_address.county,
                "governate": c_address.state,
                "regionCity": c_address.city,
                "street": str(c_address.address_line1),
                "buildingNumber": c_address.building_number,
                "postalCode": c_address.pincode,
                "floor": c_address.floor,
                "room": c_address.room,
                "landmark": c_address.landmark,
                "additionalInformation": c_address.additional_info
            },
            "type": customer_type,
            "id": customer.tax_id,
            "name": customer.customer_name
        }
    else:
        customer_type = "P"
        temp["receiver"] = {
            "address": {
                "country": "",
                "governate": "",
                "regionCity": "",
                "street": "",
                "buildingNumber": "",
                "postalCode": "",
                "floor": "",
                "room": "",
                "landmark": "",
                "additionalInformation": ""
            },
            "type": customer_type,
            "id": "",
            "name": customer.customer_name
        }

    ## Document Type Invoice, Credit Note, Debit Note

    if invoice.is_return == 0 and invoice.is_debit_note == 0:
        temp["documentType"] = "I"

    elif invoice.is_return == 1:
        temp["documentType"] = "C"
        references.append(str(invoice.against_uuid))
        temp["references"] = references

    elif invoice.is_debit_note == 1:
        temp["documentType"] = "D"
        references.append(str(invoice.against_uuid))
        temp["references"] = references

    ## Enviroment
    temp["documentTypeVersion"] = "1.0"
    temp["dateTimeIssued"] = str(add_to_date(invoice.posting_date, days=0)) + "T00:00:01Z"

    ## activity Code
    temp["taxpayerActivityCode"] = activity_code

    # Invoice Data
    temp["internalID"] = kwargs['name']
    temp["purchaseOrderReference"] = invoice.po_no
    temp["purchaseOrderDescription"] = str(invoice.po_date)
    temp["salesOrderReference"] = ""
    temp["salesOrderDescription"] = ""
    temp["proformaInvoiceNumber"] = ""

    temp.update({"payment": {
        "bankName": "",
        "bankAddress": "",
        "bankAccountNo": "",
        "bankAccountIBAN": "",
        "swiftCode": "",
        "terms": ""
        },
    })

    temp.update({"delivery": {
        "approach": "",
        "packaging": "",
        "dateValidity": "",
        "exportPort": "",
        "countryOfOrigin": "EG",
        "grossWeight": 0,
        "netWeight": 0,
        "terms": ""
        },
    })

    invoiceLines = []
    for x in invoice.items:
        item_tax_rate = frappe.db.sql(
            """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                parent=x.item_tax_template), as_dict=0)
        salesTotal = x.rate #+ x.discount_amount
        invoiceLines.append({
            "description": x.item_name,
            "itemType": x.eta_item_type,
            "itemCode": x.eta_item_code,
            "unitType": "EA",
            "quantity": x.qty,
            "internalCode": x.item_code,

            "salesTotal": round((salesTotal * x.qty), 5),
            "total": round(((x.rate + (x.rate * item_tax_rate[0][0] / 100)) * x.qty), 5),
            "valueDifference": 0.00,
            "totalTaxableFees": 0,
            "netTotal": round(x.amount, 5),
            "itemsDiscount": 0,  # round((x.discount_amount * x.qty), 5),
            "unitValue": {
                "currencySold": invoice.currency,
                "amountEGP": round(salesTotal, 5),
                #"amountSold": round(salesTotal, 5),
                #"currencyExchangeRate": 1
            },
            "discount": {
                "rate": 0, #round(x.discount_percentage, 5),
                "amount": 0, #round((x.discount_amount * x.qty), 5)
            },
            "taxableItems": [
                {
                    "taxType": x.tax_code,
                    "amount": round((x.amount * item_tax_rate[0][0] / 100), 5),
                    "subType": x.tax_subtype_code,
                    "rate": item_tax_rate[0][0]
                },
            ]
        })

    temp["invoiceLines"] = invoiceLines

    total_discount = 0
    net_amount = 0
    for z in invoice.items:
        total_discount += (z.discount_amount * z.qty)
        net_amount += round(z.amount, 5)

    temp["totalDiscountAmount"] = 0 #round(total_discount, 5)
    new_total = 0
    for v in invoice.items:
        new_total += (v.qty * v.rate) #+ (v.qty * v.discount_amount)

    temp["totalSalesAmount"] = round(new_total, 5)

    temp["netAmount"] = round(net_amount, 5)

    total_taxes = 0
    for y in invoice.items:
        item_tax_rate = frappe.db.sql(
            """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                parent=y.item_tax_template), as_dict=0)
        total_taxes += round((y.amount * item_tax_rate[0][0] / 100), 5)

    ss = []

    tax_type = frappe.db.sql(
        """ select distinct tax_code, item_tax_template from `tabSales Invoice Item` where parent = '{parent}' """.format(
            parent=invoice.name), as_dict=1)

    for w in tax_type:
        tax = frappe.db.sql(
            """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                parent=w.item_tax_template), as_dict=0)
        sum_tax = frappe.db.sql(
            """ select sum(amount) from `tabSales Invoice Item` where parent = '{parent}' and tax_code = '{tax_code}' """.format(
                parent=invoice.name, tax_code=w.tax_code), as_dict=0)

        new_tax = tax[0][0] * sum_tax[0][0] / 100
        ss.append({
            "taxType": w.tax_code,
            "amount": round(new_tax, 5)
        })

    temp["taxTotals"] = ss

    temp["totalAmount"] = round(invoice.grand_total, 5)

    temp["extraDiscountAmount"] = round(invoice.discount_amount, 5)
    temp["totalItemsDiscountAmount"] = 0

    # Append temp dict into document list then assign document to data
    documents.append(temp)

    data['documents'] = documents

    return documents

@frappe.whitelist()
def receive_signature(name, signature, signed_json):
    invoice = frappe.get_doc("Sales Invoice", name)
    generated_access_token = frappe.db.get_value('EInvoice Settings', {'company': invoice.company},
                                                 'generated_access_token')
    environment = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'environment')
    api_base_url = ""
    if environment == "Pre-Production":
        api_base_url = "https://api.preprod.invoicing.eta.gov.eg/api/v1/documentsubmissions"
    if environment == "Production":
        api_base_url = "https://api.invoicing.eta.gov.eg/api/v1/documentsubmissions"
    invoice.e_signed = 1
    invoice.json = signed_json
    invoice.save()

    '''
    headers = {'content-type': 'application/json;charset=utf-8',
               "Authorization": "Bearer " + generated_access_token,
               "Content-Length": "376"}

    response = requests.post(url=api_base_url, data=signed_json.encode('utf-8'), headers=headers)
    sleep(5)
    returned_data = response.json()
    uuid_no = returned_data['acceptedDocuments'][0]['uuid']
    invoice.uuid = uuid_no
    invoice.save()
    get_invoice(name)
    '''
    if invoice.e_signed == 1:
        response = {
            "status": "200",
            "message": "success message",
            "data": [
            ]
        }
        return response
    else:
        response = {
            "status": "500",
            "message": "failed message",
            "data": [
            ]
        }
        return response

@frappe.whitelist(allow_guest=True)
def pdf(name):
    invoice = frappe.get_doc("Sales Invoice", name)
    generated_access_token = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'generated_access_token')
    internal_user_key = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'internal_user_key')
    internal_user_secret = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'internal_user_secret')
    internal_url = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'internal_url')
    url = "https://api.preprod.invoicing.eta.gov.eg/api/v1.0/documents/"+invoice.uuid+"/pdf"
    headers = {"Authorization": "Bearer " + generated_access_token,
                "Accept": "*/*"
                }
    response = requests.get(url,params={"documentUUID": invoice.uuid}, headers=headers, allow_redirects=True, stream=True)
    #file = open('facebook.pdf', 'wb').write(response.content)
    #file = open(response, "rb")
    #data = response.json()
    #file.write(response.content)
    #invoice.rem = file.write(response.content)
    #invoice.save()
    frappe.msgprint(response.status_code)

    ###
    headers2 = {"Authorization": "token " + internal_user_key + ":" +internal_user_secret,
                "Content-Type" : "application/x-www-form-urlencoded",
                "Accept": "*/*"
                }
    response2 = requests.post(internal_url,data={
        "doctype": "Sales Invoice",
        "docname": invoice.name,
        "filename": invoice.uuid + ".pdf",
        "filedata": file,
        "decode_base64": 1
        }, headers=headers2)
    frappe.msgprint(response2.content)





