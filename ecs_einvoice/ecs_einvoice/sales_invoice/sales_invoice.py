from __future__ import unicode_literals
from re import A
import frappe
from frappe import auth
import datetime
import json, ast, requests
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
    s_invoice = frappe.get_doc("Sales Invoice", name)
    enable = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'enable')
    if enable == 1 and not s_invoice.uuid:
        api_base_url = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'api_base_url')
        api_document_url = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company},
                                                      'api_document_url')
        id_server_base_url = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company},
                                                        'id_server_base_url')
        client_id = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'client_id')
        client_secret = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'client_secret')
        generated_access_token = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company},
                                                            'generated_access_token')
        environment = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'environment')
        signature_type = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'signature_type')
        activity_code = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'activity_code')
        company_type = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'company_type')
        company = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'company_name')
        tax_id = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'tax_id')
        branch_id = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'branch_id')
        country = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'country')
        governate = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'governate')
        region_city = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'region_city')
        street = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'street')
        building_number = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'building_number')
        postal_code = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'postal_code')
        floor = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'floor')
        room = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'room')
        landmark = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'landmark')
        additional_info = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'additional_info')

        data = {}
        documents = []
        references = []
        temp = {}

        ## Enviroment
        if signature_type == "Without Signature":
            documentTypeVersion = "0.9"
        else:
            documentTypeVersion = "1.0"
        temp["documentTypeVersion"] = documentTypeVersion

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
        invoice = frappe.get_doc("Sales Invoice", name)
        temp["internalID"] = name
        #temp["dateTimeIssued"] = invoice.posting_date.strftime('%Y-%m-%dT%H:%M:%SZ') #str(invoice.posting_date) + "T" + str(invoice.posting_time + timedelta(hours=-2)) + "Z"

        # 2015-02-13T13:15:00Z#
        # "2022-03-11T02:04:45Z"#str(invoice.creation)

        compared_time = "12:00:00.0"
        #issued_time = datetime(invoice.posting_time)
        #issued_time1 = str(invoice.posting_time)
        #if datetime.strptime(issued_time1, '%H:%M:%S.%f') < datetime.strptime(compared_time, '%H:%M:%S.%f'):
        #    temp["dateTimeIssued"] = str(add_to_date(invoice.posting_date, days=0)) + "T0" + datetime.strptime(issued_time, '%H:%M:%S')+ "Z"
        #else:
        temp["dateTimeIssued"] = str(add_to_date(invoice.posting_date, days=0)) + "T" +  datetime.now().strftime("%H:%M:%S") + "Z"

        temp["purchaseOrderReference"] = invoice.po_no
        temp["purchaseOrderDescription"] = str(invoice.po_date)
        # so = frappe.db.sql(""" select sales_order from `tabSales Invoice Item` where parent = '{parent}'  """.format(parent=invoice.name),as_dict=0)
        # if so :
        #    temp["salesOrderReference"] = so[0][0]
        #    so_detail = frappe.get_doc("Sales Order", so[0][0])
        #    temp["salesOrderDescription"] = str(so_detail.transaction_date)
        temp["proformaInvoiceNumber"] = "Null"
        """
        temp["signatures"] = [
            {
                "signatureType": "I",
                "value": "MIIGywYJKoZIhvcNAQcCoIIGvDCCBrgCAQMxDTALBglghkgBZQMEAgEwCwYJKoZIhvcNAQcFoIID/zCCA/swggLjoAMCAQICEEFkOqRVlVar0F0n3FZOLiIwDQYJKoZIhvcNAQELBQAwSTELMAkGA1UEBhMCRUcxFDASBgNVBAoTC0VneXB0IFRydXN0MSQwIgYDVQQDExtFZ3lwdCBUcnVzdCBDb3Jwb3JhdGUgQ0EgRzIwHhcNMjAwMzMxMDAwMDAwWhcNMjEwMzMwMjM1OTU5WjBgMRUwEwYDVQQKFAxFZ3lwdCBUcnVzdCAxGDAWBgNVBGEUD1ZBVEVHLTExMzMxNzcxMzELMAkGA1UEBhMCRUcxIDAeBgNVBAMMF1Rlc3QgU2VhbGluZyBEZW1vIHVzZXIyMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApmVGVJtpImeq\u002BtIJiVWSkIEEOTIcnG1XNYQOYtf5\u002BDg9eF5H5x1wkgR2G7dvWVXrTsdNv2Q\u002Bgvml9SdfWxlYxaljg2AuBrsHFjYVEAQFI37EW2K7tbMT7bfxwT1M5tbjxnkTTK12cgwxPr2LBNhHpfXp8SNyWCxpk6eyJb87DveVwCLbAGGXO9mhDj62glVTrCFit7mHC6bZ6MOMAp013B8No9c8xnrKQiOb4Tm2GxBYHFwEcfYUGZNltGZNdVUtu6ty\u002BNTrSRRC/dILeGHgz6/2pgQPk5OFYRTRHRNVNo\u002BjG\u002BnurUYkSWxA4I9CmsVt2FdeBeuvRFs/U1I\u002BieKg1wIDAQABo4HHMIHEMAkGA1UdEwQCMAAwVAYDVR0fBE0wSzBJoEegRYZDaHR0cDovL21wa2ljcmwuZWd5cHR0cnVzdC5jb20vRWd5cHRUcnVzdENvcnBvcmF0ZUNBRzIvTGF0ZXN0Q1JMLmNybDAdBgNVHQ4EFgQUqzFDImtytsUbghbmtnl2/k4d5jEwEQYJYIZIAYb4QgEBBAQDAgeAMB8GA1UdIwQYMBaAFCInP8ziUIPmu86XJUWXspKN3LsFMA4GA1UdDwEB/wQEAwIGwDANBgkqhkiG9w0BAQsFAAOCAQEAxE3KpyYlPy/e3\u002B6jfz5RqlLhRLppWpRlKYUvH1uIhCNRuWaYYRchw1xe3jn7bLKbNrUmey\u002BMRwp1hZptkxFMYKTIEnNjOKCrLmVIuPFcfLXAQFq5vgLDSbnUhG/r5D\u002B50ndPucyUPhX3gw8gFlA1R\u002BtdNEoeKqYSo9v3p5qNANq12OuZbkhPg6sAD4dojWoNdlkc8J2ML0eq4a5AQvb4yZVb\u002BezqJyqKj83RekRZi0kMxoIm8l82CN8I/Bmp6VVNJRhQKhSeb7ShpdkZcMwcfKdDw6LW02/XcmzVl8NBBbLjKSJ/jxdL1RxPPza7RbGqSx9pfyav5\u002BAxO9sXnXXc5jGCApIwggKOAgEBMF0wSTELMAkGA1UEBhMCRUcxFDASBgNVBAoTC0VneXB0IFRydXN0MSQwIgYDVQQDExtFZ3lwdCBUcnVzdCBDb3Jwb3JhdGUgQ0EgRzICEEFkOqRVlVar0F0n3FZOLiIwCwYJYIZIAWUDBAIBoIIBCjAYBgkqhkiG9w0BCQMxCwYJKoZIhvcNAQcFMBwGCSqGSIb3DQEJBTEPFw0yMTAyMDEyMzUwMjFaMC8GCSqGSIb3DQEJBDEiBCD5bGXJu9uJZIPMGXK98UrHzJM/V2U/WAO6BErxpX5wdTCBngYLKoZIhvcNAQkQAi8xgY4wgYswgYgwgYUEIAJA8uO/ek3l9i3ZOgRtPhGWwwFYljbeJ7yAgEnyYNCWMGEwTaBLMEkxCzAJBgNVBAYTAkVHMRQwEgYDVQQKEwtFZ3lwdCBUcnVzdDEkMCIGA1UEAxMbRWd5cHQgVHJ1c3QgQ29ycG9yYXRlIENBIEcyAhBBZDqkVZVWq9BdJ9xWTi4iMAsGCSqGSIb3DQEBAQSCAQB13E1WX\u002BzbWppfJi3DBK9MMSB1TXuxcNkGXQ19OcRUUAaAe2K\u002BisobYrUCZbi3ygc2AWOMyafboxjjomzrnvXKrFgspT4wAFPYaAGFzKWq\u002BW/nqMhIqJVIpS/NM7Al4HvuBA5iGuZEQFusElB0yIxOIiYDI4v8Ilkff4/duj/V2CNaN5cqXLOpL5RP6Y5i\u002BVsPGb89t/L0dSIldGN0JqaqarqYo5/RwsUFJJq01DFpPGNbOIX3gSCDmycfhJPS9csnne9Zt\u002BabNpja5ZR6KA8JMe4DHes7FDZqHBNHdC\u002BRDXT4crqmnyiJjizULu6MqDc0Fv3vrMMWDLRlwDecgq7i"
            }
        ]
        """
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
        c_address = frappe.get_doc("Address", invoice.customer_address)
        customer = frappe.get_doc("Customer", invoice.customer)
        if customer.customer_type == "Company":
            customer_type = "B"
        else:
            customer_type = "A"
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

        invoiceLines = []
        for x in invoice.items:
            item_tax_rate = frappe.db.sql(
                """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                    parent=x.item_tax_template), as_dict=0)
            salesTotal = x.rate + x.discount_amount
            invoiceLines.append({
                "description": x.item_name,
                "itemType": x.eta_item_type,
                "itemCode": x.eta_item_code,
                "unitType": x.uom,
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
                    "rate": round(x.discount_percentage, 5),
                    "amount": round((x.discount_amount * x.qty), 5)
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

        temp["netAmount"] = net_amount
        temp["totalAmount"] = round(invoice.grand_total, 5)
        temp["totalDiscountAmount"] = round(total_discount, 5)

        temp["extraDiscountAmount"] = round(invoice.discount_amount, 5)
        temp["totalItemsDiscountAmount"] = 0#round(total_discount, 5)

        new_total = 0
        for v in invoice.items:
            new_total += (v.qty * v.rate) + (v.qty * v.discount_amount)

        temp["totalSalesAmount"] = round(new_total, 5)

        if invoice.is_return == 1:
            invoiceLines = []
            for x in invoice.items:
                item_tax_rate = frappe.db.sql(
                    """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                        parent=x.item_tax_template), as_dict=0)
                salesTotal = x.rate + x.discount_amount
                invoiceLines.append({
                    "description": x.item_name,
                    "itemType": x.eta_item_type,
                    "itemCode": x.eta_item_code,
                    "unitType": x.uom,
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
                        "rate": round(x.discount_percentage, 5),
                        "amount": round((x.discount_amount * x.qty * -1), 5)
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

            temp["netAmount"] = net_amount
            temp["totalAmount"] = round(invoice.grand_total * -1, 5)
            temp["totalDiscountAmount"] = round(total_discount, 5)

            temp["extraDiscountAmount"] = round(invoice.discount_amount * -1, 5)
            temp["totalItemsDiscountAmount"] = 0#round(total_discount, 5)

            new_total = 0
            for v in invoice.items:
                new_total += (v.qty * v.rate) + (v.qty * v.discount_amount)

            temp["totalSalesAmount"] = round(new_total * -1, 5)

        # Append temp dict into document list then assign document to data
        documents.append(temp)

        data['documents'] = documents

        # frappe.msgprint(json.dumps(data))

        headers = {'content-type': 'application/json;charset=utf-8',
                   "Authorization": "Bearer " + generated_access_token,
                   "Content-Length": "376"
                   }
        response = requests.post(api_base_url, data=json.dumps(data), headers=headers)
        sleep(3)
        frappe.msgprint(json.dumps(data))
        frappe.msgprint(response.content)
        returned_data = response.json()
        #frappe.msgprint(returned_data['acceptedDocuments'][0]['uuid'])
        uuid_no = returned_data['acceptedDocuments'][0]['uuid']
        invoice.uuid = uuid_no
        invoice.save()
        ### Get Document
        #### Get PDF Format and attache it here
        #response2 = requests.get(api_document_url, params={"documentUUID": uuid_no}, headers=headers)
        #frappe.msgprint(response2.content)
        '''
        for key in jsons:
            if key == "acceptedDocuments":
                frappe.msgprint(key.uuid)
                frappe.msgprint(jsons[key])
        '''

        get_invoice(name)
        #invoice.reload()

@frappe.whitelist(allow_guest=True)
def get_invoice(name):
    invoice = frappe.get_doc("Sales Invoice", name)
    generated_access_token = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'generated_access_token')
    api_document_url = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'api_document_url')
    headers = {'content-type': 'application/json',
                "Authorization": "Bearer " + generated_access_token,

                "Accept": "application/json"
                }
    #headers2 = {"Authorization": "Bearer " + generated_access_token,
    #            "Accept": "*/*"
    #            }
    url = api_document_url + invoice.uuid + "/raw"
    #url2 = "https://api.preprod.invoicing.eta.gov.eg/api/v1/documents/"+invoice.uuid+"/pdf"
    response = requests.get(url, params={"documentUUID": invoice.uuid}, headers=headers)
    sleep(3)
    #response2 = requests.get(url2, params={"documentUUID": invoice.uuid}, headers=headers2)
    returned_data = response.json()
    #returned_data2 = response2.json()
    #frappe.msgprint(returned_data['validationResults']['status'])
    invoice.eta_status = returned_data['validationResults']['status']
    invoice.submission_uuid = returned_data['submissionUUID']
    invoice.long_id = returned_data['longId']
    #frappe.msgprint(json.dumps(response2))
    #invoice.eta_pdf = response2.content
    invoice.eta_invoice_link = "https://preprod.invoicing.eta.gov.eg/print/documents/" + invoice.uuid + "/share/" + invoice.long_id
    invoice.eta_link = "https://preprod.invoicing.eta.gov.eg/documents/" + invoice.uuid + "/share/" + invoice.long_id
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
    new_comment = frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Comment",
        "reference_doctype": "Sales Invoice",
        "reference_name": invoice.name,
        "content": "تم إرسال طلب إلغاء الفاتورة إلى نظام مصلحة الضرائب بنجاح",
    })
    new_comment.insert(ignore_permissions=True)
    generated_access_token = frappe.db.get_value('EInvoice Settings', {'company': invoice.company}, 'generated_access_token')
    headers = {'content-type': 'application/json',
            "Authorization": "Bearer " + generated_access_token,

            "Accept": "*/*"
            }
    url = "https://api.preprod.invoicing.eta.gov.eg/api/v1.0/documents/state/"+invoice.uuid+"/state"
    response = requests.put(url, json={"status":"cancelled","reason":"some reason for cancelled document"},params={"documentUUID": invoice.uuid}, headers=headers)
    # frappe.msgprint(response.content)
    user = frappe.session.user
    lang = frappe.db.get_value("User", {'name': user}, "language")
    if response.content:
        if lang == "ar":
            frappe.msgprint(" تم إرسال طلب إلغاء الفاتورة إلى نظام مصلحة الضرائب بنجاح ")
        else:
            frappe.msgprint(" Cancellation Request Has Been Sent Successfully To ETA ")



