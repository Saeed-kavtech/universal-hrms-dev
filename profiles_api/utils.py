from django.core.mail import EmailMessage
import requests

class Util:
    @staticmethod
    def send_email(data):
        print("Payload Data before sending:", data)
 
        try:
            response = requests.post(
                "http://blogpepper.com/hrms-mail/send_mail.php",
                json=data  # send as JSON like in Postman
            )
            response.raise_for_status()
            print("Email API Response:", response.text)
        except requests.exceptions.RequestException as e:
            print("Error sending email:", str(e))
