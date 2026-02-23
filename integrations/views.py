# import base64
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import os
from pathlib import Path
import platform
# import pytz
# import requests
import re
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from helpers.decode_token import decodeToken
# from helpers.email_data import SendMeetingMails
from organizations.models import *
from .serializers import *
from helpers.status_messages import *
# import json
import imaplib
import email
import regex as re
import codecs
import string
import smtplib
from email.mime.text import MIMEText
# Create your views here.
              
class MailCredentialsviewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = MailsCredentials.objects.all() 
    serializer_class = MailsCredentialsSerializer 


    def create(self, request, *args, **kwargs):
        try:
            
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            required_fields = ['email','password','medium']
            if not all(field in request.data for field in required_fields):
                        return errorMessageWithData('make sure you have added all required fields','email,password,medium')
            
            query = self.queryset.filter(organization=organization_id,email=request.data['email'],is_active=True)

            encrypted_text = encrypt(request.data['password'],3)
            request.data['password']=encrypted_text
            request.data['created_by'] = request.user.id
            request.data['organization'] = organization_id
            if not query.exists():
                serializer=self.serializer_class(data = request.data)
                if not serializer.is_valid():
                    return serializerError(serializer.errors)
                serializer.save()
                return successfullyCreated(serializer.data)
            
            else:
                return errorMessage('Credentials is already exists in this organization')
            
        except Exception as e:
            return exception(e)
        

  
    
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            query = self.queryset.filter(organization=organization_id,created_by=request.user.id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def patch(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            if not request.data:
                return errorMessage("Request Data is empty")

            query=self.queryset.filter(id=pk,created_by=request.user.id,organization=organization_id,is_active=True)

            if not query.exists():
                    return errorMessage("Data not exists in current organization")
                
            obj=query.get()
            
            serializer=self.serializer_class(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()

            return successfullyUpdated(serializer.data)
            
        except Exception as e:
            return exception(e)
        


    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            
            query = self.queryset.filter(id=pk,created_by=request.user.id)
            if not query.exists():
                return errorMessage('Credentials does not exists')
            if not query.filter(is_active=True).exists():
                return errorMessage('Credentials is already deactivated at this id')
            obj = query.get()
            obj.is_active=False
            obj.save()

            
            return successMessage('Credentials is deactivated successfully')
        except Exception as e:
            return exception(e)
    


class MailInboxviewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def send_message(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            required_fields = ['to_email','subject','body']
            if not all(field in request.data for field in required_fields):
                        return errorMessageWithData('make sure you have added all required fields','to_email,subject,body')
            query= MailsCredentials.objects.filter(organization=organization_id,created_by=request.user.id,is_active=True)
            if not query.exists():
                 return errorMessage("Please add your credientials")
            obj=query.get()
            cc=request.data.get('cc',None)
            
            decrypted_text = decrypt(obj.password,3)
            # print(decrypted_text)

            # Set the recipient's email and email content
            to_email = request.data['to_email']
            subject = request.data['subject']
            body = request.data['body']
            
            msg = MIMEMultipart()
            msg['From'] = obj.email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            # print(obj.email,obj.medium)
            # Check for attachments and add them
            attachments = request.data.get('attachments', None)
            if attachments:
                for attachment in attachments:
                    attachment_name = attachment['name']
                    attachment_content = attachment['content']  # Base64 encoded
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment_content.encode('utf-8'))
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition', 
                        f'attachment; filename={attachment_name}'
                    )
                    msg.attach(part)
            # Establish a connection to Gmail's SMTP server
            medium=f'smtp.{obj.medium}.com'
            server = smtplib.SMTP_SSL(medium, 465)  # SSL for security
            server.login(obj.email,decrypted_text)  # Use the App Password
            # print("Test")
            new_list=[email.strip() for email in to_email.split(',')]
            # print(new_list)
             # Step 2: Split the string into a list
            if cc is not None:
              email_list=[]
              email_list = cc.split(',')
              email_list.insert(0,to_email)
              new_list.extend(email_list)
              print(new_list)
              msg['CC'] = cc
              server.sendmail(obj.email,email_list, msg.as_string())

            else:
                server.sendmail(obj.email,new_list, msg.as_string())
                 
            server.quit()

            return successMessage("Success")
             
        except Exception as e:
            return exception(e)  
        
    
    def get_inbox(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            required_fields = ['status','action']
            if not all(field in request.data for field in required_fields):
                        return errorMessageWithData('make sure you have added all required fields','status,action')
            
            query= MailsCredentials.objects.filter(organization=organization_id,created_by=request.user.id,is_active=True)
            if not query.exists():
                 return errorMessage("Please add your credientials")
            obj=query.get()
            medium=f'imap.{obj.medium}.com'
            # action=request.data['action']
            action = get_action(obj.medium, request.data["action"])

            # print(action)

            mail_status=request.data['status'].lower()
            email_json_list = []

            status_list = ['unseen', 'seen', 'all']
            if mail_status not in status_list:
                return errorMessage(f'Status can only be {status_list}')
            decrypted_text = decrypt(obj.password,3)

            
            
            imap = imaplib.IMAP4_SSL(medium)
            username =obj.email
            password = decrypted_text #should be an app password, to create one follow this link:https://support.google.com/accounts/answer/185833
            login_result=imap.login(username, password)
            if login_result[0] == "OK":
                for i in imap.list()[1]:
                    l = i.decode().split(' "/" ')
                    # print(l[0] + " = " + l[1])

                imap.select(f'"{action}"')
                status, messages = imap.search(None,mail_status)

                if status == "OK":
                # Pagination logic
                    message_ids = messages[0].split()[::-1]
                    page_size = int(request.data.get('page_size', 10))  # Default page size is 10
                    page_number = int(request.data.get('page_number', 1))  # Default page number is 1

                    start_index = (page_number - 1) * page_size
                    end_index = start_index + page_size

                    # if start_index >= len(message_ids):
                    #     return successMessage("Page number is out of range.")

                    # Get the selected subset of message IDs
                    selected_ids = message_ids[start_index:end_index]
                    for num in selected_ids:
                        _, msg = imap.fetch(num, "(RFC822)")
                        message = email.message_from_bytes(msg[0][1])

                        # print the message details
                        subject_header = message['Subject']
                        decoded_subject = email.header.decode_header(subject_header)
                        subject = decoded_subject[0][0]
                        email_data = {
                            "Message_ID": num.decode('utf-8'),
                            "Subject": subject,
                            "From": message["From"],
                            'CC': message.get("CC", "None"),
                            "Date":message["Date"],
                        }

                        # Append the dictionary to the list
                        email_json_list.append(email_data)

                    return success(email_json_list)

                else:
                    return successMessage(f"No {mail_status} messages found.")
                
            else:
                 return errorMessageWithData("Error details:", login_result[1])
            
        except Exception as e:
            return exception(e)
        
    def mail_data(self,request,*args, **kwargs):
        try:
            pk=self.kwargs['pk']
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            required_fields = ['action']
            if not all(field in request.data for field in required_fields):
                        return errorMessageWithData('make sure you have added all required fields','action')
            # action=request.data['action']
            query= MailsCredentials.objects.filter(organization=organization_id,created_by=request.user.id,is_active=True)
            if not query.exists():
                 return errorMessage("Please add your credientials")
            obj=query.get()
            medium=f'imap.{obj.medium}.com'
            # action=
            # if obj.medium='zoho':
            action = get_action(obj.medium, request.data["action"])
            # download_folder = get_default_download_folder()
            decrypted_text = decrypt(obj.password,3)
            imap = imaplib.IMAP4_SSL(medium)
            username =obj.email
            password = decrypted_text #should be an app password, to create one follow this link:https://support.google.com/accounts/answer/185833
            login_result=imap.login(username, password)
            if login_result[0] == "OK":
            # Select the inbox
                imap.select(f'"{action}"')

                status, msg = imap.fetch(pk, "(RFC822)")
                if status != "OK":
                    return errorMessage("Failed to fetch message against given id")
                
                message = email.message_from_bytes(msg[0][1])
                # Extract details from the email
                # raw=msg[0][1]
                # print(raw)
                subject_header = message['Subject']
                decoded_subject = email.header.decode_header(subject_header)
                subject = decoded_subject[0][0]
                email_body = extract_email_body(message)
                email_attachments = extract_email_attachments_metadata(message)
                email_data = {
                            "Message_ID": pk,
                            "Subject": subject,
                            "From": message["From"],
                            "Date":message["Date"],
                            'CC': message.get("CC", "None"),
                            "Body": email_body,
                            "email_attachments":email_attachments,

                        }

                return success(email_data)
            
            else:
                 return errorMessageWithData("Error details:", login_result[1])
            



        except Exception as e:
            return exception(e)
        
        
    def download_attachments_data(self,request,*args, **kwargs):
        try:
            pk=self.kwargs['pk']
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            required_fields = ['action']
            if not all(field in request.data for field in required_fields):
                        return errorMessageWithData('make sure you have added all required fields','action')
            query= MailsCredentials.objects.filter(organization=organization_id,created_by=request.user.id,is_active=True)
            if not query.exists():
                 return errorMessage("Please add your credientials")
            obj=query.get()
            medium=f'imap.{obj.medium}.com'
            action = get_action(obj.medium, request.data["action"])
            filename=request.data.get
           # Specify the folder path on your local machine
            # download_folder_name = os.path.join('Downloads', 'emails_attachements')
            download_folder_path = os.path.expanduser('~') + '/Downloads'
            os.makedirs(download_folder_path, exist_ok=True)
            # print(download_folder_path)
            decrypted_text = decrypt(obj.password,3)
            imap = imaplib.IMAP4_SSL(medium)
            username =obj.email
            password = decrypted_text #should be an app password, to create one follow this link:https://support.google.com/accounts/answer/185833
            login_result=imap.login(username, password)
            if login_result[0] == "OK":
            # Select the inbox
                imap.select(f'"{action}"')

                status, msg = imap.fetch(pk, "(RFC822)")
                if status != "OK":
                    return errorMessage("Failed to fetch message against given id")
                
                message = email.message_from_bytes(msg[0][1])
               
               
                email_attachments = download_attachments(message,filename,download_folder_path)
                return success(email_attachments)
            
            else:
                 return errorMessageWithData("Error details:", login_result[1])
            



        except Exception as e:
            return exception(e)
    
# Helper function to extract the email body content
# 
def extract_email_body(message):
    for part in message.walk():
        # Check if the content type is 'text/html' and it's not an attachment
        if part.get_content_type() == 'text/html' and not part.get('Content-Disposition'):
            charset = part.get_content_charset() or 'utf-8'
            try:
                # Decode the HTML content
                return part.get_payload(decode=True).decode(charset, errors='replace')
            except Exception as e:
                # Return an error message if decoding fails
                return f"Error decoding email HTML body: {e}"
    # Return None if no HTML body is found
    return None


def extract_email_attachments_metadata(message):
    attachments_metadata = []
    for part in message.walk():
        content_disposition = part.get("Content-Disposition", None)
        if content_disposition and content_disposition.startswith(("attachment", "inline")):
            filename = part.get_filename()
            if filename:
                # Collect metadata without fetching the content
                attachments_metadata.append({
                    'filename': filename,
                    'content_type': part.get_content_type(),
                    'content_disposition': content_disposition,
                })

                # # Download the attachment
                # file_path = download_folder / filename
                # with open(file_path, 'wb') as f:
                #     f.write(part.get_payload(decode=True))
    return attachments_metadata

def download_attachments(message,file_name, download_folder):
    attachments_metadata = []
    for part in message.walk():
        content_disposition = part.get("Content-Disposition", None)
        if content_disposition and content_disposition.startswith(("attachment", "inline")):
            if file_name is None:
                filename = part.get_filename()
            else:
                filename=file_name
            if filename:
                    # Download the attachment
                    file_path = os.path.join(download_folder, filename)
                    with open(file_path, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    attachments_metadata.append({'filename': filename, 'path': file_path})
        
    if attachments_metadata:
        return f"Attachments downloaded successfully."
    else:
        return "No attachments found."




# Function to encrypt text with a specified shift value
def encrypt(text, shift):
    encrypted_text = ""
    for char in text:
        # Encrypt only alphabetic characters, preserve others
        if char.isalpha():
            # Determine ASCII base (lowercase or uppercase)
            ascii_base = ord('a') if char.islower() else ord('A')
            # Compute new shifted position
            new_pos = (ord(char) - ascii_base + shift) % 26
            # Append the encrypted character
            encrypted_text += chr(ascii_base + new_pos)
        else:
            encrypted_text += char  # Non-alphabetic characters remain unchanged
    return encrypted_text


# Function to decrypt text with a specified shift value
def decrypt(text, shift):
    decrypted_text = ""
    for char in text:
        if char.isalpha():
            ascii_base = ord('a') if char.islower() else ord('A')
            new_pos = (ord(char) - ascii_base - shift) % 26
            decrypted_text += chr(ascii_base + new_pos)
        else:
            decrypted_text += char
    return decrypted_text


def get_action(medium, action):
    # Define dictionary for Zoho
    zoho_mailboxes = {
        "inbox": "INBOX",
        "drafts": "Drafts",
        "templates": "Templates",
        "snoozed": "Snoozed",
        "sent": "Sent",
        "spam": "Spam",
        "trash": "Trash",
        "notification": "Notification",
        "newsletter": "Newsletter"
    }

    # Define dictionary for Gmail
    gmail_mailboxes = {
        "inbox": "INBOX",
        "all mail": "[Gmail]/All Mail",
        "drafts": "[Gmail]/Drafts",
        "important": "[Gmail]/Important",
        "sent": "[Gmail]/Sent Mail",
        "spam": "[Gmail]/Spam",
        "starred": "[Gmail]/Starred",
        "trash": "[Gmail]/Trash"
    }
    # Normalize medium to lower case to match against known dictionaries
    if medium.lower() == "zoho":
        mailboxes = zoho_mailboxes
    elif medium.lower() == "gmail":
        mailboxes = gmail_mailboxes
    else:
        # If medium is not recognized, return None
        return None
    
    # Return the corresponding mailbox value while treating the action as case-insensitive
    return mailboxes.get(action.lower(), None)


def get_default_download_folder():
    if platform.system() == 'Windows':
        # Get the "Downloads" folder on Windows
        return Path.home() / 'Downloads'
    elif platform.system() == 'Darwin':
        # Get the "Downloads" folder on macOS
        return Path.home() / 'Downloads'
    elif platform.system() == 'Linux':
        # Get the "Downloads" folder on Linux
        return Path.home() / 'Downloads'
    else:
        # Default to current directory if unknown system
        return Path.cwd()