@frappe.whitelist(allow_guest=True)
def update_uuid_status():
    invoices = frappe.db.sql(""" select name as name from `tabSales Invoice` where docstatus = 1 and uuid is not null and eta_status != "Valid" """,as_dict=1)
    for x in invoices:
        name = x.name
        get_invoice(name)


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


@frappe.whitelist()
def list_invoices_for_signature_old_service():
    invoices = frappe.db.sql(
        """ select name, customer_name, posting_date, grand_total, discount_amount
         from `tabSales Invoice`
         where docstatus = 1 
         and e_signed = 0 
         and e_invoice = 1 
         """, as_dict=1)

    result = []
    for x in invoices:
        total_items_discount = 0
        item_discounts = frappe.db.sql(""" select discount_amount, qty
                                           from `tabSales Invoice Item` where parent = '{name}'
                                       """.format(name=x.name), as_dict=1)
        for z in item_discounts:
            total_items_discount += z.discount_amount * z.qty
            data = {
                'document_no': x.name,
                'document_date': x.posting_date,
                'customer': x.customer_name,
                'total_before_discount': x.grand_total + x.discount_amount + total_items_discount,
                'total_after_discount': x.grand_total,
            }
            result.append(data)
    if result:
        return result
    else:
        return("No Invoices Found")


