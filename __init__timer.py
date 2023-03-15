import logging
import azure.functions as func
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential
import datetime
import smtplib
import os
from email.message import EmailMessage
import http.client
import json
import azure.functions as func
import requests


def SendHttpFunctionRequest(subject,sentFrom,sentTo,notificationMsg,notificationType,authCode,httpFunctionUrl):
    requestHeaders = {'Content-type': 'application/json'}
    requestBody = {
            "Subject": subject + ' - '+notificationType,
            "SentFrom":sentFrom,
            "SentTo":sentTo,
            "Body": notificationMsg
        }
    requestBodyJson = json.dumps(requestBody)
    params = {'code': authCode}
    response = requests.post(httpFunctionUrl, json=requestBodyJson,params=params, headers=requestHeaders)
    print("Status Code", response.status_code)
    print("JSON Response ", response.json())

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logging.info('Python Timer Trigger function execution started.')
    
    # Key vault configuration
    tenantId = os.environ["tenantId"]
    clientId = os.environ["clientId"]
    clientSecret = os.environ["clientSecret"]
    KVUri = os.environ["KVUri"]

    # SMTP configuration
    subject = os.environ["Subject"]
    sentFrom = os.environ["sentFrom"]
    sentTo = os.environ["sentTo"]

    # Http function url
    httpFunctionUrl = os.environ["httpFunctionUrl"]
    authCode = os.environ["authCode"]

    credential = ClientSecretCredential(tenantId, clientId, clientSecret)
    client = SecretClient(vault_url=KVUri, credential=credential)
    secrets = client.list_properties_of_secrets()
    notificationMsgWarning = ""
    notificationMsgAlert = ""

    for secret in  secrets:
        if secret.enabled == True:
            secretInfo = client.get_secret(secret.name)
            if secret.expires_on is not None:
                expiryDate = secretInfo.properties.expires_on
                expiryDate = secret.expires_on
                today = datetime.datetime.utcnow()
                diff = expiryDate.replace(tzinfo=None) - today.replace(tzinfo=None)
                if(diff.days > 15 and diff.days  <= 30):
                    msg = " Secret Name: "+secret.name+" Expire Date: "+secret.expires_on.strftime('%m/%d/%Y')
                    notificationMsgWarning +=msg+"\r\r\n"
                if(diff.days <= 15):
                    msg = " Secret Name: "+secret.name+" Expire Date: "+secret.expires_on.strftime('%m/%d/%Y')
                    notificationMsgAlert +=msg+"\r\r\n"

    if notificationMsgWarning != "":
        print ("Secret that expired….", notificationMsgWarning)
        SendHttpFunctionRequest(subject=subject,sentFrom=sentFrom,sentTo=sentTo,notificationMsg=notificationMsgWarning,notificationType='Warning',authCode=authCode,httpFunctionUrl=httpFunctionUrl)

    if notificationMsgAlert != "":
        print ("Secret that expired….", notificationMsgAlert)
        SendHttpFunctionRequest(subject=subject,sentFrom=sentFrom,sentTo=sentTo,notificationMsg=notificationMsgAlert,notificationType='Alert',authCode=authCode,httpFunctionUrl=httpFunctionUrl)    

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
