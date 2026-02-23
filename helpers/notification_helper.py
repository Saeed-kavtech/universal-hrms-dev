from django.core.mail import EmailMessage
from profiles_api.models import HrmsUsers
from employees.models import Employees
import html
from django.conf import settings
import time
# def get_document_url(document_id, document_type='rich'):
#     """
#     Generate proper document URL based on document type
#     document_type: 'rich' for rich documents, 'regular' for uploaded documents
#     """
#     try:
#         # Get base URL from settings or use default
#         base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        
#         if document_type == 'rich':
#             return f"{base_url}/kavpedia/view/{document_id}"
#         else:
#             return f"{base_url}/documents/view/{document_id}"
            
#     except Exception as e:
#         print(f"[WARNING] Could not generate document URL: {str(e)}")
#         return f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/employee/dashboard"

# def send_collaboration_notification(user_id, document_id, document_title, action_type, role=None, document_type='rich'):
#     """
#     Send notification when someone is added/removed as a collaborator
#     """
#     try:
#         print(f"\n=== [COLLABORATION EMAIL DEBUG] ===")
#         print(f"User ID: {user_id}")
#         print(f"Document ID: {document_id}")
#         print(f"Document Type: {document_type}")
        
#         # Get user details
#         user = HrmsUsers.objects.filter(id=user_id).first()
#         if not user:
#             print(f"ERROR: User not found with id={user_id}")
#             return False
            
#         print(f"User Email: {user.email}")
        
#         # Get user name
#         user_name = get_user_display_name(user_id)
#         print(f"User Name: {user_name}")
        
#         # Generate document URL (for "added" case) or dashboard URL (for "removed" case)
#         document_url = get_document_url(document_id, document_type)
#         dashboard_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/employee/dashboard"
        
#         print(f"Document URL: {document_url}")
#         print(f"Dashboard URL: {dashboard_url}")
        
#         # Prepare email content
#         subject = f"You've been {action_type} as a collaborator"
#         role_text = f" as <strong>{role}</strong>" if role else ""
        
#         # Determine button text and URL based on action
#         if action_type == 'added':
#             button_text = "View Document"
#             button_url = document_url
#             access_message = f"You can now access this document through your HRMS account."
#         else:
#             button_text = "View HRMS Dashboard"
#             button_url = dashboard_url
#             access_message = "You no longer have access to this document."
        
#         # Create HTML email
#         body = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <meta charset="UTF-8">
#             <style>
#                 body {{
#                     font-family: Arial, sans-serif;
#                     line-height: 1.6;
#                     color: #333;
#                     max-width: 600px;
#                     margin: 0 auto;
#                     padding: 20px;
#                 }}
#                 .header {{
#                     background-color: {'#4CAF50' if action_type == 'added' else '#f44336'};
#                     color: white;
#                     padding: 20px;
#                     text-align: center;
#                     border-radius: 5px 5px 0 0;
#                 }}
#                 .content {{
#                     background-color: #f9f9f9;
#                     padding: 20px;
#                     border-radius: 0 0 5px 5px;
#                     border: 1px solid #ddd;
#                     border-top: none;
#                 }}
#                 .document-title {{
#                     background-color: {'#e8f5e9' if action_type == 'added' else '#ffebee'};
#                     padding: 15px;
#                     border-left: 4px solid {'#4CAF50' if action_type == 'added' else '#f44336'};
#                     margin: 15px 0;
#                     font-weight: bold;
#                 }}
#                 .permission {{
#                     background-color: {'#e8f5e9' if action_type == 'added' else '#ffebee'};
#                     padding: 10px;
#                     border-radius: 3px;
#                     margin: 10px 0;
#                 }}
#                 .button {{
#                     display: inline-block;
#                     background-color: {'#4CAF50' if action_type == 'added' else '#2196F3'};
#                     color: white;
#                     padding: 12px 24px;
#                     text-decoration: none;
#                     border-radius: 5px;
#                     margin-top: 20px;
#                     font-weight: bold;
#                 }}
#                 .button:hover {{
#                     background-color: {'#45a049' if action_type == 'added' else '#1976D2'};
#                 }}
#                 .footer {{
#                     margin-top: 30px;
#                     padding-top: 20px;
#                     border-top: 1px solid #eee;
#                     color: #666;
#                     font-size: 12px;
#                 }}
#             </style>
#         </head>
#         <body>
#             <div class="header">
#                 <h2>{'Added as Collaborator' if action_type == 'added' else 'Removed as Collaborator'}</h2>
#             </div>
            