@frappe.whitelist()
def list_invoices_for_signature():
    invoices = frappe.db.sql(
        """ select name, customer_name, posting_date, grand_total, discount_amount, owner
         from `tabSales Invoice`
         where docstatus = 1 
         and e_signed = 0 
         and e_invoice = 1 
          """, as_dict=1)

    results = {}
    invoice = []
    results["status"] = ""
    results["message"] = ""

    for x in invoices:
        total_items_discount = 0
        item_discounts = frappe.db.sql(""" select discount_amount, qty
                                           from `tabSales Invoice Item` where parent = '{name}'
                                       """.format(name=x.name), as_dict=1)
        invoice_data = {
            "ID": x.name,
            "DocumentNumber": x.name,
            "DocumentDate": x.posting_date,
        }
        for z in item_discounts:
            total_items_discount += z.discount_amount * z.qty
            total = x.grand_total + x.discount_amount + total_items_discount
        invoice_data.update({"InvoiceTotal": total,
                             "TotalAfterDiscount": x.grand_total,
                             "LastUpdateBy": x.owner,
                             "CustomerID_Text": x.customer_name
         })

        invoice.append(invoice_data)
        results["data"] = invoice
    if results:
        return results
    else:
        return "No Invoices Found"

@frappe.whitelist()
def receive_signature(name, signature):
    invoice = frappe.get_doc("Sales Invoice", name)
    invoice.signature = signature
    invoice.e_signed = 1
    invoice.save()

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
def multi_get_invoice_to_sign(data):
    #for x in data:
    for i in range(len(data)):
        return data[i]
    '''
        s_invoice = frappe.get_doc("Sales Invoice", data[i])
        enable = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'enable')
        if enable == 1 and not s_invoice.uuid:
            api_base_url = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'api_base_url')
            api_document_url = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company},
                                                        'api_document_url')
            id_server_base_url = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company},
                                                            'id_server_base_url')
            client_id = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'client_id')
            client_secret = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'client_secret')
            generated_access_token = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company},
                                                                'generated_access_token')
            environment = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'environment')
            signature_type = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'signature_type')
            activity_code = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'activity_code')
            company_type = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'company_type')
            company = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'company_name        ')
            tax_id = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'tax_id')
            branch_id = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'branch_id')
            country = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'country')
            governate = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'governate')
            region_city = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'region_city')
            street = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'street')
            building_number = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'building_number')
            postal_code = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'postal_code')
            floor = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'floor')
            room = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'room')
            landmark = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'landmark')
            additional_info = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'additional_info')

            data = {}
            documents = []
            references = []
            
            for k in data:
                temp = {}
                s_invoice = frappe.get_doc("Sales Invoice", data[i])
                ## Enviroment
                if signature_type == "Without Signature":
                    documentTypeVersion = "0.9"         
                else:
                    documentTypeVersion = "1.0"
                temp["documentTypeVersion"] = documentTypeVersion

                ## Document Type Invoice, Credit Note, Debit Note
                invoice = frappe.get_doc("Sales Invoice", data[i])
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
                invoice = frappe.get_doc("Sales Invoice", name)
                temp["internalID"] = name
                #temp["dateTimeIssued"] = invoice.posting_date.strftime('%Y-%m-%dT%H:%M:%SZ') #str(invoice.posting_date) + "T" + str(invoice.posting_time + timedelta(hours=-2)) + "Z"

                # 2015-02-13T13:15:00Z#
                # "2022-03-11T02:04:45Z"#str(invoice.creation)

                compared_time = "12:00:00.0"
                #issued_time = datetime(invoice.posting_time)
                #issued_time1 = str(invoice.posting_time)
                #if datetime.strptime(issued_time1, '%H:%M:%S.%f') < datetime.strptime(compared_time, '%H:%M:%S.%f'):
                #    temp["dateTimeIssued"] = str(add_to_date(invoice.posting_date, days=0)) + "T0" + datetime.strptime(issued_time, '%H:%M:%S')+ "Z"
                #else:
                temp["dateTimeIssued"] = str(add_to_date(invoice.posting_date, days=0)) + "T" +  datetime.now().strftime("%H:%M:%S") + "Z"

                temp["purchaseOrderReference"] = invoice.po_no
                temp["purchaseOrderDescription"] = str(invoice.po_date)
                # so = frappe.db.sql(""" select sales_order from `tabSales Invoice Item` where parent = '{parent}'  """.format(parent=invoice.name),as_dict=0)
                # if so :
                #    temp["salesOrderReference"] = so[0][0]
                #    so_detail = frappe.get_doc("Sales Order", so[0][0])
                #    temp["salesOrderDescription"] = str(so_detail.transaction_date)
                temp["proformaInvoiceNumber"] = "Null"
                """
                temp["signatures"] = [
                    {
                        "signatureType": "I",
                        "value": "MIIGywYJKoZIhvcNAQcCoIIGvDCCBrgCAQMxDTALBglghkgBZQMEAgEwCwYJKoZIhvcNAQcFoIID/zCCA/swggLjoAMCAQICEEFkOqRVlVar0F0n3FZOLiIwDQYJKoZIhvcNAQELBQAwSTELMAkGA1UEBhMCRUcxFDASBgNVBAoTC0VneXB0IFRydXN0MSQwIgYDVQQDExtFZ3lwdCBUcnVzdCBDb3Jwb3JhdGUgQ0EgRzIwHhcNMjAwMzMxMDAwMDAwWhcNMjEwMzMwMjM1OTU5WjBgMRUwEwYDVQQKFAxFZ3lwdCBUcnVzdCAxGDAWBgNVBGEUD1ZBVEVHLTExMzMxNzcxMzELMAkGA1UEBhMCRUcxIDAeBgNVBAMMF1Rlc3QgU2VhbGluZyBEZW1vIHVzZXIyMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApmVGVJtpImeq\u002BtIJiVWSkIEEOTIcnG1XNYQOYtf5\u002BDg9eF5H5x1wkgR2G7dvWVXrTsdNv2Q\u002Bgvml9SdfWxlYxaljg2AuBrsHFjYVEAQFI37EW2K7tbMT7bfxwT1M5tbjxnkTTK12cgwxPr2LBNhHpfXp8SNyWCxpk6eyJb87DveVwCLbAGGXO9mhDj62glVTrCFit7mHC6bZ6MOMAp013B8No9c8xnrKQiOb4Tm2GxBYHFwEcfYUGZNltGZNdVUtu6ty\u002BNTrSRRC/dILeGHgz6/2pgQPk5OFYRTRHRNVNo\u002BjG\u002BnurUYkSWxA4I9CmsVt2FdeBeuvRFs/U1I\u002BieKg1wIDAQABo4HHMIHEMAkGA1UdEwQCMAAwVAYDVR0fBE0wSzBJoEegRYZDaHR0cDovL21wa2ljcmwuZWd5cHR0cnVzdC5jb20vRWd5cHRUcnVzdENvcnBvcmF0ZUNBRzIvTGF0ZXN0Q1JMLmNybDAdBgNVHQ4EFgQUqzFDImtytsUbghbmtnl2/k4d5jEwEQYJYIZIAYb4QgEBBAQDAgeAMB8GA1UdIwQYMBaAFCInP8ziUIPmu86XJUWXspKN3LsFMA4GA1UdDwEB/wQEAwIGwDANBgkqhkiG9w0BAQsFAAOCAQEAxE3KpyYlPy/e3\u002B6jfz5RqlLhRLppWpRlKYUvH1uIhCNRuWaYYRchw1xe3jn7bLKbNrUmey\u002BMRwp1hZptkxFMYKTIEnNjOKCrLmVIuPFcfLXAQFq5vgLDSbnUhG/r5D\u002B50ndPucyUPhX3gw8gFlA1R\u002BtdNEoeKqYSo9v3p5qNANq12OuZbkhPg6sAD4dojWoNdlkc8J2ML0eq4a5AQvb4yZVb\u002BezqJyqKj83RekRZi0kMxoIm8l82CN8I/Bmp6VVNJRhQKhSeb7ShpdkZcMwcfKdDw6LW02/XcmzVl8NBBbLjKSJ/jxdL1RxPPza7RbGqSx9pfyav5\u002BAxO9sXnXXc5jGCApIwggKOAgEBMF0wSTELMAkGA1UEBhMCRUcxFDASBgNVBAoTC0VneXB0IFRydXN0MSQwIgYDVQQDExtFZ3lwdCBUcnVzdCBDb3Jwb3JhdGUgQ0EgRzICEEFkOqRVlVar0F0n3FZOLiIwCwYJYIZIAWUDBAIBoIIBCjAYBgkqhkiG9w0BCQMxCwYJKoZIhvcNAQcFMBwGCSqGSIb3DQEJBTEPFw0yMTAyMDEyMzUwMjFaMC8GCSqGSIb3DQEJBDEiBCD5bGXJu9uJZIPMGXK98UrHzJM/V2U/WAO6BErxpX5wdTCBngYLKoZIhvcNAQkQAi8xgY4wgYswgYgwgYUEIAJA8uO/ek3l9i3ZOgRtPhGWwwFYljbeJ7yAgEnyYNCWMGEwTaBLMEkxCzAJBgNVBAYTAkVHMRQwEgYDVQQKEwtFZ3lwdCBUcnVzdDEkMCIGA1UEAxMbRWd5cHQgVHJ1c3QgQ29ycG9yYXRlIENBIEcyAhBBZDqkVZVWq9BdJ9xWTi4iMAsGCSqGSIb3DQEBAQSCAQB13E1WX\u002BzbWppfJi3DBK9MMSB1TXuxcNkGXQ19OcRUUAaAe2K\u002BisobYrUCZbi3ygc2AWOMyafboxjjomzrnvXKrFgspT4wAFPYaAGFzKWq\u002BW/nqMhIqJVIpS/NM7Al4HvuBA5iGuZEQFusElB0yIxOIiYDI4v8Ilkff4/duj/V2CNaN5cqXLOpL5RP6Y5i\u002BVsPGb89t/L0dSIldGN0JqaqarqYo5/RwsUFJJq01DFpPGNbOIX3gSCDmycfhJPS9csnne9Zt\u002BabNpja5ZR6KA8JMe4DHes7FDZqHBNHdC\u002BRDXT4crqmnyiJjizULu6MqDc0Fv3vrMMWDLRlwDecgq7i"
                    }
                ]
                """
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
                c_address = frappe.get_doc("Address", invoice.customer_address)
                customer = frappe.get_doc("Customer", invoice.customer)
                if customer.customer_type == "Company":
                    customer_type = "B"
                else:
                    customer_type = "A"
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

                invoiceLines = []
                for x in invoice.items:
                    item_tax_rate = frappe.db.sql(
                        """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                            parent=x.item_tax_template), as_dict=0)
                    salesTotal = x.rate + x.discount_amount
                    invoiceLines.append({
                        "description": x.item_name,
                        "itemType": x.eta_item_type,
                        "itemCode": x.eta_item_code,
                        "unitType": x.uom,
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
                            "rate": round(x.discount_percentage, 5),
                            "amount": round((x.discount_amount * x.qty), 5)
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

                temp["netAmount"] = net_amount
                temp["totalAmount"] = round(invoice.grand_total, 5)
                temp["totalDiscountAmount"] = round(total_discount, 5)

                temp["extraDiscountAmount"] = round(invoice.discount_amount, 5)
                temp["totalItemsDiscountAmount"] = 0#round(total_discount, 5)

                new_total = 0
                for v in invoice.items:
                    new_total += (v.qty * v.rate) + (v.qty * v.discount_amount)

                temp["totalSalesAmount"] = round(new_total, 5)

                if invoice.is_return == 1:
                    invoiceLines = []
                    for x in invoice.items:
                        item_tax_rate = frappe.db.sql(
                            """ select tax_rate from `tabItem Tax Template Detail` where parent = '{parent}' """.format(
                                parent=x.item_tax_template), as_dict=0)
                        salesTotal = x.rate + x.discount_amount
                        invoiceLines.append({
                            "description": x.item_name,
                            "itemType": x.eta_item_type,
                            "itemCode": x.eta_item_code,
                            "unitType": x.uom,
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
                                "rate": round(x.discount_percentage, 5),
                                "amount": round((x.discount_amount * x.qty * -1), 5)
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

                    temp["netAmount"] = net_amount
                    temp["totalAmount"] = round(invoice.grand_total * -1, 5)
                    temp["totalDiscountAmount"] = round(total_discount, 5)

                    temp["extraDiscountAmount"] = round(invoice.discount_amount * -1, 5)
                    temp["totalItemsDiscountAmount"] = 0#round(total_discount, 5)

                    new_total = 0
                    for v in invoice.items:
                        new_total += (v.qty * v.rate) + (v.qty * v.discount_amount)

                    temp["totalSalesAmount"] = round(new_total * -1, 5)

                # Append temp dict into document list then assign document to data
                documents.append(temp)

            
            data['documents'] = documents
        

     '''

