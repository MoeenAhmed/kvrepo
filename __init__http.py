import logging
import azure.functions as func
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential
import datetime
import smtplib
import os
from email.message import EmailMessage

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python Http Trigger function execution started.')
    
    requestJson = req.get_json()
    sentFrom = requestJson.get('SentFrom')
    sentTo = requestJson.get('SentTo')
    subject = requestJson.get('Subject')
    body = requestJson.get('Body')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sentFrom
    msg['To'] = sentTo
    msg.set_content(body)

    try:
        smtp_server = smtplib.SMTP('mailhub.utc.com', 25)
        smtp_server.ehlo()
        smtp_server.send_message(msg)
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)
    
    return func.HttpResponse(
             body="This HTTP triggered function executed successfully.Email sent successfully!",
             status_code=200
    )