#             <div class="content">
#                 <p>Hi <strong>{user_name}</strong>,</p>
                
#                 <p>You have been <strong>{action_type}</strong>{role_text} as a collaborator to the document:</p>
                
#                 <div class="document-title">
#                     📄 {document_title}
#                 </div>
                
#                 {f'<div class="permission">Role: <strong>{role}</strong></div>' if role and action_type == 'added' else ''}
                
#                 <p>{access_message}</p>
                
#                 <a href="{button_url}" class="button">{button_text}</a>
                
#                 <div class="footer">
#                     <p>Best regards,<br>
#                     <strong>HRMS Team</strong></p>
                    
#                     <p style="font-size: 10px; color: #999;">
#                         This is an automated notification. Please do not reply to this email.
#                     </p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
        
#         print(f"Email prepared successfully")
#         print(f"Subject: {subject}")
#         print(f"Recipient: {user.email}")
#         print(f"Action: {action_type}")
#         print(f"Button: {button_text} -> {button_url}")
        
#         # Send email
#         email = EmailMessage(
#             subject=subject,
#             body=body,
#             from_email="HRMS Notifications <noreply@kavmails.net>",
#             to=[user.email],
#         )
#         email.content_subtype = "html"
        
#         print("Sending email...")
#         result = email.send()
#         print(f"Email send result: {result}")
#         print(f"=== [END DEBUG] ===\n")
        
#         return True
        
#     except Exception as e:
#         print(f"\n=== [COLLABORATION EMAIL ERROR] ===")
#         print(f"Error: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         print(f"=== [END ERROR] ===\n")
#         return False

# def send_comment_notification(document_owner_id, commenter_id, document_id, document_title, comment_preview=None, document_type='rich'):
#     """
#     Send notification when someone comments on a document
#     """
#     try:
#         print(f"\n=== [COMMENT EMAIL DEBUG] ===")
#         print(f"Document Owner ID: {document_owner_id}")
#         print(f"Commenter ID: {commenter_id}")
#         print(f"Document ID: {document_id}")
#         print(f"Document Type: {document_type}")
        
#         # Get document owner details
#         owner = HrmsUsers.objects.filter(id=document_owner_id).first()
#         if not owner:
#             print(f"ERROR: Document owner not found with id={document_owner_id}")
#             return False
            
#         print(f"Document Owner Email: {owner.email}")
        
#         # Get commenter name
#         commenter_name = get_user_display_name(commenter_id)
#         print(f"Commenter Name: {commenter_name}")
        
#         # Get owner name
#         owner_name = get_user_display_name(document_owner_id)
#         print(f"Owner Name: {owner_name}")
        
#         # Generate document URL
#         document_url = get_document_url(document_id, document_type)
#         print(f"Document URL: {document_url}")
        
#         # Prepare email content
#         subject = f"New comment on '{document_title[:50]}{'...' if len(document_title) > 50 else ''}'"
        
#         comment_preview_text = ""
#         if comment_preview:
#             # Escape HTML to prevent XSS and limit length
#             safe_preview = html.escape(comment_preview[:200])
#             if len(comment_preview) > 200:
#                 safe_preview += "..."
#             comment_preview_text = f"""
#             <div class="comment-preview">
#                 "{safe_preview}"
#             </div>
#             """
        
