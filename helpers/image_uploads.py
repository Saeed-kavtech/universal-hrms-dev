import os
from datetime import datetime

# function to upload profile image of users. 

def hrms_user_profile_upload_prev(instance, filename):
	name, extension = os.path.splitext(filename)
	now = datetime.now().strftime("%Y%m%d%H%M%S%f")
	image_name = str(now) + str(extension)
	return 'images/{filename}'.format(filename=image_name)

def hrms_user_profile_upload(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'images/' + str(now) + str(extension)
    return var

# organization logo image
def upload_to(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'organizations/' + str(now) + str(extension)
    return var

def upload_candidate_resume(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'candidate/' + str(now) + str(extension)
    return var

def upload_candidate_attachments(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'candidate/emails/attachments/' + str(now) + str(extension)
    return var

def upload_assessment_tests(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'assessments/' + str(now) + str(extension)
    return var

def upload_assessment_questions(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'assessments/questions/' + str(now) + str(extension)
    return var

def upload_employee_cnic(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'employees/cnic/' + str(now) + str(extension)
    return var

def upload_employee_passport(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'employees/passport/' + str(now) + str(extension)
    return var

def upload_employee_profile(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'employees/profile/' + str(now) + str(extension)
    return var

def upload_employee_attachments(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'employees/attachments/' + str(now) + str(extension)
    return var

def upload_employee_degrees(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'employees/degrees/' + str(now) + str(extension)
    return var

def upload_employee_experience(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'employees/experience/' + str(now) + str(extension)
    return var

def upload_course_applicant_attachments(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'course-applicant-emails/attachment/' + str(now) + str(extension)
    return var

def upload_gym_receipts(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'organization/gym/' + str(now) + str(extension)
    return var

def upload_medical_receipts(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'organization/medical/' + str(now) + str(extension)
    # print("var",var)
    return var

def upload_leave_attachments(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'organization/leave/' + str(now) + str(extension)
    return var

def upload_work_attachments(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'organization/work/' + str(now) + str(extension)
    return var

def upload_organization_attendance_files(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'organization/attendance/' + str(now) + str(extension)
    return var

def upload_manuals(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'manuals/manual/' + str(now) + str(extension)
    return var

def upload_kav_skills_resume(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'kav_skills/resume/' + str(now) + str(extension)
    return var

def upload_kav_skills_cover_letter(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'kav_skills/cover-letter/' + str(now) + str(extension)
    return var

def upload_course_skills_details(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'kav_skills/course-details/' + str(now) + str(extension)
    return var

def upload_certificate(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'certifyskills/certificate/' + str(now) + str(extension)
    # print("Var:",var)
    return var


def upload_certificate_receipt(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'certifyskills/certificate-receipt/' + str(now) + str(extension)
    # print("Var:",var)
    return var

def upload_training_receipt(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'training/training-receipt/' + str(now) + str(extension)
    # print("Var:",var)
    return var

def upload_assignment(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'training/assignment/' + str(now) + str(extension)
    # print("Var:",var)
    return var


def upload_by_employee_assignment(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'training/employee-assignmenet/' + str(now) + str(extension)
    # print("Var:",var)
    return var


def upload_kpis_attachments(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'kpis/attachments/' + str(now) + str(extension)
    # print("Var:",var)
    return var


def upload_tasks_attachments(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'tasks/attachments/' + str(now) + str(extension)
    # print("Var:",var)
    return var

def upload_datahive_files(instance, filename):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    extension = os.path.splitext(filename)[1]
    var = 'datahive/files/' + str(now) + str(extension)
    # print("Var:",var)
    return var