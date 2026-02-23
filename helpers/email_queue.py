import threading
import queue
import time
from django.core.mail import EmailMessage
from profiles_api.models import HrmsUsers
from employees.models import Employees
import html
from django.conf import settings

class EmailQueueManager:
    """Simple thread-safe email queue manager"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the email queue"""
        self.email_queue = queue.Queue()
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        # print("[EmailQueue] Email queue manager initialized and worker started")
    
    def add_email_task(self, email_data):
        """Add an email task to the queue"""
        try:
            self.email_queue.put(email_data)
            # print(f"[EmailQueue] Email task added to queue. Queue size: {self.email_queue.qsize()}")
            return True
        except Exception as e:
            # print(f"[EmailQueue] Failed to add email task: {str(e)}")
            return False
    
    def _process_queue(self):
        """Background worker that processes email queue"""
        # print("[EmailQueue] Email queue worker started")
        while self.is_running:
            try:
                # Wait for email task with timeout to allow graceful shutdown
                email_data = self.email_queue.get(timeout=1)
                
                # print(f"[EmailQueue] Processing email task. Queue size: {self.email_queue.qsize()}")
                
                try:
                    # Send the email
                    email = EmailMessage(
                        subject=email_data['subject'],
                        body=email_data['body'],
                        from_email=email_data.get('from_email', 'HRMS Notifications <noreply@kavmails.net>'),
                        to=email_data['to'],
                    )
                    email.content_subtype = "html"
                    
                    result = email.send()
                    # print(f"[EmailQueue] Email sent successfully to {email_data['to']}. Result: {result}")
                    
                except Exception as e:
                    print(f"[EmailQueue] Failed to send email: {str(e)}")
                    # Optionally retry failed emails (simple retry logic)
                    if email_data.get('retry_count', 0) < 2:
                        email_data['retry_count'] = email_data.get('retry_count', 0) + 1
                        print(f"[EmailQueue] Retrying email (attempt {email_data['retry_count']})")
                        time.sleep(2)  # Wait before retry
                        self.email_queue.put(email_data)
                
                # Mark task as done
                self.email_queue.task_done()
                
            except queue.Empty:
                # No tasks in queue, just continue
                continue
            except Exception as e:
                print(f"[EmailQueue] Queue worker error: {str(e)}")
                time.sleep(5)  # Wait before retry if there's an error
    
    def shutdown(self):
        """Gracefully shutdown the email queue"""
        print("[EmailQueue] Shutting down email queue...")
        self.is_running = False
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=10)
        print("[EmailQueue] Email queue shutdown complete")

# Global instance
email_queue_manager = EmailQueueManager()

def get_user_display_name(user_id):
    """Get display name for a user"""
    try:
        user = HrmsUsers.objects.filter(id=user_id).first()
        if not user:
            return "User"
        
        # Try Employees table first
        employee = Employees.objects.filter(hrmsuser=user, is_active=True).first()
        if employee:
            if employee.first_name:
                return employee.first_name
            elif hasattr(employee, 'name') and employee.name:
                return employee.name
        
        # Fallback to HrmsUsers
        if user.first_name:
            return user.first_name
        elif user.email:
            return user.email.split('@')[0]
        
        return "User"
    except Exception:
        return "User"

def get_document_url(document_id, document_type='rich'):
    """Generate proper document URL"""
    try:
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        
        if document_type == 'rich':
            return f"{base_url}/kavpedia/view/{document_id}"
        else:
            return f"{base_url}/documents/view/{document_id}"
    except Exception:
        return f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/employee/dashboard"