#         # Create HTML email
#         body = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <meta charset="UTF-8">
#             <style>
#                 body {{
#                     font-family: Arial, sans-serif;
#                     line-height: 1.6;
#                     color: #333;
#                     max-width: 600px;
#                     margin: 0 auto;
#                     padding: 20px;
#                 }}
#                 .header {{
#                     background-color: #2196F3;
#                     color: white;
#                     padding: 20px;
#                     text-align: center;
#                     border-radius: 5px 5px 0 0;
#                 }}
#                 .content {{
#                     background-color: #f9f9f9;
#                     padding: 20px;
#                     border-radius: 0 0 5px 5px;
#                     border: 1px solid #ddd;
#                     border-top: none;
#                 }}
#                 .document-title {{
#                     background-color: #e8f5e9;
#                     padding: 15px;
#                     border-left: 4px solid #4CAF50;
#                     margin: 15px 0;
#                     font-weight: bold;
#                 }}
#                 .comment-preview {{
#                     background-color: #e3f2fd;
#                     padding: 15px;
#                     border-left: 4px solid #2196F3;
#                     margin: 15px 0;
#                     font-style: italic;
#                     border-radius: 3px;
#                 }}
#                 .button {{
#                     display: inline-block;
#                     background-color: #2196F3;
#                     color: white;
#                     padding: 10px 20px;
#                     text-decoration: none;
#                     border-radius: 5px;
#                     margin-top: 15px;
#                 }}
#                 .button:hover {{
#                     background-color: #1976D2;
#                 }}
#                 .footer {{
#                     margin-top: 20px;
#                     padding-top: 20px;
#                     border-top: 1px solid #eee;
#                     color: #666;
#                     font-size: 12px;
#                 }}
#             </style>
#         </head>
#         <body>
#             <div class="header">
#                 <h2>New Comment on Your Document</h2>
#             </div>
            
#             <div class="content">
#                 <p>Hi <strong>{owner_name}</strong>,</p>
                
#                 <p><strong>{commenter_name}</strong> has commented on your document:</p>
                
#                 <div class="document-title">
#                     📄 {document_title}
#                 </div>
                
#                 {comment_preview_text}
                
#                 <p>To view the full comment and respond, please click the button below:</p>
                
#                 <a href="{document_url}" class="button">View Document & Comment</a>
                
                
                
#                 <div class="footer">
#                     <p>Best regards,<br>
#                     <strong>HRMS Team</strong></p>
                    
#                     <p style="font-size: 10px; color: #999;">
#                         This is an automated notification. Please do not reply to this email.
#                     </p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
        
#         print(f"Email prepared successfully")
#         print(f"Subject: {subject}")
#         print(f"Recipient: {owner.email}")
        
#         # Send email
#         email = EmailMessage(
#             subject=subject,
#             body=body,
#             from_email="HRMS Notifications <noreply@kavmails.net>",
#             to=[owner.email],
#         )
#         email.content_subtype = "html"
        
#         print("Sending email...")
#         result = email.send()
#         print(f"Email send result: {result}")
#         print(f"=== [END DEBUG] ===\n")
        
#         return True
        
#     except Exception as e:
#         print(f"\n=== [COMMENT EMAIL ERROR] ===")
#         print(f"Error: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         print(f"=== [END ERROR] ===\n")
#         return False    
    
    
    
# def send_mention_notification(mentioned_user_id, mentioned_by_id, document_title, document_id=None):
#     """
#     Send notification when someone is mentioned in a document
    
#     Parameters:
#     - mentioned_user_id: ID of the user mentioned
#     - mentioned_by_id: ID of the user who mentioned
#     - document_title: Title of the document
#     - document_id: ID of the document (for link generation)
#     """
#     try:
#         # Get mentioned user details
#         mentioned_user = HrmsUsers.objects.filter(id=mentioned_user_id).first()
#         if not mentioned_user:
#             return False
            
#         # Get mentioned by user details
#         mentioned_by = HrmsUsers.objects.filter(id=mentioned_by_id).first()
#         mentioned_by_name = mentioned_by.first_name if mentioned_by else "Someone"
        
#         # Get mentioned user employee details
#         mentioned_employee = Employees.objects.filter(hrmsuser=mentioned_user, is_active=True).first()
#         mentioned_name = mentioned_employee.first_name if mentioned_employee else mentioned_user.first_name
        
