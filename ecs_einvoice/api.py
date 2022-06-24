from __future__ import unicode_literals
from re import A
import frappe
from frappe import auth
import datetime
import json, ast, requests
from frappe.utils import money_in_words
import urllib.request

@frappe.whitelist()
def login():
    companies = frappe.db.sql(""" Select name, company, environment, client_id, client_secret, generated_access_token
                                  From `tabEInvoice Settings` """, as_dict=1)

    for x in companies:
        if x.environment == "Pre-Production":
            id_server_base_url = "https://id.preprod.eta.gov.eg/connect/token"
        if x.environment == "Production":
            id_server_base_url = "https://id.eta.gov.eg/connect/token"
        client_id = x.client_id
        client_secret = x.client_secret
        generated_access_token = x.generated_access_token

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(id_server_base_url, data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'InvoicingAPI'
        }, headers=headers)
        json = response.json()
        for key in json:
            if key == "access_token":
                frappe.db.sql(
                    """ update `tabEInvoice Settings` set generated_access_token = '{new_token}' where name = '{name}' 
                    """.format(name=x.name, new_token=json[key]))

    pass

@frappe.whitelist(allow_guest=True)
def signature_login(Username, Password):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=Username, pwd=Password)
        login_manager.post_login()


    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key": true,
            "message": "اسم المستخدم او كلمة المرور غير صحيحة !"
        }
    api_generate = generate_keys(frappe.session.user)
    user = frappe.get_doc('User', frappe.session.user)

    frappe.response["message"] = {
        "success": "200",
        "message": "Authentication Success",
        "data": [
            {
                "ID": frappe.session.sid,
                "Username": Username,
                "user_id": user.name,
                "CompanyNumber": "1000"
            }
        ]
    }
    return

def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save()
    return api_secret

