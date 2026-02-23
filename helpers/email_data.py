from profiles_api.utils import Util
from django.core.mail import EmailMessage

def requestEmailsFromEmployees(request_type, official_email):
    try:
        # result = {'status': 400, 'message': None, 'system_error_message': ''}
        body = f'{request_type} request has been generated' 
        data = {
            'subject': 'Request through ESS',
            'body':  body,
            'to_email': official_email,
        }
        
        Util.send_email(data)
        return None
    except Exception as e:
        print(str(e))
        return None
    

def requestEmailsFromEmployeesnontl(emp_name,subject,request_type, official_email,name):
    try:
        # result = {'status': 400, 'message': None, 'system_error_message': ''}
        body = f'''Hi {name},

                    {emp_name} has applied for {request_type}. Please review the request and take the necessary actions.
                    
                    Thank you,

                    HRMS''' 
        data = {
            'subject': subject,
            'body':  body,
            'to_email': official_email,
        }
        
        Util.send_email(data)
        return None
    except Exception as e:
        print(str(e))
        return None
    
def LeaveRequestEmailsFromEmployees(tl_name,emp_name,subject,request_type,official_email,cc_emial,date):
    try:
        # result = {'status': 400, 'message': None, 'system_error_message': ''}
        body=None

        if date is not None:
            body = f'''Hi {tl_name},

                    {emp_name} worked on {date} and has requested approval to add this to compensatory time. Please review the request and take the necessary actions.
                    
                    Thank you,

                    HRMS''' 
        # else:

        #     body = f'''Hi {tl_name},

        #                 {emp_name} has applied for {request_type}. Please review the request and take the necessary actions.
                        
        #                 Thank you,

        #                 HRMS''' 
        

        data = {
            'subject': subject,
            'body':  body,
            'to_email': official_email,
        }

        if official_email is not None :
            data['cc_email'] = cc_emial
        
        Util.send_email(data)
        return None
    except Exception as e:
        print(str(e))
        return None
    
def SimpleLeaveRequestEmailsFromEmployees(tl_name,
                                          emp_name,
                                          subject,
                                          request_type,
                                          cc_emial,
                                          official_email,
                                          date):
    try:
        # result = {'status': 400, 'message': None, 'system_error_message': ''}
        body=None

        if cc_emial is not None:
                    body = f'''Hi {tl_name},

                    {emp_name} has applied for {request_type} on {date}. Please review the request and take the necessary actions.
                        
                    Thank you,

                    HRMS''' 
        # else:

        #     body = f'''Hi {name},

        #             {emp_name} has applied for {request_type} on {date}. Please review the request and take the necessary actions.
                    
        #             Thank you,

        #             HRMS''' 
        

        data = {
            'subject': subject,
            'body':  body,
            'to_email': official_email,
        }

        if official_email is not None:
            data['cc_email'] = cc_emial
        
        Util.send_email(data)
        return None
    except Exception as e:
        print(str(e))
        return None
    

    
def WFHEmailsFromEmployees(tl_name,emp_name,subject, official_email,cc_email,date):
    try:
        # result = {'status': 400, 'message': None, 'system_error_message': ''}
        body = f'''Hi {tl_name},

                Just a heads up, {emp_name} will be working from home on {date}. If there are any specific arrangements 
                needed, please let them know.
                
                Best regards,
                
                HRMS
''' 
        data = {
            'subject': subject,
            'body':  body,
            'to_email': official_email,
        }

        if official_email is not None :
            data['cc_email'] = cc_email
        
        Util.send_email(data)
        return None
    except Exception as e:
        print(str(e))
        return None
    
def requestDecisionFromManagement(name,subject,request_type, decision_status,decision_reason,official_email):
    try:
        body=None

        if decision_reason is None:
            body = f'''Hi {name},

            Your {request_type} has been {decision_status}. If you have any questions or concerns, feel free to reach out.

            Best regards,
            Human Resources Department
            Kavtech Solutions'''

        else:

            body = f'''Hi {name},

            Your {request_type} has been {decision_status} because {decision_reason}. If you have any questions or concerns, feel free to reach out.

            Best regards,
            Human Resources Department
            Kavtech Solutions'''


        data = {
            'subject': subject,
            'body':  body,
            'to_email': official_email,
        }
        
        Util.send_email(data)
        return None
    except Exception as e:
        print(str(e))
        return None
    