#         # Prepare email content
#         subject = f"You've been mentioned in '{document_title[:50]}{'...' if len(document_title) > 50 else ''}'"
        
#         # Generate document link if ID is provided
#         document_link = f"/documents/view/{document_id}" if document_id else "#"
        
#         body = f"""
#         <html>
#         <body>
#             <p>Hi {mentioned_name},</p>
            
#             <p><strong>{mentioned_by_name}</strong> has mentioned you in a document:</p>
            
#             <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #FF9800; margin: 15px 0;">
#                 <strong>{document_title}</strong>
#             </div>
            
#             <p>Click <a href="{document_link}">here</a> to view the document.</p>
            
#             <p>Best regards,<br>
#             HRMS Team</p>
#         </body>
#         </html>
#         """
        
#         # Send email
#         email = EmailMessage(
#             subject=subject,
#             body=body,
#             from_email="noreply@kavmails.net",
#             to=[mentioned_user.email],
#         )
#         email.content_subtype = "html"
#         email.send()
        
#         return True
        
#     except Exception as e:
#         print(f"Error sending mention notification: {str(e)}")
#         return False
    
    
    



# def get_user_display_name(user_id):
#     """
#     Get display name for a user, trying Employees table first, then HrmsUsers
#     """
#     try:
#         user = HrmsUsers.objects.filter(id=user_id).first()
#         if not user:
#             return "User"
        
#         # Try Employees table first
#         employee = Employees.objects.filter(hrmsuser=user, is_active=True).first()
#         if employee:
#             if employee.first_name:
#                 return employee.first_name
#             elif hasattr(employee, 'name') and employee.name:
#                 return employee.name
        
#         # Fallback to HrmsUsers
#         if user.first_name:
#             return user.first_name
#         elif user.email:
#             return user.email.split('@')[0]  # Use email username
        
#         return "User"
        
#     except Exception:
#         return "User"








from .email_queue import email_queue_manager, get_user_display_name, get_document_url
import html