@frappe.whitelist()
def get_invoice_details(**kwargs):
    s_invoice = frappe.get_doc("Sales Invoice", kwargs['name'])
    enable = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'enable')
    #if enable == 1 and not s_invoice.uuid:
    api_base_url = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'api_base_url')
    api_document_url = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company},
                                           'api_document_url')
    id_server_base_url = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company},
                                             'id_server_base_url')
    client_id = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'client_id')
    client_secret = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'client_secret')
    generated_access_token = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company},
                                                 'generated_access_token')
    environment = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'environment')
    signature_type = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'signature_type')
    activity_code = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'activity_code')
    company_type = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'company_type')
    company = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'company_name')
    tax_id = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'tax_id')
    branch_id = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'branch_id')
    country = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'country')
    governate = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'governate')
    region_city = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'region_city')
    street = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'street')
    building_number = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'building_number')
    postal_code = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'postal_code')
    floor = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'floor')
    room = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'room')
    landmark = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'landmark')
    additional_info = frappe.db.get_value('EInvoice Settings', {'company': s_invoice.company}, 'additional_info')

    data = {}
    documents = []
    references = []
    temp = {}

    invoice = frappe.get_doc("Sales Invoice", kwargs['name'])
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
    c_address = frappe.get_doc("Address", invoice.customer_address)
    customer = frappe.get_doc("Customer", invoice.customer)
    if customer.customer_type == "Company":
        customer_type = "B"
    else:
        customer_type = "A"
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
    if signature_type == "Without Signature":
        documentTypeVersion = "0.9"
    else:
        documentTypeVersion = "1.0"
    temp["documentTypeVersion"] = documentTypeVersion

    invoice = frappe.get_doc("Sales Invoice", kwargs['name'])
    temp["dateTimeIssued"] = str(add_to_date(invoice.posting_date, days=0)) + "T" + datetime.now().strftime(
        "%H:%M:%S") + "Z"
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
        "dateValidity": str(add_to_date(invoice.posting_date, days=0)) + "T" + datetime.now().strftime("%H:%M:%S") + "Z",
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
        salesTotal = x.rate + x.discount_amount
        invoiceLines.append({
            "description": x.item_name,
            "itemType": x.eta_item_type,
            "itemCode": x.eta_item_code,
            "unitType": x.uom,
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
                "amountSold": round(salesTotal, 5),
                "currencyExchangeRate": 1
            },
            "discount": {
                "rate": round(x.discount_percentage, 5),
                "amount": round((x.discount_amount * x.qty), 5)
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

    temp["totalDiscountAmount"] = round(total_discount, 5)
    new_total = 0
    for v in invoice.items:
        new_total += (v.qty * v.rate) + (v.qty * v.discount_amount)

    temp["totalSalesAmount"] = round(new_total, 5)

    temp["netAmount"] = net_amount

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
    temp["totalItemsDiscountAmount"] = 0  # round(total_discount, 5)





    # Append temp dict into document list then assign document to data
    documents.append(temp)

    data['documents'] = documents

    return documents