def AttendanceEmailFromManagement(name,message,official_email):
    try:
        body = f'''Hi {name},

        It has come to our attention that {message}.
        Please ensure timely time entries to maintain accurate records

        Thank you,
        Human Resources Department
        Kavtech Solutions'''
        data = {
            'subject':' Time Logging Alert',
            'body':  body,
            'to_email': official_email,
        }
        
        Util.send_email(data)
        return None
    except Exception as e:
        print(str(e))
        return None
    
def notify_candidates_by_email(subject, body, to):
    try:
        email_data = {'is_send': None, 'email_error': None}
        email = EmailMessage(
            subject = subject,
            body = body,
            from_email = "noreply@kavmails.net",
            to = to,
        )
        # print("test")
        email.content_subtype = "html"
        email.send()
        return email_data
    except Exception as e:
        print(str(e))
        email_data['email_error'] = str(e)
        return email_data
    
def notify_candidates_and_admin_by_email(subject, body, to,cc):
    try:
        email_data = {'is_send': None, 'email_error': None}
        email = EmailMessage(
            subject = subject,
            body = body,
            from_email = "noreply@kavmails.net",
            to = to,
            cc=cc,
        )
        email.content_subtype = "html"
        email.send()
        return email_data
    except Exception as e:
        print(str(e))
        email_data['email_error'] = str(e)
        return email_data


# Training Emial 
def  PojectTrainingNotificationEmail(title,project_name,official_email):
    try:
        body = f'''Hi {project_name} Team,

        We wanted to inform you that a new "{title}" has been assigned to your project. Team members 
        need to participate and enhance their skills.
  
        Best Regards,
        HRMS'''
        data = {
            'subject': 'New Training Material is added to your project',
            'body':  body,
            'to_email': official_email,
        }
        
        Util.send_email(data)
        return None
    except Exception as e:
        print(str(e))
        return None
    
def TrainingStartNotificationEmail(title,stauts,emp_name,name,official_email):
    try:
        body = f'''Hi {name},

        This is to notify you that {emp_name} has {stauts} their "{title}". Please monitor their progress 
        and address any concerns.
           
        Best Regards,
        HRMS'''
        data = {
            'subject': 'Training Commencement Alert',
            'body':  body,
            'to_email': official_email,
        }
        
        Util.send_email(data)
        return None
    except Exception as e:
        print(str(e))
        return None
    
def AssignmentSubmissionNotificationEmail(title,emp_name,name,official_email):
    try:
        body = f'''Hi {name},

        Good news! {emp_name} has successfully submitted their "{title}" assignment. Kindly review 
        and provide feedback as necessary.
  
        Best Regards,
        HRMS'''
        data = {
            'subject': 'Assignment Submission Received',
            'body':  body,
            'to_email': official_email,
        }
        
        Util.send_email(data)
        return None
    except Exception as e:
        print(str(e))
        return None
    

#Meeting Emails
def SendMeetingMails(name,official_email,start_time,date,topic,join_url,id,password):
    try:
        body = f''' Hi {name} ,

        I hope this email finds you well.

        This is a reminder for our upcoming Zoom meeting scheduled for {date} at {start_time}.It's important that you attend and actively participate as we will be covering key topics that affect our work.
        
        Here are the details for the Zoom meeting:
        Meeting Link: {join_url}
        Meeting ID: {id}
        Password: {password}

        Please be on time and ensure you have a stable internet connection. If you have any questions or need assistance with Zoom, feel free to reach out to.

        Thank you, and I look forward to our meeting.
        
        Best regards,
        HRMS'''
        data = {
            'subject':f"Upcoming Zoom Meeting: {topic} on {date}",
            'body':  body,
            'to_email': official_email,
        }
        
        Util.send_email(data)
        return None
    except Exception as e:
        print(str(e))
        return None
    
    
    
def SendMeetMails(name,official_email,start_time,date,topic,join_url,id):
    try:
        body = f''' Hi {name} ,

        I hope this email finds you well.

        This is a reminder for our upcoming Zoom meeting scheduled for {date} at {start_time}.It's important that you attend and actively participate as we will be covering key topics that affect our work.
        
        Here are the details for the Zoom meeting:
        Meeting Link: {join_url}
        Meeting ID: {id}

        Please be on time and ensure you have a stable internet connection. If you have any questions or need assistance with Zoom, feel free to reach out to.

        Thank you, and I look forward to our meeting.
        
        Best regards,
        HRMS'''
        data = {
            'subject':f"Upcoming Zoom Meeting: {topic} on {date}",
            'body':  body,
            'to_email': official_email,
        }
        
        Util.send_email(data)
        return None
    except Exception as e:
        print(str(e))
        return None