def send_collaboration_notification(user_id, document_id, document_title, action_type, role=None, document_type='rich'):
    """
    Queue notification when someone is added/removed as a collaborator
    """
    try:
        # print(f"\n=== [COLLABORATION EMAIL QUEUED] ===")
        # print(f"User ID: {user_id}")
        # print(f"Document ID: {document_id}")
        
        # Get user details
        from profiles_api.models import HrmsUsers
        user = HrmsUsers.objects.filter(id=user_id).first()
        if not user:
            print(f"ERROR: User not found with id={user_id}")
            return False
        
        if not user.email:
            print(f"ERROR: User has no email address")
            return False
        
        # print(f"User Email: {user.email}")
        
        # Get user name
        user_name = get_user_display_name(user_id)
        # print(f"User Name: {user_name}")
        
        # Generate URLs
        document_url = get_document_url(document_id, document_type)
        dashboard_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/employee/dashboard"
        
        # Prepare email content
        subject = f"You've been {action_type} as a collaborator"
        role_text = f" as <strong>{role}</strong>" if role else ""
        
        # Determine button text and URL
        if action_type == 'added':
            button_text = "View Document"
            button_url = document_url
            access_message = f"You can now access this document through your HRMS account."
        else:
            button_text = "View HRMS Dashboard"
            button_url = dashboard_url
            access_message = "You no longer have access to this document."
        
        # Create HTML email
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: {'#4CAF50' if action_type == 'added' else '#f44336'};
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 0 0 5px 5px;
                    border: 1px solid #ddd;
                    border-top: none;
                }}
                .document-title {{
                    background-color: {'#e8f5e9' if action_type == 'added' else '#ffebee'};
                    padding: 15px;
                    border-left: 4px solid {'#4CAF50' if action_type == 'added' else '#f44336'};
                    margin: 15px 0;
                    font-weight: bold;
                }}
                .permission {{
                    background-color: {'#e8f5e9' if action_type == 'added' else '#ffebee'};
                    padding: 10px;
                    border-radius: 3px;
                    margin: 10px 0;
                }}
                .button {{
                    display: inline-block;
                    background-color: {'#4CAF50' if action_type == 'added' else '#2196F3'};
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                    font-weight: bold;
                }}
                .button:hover {{
                    background-color: {'#45a049' if action_type == 'added' else '#1976D2'};
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>{'Added as Collaborator' if action_type == 'added' else 'Removed as Collaborator'}</h2>
            </div>
            
            <div class="content">
                <p>Hi <strong>{user_name}</strong>,</p>
                
                <p>You have been <strong>{action_type}</strong>{role_text} as a collaborator to the document:</p>
                
                <div class="document-title">
                    📄 {document_title}
                </div>
                
                {f'<div class="permission">Role: <strong>{role}</strong></div>' if role and action_type == 'added' else ''}
                
                <p>{access_message}</p>
                
                <a href="{button_url}" class="button">{button_text}</a>
                
                <div class="footer">
                    <p>Best regards,<br>
                    <strong>HRMS Team</strong></p>
                    
                    <p style="font-size: 10px; color: #999;">
                        This is an automated notification. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Prepare email data for queue
        email_data = {
            'subject': subject,
            'body': body,
            'from_email': 'HRMS Notifications <noreply@kavmails.net>',
            'to': [user.email],
            'metadata': {
                'type': 'collaboration',
                'action': action_type,
                'user_id': user_id,
                'document_id': document_id,
                'timestamp': time.time()
            }
        }
        
        # Add to queue (non-blocking)
        result = email_queue_manager.add_email_task(email_data)
        
        # print(f"[QUEUE] Email queued successfully. Queue result: {result}")
        # print(f"[QUEUE] Subject: {subject}")
        # print(f"[QUEUE] Recipient: {user.email}")
        # print(f"=== [END QUEUE] ===\n")
        
        return result  # Return True if queued successfully
        
    except Exception as e:
        print(f"\n=== [EMAIL QUEUE ERROR] ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"=== [END ERROR] ===\n")
        return False

def send_comment_notification(document_owner_id, commenter_id, document_id, document_title, comment_preview=None, document_type='rich'):
    """
    Queue notification when someone comments on a document
    """
    try:
        # print(f"\n=== [COMMENT EMAIL QUEUED] ===")
        # print(f"Document Owner ID: {document_owner_id}")
        # print(f"Commenter ID: {commenter_id}")
        
        # Get document owner details
        from profiles_api.models import HrmsUsers
        owner = HrmsUsers.objects.filter(id=document_owner_id).first()
        if not owner:
            print(f"ERROR: Document owner not found with id={document_owner_id}")
            return False
        
        if not owner.email:
            print(f"ERROR: Document owner has no email address")
            return False
        
        # print(f"Document Owner Email: {owner.email}")
        
        # Get commenter name
        commenter_name = get_user_display_name(commenter_id)
        # print(f"Commenter Name: {commenter_name}")
        
        # Get owner name
        owner_name = get_user_display_name(document_owner_id)
        # print(f"Owner Name: {owner_name}")
        
        # Generate document URL
        document_url = get_document_url(document_id, document_type)
        # print(f"Document URL: {document_url}")
        
        # Prepare email content
        subject = f"New comment on '{document_title[:50]}{'...' if len(document_title) > 50 else ''}'"
        
        comment_preview_text = ""
        if comment_preview:
            safe_preview = html.escape(comment_preview[:200])
            if len(comment_preview) > 200:
                safe_preview += "..."
            comment_preview_text = f"""
            <div class="comment-preview">
                "{safe_preview}"
            </div>
            """
        
        # Create HTML email
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #2196F3;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 0 0 5px 5px;
                    border: 1px solid #ddd;
                    border-top: none;
                }}
                .document-title {{
                    background-color: #e8f5e9;
                    padding: 15px;
                    border-left: 4px solid #4CAF50;
                    margin: 15px 0;
                    font-weight: bold;
                }}
                .comment-preview {{
                    background-color: #e3f2fd;
                    padding: 15px;
                    border-left: 4px solid #2196F3;
                    margin: 15px 0;
                    font-style: italic;
                    border-radius: 3px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #2196F3;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 15px;
                }}
                .button:hover {{
                    background-color: #1976D2;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>New Comment on Your Document</h2>
            </div>
            
            <div class="content">
                <p>Hi <strong>{owner_name}</strong>,</p>
                
                <p><strong>{commenter_name}</strong> has commented on your document:</p>
                
                <div class="document-title">
                    📄 {document_title}
                </div>
                
                {comment_preview_text}
                
                <p>To view the full comment and respond, please click the button below:</p>
                
                <a href="{document_url}" class="button">View Document & Comment</a>
                
                <p style="margin-top: 20px; font-size: 14px; color: #666;">
                    You can also access this document from your HRMS dashboard.
                </p>
                
                <div class="footer">
                    <p>Best regards,<br>
                    <strong>HRMS Team</strong></p>
                    
                    <p style="font-size: 10px; color: #999;">
                        This is an automated notification. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Prepare email data for queue
        email_data = {
            'subject': subject,
            'body': body,
            'from_email': 'HRMS Notifications <noreply@kavmails.net>',
            'to': [owner.email],
            'metadata': {
                'type': 'comment',
                'document_owner_id': document_owner_id,
                'commenter_id': commenter_id,
                'document_id': document_id,
                'timestamp': time.time()
            }
        }
        
        # Add to queue (non-blocking)
        result = email_queue_manager.add_email_task(email_data)
        
        # print(f"[QUEUE] Comment email queued successfully. Queue result: {result}")
        # print(f"[QUEUE] Subject: {subject}")
        # print(f"[QUEUE] Recipient: {owner.email}")
        # print(f"=== [END QUEUE] ===\n")
        
        return result  # Return True if queued successfully
        
    except Exception as e:
        print(f"\n=== [COMMENT EMAIL QUEUE ERROR] ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        # print(f"=== [END ERROR] ===\n")
        return False
    
    
    
    
    
    
    
    
def send_mention_notification(mentioned_user_id, mentioned_by_id, document_title, document_id=None):
    """
    Send notification when someone is mentioned in a document

    Parameters:
    - mentioned_user_id: ID of the user mentioned
    - mentioned_by_id: ID of the user who mentioned
    - document_title: Title of the document
    - document_id: ID of the document (for link generation)
    """
    try:
        # Get mentioned user details
        mentioned_user = HrmsUsers.objects.filter(id=mentioned_user_id).first()
        if not mentioned_user:
            return False
        
        # Get mentioned by user details
        mentioned_by = HrmsUsers.objects.filter(id=mentioned_by_id).first()
        mentioned_by_name = mentioned_by.first_name if mentioned_by else "Someone"
    
        # Get mentioned user employee details
        mentioned_employee = Employees.objects.filter(hrmsuser=mentioned_user, is_active=True).first()
        mentioned_name = mentioned_employee.first_name if mentioned_employee else mentioned_user.first_name
    
        # Prepare email content
        subject = f"You've been mentioned in '{document_title[:50]}{'...' if len(document_title) > 50 else ''}'"
    
        # Generate document link if ID is provided
        document_link = f"/documents/view/{document_id}" if document_id else "#"
    
        body = f"""
        <html>
        <body>
            <p>Hi {mentioned_name},</p>
        
            <p><strong>{mentioned_by_name}</strong> has mentioned you in a document:</p>
        
            <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #FF9800; margin: 15px 0;">
                <strong>{document_title}</strong>
            </div>
        
            <p>Click <a href="{document_link}">here</a> to view the document.</p>
        
            <p>Best regards,<br>
            HRMS Team</p>
        </body>
        </html>
        """
    
        # Send email
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email="noreply@kavmails.net",
            to=[mentioned_user.email],
        )
        email.content_subtype = "html"
        email.send()
    
        return True
    
    except Exception as e:
        print(f"Error sending mention notification: {str(e)}")
        return False


