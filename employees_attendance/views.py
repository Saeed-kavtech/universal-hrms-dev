from rest_framework.decorators import permission_classes

import json
from django.conf import settings
from django.db import connection
import numpy as np
from django.utils import timezone
from django.utils.timezone import (
    is_naive,
    make_aware,
    get_current_timezone
)
from rest_framework import viewsets, status
from collections import defaultdict

from dateutil import parser
from django.core.serializers import serialize
from rest_framework.decorators import api_view, action
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import viewsets
from email_templates.models import EmailRecipients
from helpers.email_data import AttendanceEmailFromManagement, WFHEmailsFromEmployees
from helpers.status_messages import errorMessageWithData, exception, errorMessage, success, successMessage, successMessageWithData
from helpers.decode_token import decodeToken
from helpers.custom_permissions import IsAuthenticated, IsEmployeeOnly
from reimbursements.models import EmployeesOfficialHolidays,EmployeeLeaveDates,EmployeesLeaves, EmployeesWFHRequestDates
from employees.models import Employees
from .serializers import ( 
    EmployeesAttendanceEmailLogsSerializer, EmployeesAttendanceViewsetSerializers, AttendanceMachinesSerializers, 
    CUAttendanceMachineLogFilesSerializers, CUEmployeesAttendanceViewsetSerializers,
    EmployeesAttendanceLabelSerializers, EmployeesLabelSerializers, ScreenshotSerializer  
)
from .models import (
    AttendanceMachineslogs, EmployeesAttendance, AttendanceMachines, AttendanceMachineLogFiles, EmployeesAttendanceEmailLogs, EmployeesAttendanceLabel
)
from reimbursements.models import EmployeesWFHAllowance
import pytz
import datetime
import calendar
import pandas as pd
import csv
import os
import math
from zk import ZK, const
from django.db.models import Q
# from datetime import datetime, date, time
# Create your views here.
class EmployeesAttendanceViewset(viewsets.ModelViewSet):
    serializer_class = EmployeesAttendanceViewsetSerializers
    # def mark_attendnace(self,request,*args, **kwargs):
    #     try:
    #         zk = ZK('202.163.113.76', port=88, timeout=5, password=0, force_udp=False, ommit_ping=False)
    #         try:
    #             # connect to device
    #             conn = zk.connect()
    #             conn.set_attendance(uid=1, timestamp='2024-09-11 09:00:00')
    #             conn.disable_device()
    #         except Exception as e:
    #             print ("Process terminate : {}".format(e))
    #             return exception(e)
    #         finally:
    #             if conn:
    #                 conn.disconnect()
    #     except Exception as e:
    #       exception(e)


    def machine_attenadnace_data(self,request,*args, **kwargs):
        try:
            filename='attendance_job_log'
            log_to_file("Job started",filename)
            organization_id=self.kwargs['pk']
            current_date = datetime.datetime.today().date()
            current_time = datetime.datetime.now().time()  # Current time
            # Calculate one hour and ten minutes before the current time
            # Create a timedelta for 11 minutes
            time_delta = datetime.timedelta(minutes=16)  # Time difference of 16 minutes

            # Get the combined current date and time
            current_datetime = datetime.datetime.combine(current_date, current_time)

            # # Calculate 11 minutes earlier
            sixteen_minutes_prior = (current_datetime - time_delta).time()

            self=None
            conn = None
            data=None
            user_data = []
            # create ZK instance
            zk = ZK('202.163.113.76', port=88, timeout=5, password=0, force_udp=False, ommit_ping=False)
            try:
                # connect to device
                conn = zk.connect()
                data = conn.get_attendance()
                ser_no=conn.get_serialnumber()
                conn.disable_device()
            except Exception as e:
                print ("Process terminate : {}".format(e))
                log_to_file("Process terminate : {}".format(e),filename)
                return exception(e)
            finally:
                if conn:
                    conn.disconnect()
            
            attendance_list = []
            data = list(data)
            # print(data)
            # Use a for loop to parse each record and add to the list
            for record in data:
                record=str(record)
                clean_record = record.split(":", 1)[1].strip()
                attendance_data = parse_attendance(clean_record)
                # print(attendance_data["date"]==str(current_date))
                if attendance_data["date"]==str(current_date):
                    if str(sixteen_minutes_prior) <= attendance_data['time'] <= str(current_time):
                            attendance_list.append(attendance_data)

            attendance_list.sort(key=lambda x: (x['date'], x['time']))

            if not attendance_list:
               log_to_file("No data found from the machine",filename)
               return successMessage("No data found from the machine")

            
 
            df = pd.DataFrame(attendance_list)
            grouped = df.groupby("user_id")

            grouped_dict =[]
            
            


            # Loop through the groups and add to the dictionary
            
            for user_id, group in grouped:
                # Convert the group to a list of dictionaries
                        user_records = group.to_dict(orient='records')
                        # Create a dictionary with the user_id and corresponding data
                        user_data = {
                            "user_id": user_id,
                            "data": user_records
                        }
                        
                        # Append the dictionary to the list
                        grouped_dict.append(user_data)

            # Display or return the formatted data

            # return "Pass"

            for group in grouped_dict:
                    # Extract `user_id` and `data`
                    user_id = group["user_id"]
                    attendance_list = group["data"]
                    emp_query=Employees.objects.filter(id=user_id,organization=organization_id,is_active=True)
                    if not emp_query.exists():
                            continue
                    emp_id=emp_query.get()

                    for result in attendance_list:

                        if AttendanceMachineslogs.objects.filter( employee=emp_id,
                                                        date=result['date'],
                                                        time=result['time'],
                                                        mode=result['mode'],is_active=True).exists():
                            continue
                        else:
                                if result['state']==0:
                                    # if attendance already exists
                                    emp_attendance = EmployeesAttendance.objects.filter(employee=emp_id.id, date=result['date'])
                                    if emp_attendance.exists():
                                        emp_attendance_obj = emp_attendance.last()
                                        #Case to add multipul after 1 check in check out completed check in 
                                        if emp_attendance_obj.is_check_out == True and emp_attendance_obj.is_check_in == False:
                                                if emp_attendance_obj.check_out!=None and str(emp_attendance_obj.check_out)<result['time']:
                                                    attendance = EmployeesAttendance.objects.create(
                                                        employee = emp_id,
                                                        attendance_type = 'office',
                                                        date = result['date'],
                                                        is_check_in = True,
                                                        check_in = result['time'],
                                                        is_custom_time_set = True,
                                                        is_check_out = False,
                                                        is_active = True
                                                        )
                                                    create_attendance_log(emp_id, result, 'added',ser_no)
                                                    emp_attendance_object = attendance
                                                    attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)

                                                elif emp_attendance_obj.check_in==None and emp_attendance_obj.is_check_out!=None:
                                                    if str(emp_attendance_obj.check_out)>result['time']:
                                                        emp_attendance_obj.check_in = result['time']
                                                        emp_attendance_obj.save()
                                                        create_attendance_log(emp_id, result, 'added',ser_no)

                                            
                                        elif emp_attendance_obj.is_check_in == True and emp_attendance_obj.is_check_out == False:
                                            if emp_attendance_obj.attendance_type=='WFH':
                                                    attendance = EmployeesAttendance.objects.create(
                                                        employee = emp_id,
                                                        attendance_type = 'office',
                                                        date = result['date'],
                                                        is_check_in = True,
                                                        check_in = result['time'],
                                                        is_custom_time_set = True,
                                                        is_check_out = False,
                                                        is_active = True
                                                        )
                                                    create_attendance_log(emp_id, result, 'added',ser_no)
                                                    emp_attendance_object = attendance
                                                    attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)
                                            
                                            else:        
                                                    if not AttendanceMachineslogs.objects.filter( employee=emp_id,
                                                                        date=result['date'],
                                                                        time=result['time'],
                                                                        mode=result['mode'],
                                                                        state=0,is_active=True).exists():
                                                                        create_attendance_log(emp_id, result, 'skipped',ser_no)
                                                    continue
                                    
                                    else:
                                        attendance = EmployeesAttendance.objects.create(
                                        employee = emp_id,
                                        attendance_type = 'office',
                                        date = result['date'],
                                        is_check_in = True,
                                        check_in = result['time'],
                                        is_custom_time_set = True,
                                        is_check_out = False,
                                        is_active = True
                                        )
                                        create_attendance_log(emp_id, result, 'added',ser_no)
                                        
                                        emp_attendance_object = attendance
                                        
                                        attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)

                                elif result['state']==1:
                                    emp_attendance = EmployeesAttendance.objects.filter(
                                        employee=emp_id, 
                                        date=result['date'])
                                    # print(emp_attendance.last())
                                
                                    if emp_attendance.exists():
                                        emp_attendance_obj = emp_attendance.last()
                                        
                                        if emp_attendance_obj.is_check_out == True and emp_attendance_obj.is_check_in == False:
                                            if emp_attendance_obj.check_in!=None and emp_attendance_obj.check_out!=None:
                                                
                                                    # Convert times to datetime objects
                                                    format_str = '%H:%M:%S'  # Assuming time is in the format 'HH:MM:SS'
                                                    result_time = datetime.datetime.strptime(result['time'], format_str)
                                                    query_time = datetime.datetime.strptime(str(emp_attendance_obj.check_out), format_str)

                                                    # Calculate the difference
                                                    time_difference = result_time - query_time

                                                    if time_difference >= datetime.timedelta(hours=1):
                                                        attendance = EmployeesAttendance.objects.create(
                                                        employee = emp_id,
                                                        attendance_type = 'office',
                                                        date = result['date'],
                                                        is_check_in = False,
                                                        check_out = result['time'],
                                                        is_custom_time_set = True,
                                                        is_check_out = True,
                                                        is_active = True
                                                        )
                                                        create_attendance_log(emp_id, result, 'added',ser_no)
                                                        emp_attendance_object = attendance
                                                        attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)
                                                        
                                                    
                                                    else:
                                                        if not AttendanceMachineslogs.objects.filter( employee=emp_id,
                                                                date=result['date'],
                                                                time=result['time'],
                                                                mode=result['mode'],
                                                                state=1,is_active=True).exists():
                                                            create_attendance_log(emp_id, result, 'skipped',ser_no)
                                                        # print("Check-out",result)
                                                        
                                                        continue
                                            else:
                                                if not AttendanceMachineslogs.objects.filter( employee=emp_id,
                                                        date=result['date'],
                                                        time=result['time'],
                                                        mode=result['mode'],
                                                        state=1,is_active=True).exists():
                                                    create_attendance_log(emp_id, result, 'skipped',ser_no)
                                                # print("Check-out",result)
                                                continue

                                        else:
                                                    emp_attendance_obj.is_check_in = False
                                                    emp_attendance_obj.is_check_out = True
                                                    emp_attendance_obj.check_out = result['time']
                                                    emp_attendance_obj.save()
                                                    create_attendance_log(emp_id, result, 'added',ser_no)

                                    else:
                                        attendance = EmployeesAttendance.objects.create(
                                        employee = emp_id,
                                        attendance_type = 'office',
                                        date = result['date'],
                                        is_check_in = False,
                                        check_out = result['time'],
                                        is_custom_time_set = True,
                                        is_check_out = True,
                                        
                                        is_active = True
                                        )
                                        create_attendance_log(emp_id, result, 'added',ser_no)
                                        emp_attendance_object = attendance
                                        attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)
                
            # print(attendance_list)
            log_to_file("Job completed successfully",filename)
            
            return success(grouped_dict)
            

        except Exception as e:
            return exception(e)
    
    def current_date_machine_attenadnace_data(self,request,*args, **kwargs):
        try:
            filename='current_date_attendance_job_log'
            log_to_file("Job started",filename)
            organization_id=self.kwargs['pk']
            current_date = datetime.datetime.today().date()
            
            previous_date = current_date 
            

            self=None
            conn = None
            data=None
            user_data = []
            # create ZK instance
            zk = ZK('202.163.113.76', port=88, timeout=15, password=0, force_udp=False, ommit_ping=False)
            try:
                # connect to device
                conn = zk.connect()
                data = conn.get_attendance()
                ser_no=conn.get_serialnumber()
                conn.disable_device()
            except Exception as e:
                print ("Process terminate : {}".format(e))
                log_to_file("Process terminate : {}".format(e),filename)
                return exception(e)
            finally:
                if conn:
                    conn.disconnect()
            
            attendance_list = []
            data = list(data)
            # print(data)
            # Use a for loop to parse each record and add to the list
            for record in data:
                record=str(record)
                clean_record = record.split(":", 1)[1].strip()
                attendance_data = parse_attendance(clean_record)
                # print(attendance_data["date"]==str(current_date))
                if attendance_data["date"]==str(previous_date):
                            attendance_list.append(attendance_data)

            attendance_list.sort(key=lambda x: (x['date'], x['time']))

            

            if not attendance_list:
               log_to_file("No data found from the machine",filename)
               return successMessage("No data found from the machine")

            
 
            df = pd.DataFrame(attendance_list)
            grouped = df.groupby("user_id")

            grouped_dict =[]
            
            


            # Loop through the groups and add to the dictionary
            
            for user_id, group in grouped:
                # Convert the group to a list of dictionaries
                        user_records = group.to_dict(orient='records')
                    
                        # Create a dictionary with the user_id and corresponding data
                        user_data = {
                            "user_id": user_id,
                            "data": user_records
                        }
                        
                        # Append the dictionary to the list
                        grouped_dict.append(user_data)

            # Display or return the formatted data

            # return "Pass"

            for group in grouped_dict:
                    # Extract `user_id` and `data`
                    user_id = group["user_id"]
                    attendance_list = group["data"]
                    emp_query=Employees.objects.filter(id=user_id,organization=organization_id,is_active=True)
                    if not emp_query.exists():
                            continue
                    emp_id=emp_query.get()

                    for result in attendance_list:

                        if AttendanceMachineslogs.objects.filter( employee=emp_id,
                                                        date=result['date'],
                                                        time=result['time'],
                                                        mode=result['mode'],is_active=True).exists():
                            continue
                        else:
                                if result['state']==0:
                                    # if attendance already exists
                                    emp_attendance = EmployeesAttendance.objects.filter(employee=emp_id.id, date=result['date'])
                                    if emp_attendance.exists():
                                        emp_attendance_obj = emp_attendance.last()
                                        #Case to add multipul after 1 check in check out completed check in 
                                        if emp_attendance_obj.is_check_out == True and emp_attendance_obj.is_check_in == False:
                                                if emp_attendance_obj.check_out!=None and str(emp_attendance_obj.check_out)<result['time']:
                                                    attendance = EmployeesAttendance.objects.create(
                                                        employee = emp_id,
                                                        attendance_type = 'office',
                                                        date = result['date'],
                                                        is_check_in = True,
                                                        check_in = result['time'],
                                                        is_custom_time_set = True,
                                                        is_check_out = False,
                                                        is_active = True
                                                        )
                                                    create_attendance_log(emp_id, result, 'added',ser_no)
                                                    emp_attendance_object = attendance
                                                    attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)

                                                elif emp_attendance_obj.check_in==None and emp_attendance_obj.is_check_out!=None:
                                                    if str(emp_attendance_obj.check_out)>result['time']:
                                                        emp_attendance_obj.check_in = result['time']
                                                        emp_attendance_obj.save()
                                                        create_attendance_log(emp_id, result, 'added',ser_no)

                                            
                                        elif emp_attendance_obj.is_check_in == True and emp_attendance_obj.is_check_out == False:
                                            if emp_attendance_obj.attendance_type=='WFH':
                                                    attendance = EmployeesAttendance.objects.create(
                                                        employee = emp_id,
                                                        attendance_type = 'office',
                                                        date = result['date'],
                                                        is_check_in = True,
                                                        check_in = result['time'],
                                                        is_custom_time_set = True,
                                                        is_check_out = False,
                                                        is_active = True
                                                        )
                                                    create_attendance_log(emp_id, result, 'added',ser_no)
                                                    emp_attendance_object = attendance
                                                    attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)
                                            
                                            else:        
                                                    if not AttendanceMachineslogs.objects.filter( employee=emp_id,
                                                                        date=result['date'],
                                                                        time=result['time'],
                                                                        mode=result['mode'],
                                                                        state=0,is_active=True).exists():
                                                                        create_attendance_log(emp_id, result, 'skipped',ser_no)
                                                    continue
                                    
                                    else:
                                        attendance = EmployeesAttendance.objects.create(
                                        employee = emp_id,
                                        attendance_type = 'office',
                                        date = result['date'],
                                        is_check_in = True,
                                        check_in = result['time'],
                                        is_custom_time_set = True,
                                        is_check_out = False,
                                        is_active = True
                                        )
                                        create_attendance_log(emp_id, result, 'added',ser_no)
                                        
                                        emp_attendance_object = attendance
                                        
                                        attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)

                                elif result['state']==1:
                                    emp_attendance = EmployeesAttendance.objects.filter(
                                        employee=emp_id, 
                                        date=result['date'])
                                    # print(emp_attendance.last())
                                
                                    if emp_attendance.exists():
                                        emp_attendance_obj = emp_attendance.last()
                                        
                                        if emp_attendance_obj.is_check_out == True and emp_attendance_obj.is_check_in == False:
                                            if emp_attendance_obj.check_in!=None and emp_attendance_obj.check_out!=None:
                                                
                                                    # Convert times to datetime objects
                                                    format_str = '%H:%M:%S'  # Assuming time is in the format 'HH:MM:SS'
                                                    result_time = datetime.datetime.strptime(result['time'], format_str)
                                                    query_time = datetime.datetime.strptime(str(emp_attendance_obj.check_out), format_str)

                                                    # Calculate the difference
                                                    time_difference = result_time - query_time

                                                    if time_difference >= datetime.timedelta(hours=1):
                                                        attendance = EmployeesAttendance.objects.create(
                                                        employee = emp_id,
                                                        attendance_type = 'office',
                                                        date = result['date'],
                                                        is_check_in = False,
                                                        check_out = result['time'],
                                                        is_custom_time_set = True,
                                                        is_check_out = True,
                                                        is_active = True
                                                        )
                                                        create_attendance_log(emp_id, result, 'added',ser_no)
                                                        emp_attendance_object = attendance
                                                        attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)
                                                        
                                                    
                                                    else:
                                                        if not AttendanceMachineslogs.objects.filter( employee=emp_id,
                                                                date=result['date'],
                                                                time=result['time'],
                                                                mode=result['mode'],
                                                                state=1,is_active=True).exists():
                                                            create_attendance_log(emp_id, result, 'skipped',ser_no)
                                                        # print("Check-out",result)
                                                        
                                                        continue
                                            else:
                                                if not AttendanceMachineslogs.objects.filter( employee=emp_id,
                                                        date=result['date'],
                                                        time=result['time'],
                                                        mode=result['mode'],
                                                        state=1,is_active=True).exists():
                                                    create_attendance_log(emp_id, result, 'skipped',ser_no)
                                                # print("Check-out",result)
                                                continue

                                        else:
                                                    emp_attendance_obj.is_check_in = False
                                                    emp_attendance_obj.is_check_out = True
                                                    emp_attendance_obj.check_out = result['time']
                                                    emp_attendance_obj.save()
                                                    create_attendance_log(emp_id, result, 'added',ser_no)

                                    else:
                                        attendance = EmployeesAttendance.objects.create(
                                        employee = emp_id,
                                        attendance_type = 'office',
                                        date = result['date'],
                                        is_check_in = False,
                                        check_out = result['time'],
                                        is_custom_time_set = True,
                                        is_check_out = True,
                                        
                                        is_active = True
                                        )
                                        create_attendance_log(emp_id, result, 'added',ser_no)
                                        emp_attendance_object = attendance
                                        attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)
                
                
            # print(attendance_list)
            log_to_file("Job completed successfully",filename)
            
            return success(grouped_dict)
            

        except Exception as e:
            return exception(e)        
    def previous_date_machine_attenadnace_data(self,request,*args, **kwargs):
        try:
            filename='previous_date_attendance_job_log'
            log_to_file("Job started",filename)
            organization_id=self.kwargs['pk']
            current_date = datetime.datetime.today().date()
           # Check if previous_date is passed in query params
            previous_date_param = request.GET.get('previous_date')

            if previous_date_param:
                # Convert query param string to date
                previous_date = datetime.datetime.strptime(previous_date_param, "%Y-%m-%d").date()
            else:
                # Default to previous day
                previous_date = current_date - datetime.timedelta(days=1)
            

            self=None
            conn = None
            data=None
            user_data = []
            # create ZK instance
            zk = ZK('202.163.113.76', port=88, timeout=5, password=0, force_udp=False, ommit_ping=False)
            try:
                # connect to device
                conn = zk.connect()
                data = conn.get_attendance()
                ser_no=conn.get_serialnumber()
                conn.disable_device()
            except Exception as e:
                print ("Process terminate : {}".format(e))
                log_to_file("Process terminate : {}".format(e),filename)
                return exception(e)
            finally:
                if conn:
                    conn.disconnect()
            
            attendance_list = []
            data = list(data)
            # print(data)
            # Use a for loop to parse each record and add to the list
            for record in data:
                record=str(record)
                clean_record = record.split(":", 1)[1].strip()
                attendance_data = parse_attendance(clean_record)
                # print(attendance_data["date"]==str(current_date))
                if attendance_data["date"]==str(previous_date):
                            attendance_list.append(attendance_data)

            attendance_list.sort(key=lambda x: (x['date'], x['time']))

            

            if not attendance_list:
               log_to_file("No data found from the machine",filename)
               return successMessage("No data found from the machine")

            
 
            df = pd.DataFrame(attendance_list)
            grouped = df.groupby("user_id")

            grouped_dict =[]
            
            


            # Loop through the groups and add to the dictionary
            
            for user_id, group in grouped:
                # Convert the group to a list of dictionaries
                        user_records = group.to_dict(orient='records')
                    
                        # Create a dictionary with the user_id and corresponding data
                        user_data = {
                            "user_id": user_id,
                            "data": user_records
                        }
                        
                        # Append the dictionary to the list
                        grouped_dict.append(user_data)

            # Display or return the formatted data

            # return "Pass"

            for group in grouped_dict:
                    # Extract `user_id` and `data`
                    user_id = group["user_id"]
                    attendance_list = group["data"]
                    emp_query=Employees.objects.filter(id=user_id,organization=organization_id,is_active=True)
                    if not emp_query.exists():
                            continue
                    emp_id=emp_query.get()

                    for result in attendance_list:

                        if AttendanceMachineslogs.objects.filter( employee=emp_id,
                                                        date=result['date'],
                                                        time=result['time'],
                                                        mode=result['mode'],is_active=True).exists():
                            continue
                        else:
                                if result['state']==0:
                                    # if attendance already exists
                                    emp_attendance = EmployeesAttendance.objects.filter(employee=emp_id.id, date=result['date'])
                                    if emp_attendance.exists():
                                        emp_attendance_obj = emp_attendance.last()
                                        #Case to add multipul after 1 check in check out completed check in 
                                        if emp_attendance_obj.is_check_out == True and emp_attendance_obj.is_check_in == False:
                                                if emp_attendance_obj.check_out!=None and str(emp_attendance_obj.check_out)<result['time']:
                                                    attendance = EmployeesAttendance.objects.create(
                                                        employee = emp_id,
                                                        attendance_type = 'office',
                                                        date = result['date'],
                                                        is_check_in = True,
                                                        check_in = result['time'],
                                                        is_custom_time_set = True,
                                                        is_check_out = False,
                                                        is_active = True
                                                        )
                                                    create_attendance_log(emp_id, result, 'added',ser_no)
                                                    emp_attendance_object = attendance
                                                    attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)

                                                elif emp_attendance_obj.check_in==None and emp_attendance_obj.is_check_out!=None:
                                                    if str(emp_attendance_obj.check_out)>result['time']:
                                                        emp_attendance_obj.check_in = result['time']
                                                        emp_attendance_obj.save()
                                                        create_attendance_log(emp_id, result, 'added',ser_no)

                                            
                                        elif emp_attendance_obj.is_check_in == True and emp_attendance_obj.is_check_out == False:
                                            if emp_attendance_obj.attendance_type=='WFH':
                                                    attendance = EmployeesAttendance.objects.create(
                                                        employee = emp_id,
                                                        attendance_type = 'office',
                                                        date = result['date'],
                                                        is_check_in = True,
                                                        check_in = result['time'],
                                                        is_custom_time_set = True,
                                                        is_check_out = False,
                                                        is_active = True
                                                        )
                                                    create_attendance_log(emp_id, result, 'added',ser_no)
                                                    emp_attendance_object = attendance
                                                    attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)
                                            
                                            else:        
                                                    if not AttendanceMachineslogs.objects.filter( employee=emp_id,
                                                                        date=result['date'],
                                                                        time=result['time'],
                                                                        mode=result['mode'],
                                                                        state=0,is_active=True).exists():
                                                                        create_attendance_log(emp_id, result, 'skipped',ser_no)
                                                    continue
                                    
                                    else:
                                        attendance = EmployeesAttendance.objects.create(
                                        employee = emp_id,
                                        attendance_type = 'office',
                                        date = result['date'],
                                        is_check_in = True,
                                        check_in = result['time'],
                                        is_custom_time_set = True,
                                        is_check_out = False,
                                        is_active = True
                                        )
                                        create_attendance_log(emp_id, result, 'added',ser_no)
                                        
                                        emp_attendance_object = attendance
                                        
                                        attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)

                                elif result['state']==1:
                                    emp_attendance = EmployeesAttendance.objects.filter(
                                        employee=emp_id, 
                                        date=result['date'])
                                    # print(emp_attendance.last())
                                
                                    if emp_attendance.exists():
                                        emp_attendance_obj = emp_attendance.last()
                                        
                                        if emp_attendance_obj.is_check_out == True and emp_attendance_obj.is_check_in == False:
                                            if emp_attendance_obj.check_in!=None and emp_attendance_obj.check_out!=None:
                                                
                                                    # Convert times to datetime objects
                                                    format_str = '%H:%M:%S'  # Assuming time is in the format 'HH:MM:SS'
                                                    result_time = datetime.datetime.strptime(result['time'], format_str)
                                                    query_time = datetime.datetime.strptime(str(emp_attendance_obj.check_out), format_str)

                                                    # Calculate the difference
                                                    time_difference = result_time - query_time

                                                    if time_difference >= datetime.timedelta(hours=1):
                                                        attendance = EmployeesAttendance.objects.create(
                                                        employee = emp_id,
                                                        attendance_type = 'office',
                                                        date = result['date'],
                                                        is_check_in = False,
                                                        check_out = result['time'],
                                                        is_custom_time_set = True,
                                                        is_check_out = True,
                                                        is_active = True
                                                        )
                                                        create_attendance_log(emp_id, result, 'added',ser_no)
                                                        emp_attendance_object = attendance
                                                        attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)
                                                        
                                                    
                                                    else:
                                                        if not AttendanceMachineslogs.objects.filter( employee=emp_id,
                                                                date=result['date'],
                                                                time=result['time'],
                                                                mode=result['mode'],
                                                                state=1,is_active=True).exists():
                                                            create_attendance_log(emp_id, result, 'skipped',ser_no)
                                                        # print("Check-out",result)
                                                        
                                                        continue
                                            else:
                                                if not AttendanceMachineslogs.objects.filter( employee=emp_id,
                                                        date=result['date'],
                                                        time=result['time'],
                                                        mode=result['mode'],
                                                        state=1,is_active=True).exists():
                                                    create_attendance_log(emp_id, result, 'skipped',ser_no)
                                                # print("Check-out",result)
                                                continue

                                        else:
                                                    emp_attendance_obj.is_check_in = False
                                                    emp_attendance_obj.is_check_out = True
                                                    emp_attendance_obj.check_out = result['time']
                                                    emp_attendance_obj.save()
                                                    create_attendance_log(emp_id, result, 'added',ser_no)

                                    else:
                                        attendance = EmployeesAttendance.objects.create(
                                        employee = emp_id,
                                        attendance_type = 'office',
                                        date = result['date'],
                                        is_check_in = False,
                                        check_out = result['time'],
                                        is_custom_time_set = True,
                                        is_check_out = True,
                                        
                                        is_active = True
                                        )
                                        create_attendance_log(emp_id, result, 'added',ser_no)
                                        emp_attendance_object = attendance
                                        attendance_labels(self, emp_attendance_object,emp_id.hrmsuser)
                
                
            # print(attendance_list)
            log_to_file("Job completed successfully",filename)
            
            return success(grouped_dict)
            

        except Exception as e:
            return exception(e)

    def machine_attenadnace_check_in(self,request,*args, **kwargs):
        try:
            organization_id=self.kwargs['pk']
            current_date = datetime.datetime.today().date()
            
            get_missing_check_in=EmployeesAttendance.objects.filter(employee__organization=organization_id,is_active=True,date=current_date,check_in__isnull=True,check_out__isnull=False,is_check_in=False,is_check_out=True)
            
            if not get_missing_check_in.exists():
                return success("No data found")

            # for result in attendance_list:
            #         if result['state']==0:
            #             # if attendance already exists
            #             emp_attendance = EmployeesAttendance.objects.filter(employee=emp_id.id, date=result['date'])
            #             if emp_attendance.exists():
            #                 emp_attendance_obj = emp_attendance.last()
            #                 if emp_attendance_obj.is_check_out == True and emp_attendance_obj.is_check_in == False:
            #                     if emp_attendance_obj.check_in==None and emp_attendance_obj.is_check_out!=None:
            #                         query=AttendanceMachineslogs.objects.filter(employee=emp_id,date=result['date'],state=1,status='added',is_active=True).last()
            #                         if emp_attendance_obj.check_out<result['time']:
            #                             return errorMessage('Checked in time must be less then check out time')
            #                         emp_attendance_obj.check_in = ""
            #                         emp_attendance_obj.save()
            #                         return successMessage('Check in successfully')
            #                 #Case to add multipul after 1 check in check out completed check in 
            #                 if emp_attendance_obj.is_check_out == True and emp_attendance_obj.is_check_in == False:
            #                         query=AttendanceMachineslogs.objects.filter(employee=emp_id,date=result['date'],state=1,status='added',is_active=True).last()
            #                         if query is not None and str(query.time)<result['time']:
            #                             attendance = EmployeesAttendance.objects.create(
            #                                 employee = emp_id,
            #                                 attendance_type = 'office',
            #                                 date = result['date'],
            #                                 is_check_in = True,
            #                                 check_in = result['time'],
            #                                 is_custom_time_set = True,
            #                                 is_check_out = False,
            #                                 is_active = True
            #                                 )
            print(get_missing_check_in.values())
            return success(get_missing_check_in.values())
            

        except Exception as e:
            return exception(e)

    def attendance_report(self,request,*args, **kwargs):
        try:
            organization_id = self.kwargs['organization_id']

            required_fields = ['start_date','end_date']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData(
                    'make sure you have added all the required fields:','start_date,end_date'
                   
                )

            start_date=request.data['start_date']
            end_date=request.data['end_date']
            query_data=custom_query(start_date,end_date,start_date,end_date,organization_id)
            start_date = np.datetime64(start_date)
            end_date = np.datetime64(end_date)
            total_working_days = np.busday_count(start_date, end_date) + 1 if np.is_busday(start_date) and np.is_busday(end_date) else np.busday_count(start_date, end_date)
            data={
            'total_working_days':total_working_days,
            'query_data':query_data,
            }
            

            return successMessageWithData('Success',data)

        except Exception as e:
            return exception(e)   
    
    def attendance_report_employee(self,request,*args, **kwargs):
        try:
            employee_id = decodeToken(self, self.request)['employee_id']
            organization_id = decodeToken(self, self.request)['organization_id']
            required_fields = ['start_date','end_date']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData(
                    'make sure you have added all the required fields:','start_date,end_date'
                   
                )

            start_date=request.data['start_date']
            end_date=request.data['end_date']
            query_data=custom_query_employee(start_date,end_date,start_date,end_date,employee_id,organization_id)
            start_date = np.datetime64(start_date)
            end_date = np.datetime64(end_date)
            total_working_days = np.busday_count(start_date, end_date) + 1 if np.is_busday(start_date) and np.is_busday(end_date) else np.busday_count(start_date, end_date)
            data={
            'total_working_days':total_working_days,
            'query_data':query_data,
            }
            

            return successMessageWithData('Success',data)

        except Exception as e:
            return exception(e)   
    

    def list(self, request, *args, **kwargs):
        try: 
            organization_id = self.kwargs['organization_id']
            emp_code = self.kwargs['emp_code']

            # checks if active employee exists or not
            emp_query = Employees.objects.filter(emp_code=emp_code, organization=organization_id)
            if not emp_query.exists():
                return errorMessage('Employee does not exists')
            elif not emp_query.filter(is_active=True):
                return errorMessage('Employee is deactivated')
            

            # Get the current date
            current_date = datetime.date.today()

            # Calculate the date 7 days ago
            seven_days_ago = current_date - datetime.timedelta(days=7)
        
            # Filter the attendance records for the employee in the last 7 days
            emp_attendance = EmployeesAttendance.objects.filter(employee__emp_code=emp_code, 
                                                                employee__organization=organization_id, 
                                                                date__range=[seven_days_ago, current_date],
                                                                ).order_by('-id')

            # Serialize the attendance data
            serializer = EmployeesAttendanceViewsetSerializers(emp_attendance, many=True)

            # Return the serialized data
            return success(serializer.data)
        except Exception as e:
            return exception(e) 

    def check_in(self, request, *args, **kwargs):
        try:
            organization_id = self.kwargs['organization_id']
            emp_code = self.kwargs['emp_code']
            
            #checks if active employee exists or not
            emp_query = Employees.objects.filter(emp_code=emp_code, organization=organization_id)
            if not emp_query.exists():
                return errorMessage('Employee does not exists')
            elif not emp_query.filter(is_active=True).exists():
                return errorMessage('Employee is deactivated')
            elif not emp_query.filter(emp_code=emp_code).exists():
                return errorMessage('Employee code is not correct')
            
            emp_obj = Employees.objects.get(emp_code=emp_code, organization=organization_id)

            # if attendance already exists
            emp_attendance = EmployeesAttendance.objects.filter(employee=emp_obj.id, date=datetime.date.today())
            if emp_attendance.exists():
                emp_attendance_obj = emp_attendance.last()
                # if emp is already checked in or checkout is true
                if emp_attendance_obj.is_check_in == True:
                    return successMessage('Employee is already checked in')
                elif emp_attendance_obj.is_check_out == False:
                    return errorMessage('checkout the employee first')   

    
            pk_tz = pytz.timezone('Asia/Karachi')
            attendance = EmployeesAttendance.objects.create(
                employee = emp_obj,
                attendance_type = 'office',
                date = datetime.date.today(),
                is_check_in = True,
                check_in = datetime.datetime.now(pk_tz).time().strftime('%H:%M:%S'),
                is_check_out = False,
                is_active = True
            )
            attendance.save()
            serializer = EmployeesAttendanceViewsetSerializers(attendance, many=False)
            return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'Check in successfully', 'system_error_message': ''})
            
        except Exception as e:
            return exception(e)
        
    def check_out(self, request, *args, **kwargs):
        try:
            organization_id = self.kwargs['organization_id']
            emp_code = self.kwargs['emp_code']
            
            #checks if active employee exists or not
            emp_query = Employees.objects.filter(emp_code=emp_code, organization=organization_id)
            if not emp_query.exists():
                return errorMessage('Employee does not exists')
            elif not emp_query.filter(is_active=True).exists():
                return errorMessage('Employee is deactivated')
            elif not emp_query.filter(emp_code=emp_code).exists():
                return errorMessage('Employee code is not correct')
            
            emp_obj = Employees.objects.get(emp_code=emp_code, organization=organization_id)
            emp_id = emp_obj.id
            pk_tz = pytz.timezone('Asia/Karachi')
            emp_attendance = EmployeesAttendance.objects.filter(employee=emp_id, date=datetime.date.today())
            if emp_attendance.exists():
                emp_attendance_obj = emp_attendance.last()
                if emp_attendance_obj.is_check_out == True:
                    return successMessage('Employee is already checked out')
                elif emp_attendance_obj.is_check_in == False:
                    return errorMessage('checkin the employee first')   
                elif emp_attendance_obj.is_check_in == True and emp_attendance_obj.is_check_out == False:
                    emp_attendance_obj.is_check_in=False
                    emp_attendance_obj.is_check_out=True
                    emp_attendance_obj.check_out=datetime.datetime.now(pk_tz).time().strftime('%H:%M:%S')
                    emp_attendance_obj.save()
                    serializer = EmployeesAttendanceViewsetSerializers(emp_attendance_obj)
                    return Response({'status': 200, 'system_status': 200, 'data': serializer.data, 'message': 'checkout successfully', 'system_error_message': ''})
            
            return errorMessage('Employee cannot be checkout. As the employee has not checked in today')                     
        except Exception as e:
            return exception(e)
        

    def employee_attendance_email(self,request,*args, **kwargs):
        try:
            
            # token_data = decodeToken(self, self.request)
            # organization_id = token_data['organization_id']
            organization_id=self.kwargs['pk']
            employees=Employees.objects.filter(organization=organization_id,is_active=True)
            last_three_dates = []
            today = datetime.datetime.now().date()

            # Check if today is a weekend
            if today.weekday() >= 5:  # Saturday or Sunday
            # Adjust today to Friday to skip the weekend
                today = today - datetime.timedelta(days=today.weekday() - 4)

            # Generate past three weekdays excluding today
            
            while len(last_three_dates) < 3:
            # Move to the previous day
                today -= datetime.timedelta(days=1)
                # Only include weekdays
                if today.weekday() < 5:  # Monday to Friday
                    last_three_dates.append(today.strftime('%Y-%m-%d'))

            new_dates_list = [date for date in last_three_dates if not EmployeesOfficialHolidays.objects.filter(organization=organization_id, date=date, is_active=True).exists()]


            
            # print(formatted_dates)
            missing_attendance = []
            # Fetch employees
            employees = Employees.objects.filter(organization=organization_id, is_active=True)
            
            
            
            for emp in employees:
                email_send=EmployeesAttendanceEmailLogs.objects.filter(employee=emp,date=today,email_sended=True,is_active=True)
                if email_send.exists():
                    continue
                # has_check_in = False
                consecutive_missing_check_ins = 0
                missing_check_ins = []
                missing_check_outs = []
                missing_message=''
                for date in new_dates_list:
                    leave_date_check=EmployeeLeaveDates.objects.filter(date=date,employee_leave__employee=emp,employee_leave__status='approved',is_active=True,employee_leave__is_active=True)
                    
                    if leave_date_check.exists():
                        continue

                    attendance_records = EmployeesAttendance.objects.filter(employee=emp, date=date, is_active=True)
                    
                    if attendance_records.exists():
                        # has_check_in = True
                        for attendance_record in attendance_records:
                            if not attendance_record.is_check_out:
                                missing_check_outs.append(date)
                    else:
                        missing_check_ins.append(date)
                        consecutive_missing_check_ins += 1

                if consecutive_missing_check_ins == len(last_three_dates):
                    missing_message = 'you haven\'t logged your working hours for the past three consecutive days'
                
                else:
                    if missing_check_ins:
                        missing_message = ', '.join([f"check-in missing of {date}" for date in missing_check_ins])
                    if missing_check_outs:
                        missing_message += ', ' + ', '.join([f"check-out missing of {date}" for date in missing_check_outs])
                if missing_message:
                    # print("Test",missing_message)
                    AttendanceEmailFromManagement(emp.name,missing_message,emp.official_email)
                    EmployeesAttendanceEmailLogs.objects.create(
                                employee=emp,
                                message=missing_message,
                                date=today ,
                                email_sended=True
                                )

                    missing_attendance.append({
                        'employee_id': emp.id,
                        'employee_name': emp.name,
                        'employee_email': emp.official_email,
                        'missing_message': missing_message
                    })
            
            return successMessage("Success")
        except Exception as e:
            return exception(e)
        
    def attendance_email_log(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, request)
            organization_id = token_data['organization_id']
            # print(organization_id)
            if 'date' not in request.data:
                return errorMessage("Date field is required")
            
            date=request.data['date']

            query=EmployeesAttendanceEmailLogs.objects.filter(date=date,employee__organization=organization_id,email_sended=True,is_active=True)

            serializer=EmployeesAttendanceEmailLogsSerializer(query,many=True)
            
            return success(serializer.data)

        except Exception as e:
            return exception(e)
    

class HrmsEmployeesAttendanceViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    from django.db.models import Q

    def list(self, request, *args, **kwargs):
        try: 
            token_data = decodeToken(self, request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']

            current_date = datetime.date.today()
            seven_days_ago = current_date - datetime.timedelta(days=7)

            emp_attendance = EmployeesAttendance.objects.filter(
                employee=employee_id,
                employee__organization=organization_id,
                date__range=[seven_days_ago, current_date]
            ).filter(
                Q(is_active=True) | Q(is_check_out=True)
            ).order_by('-id')

            serializer = EmployeesAttendanceViewsetSerializers(emp_attendance, many=True)
            return success(serializer.data)
        
        except Exception as e:
            return exception(e)
 
        
    from django.db.models import Q

    def emp_attendance_list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            employee_id = request.data.get('employee', None)
            if employee_id is None:
                employee_id = token_data['employee_id']

            current_date = datetime.date.today()
            month = request.data.get('month', current_date.month)
            year = request.data.get('year', current_date.year)

            query = EmployeesAttendance.objects.filter(
                employee=employee_id,
                employee__organization=organization_id,
                date__month=month,
                date__year=year
            ).filter(
                Q(is_active=True) | Q(is_check_out=True)
            ).order_by('date')

            serializer = EmployeesAttendanceViewsetSerializers(query, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)


    # def emp_check_in(self, request, *args, **kwargs):
    #     try:
    #         # Decode token
    #         token_data = decodeToken(self, request)
    #         organization_id = token_data['organization_id']
    #         employee_id = token_data['employee_id']
    #         user = request.user

    #         # Validate attendance type
    #         if 'attendance_type' not in request.data:
    #             return errorMessage('attendance_type is a required field')
    #         if request.data['attendance_type'] not in ['WFH']:
    #             return errorMessage('attendance_type must be WFH')

    #         emp_obj = Employees.objects.get(id=employee_id, organization=organization_id)

    #         # --------------------------------------
    #         # DATE HANDLING (SAFE, SIMPLE)
    #         # --------------------------------------
    #         today = datetime.date.today()
    #         if 'date' in request.data:
    #             date = datetime.datetime.strptime(request.data['date'], "%Y-%m-%d").date()
    #         else:
    #             date = today

    #         # --------------------------------------
    #         # TIME HANDLING (REMOVE MICROSECONDS)
    #         # --------------------------------------
    #         now = datetime.datetime.now()

    #         if 'check_in' in request.data:
    #             time_str = request.data['check_in']

    #             # Remove microseconds safely
    #             if '.' in time_str:
    #                 time_str = time_str.split('.')[0]

    #             # Parse clean HH:MM:SS
    #             check_in_time = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
    #             is_custom_time = True

    #             # Future check (only for today)
    #             if date == today and check_in_time > now.time():
    #                 return errorMessage("Cannot check in at a future time")

    #         else:
    #             # Auto assign without microseconds
    #             check_in_time = now.replace(microsecond=0).time()
    #             is_custom_time = False

    #         # --------------------------------------
    #         # CHECK IF TODAY ALREADY EXISTS
    #         # --------------------------------------
    #         existing = EmployeesAttendance.objects.filter(
    #             employee=emp_obj.id,
    #             date=date,
    #             is_active=True
    #         )

    #         if existing.exists():
    #             last_att = existing.last()

    #             if last_att.is_check_in and not last_att.is_check_out:
    #                 return errorMessage("Employee already checked in today")

    #             if last_att.is_check_out and last_att.check_out >= check_in_time:
    #                 return errorMessage("Check-in time must be greater than last check-out time")

    #         # --------------------------------------
    #         # CREATE NEW ATTENDANCE
    #         # --------------------------------------
    #         attendance = EmployeesAttendance.objects.create(
    #             employee=emp_obj,
    #             attendance_type=request.data['attendance_type'],
    #             date=date,
    #             is_check_in=True,
    #             is_check_out=False,
    #             check_in=check_in_time,
    #             is_custom_time_set=is_custom_time,
    #             wfh_reason=request.data.get('wfh_reason', None),
    #             is_active=True
    #         )

    #         serializer = EmployeesAttendanceViewsetSerializers(attendance, many=False)
    #         attendance_labels(self, attendance, user)

    #         # Tracker URL
    #         if attendance.attendance_type.upper() == 'WFH':
    #             tracker_script_url = request.build_absolute_uri(
    #                 f'/api/attendance/tracker/{attendance.id}/script/'
    #             )
    #         else:
    #             tracker_script_url = None

    #         resp = serializer.data
    #         resp["tracker_script_url"] = tracker_script_url

    #         return successMessageWithData("Check in successfully", resp)

    #     except Exception as e:
    #         return exception(e)
    
    
    
    def emp_check_in(self, request, *args, **kwargs):
        try:
            # Decode token
            token_data = decodeToken(self, request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            user = request.user

            # Validate attendance type
            if 'attendance_type' not in request.data:
                return errorMessage('attendance_type is a required field')
            if request.data['attendance_type'] not in ['WFH']:
                return errorMessage('attendance_type must be WFH')

            emp_obj = Employees.objects.get(id=employee_id, organization=organization_id)

            # --------------------------------------
            # DATE VALIDATION - ONLY TODAY ALLOWED
            # --------------------------------------
            today = datetime.date.today()
            
            if 'date' in request.data:
                date = datetime.datetime.strptime(request.data['date'], "%Y-%m-%d").date()
                
                # Check if date is not today
                if date != today:
                    if date > today:
                        return errorMessage("Cannot check in for future dates. Please use today's date.")
                    else:
                        return errorMessage("Cannot check in for past dates. Please use today's date.")
            else:
                date = today

            # --------------------------------------
            # TIME HANDLING (REMOVE MICROSECONDS)
            # --------------------------------------
            now = datetime.datetime.now()

            if 'check_in' in request.data:
                time_str = request.data['check_in']

                # Remove microseconds safely
                if '.' in time_str:
                    time_str = time_str.split('.')[0]

                # Parse clean HH:MM:SS
                check_in_time = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
                is_custom_time = True

                # Future check (only for today)
                if date == today and check_in_time > now.time():
                    return errorMessage("Cannot check in at a future time")

            else:
                # Auto assign without microseconds
                check_in_time = now.replace(microsecond=0).time()
                is_custom_time = False

            # --------------------------------------
            # CHECK IF TODAY ALREADY EXISTS
            # --------------------------------------
            existing = EmployeesAttendance.objects.filter(
                employee=emp_obj.id,
                date=date,
                is_active=True
            )

            if existing.exists():
                last_att = existing.last()

                if last_att.is_check_in and not last_att.is_check_out:
                    return errorMessage("Employee already checked in today")

                if last_att.is_check_out and last_att.check_out >= check_in_time:
                    return errorMessage("Check-in time must be greater than last check-out time")

            # --------------------------------------
            # CREATE NEW ATTENDANCE
            # --------------------------------------
            attendance = EmployeesAttendance.objects.create(
                employee=emp_obj,
                attendance_type=request.data['attendance_type'],
                date=date,
                is_check_in=True,
                is_check_out=False,
                check_in=check_in_time,
                is_custom_time_set=is_custom_time,
                wfh_reason=request.data.get('wfh_reason', None),
                is_active=True
            )

            serializer = EmployeesAttendanceViewsetSerializers(attendance, many=False)
            attendance_labels(self, attendance, user)

            # Tracker URL
            if attendance.attendance_type.upper() == 'WFH':
                tracker_script_url = request.build_absolute_uri(
                    f'/api/attendance/tracker/{attendance.id}/script/'
                )
            else:
                tracker_script_url = None

            resp = serializer.data
            resp["tracker_script_url"] = tracker_script_url

            return successMessageWithData("Check in successfully", resp)

        except Exception as e:
            return exception(e)



    
    
    
    def emp_check_in_pk(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, request)
            pk=self.kwargs['pk']
            # checks if active employee exists or not



            pk_tz = pytz.timezone('Asia/Karachi')
            present_time = datetime.datetime.now(pk_tz).time().strftime('%H:%M:%S') 

            
            if 'check_in' in request.data:
                current_time = request.data['check_in']
            else:
                current_time = present_time
                
            current_time_obj = datetime.datetime.strptime(current_time, "%H:%M:%S").time()
            current_time = current_time_obj

            # if attendance already exists
            emp_attendance = EmployeesAttendance.objects.filter(id=pk)
            if emp_attendance.exists():
                emp_attendance_obj = emp_attendance.get()

                if emp_attendance_obj.is_check_out == True and emp_attendance_obj.is_check_in == False and emp_attendance_obj.check_in==None and emp_attendance_obj.is_check_out!=None:
                        if emp_attendance_obj.check_out<= current_time:
                            return errorMessage('Checked in time must be less then check out time')
                        # check if some check in and checkout exists in that duration
                        emp_attendance_duration_check = emp_attendance.filter(
                            check_in__lte = current_time, 
                            check_out__gte = current_time,
                            date = emp_attendance_obj.date
                        )
                        if emp_attendance_duration_check.exists():
                            duration_check = emp_attendance_duration_check.last()
                            error_message = f'You have already checked in during this duration: [check_in: {duration_check.check_in}, check_out: {duration_check.check_out}]'
                            return errorMessage(error_message)   
                        
                        emp_attendance_obj.check_in = current_time
                        emp_attendance_obj.save()     
                    
                        serializer = EmployeesAttendanceViewsetSerializers(emp_attendance_obj)
                        emp_attendance_obj.save()
                            

                        return successMessageWithData('Check in successfully', serializer.data)
                
                                    # if emp is already checked in or checkout is true
                elif emp_attendance_obj.is_check_in == True:
                            return errorMessage('Employee is already checked in')
                elif emp_attendance_obj.is_check_out == False:
                            return errorMessage('checkout the employee first')  
                        
                        
            else:
                return errorMessage('Record not exists at this id')
        except Exception as e:
            return exception(e)



    @action(detail=False, methods=['POST'], url_path='check_out')
    def emp_check_out(self, request, *args, **kwargs):
        try:
            # Decode token
            token_data = decodeToken(self, request)
            employee_id = token_data['employee_id']
            organization_id = token_data['organization_id']

            # Current date & time (microseconds removed)
            now = datetime.datetime.now().replace(microsecond=0)

            # --------------------------------------
            # DATE HANDLING (SAFE & SIMPLE)
            # --------------------------------------
            date_today = request.data.get('date', now.date())
            if isinstance(date_today, str):
                date_today = datetime.datetime.strptime(date_today, "%Y-%m-%d").date()

            # --------------------------------------
            # TIME HANDLING (REMOVE MICROSECONDS)
            # --------------------------------------
            time_str = request.data.get('check_out', now.strftime("%H:%M:%S"))

            # Remove microseconds if present
            if '.' in time_str:
                time_str = time_str.split('.')[0]

            # Parse HH:MM:SS cleanly
            check_out_time = datetime.datetime.strptime(time_str, "%H:%M:%S").time()

            # --------------------------------------
            # FIND ACTIVE CHECK-IN FOR TODAY
            # --------------------------------------
            last_slot = EmployeesAttendance.objects.filter(
                employee=employee_id,
                employee__organization=organization_id,
                date=date_today,
                is_check_in=True,
                is_check_out=False,
                is_active=True
            ).order_by('-check_in').first()

            if not last_slot:
                return errorMessage("No active check-in found for today. Please check in first.")

            # --------------------------------------
            # VALIDATION: FUTURE TIME NOT ALLOWED
            # --------------------------------------
            if date_today == now.date() and check_out_time > now.time():
                return errorMessage("Check-out time cannot be in the future.")

            # --------------------------------------
            # VALIDATION: MUST BE AFTER CHECK-IN
            # --------------------------------------
            if check_out_time <= last_slot.check_in:
                return errorMessage("Check-out time must be greater than check-in time.")

            # --------------------------------------
            # UPDATE RECORD
            # --------------------------------------
            last_slot.check_out = check_out_time
            last_slot.is_check_out = True
            last_slot.is_active = False
            last_slot.save()

            # --------------------------------------
            # TRACKER: ONLY FOR WFH
            # --------------------------------------
            if last_slot.attendance_type.upper() == "WFH":
                stop_tracker_url = request.build_absolute_uri(
                    f"/api/attendance/tracker/{last_slot.id}/stop_script/"
                )
                tracker_message = "Download the stop script to end tracking."
            else:
                stop_tracker_url = None
                tracker_message = "No tracker used for this attendance type."

            serializer = EmployeesAttendanceViewsetSerializers(last_slot)
            resp = serializer.data
            resp["stop_tracker_url"] = stop_tracker_url

            return successMessageWithData(
                f"Check-out successful. {tracker_message}",
                resp
            )

        except Exception as e:
            return exception(e)





    def emp_check_out_pk(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            pk=self.kwargs['pk']

            pk_tz = pytz.timezone('Asia/Karachi')

            emp_attendance = EmployeesAttendance.objects.filter(id=pk)
            
            present_time = datetime.datetime.now(pk_tz).time().strftime('%H:%M:%S')
                    
            if 'check_out' in request.data:
                        check_out_time = request.data['check_out']
            else:
                        check_out_time = present_time
                        
            check_out_time_obj = datetime.datetime.strptime(check_out_time, "%H:%M:%S").time()
            check_out_time = check_out_time_obj
        
            if emp_attendance.exists():
                emp_attendance_obj=emp_attendance.get()
                # emp_attendance_last_check_in = EmployeesAttendance.objects.filter(
                #     employee=employee_id, 
                #     employee__organization=organization_id, 
                #     date=emp_attendance_obj.date
                #     ).last()
                
                if emp_attendance_obj.check_in>check_out_time:
                        return errorMessage(f'check out time should be greater than check in time of {emp_attendance_obj.date}')
                        
                    
                if emp_attendance_obj.attendance_type=='office':
                    return errorMessage('Office checkouts are to be logged exclusively through the designated machine. For any concerns or inquiries, please feel free to contact HR')
                
                if emp_attendance_obj.is_check_out == True:
                    return errorMessage('Employee is already checked out')
                elif emp_attendance_obj.is_check_in == False:
                    return errorMessage('checkin the employee first')   
                elif emp_attendance_obj.is_check_in == True and emp_attendance_obj.is_check_out == False:
                    emp_attendance_obj.is_check_in = False
                    emp_attendance_obj.is_check_out = True
                    present_time = datetime.datetime.strptime(present_time, "%H:%M:%S").time()
                    if check_out_time <= emp_attendance_obj.check_in:
                        return errorMessage('check out time should be greater than check in time')

                    # if check_out_time > present_time:
                    #     return errorMessage('You cannot checkout at future time')
                    
                    emp_attendance_obj.check_out = check_out_time
                    # check if some check in and checkout exists in that duration
                    emp_attendance_duration_check = emp_attendance.filter(
                        check_in__lte = check_out_time, 
                        check_out__gte = check_out_time,
                        date = emp_attendance_obj.date
                    )
                    if emp_attendance_duration_check.exists():
                        duration_check = emp_attendance_duration_check.last()
                        error_message = f'You have already checked out during this duration: [check_in: {duration_check.check_in}, check_out: {duration_check.check_out}]'
                        return errorMessage(error_message)         

                    serializer = EmployeesAttendanceViewsetSerializers(emp_attendance_obj)
                    emp_attendance_obj.save()
                    return successMessageWithData('checkout successfully', serializer.data)

            return errorMessage('Record not exists at this id')    
            
        except Exception as e:
            return exception(e)


# =============================================
    # 🔹 WFH CHECK-IN API (Separate Endpoint)
    @action(detail=False, methods=['POST'], url_path='WFH/check_in')
    def emp_wfh_check_in(self, request, *args, **kwargs):
        """
        WFH Check-in API for desktop application
        """
        try:
            # Decode token
            token_data = decodeToken(self, request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            user = request.user

            # Validate this is for WFH only
            if 'attendance_type' not in request.data:
                return errorMessage('attendance_type is a required field')
            if request.data['attendance_type'] not in ['WFH']:
                return errorMessage('attendance_type must be WFH')

            emp_obj = Employees.objects.get(id=employee_id, organization=organization_id)

            # --------------------------------------
            # DATE HANDLING
            # --------------------------------------
            today = datetime.date.today()
            if 'date' in request.data:
                date = datetime.datetime.strptime(request.data['date'], "%Y-%m-%d").date()
            else:
                date = today

            # --------------------------------------
            # TIME HANDLING (REMOVE MICROSECONDS)
            # --------------------------------------
            now = datetime.datetime.now()

            if 'check_in' in request.data:
                time_str = request.data['check_in']

                # Remove microseconds safely
                if '.' in time_str:
                    time_str = time_str.split('.')[0]

                # Parse clean HH:MM:SS
                check_in_time = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
                is_custom_time = True

                # Future check (only for today)
                if date == today and check_in_time > now.time():
                    return errorMessage("Cannot check in at a future time")

            else:
                # Auto assign without microseconds
                check_in_time = now.replace(microsecond=0).time()
                is_custom_time = False

            # --------------------------------------
            # CHECK IF TODAY ALREADY EXISTS
            # --------------------------------------
            existing = EmployeesAttendance.objects.filter(
                employee=emp_obj.id,
                date=date,
                is_active=True
            )

            if existing.exists():
                last_att = existing.last()

                if last_att.is_check_in and not last_att.is_check_out:
                    return errorMessage("Employee already checked in today")

                if last_att.is_check_out and last_att.check_out >= check_in_time:
                    return errorMessage("Check-in time must be greater than last check-out time")

            # --------------------------------------
            # CREATE NEW ATTENDANCE
            # --------------------------------------
            attendance = EmployeesAttendance.objects.create(
                employee=emp_obj,
                attendance_type=request.data['attendance_type'],
                date=date,
                is_check_in=True,
                is_check_out=False,
                check_in=check_in_time,
                is_custom_time_set=is_custom_time,
                wfh_reason=request.data.get('wfh_reason', None),
                is_active=True
            )

            serializer = EmployeesAttendanceViewsetSerializers(attendance, many=False)
            attendance_labels(self, attendance, user)

            # Note: Tracker script URL logic is removed as per requirements
            
            return successMessageWithData("WFH Check in successful", serializer.data)

        except Exception as e:
            return exception(e)

    @action(detail=False, methods=['POST'], url_path='WFH/check_out')
    def emp_wfh_check_out(self, request, *args, **kwargs):
        """
        WFH Check-out API for desktop application
        """
        try:
            # Decode token
            token_data = decodeToken(self, request)
            employee_id = token_data['employee_id']
            organization_id = token_data['organization_id']

            # Current date & time (microseconds removed)
            now = datetime.datetime.now().replace(microsecond=0)

            # --------------------------------------
            # DATE HANDLING
            # --------------------------------------
            date_today = request.data.get('date', now.date())
            if isinstance(date_today, str):
                date_today = datetime.datetime.strptime(date_today, "%Y-%m-%d").date()

            # --------------------------------------
            # TIME HANDLING (REMOVE MICROSECONDS)
            # --------------------------------------
            time_str = request.data.get('check_out', now.strftime("%H:%M:%S"))

            # Remove microseconds if present
            if '.' in time_str:
                time_str = time_str.split('.')[0]

            # Parse HH:MM:SS cleanly
            check_out_time = datetime.datetime.strptime(time_str, "%H:%M:%S").time()

            # --------------------------------------
            # FIND ACTIVE CHECK-IN FOR TODAY
            # --------------------------------------
            last_slot = EmployeesAttendance.objects.filter(
                employee=employee_id,
                employee__organization=organization_id,
                date=date_today,
                is_check_in=True,
                is_check_out=False,
                is_active=True,
                attendance_type='WFH'  # Only WFH records
            ).order_by('-check_in').first()

            if not last_slot:
                return errorMessage("No active WFH check-in found for today. Please check in first.")

            # --------------------------------------
            # VALIDATION: FUTURE TIME NOT ALLOWED
            # --------------------------------------
            if date_today == now.date() and check_out_time > now.time():
                return errorMessage("Check-out time cannot be in the future.")

            # --------------------------------------
            # VALIDATION: MUST BE AFTER CHECK-IN
            # --------------------------------------
            if check_out_time <= last_slot.check_in:
                return errorMessage("Check-out time must be greater than check-in time.")

            # --------------------------------------
            # UPDATE RECORD
            # --------------------------------------
            last_slot.check_out = check_out_time
            last_slot.is_check_out = True
            last_slot.is_active = False
            last_slot.save()

            serializer = EmployeesAttendanceViewsetSerializers(last_slot)
            
            return successMessageWithData("WFH Check-out successful", serializer.data)

        except Exception as e:
            return exception(e)




class AttendanceMachinesViewset(viewsets.ModelViewSet):
    queryset = AttendanceMachines.objects.filter(is_active=True)
    serializer_class = AttendanceMachinesSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            return self.queryset.filter(organization_id=organization_id)
        except Exception as e:
            return exception(e)
        

    def list(self, request, *args, **kwargs):
        try:
            
            organization_id = decodeToken(self, self.request)['organization_id']
            query = self.queryset.filter(organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']

            required_fields=['machine_number','machine_title']

            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [machine_number,machine_title]')
            
            request.data['organization']=organization_id

            serializer=AttendanceMachinesSerializers(data=request.data)

            if not serializer.is_valid():
                return errorMessage(serializer.errors)

            serializer.save()
            
            return success(serializer.data)
            
        except Exception as e:
            return exception(e)


    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if AttendanceMachines.objects.filter(id=pk).exists():
                obj = AttendanceMachines.objects.get(id=pk)
                if obj.is_active == False:
                    msg = "Attendance Machine is already deactivated"
                    return errorMessage(msg)
                obj.is_active = False
                obj.save()
                serializer = AttendanceMachinesSerializers(obj)
                return success(serializer.data)
            else:
                return errorMessage('This Attendance Machine does not exists')
        except Exception as e:
            return exception(e)


class AttendanceMachineLogFilesViewset(viewsets.ModelViewSet):
    queryset = AttendanceMachineLogFiles.objects.filter(is_active=True)
    serializer_class = CUAttendanceMachineLogFilesSerializers
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user = request.user
            
            attendance_machine = request.data.get('attendance_machine', None)
            
            if attendance_machine is None:
                return errorMessage('Attendance machine does not exists.')
            
            org_id = organization_id

            # Get all the organization employees ids  
            employees = Employees.objects.filter(organization=org_id)

            employee_array = {}
            employee_code_array = {}
            if employees.exists():
                for employee in employees:
                    employee_array[employee.emp_code] = employee.id
                    employee_code_array[employee.code] = employee.id 
            else:
                return errorMessage('Organization has no employee.')
                        
            # Process the attendance log file.
            print(employee_code_array)
            request.data['uploaded_by'] = request.user.id
            serializer = CUAttendanceMachineLogFilesSerializers(data = request.data)
            
            file_columns = ['employee_code', 'employee_name', 'machine_no', 'machine_name', 'date', 
                'day', 'shift', 'check_in_1', 'check_out_1', 'check_in_2', 'check_out_2', 
                'must_days', 'absent', 'work_hours', 'remarks']
            file_col_index = {
                'employee_code': 0, 'employee_name': 1, 'machine_no': 2, 'machine_name': 3,
                'date': 4, 'day': 5, 'shift': 6, 'check_in_1': 7, 'check_out_1': 8, 
                'check_in_2': 9,  'check_out_2': 10, 'must_days': 11,
                'absent': 13, 'work_hours': 15, 'remarks': 19
            }
            total_attendance = 3
            request.data['is_active'] = True

            if serializer.is_valid():
                afile = serializer.save()
                print(afile.id)
                file = afile.attendance_file
                reader = pd.read_csv(file)
                reader = reader.dropna(how='all')
                # Remove columns with all NaN values
                reader = reader.dropna(axis=1, how='all')
                print(reader)
                options_array = []
                
                emp_attendance_array = {
                    'employee':'', 'date':'', 'attendance_machine_log_file':afile.id, 
                    'attendance_type':'office', 
                    'is_check_in':False, 'check_in':'', 'is_check_out':False, 'check_out': None,

                }
                print('hey')
                for row in reader.iterrows():
                    
                    if file_col_index['employee_code'] is not None:
                        employee_code = row[1][file_col_index['employee_code']]
                        # print(employee_code)
                        if employee_code not in employee_array and str(employee_code) not in employee_code_array:
                            print('not in list or db')
                            continue
                        if employee_code in employee_array:
                            print('in employee_array list')
                            emp_attendance_array['employee'] = employee_array[row[1][file_col_index['employee_code']]]
                        else:
                            print('in employee_code_array list')
                            emp_attendance_array['employee'] = employee_code_array[str(employee_code)]

                        if not row[1][file_col_index['date']]:
                            continue
                        emp_attendance_array['date'] = datetime.datetime.strptime(row[1][file_col_index['date']], "%m/%d/%Y").date()

                        # changed code
                        
                        is_attendance_exists = EmployeesAttendance.objects.filter(
                            employee=emp_attendance_array['employee'],
                            date=emp_attendance_array['date'],
                            is_active=True,
                        )
                        if is_attendance_exists.exists():
                            print('continue')
                            continue

                        # Now get the attendances

                        for i in range(1, total_attendance):
                            check_in_index = 'check_in_' + str(i)
                            check_out_index = 'check_out_' + str(i)
                            # print(i, "::", check_in_index)
                            # print(i, "::", check_out_index)
                            test1 = row[1][file_col_index.get(check_in_index)]  # Use .get() to handle missing keys gracefully
                            test2 = row[1][file_col_index.get(check_out_index)]  # Use .get() to handle missing keys gracefully
                            # print(test1, "::", test2)
                            
                            # Continue if either test1 or test2 is NaN or None
                            
                            # if (math.isnan(test1f) or test1 is None) and (math.isnan(test2) or test2 is None):
                            #     print('continue')
                            #     continue

                            if not test1 and not test2:
                                continue
                            # print(type(test1))
                            # print(type(test2))
                            emp_attendance_array_1 = emp_attendance_array

                            if type(test1) == float:
                                continue
                            else:
                                test1f = datetime.datetime.strptime(test1, "%I:%M:%S %p").time()
                                emp_attendance_array_1['check_in']=test1f
                                emp_attendance_array_1['is_check_in'] = True
                            if type(test2) == float:
                                test2f = None
                            else:
                                test2f = datetime.datetime.strptime(test2, "%I:%M:%S %p").time()
                                emp_attendance_array_1['is_check_out'] = True
                                emp_attendance_array_1['check_out'] = test2f
                            
                            # print(test1f)
                            # print(emp_attendance_array_1)
                            

                            aserializer = CUEmployeesAttendanceViewsetSerializers(data=emp_attendance_array_1)

                            if aserializer.is_valid():
                                data_obj = aserializer.save()
                                # print('hello')
                                attendance_labels(self, data_obj, user)

                        # for i in range(1, total_attendance):
                        #     # print('hellow')
                        #     check_in_index = 'check_in_'+str(i)
                        #     check_out_index = 'check_out_'+str(i)
                        #     print(i,"::",check_in_index)
                        #     print(i,"::",check_out_index)
                        #     test1=row[1][file_col_index[check_in_index]]
                        #     test2=row[1][file_col_index[check_out_index]]
                        #     print(test1,"::",test2)

                           
                            
                        #     if math.isnan(row[1][file_col_index[check_in_index]]) and math.isnan(row[1][file_col_index[check_out_index]]):
                        #         continue

                            
                        #     emp_attendance_array_1 = emp_attendance_array
                        #     print(datetime.datetime.strptime(row[1][file_col_index[check_in_index]], "%I:%M:%S %p").time())
                        #     emp_attendance_array_1['check_in'] =  datetime.datetime.strptime(row[1][file_col_index[check_in_index]], "%I:%M:%S %p").time()
                        #     emp_attendance_array_1['is_check_in'] = True
                        #     # print(emp_attendance_array_1['check_in'])
                        #     # print(emp_attendance_array_1['check_out'])
                        #     print('check out check')
                        #     print(math.isnan(test2))
                        #     if math.isnan(test2):
                        #         print('not a nan in check out')
                        #         emp_attendance_array_1['check_out'] =  datetime.datetime.strptime(row[1][file_col_index[check_out_index]], "%I:%M:%S %p").time()
                        #         emp_attendance_array_1['is_check_out'] = True
                        #         print(emp_attendance_array_1['check_out'])
                        #     else:
                        #         print('check out is not a number')
                        #         print(emp_attendance_array_1['check_out'])
                        #     print(emp_attendance_array_1)
                        #     # aserializer = CUEmployeesAttendanceViewsetSerializers(data=emp_attendance_array_1) 

                        #     # if aserializer.is_valid():
                        #     #     data_obj = aserializer.save()
                        #     #     # print('hellow')
                        #     #     attendance_labels(self, data_obj, user)
                     
                                

                    else:
                        continue
                        
                # Now update the file log processed
                
                data = serializer.data
                    
                return successMessageWithData('Successfully uploaded', serializer.data) 
            else:
                return Response({'status':400, 'system_status': 404, 'data': '', 'message': 'Validation Error', 'system_error_message': serializer.errors})

        except Exception as e:
            return exception(e)
        
    def fileupload(self, request, *args, **kwargs):
        try:
            # Read the CSV file
            df = pd.read_csv("C:\\Users\\Kavtech\\Documents\\employee code list.csv")
           
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            # Remove rows with all NaN values
            df = df.dropna(how='all')

            # Remove columns with all NaN values
            df = df.dropna(axis=1, how='all')
            # Print the first 5 rows of the DataFrame
            # Fetch data from specific columns
            emp_code_list = df['emp_code'].tolist()
            
            reg_no_list=df['Reg_No'].tolist()
            name=df['Name'].tolist()
            # print(df)
            # print(name)
            # print(reg_no_list)
            # print(emp_code_list)
            # Create a CSV file to store data for employees not found in the database
            not_found_data = []
            print(len(emp_code_list))
            print(organization_id)
           
            # Do something with the fetched data
            for i in range(len(emp_code_list)):
                try:
                    employee = Employees.objects.get(emp_code=emp_code_list[i], organization_id=organization_id)
                    employee.code=reg_no_list[i]
                    employee.save()
    
                except Employees.DoesNotExist:
                    not_found_data.append([name[i],reg_no_list[i],emp_code_list[i]])

        # If the evaluator name is not found, add the data to the not_found_data list
                
            if not_found_data:
                not_found_df = pd.DataFrame(not_found_data, columns=['name', 'Reg_No', 'emp_code'])
                not_found_df.to_csv('C:\\Users\\Kavtech\\Downloads\\not_found_employees.csv', index=False)
                
            return successMessage('success')
        except Exception as e:
            return exception(e)
    
    def list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            # print("id:",organization_id)
            attendance_log_files = AttendanceMachineLogFiles.objects.filter(is_active=True,attendance_machine__organization=organization_id)
            # print("Name:",attendance_log_files.values("attendance_machine__organization"))
            serializer = CUAttendanceMachineLogFilesSerializers(attendance_log_files, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def list_attendance(self, request, *args, **kwargs):
        try:

            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            query = EmployeesAttendance.objects.filter(
                employee__organization = organization_id,
                attendance_machine_log_file__isnull=False,
                is_active=True
            )
            serializer = CUEmployeesAttendanceViewsetSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
class MyModelViewSet(viewsets.ModelViewSet):
    queryset = EmployeesAttendance.objects.filter(is_active=True)
    # serializer_class = EmployeesAttendanceLabelSerializers
    permission_classes = [IsAuthenticated]

    
    def create(self, request, *args, **kwargs):
        
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            # print(organization_id)
            current_date = datetime.date.today()
            print(current_date)
            # month = request.data.get('month', current_date.month)
            year = request.data.get('year', current_date.year)
            
            hoildays=EmployeesOfficialHolidays.objects.filter(is_active=True, date__lte=current_date, date__year=year,organization_id=organization_id)
            
            # print(query1.values())
          
            employee = Employees.objects.filter(
                organization=organization_id, 
                is_active=True
            )# Emp data

            for holiday in hoildays:
                for emp in employee:
                    query=EmployeesAttendance.objects.filter(employee=emp,date=holiday.date,is_active=True)
                    # print(query.values())
                    if not query.exists():
                          EmployeesAttendance.objects.create(
                          employee=emp,
                          date=holiday.date,
                          attendance_type='H',  # Replace with the desired attendance type
                          )
                    else:
                        continue

            


             
            # print(serializer.data)
            return success("Hoilday Insertion Done")
        except Exception as e:
            return exception(e)

    

class EmployeesAttendanceLabelViewset(viewsets.ModelViewSet):
    queryset = EmployeesAttendanceLabel.objects.filter(is_active=True)
    serializer_class = EmployeesAttendanceLabelSerializers
    permission_classes = [IsAuthenticated]

    def notify_wfh(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            employee_id = decodeToken(self, self.request)['employee_id']
            if "team_lead" not in request.data:
                return errorMessage("Team Lead is required")
            
            if "date" not in request.data:
                return errorMessage("Date is required")
            
            employees=Employees.objects.filter(id=employee_id,organization=organization_id,is_active=True)
            emp=employees.get()

           
            
            team_lead=request.data['team_lead']
            
            if team_lead==emp.id:
                return errorMessage('You can not set yourself as team lead')
                
            team_lead_query=Employees.objects.filter(id=team_lead,organization=organization_id,is_active=True)
                
            if not team_lead_query.exists():
                    return errorMessage('Team Lead not exists at this id')
            
            date=request.data['date']
            
            cc_employee=EmailRecipients.objects.filter(employee__organization=organization_id,level=1,is_active=True)
            if cc_employee.exists():
            
                obj=cc_employee.get()
                obj1=team_lead_query.get()
                subject=f'WFH Notification: {emp.name} - {date}'
                WFHEmailsFromEmployees(obj1.name,emp.name,subject,obj1.official_email,obj.employee.official_email,date)

            return successMessage('Success')
            
        except exception as e:
            return exception(e)

    def get_queryset(self):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            return self.queryset.filter(employee__organization=organization_id)
        except Exception as e:
            return exception(e)

    def list(self, request, *args, **kwargs):
        try:
            query = self.get_queryset().filter(is_active=True)
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
    
    def list_data(self, request, *args, **kwargs):
    
    
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            # print(organization_id)
            current_date = datetime.date.today()
            # print(current_date)
            month = request.data.get('month', current_date.month)
            year = request.data.get('year', current_date.year)
           
           
            # print(query.values())
            hoildays=EmployeesOfficialHolidays.objects.filter(is_active=True, date__month=month, date__year=year,organization_id=organization_id)
            
            # print(request.user.id)
            # print(hoildays.values())

            employee = Employees.objects.filter(
                organization=organization_id, 
                is_active=True
            )# Emp data
             


            # Check if the requested month is the current month
            if month == current_date.month:
                # Calculate the last day of the specified month up to the current date
                last_day_of_month = current_date
            else:
                # Calculate the last day of the specified month
                last_day_of_month = datetime.date(year, month, calendar.monthrange(year, month)[1])

            # Calculate the number of weekends (Saturdays and Sundays)

            
            weekend_dates = []

            # Calculate the number of weekends (Saturdays and Sundays) and their dates
            for day in range(1, last_day_of_month.day + 1):
                date = datetime.date(year, month, day)
                if date.weekday() in [5, 6]:
                    weekend_dates.append(date)

            # weekend_count = len(weekend_dates)
            # print(f"Number of weekends in {calendar.month_name[month]} {year}: {weekend_count}")
            # print("Weekend dates:")
            # for date in weekend_dates:
            #     print(date)
            # print(weekend_dates)

            
            ## Weekends Added

            for date in weekend_dates:
                for emp in employee:
                    date_query=EmployeesAttendance.objects.filter(employee=emp,date=date,is_active=True)
                
                    if not date_query.exists():

                        query= query=EmployeesAttendanceLabel.objects.filter(employee=emp,date=date,is_active=True)
                        if not query.exists():
                            # print("add")
                            EmployeesAttendanceLabel.objects.create(
                            employee=emp,
                            date=date,
                            attendance_status='W', 
                            created_by=request.user,
                            comments="Weekend"                      # Replace with the desired attendance type
                            )
                            
                        else:
                            # print(query.values())
                            # print("not added")
                            continue
                    else:
                        query=EmployeesAttendanceLabel.objects.filter(employee=emp,date=date,is_active=True)
                        if not query.exists():
                            EmployeesAttendanceLabel.objects.create(
                                    employee=emp,
                                    date=date,
                                    attendance_status='P', 
                                    created_by=request.user,
                                    comments='office'                # Replace with the desired attendance type
                                    )
                        else:
                            obj=query.get()
                            obj.attendance_status='P'
                            obj.comments='office'
                            obj.save()

                            

                            
                            
                        # #    print(obj.attendance_type)
                       




            # # ### Hoildays Added 
            # for holiday in hoildays:
            #     for emp in employee:
            #         # print()
            #         query=EmployeesAttendanceLabel.objects.filter(employee=emp,date=holiday.date,is_active=True)
            #         # print(query.values())
            #         if not query.exists():
            #               EmployeesAttendanceLabel.objects.create(
            #               employee=emp,
            #               date=holiday.date,
            #               attendance_status='H', 
            #               created_by=request.user, # Replace with the desired attendance type
            #               comments=holiday.title
            #               )
                          
            #         else:
            #             continue
            #---------------------------------------------------------------------------
            
            # ### Holidays Added - Check attendance before marking as holiday
# ### Holidays Added - Comprehensive solution
            for holiday in hoildays:
                for emp in employee:
                    # 1. First check if employee is on leave for this date
                    is_on_leave = EmployeesLeaves.objects.filter(
                        employee=emp,
                        start_date__lte=holiday.date,
                        end_date__gte=holiday.date,
                        status='approved',
                        is_active=True
                    ).exists()
                    
                    # 2. Check if employee has attendance for this date
                    actual_attendance = EmployeesAttendance.objects.filter(
                        employee=emp,
                        date=holiday.date,
                        is_active=True
                    )
                    
                    query = EmployeesAttendanceLabel.objects.filter(
                        employee=emp,
                        date=holiday.date,
                        is_active=True
                    )
                    
                    # Determine the correct attendance status
                    attendance_status = None
                    comments = None
                    
                    if is_on_leave:
                        # Employee is on approved leave
                        attendance_status = 'L'
                        # Get leave type for comments
                        leave = EmployeesLeaves.objects.filter(
                            employee=emp,
                            start_date__lte=holiday.date,
                            end_date__gte=holiday.date,
                            status='approved',
                            is_active=True
                        ).first()
                        if leave and leave.set_leave_duration and leave.set_leave_duration.leave_types:
                            comments = leave.set_leave_duration.leave_types.title
                        else:
                            comments = 'Leave'
                            
                    elif actual_attendance.exists():
                        # Employee has attendance records
                        attendance_obj = actual_attendance.first()
                        
                        # Determine attendance status based on attendance_type
                        if attendance_obj.attendance_type == 'WFH':
                            attendance_status = 'WFH'
                            comments = 'WFH'
                        elif attendance_obj.attendance_type == 'office':
                            attendance_status = 'P'
                            comments = 'office'
                        else:
                            # Handle other attendance types if any
                            attendance_status = 'P'  # Default
                            comments = attendance_obj.attendance_type if attendance_obj.attendance_type else 'office'
                    else:
                        # No leave, no attendance - mark as holiday
                        attendance_status = 'H'
                        comments = holiday.title
                    
                    # Now create or update the label
                    if not query.exists():
                        EmployeesAttendanceLabel.objects.create(
                            employee=emp,
                            date=holiday.date,
                            attendance_status=attendance_status,
                            created_by=request.user,
                            comments=comments
                        )
                    else:
                        obj = query.first()
                        obj.attendance_status = attendance_status
                        obj.comments = comments
                        obj.save()
            
            ### Leaves
            # leaves_data=EmployeesLeaves.objects.filter(is_active=True,status='approved',start_date__month=month,employee__organization=organization_id).order_by('-id')
            

            # for leave in leaves_data:
            #     # print(leave.employee.id)
            #     for emp in employee:

            #         if leave.employee.id==emp.id:
            #             # Create an empty list to store the dates
            #             date_data_list = []
            #             # Calculate the number of days between start_date and end_date
            #             delta = datetime.timedelta(days=1)
            #             # Loop through the dates and append them to the list
            #             date = leave.start_date
            #             while date <= leave.end_date:
            #                 date_data_list.append(date)
            #                 date += delta

            #             for date_list in date_data_list:
            #                 query=EmployeesAttendanceLabel.objects.filter(employee=emp,date=date_list,is_active=True)
            #                 # print(date_list)
            #                 if not query.exists():
            #                     EmployeesAttendanceLabel.objects.create(
            #                     employee=emp,
            #                     date=date_list,
            #                     attendance_status='L', 
            #                     created_by=request.user, # Replace with the desired attendance type
            #                     comments=leave.set_leave_duration.leave_types.title
            #                     )
            #                 else:
            #                     # query1=EmployeesAttendance.objects.filter(employee=emp,date=date_list,is_active=True)
            #                     # if query1.exists():
            #                     #     obj=query.get()
            #                     #     obj.attendance_status='P'
            #                     #     obj.comments='office'
            #                     #     obj.save()
            #                     # else:
            #                         continue

            
            query = self.get_queryset().filter(is_active=True, date__month=month, date__year=year) #addtendance data


            serializer = EmployeesLabelSerializers(
                employee,
                context = {'query': query},
                many=True
            )
             
            # print(serializer.data)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            query = self.get_queryset().filter(is_active=True)
            if 'file_name' not in request.data:
                return errorMessage('File name is a required field')
            file_name = request.data['file_name']
            file_name_list =  [
                'jan-2023.csv', 
                'feb-2023.csv', 
                'march-2023.csv', 
                'april-2023.csv', 
                'may-2023.csv', 
                'june-2023.csv',
                'july-2023.csv',
            ]
            if file_name not in file_name_list:
                return errorMessage(f'File name is not in the list provided {file_name_list}')
            
            file_path = os.path.join('static/import/employees-attendance/', file_name)

            employees_query = Employees.objects.filter(organization=organization_id)

            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                i = 0

                # This will store all the columns values csv file
                result = []
                columns = []
                for rows in reader:
                    if i < 2:
                        i += 1
                        continue
                    if i == 2:
                        for j in range(len(rows)):
                            columns.append(rows[j])
                        break     
                
                for rows in reader:
                    if i < 2:
                        i += 1
                        continue
                    
                    # traverse all the columns in the csv file
                    for j in range(len(rows)):
                        # checks if emp_code exists or not
                        if j == 1:
                            continue
                        
                        if columns[j] == 'emp_code':
                            emp_code = rows[j]
                            if not emp_code:
                                break
                            emp_code = int(emp_code)
                            emp = employees_query.filter(emp_code=emp_code)
                            if not emp.exists():
                                break
                            emp_obj = emp.get()
                        
                        if j > 1:
                            date_value = columns[j]
                            date = datetime.datetime.strptime(date_value, "%m/%d/%Y").date()
                            print(date)
                            status = rows[j]
                            if status in ['Present', 'PRESENT', 'P']:
                                status = 'P'
                            elif status in ['Absent', 'ABSENT', 'A']:
                                status = 'A'
                            elif status.lower() in ['wfh']:
                                status = 'WFH'
                            elif status.lower() in ['weekend']:
                                status = 'W'
                            elif status.lower().endswith('holiday'):
                                status = 'H'
                            elif status.lower().strip() in [
                                    'sick', 'casual', 'emergency',
                                    'bereavement', 'marriage', 'compensatory', 'annual',
                                    'breavement', 'paternity', 'umrah'
                                ]:
                                status = 'L'
                            else:
                                status = None
                            
                            
                            data = {
                                'employee': emp_obj.id,
                                'date': date,
                                'attendance_status': status,
                                'comments': rows[j].strip(),
                                'created_by': request.user.id
                            }

                            result.append(data)
                            if query.filter(employee__emp_code=rows[0], date=date).exists():
                                obj = query.filter(employee__emp_code=rows[0], date=date).first()
                                serializer = EmployeesAttendanceLabelSerializers(obj, data=data, partial=True)
                            else:
                                serializer = EmployeesAttendanceLabelSerializers(data=data)
                            
                            if not serializer.is_valid():
                                print(serializer.errors)
                                continue
                            serializer.save()
                    
                            
            return successMessageWithData('successfully read', result)
            
        except Exception as e:
            return exception(e)
        
        
        
        
        
    def add_existing_data_from_ess(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            user = request.user
            emp_attendance = EmployeesAttendance.objects.filter(
                employee__organization=organization_id,
                is_active=True
            )
            print(emp_attendance)
            for attendance in emp_attendance:
                attendance_labels(self, attendance, user)

            return successMessage('success')
            
        except Exception as e:
            return exception(e)
        
    def all_employee_working_hours(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            current_month=request.data.get('month',None)
            current_year=request.data.get('year',None)
            # print(current_month)
            if current_month is None:
                current_date=datetime.datetime.today().date()
                current_month=current_date.month

            if current_year is None:
                current_date=datetime.datetime.today().date()
                current_year=current_date.year


            
            query_data=custom_query_working_hours(current_month,current_year,organization_id)
            return successMessageWithData('Success',query_data)

        except Exception as e:
            return exception(e)   
        

    def all_employee_attandance_count(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            employee_id=self.kwargs['employee_id']
            start_date=request.data.get('start_date',None)
            end_date=request.data.get('end_date',None)
            # start_date=None
            # end_date=None
            # employee=Employees.objects.filter(id=employee_id)
            # if not employee.exists():
            #     return errorMessage("Employee not exists at given id")
            # employee_obj=employee.get()
            # print(current_month)
            if start_date is None:
                current_year = datetime.date.today().year

                # Get the first day of the current year
                start_date = datetime.date(current_year, 1, 1)

            if end_date is None:
                end_date=datetime.datetime.today().date()

            if str(end_date)<str(start_date):
                return errorMessage("end date must be greater than start date")

            
            query_data=custom_query_employee_overall_attendance_count(start_date,end_date,employee_id,organization_id)
            return successMessageWithData('Success',query_data)

        except Exception as e:
            return exception(e) 
        
        
        
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import datetime, calendar
from employees.models import (
    Employees,
    EmployeeProjects,
    EmployeeRoles,
)
from projects.models import Projects
from roles.models import Roles
from .serializers import AttendancePMOSerializer


class AttendanceStatusPMOAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            decoded = decodeToken(self, request)
            organization_id = decoded.get('organization_id')
            logged_in_employee_id = decoded.get('employee_id')

            current_date = datetime.date.today()
            month = int(request.data.get('month', current_date.month))
            year = int(request.data.get('year', current_date.year))

            # -----------------------------
            # STEP 1: Determine visible employees
            # -----------------------------

            if request.user.is_superuser or request.user.is_admin:
                # Admin → all employees
                employees_qs = Employees.objects.filter(
                    organization=organization_id,
                    is_active=True
                )
            else:
                    # PM / APM → only project team (excluding self)

                    # PM projects
                    pmo_project_ids = EmployeeProjects.objects.filter(
                        employeeroles__role__title__in=[
                            'Project Manager',
                            'Associate Project Manager'
                        ],
                        employeeroles__is_active=True,
                        employee_id=logged_in_employee_id
                    ).values_list('project_id', flat=True).distinct()

                    # Employees under those projects
                    pmo_employee_ids = EmployeeProjects.objects.filter(
                        project_id__in=pmo_project_ids
                    ).values_list('employee_id', flat=True).distinct()

                    # EXCLUDE logged-in PM/APM
                    employees_qs = Employees.objects.filter(
                        id__in=pmo_employee_ids,
                        is_active=True
                    ).exclude(id=logged_in_employee_id)


            # -----------------------------
            # STEP 2: Attendance labels for month
            # -----------------------------
            attendance_qs = EmployeesAttendanceLabel.objects.filter(
                is_active=True,
                date__month=month,
                date__year=year,
                employee__in=employees_qs
            )

            # -----------------------------
            # STEP 3: Serialize
            # -----------------------------
            serializer = AttendancePMOSerializer(
                employees_qs,
                many=True,
                context={
                    'attendance_qs': attendance_qs,
                    'month': month,
                    'year': year
                }
            )

            return success(serializer.data)

        except Exception as e:
            return exception(e)
        
        

def attendance_labels(self, emp_attendance_object, user):
    try:
        emp_id = emp_attendance_object.employee.id
        date = emp_attendance_object.date
        comments = emp_attendance_object.attendance_type
        # print(comments)
        status = None

        if comments:
            if comments == 'office':
                status = 'P'
            elif comments == 'WFH':
                status = 'WFH'
            

        attendance_label = EmployeesAttendanceLabel.objects.filter(
            employee=emp_id, 
            date=date, 
            is_active=True
        )
        if attendance_label.exists():
            # Check the current attendance type in the existing label
            obj = attendance_label.get()

            # Logic to update or skip based on current and new attendance type
            if obj.comments == 'WFH' and comments == 'office':
                # Update from WFH to office
                obj.attendance_status = status
                obj.comments = comments
                obj.save()
            elif obj.comments == 'office' and comments == 'WFH':
                # Do not update from office to WFH
                return None
            else:
                # For repeated same attendance types, do nothing
                return None
        
        else:
            data = {
                'employee': emp_id,
                'date': date,
                'attendance_status': status,
                'comments': comments,
                'created_by': user.id
            }
            serializer = EmployeesAttendanceLabelSerializers(data=data)
            if not serializer.is_valid():
                print(serializer.errors)
            else:
                serializer.save()

        return None
    except Exception as e:
        print(str(e))
        return None
    

def custom_query(start_date,end_date,start_date1,end_date2,organization_id):
    # print(ep_yearly_segmentation, ep_batch,organization_id)
    with connection.cursor() as cursor:
        cursor.execute("""
SELECT 
    d.id,
    d.title,
    COALESCE(COUNT(DISTINCT emp_data.id), 0) AS total_employee_count,
    COALESCE(SUM(CAST(emp_data.total_presents AS INT)), 0) AS total_presents,
    COALESCE(SUM(CAST(emp_data.total_wfh AS INT)), 0) AS total_wfh,
	coalesce(sum(CAST(emp_data.total_casual_leaves AS INT)), 0) as total_casual_leaves,
    coalesce(sum(CAST(emp_data.total_annual_leaves AS INT)), 0) as total_annual_leaves
	  		 , STRING_AGG(
        DISTINCT JSON_BUILD_OBJECT(
			'department',d.title,
            'emp_id', emp_data.id,
			'employee_name',emp_data.employee_name,
			'email',emp_data.email,
			'joining_date',emp_data.joining_date,
			'salary',emp_data.salary,
			'desgination',emp_data.desgination,
			'status',emp_data.status,
			'projects', emp_data.projects,
			'degree_title',emp_data.degree_title,
			'age',emp_data.age,
			'experience',emp_data.total_work_experience_years_months
        )::TEXT, 
        ',' 
    ) AS employees_data
   
FROM 
    departments_departments AS d
JOIN 
    departments_groupheads AS gd ON d.grouphead_id = gd.id
JOIN 
    organizations_organization AS org ON gd.organization_id = org.id
LEFT JOIN (
    SELECT 
        e.id,
	    e.name as employee_name,
	    e.official_email as email,
        e.department_id AS dp_id,
	    e.joining_date as joining_date,
	    e.current_salary as salary,
	    stf.title as desgination,
	    ept.title as status,
	    project_data.projects AS projects,
	    edu.degree_title as degree_title,
	CASE 
    WHEN wrok_experience.total_work_experience_years IS NULL THEN '0'
    ELSE CONCAT(
        FLOOR(wrok_experience.total_work_experience_years), 
        '.', 
        FLOOR((wrok_experience.total_work_experience_years - FLOOR(wrok_experience.total_work_experience_years)) * 10)
    )
END AS total_work_experience_years_months,
	    EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.dob)) AS age,
	    coalesce(sum(leaves_data.total_casual_leaves)) as total_casual_leaves,
		coalesce(sum(leaves_data.total_annual_leaves)) as total_annual_leaves,
		
        COALESCE(SUM(attendance_data.etotal_presents), 0) AS total_presents,
        COALESCE(SUM(attendance_data.etotal_wfh), 0) AS total_wfh
        
    FROM 
        employees_employees AS e
	LEFT JOIN (
		select ARRAY_AGG(DISTINCT CONCAT(pp.id, ':', pp.name))  AS projects,eep.employee_id
		from
	employees_employeeprojects AS eep  
	JOIN projects_projects AS pp ON eep.project_id = pp.id
	Where eep.is_active=True and pp.is_active=True
		group by eep.employee_id
	) as project_data on e.id=project_data.employee_id

	LEFT JOIN organizations_staffclassification as stf ON e.staff_classification_id=stf.id and stf.is_active=True
    LEFT JOIN employees_employeetypes as ept ON e.employee_type_id=ept.id and ept.is_active=True
	LEFT JOIN (
    SELECT 
        ed.employee_id,
        ed.degree_title,
        ROW_NUMBER() OVER (PARTITION BY ed.employee_id ORDER BY id DESC) AS row_num
    FROM 
        institutes_employeeeducations as ed
    WHERE 
        ed.is_active = True
	
) AS edu ON e.id = edu.employee_id AND edu.row_num = 1
	
Left Join (
	select we.employee_id,   (SUM(
    (DATE_PART('year', age(we.leaving_date, we.joining_date)) * 12) +
    DATE_PART('month', age(we.leaving_date, we.joining_date))
) / 10.0) AS total_work_experience_years
	from companies_employeeworkexperience as we
	GROUP BY we.employee_id
)as wrok_experience on wrok_experience.employee_id=e.id

	LEFT JOIN (
		select ea.employee_id, 

		
			COALESCE(SUM(CASE WHEN ea.employee_presents > 0 THEN 1 ELSE 0 END), 0) AS etotal_presents,
			COALESCE(SUM(CASE WHEN ea.employee_presents =0 AND ea.employee_wfh > 0 THEN 1 ELSE 0 END), 0) AS etotal_wfh
		from (
			SELECT 
				al.employee_id
-- 				,coalesce(sum(CASE WHEN al.attendance_status = 'L' THEN 1 else 0 end))  AS employee_leaves,
-- 				coalesce(sum(CASE WHEN al.attendance_status = 'H' THEN 1 else 0 end))  AS employee_holidays,
-- 				coalesce(sum(CASE WHEN al.attendance_status = 'W' THEN 1 else 0 end))  AS employee_weekends,
				,coalesce(sum(CASE WHEN al.attendance_status = 'P' THEN 1 else 0 end))  AS employee_presents
				,coalesce(sum(CASE WHEN al.attendance_status = 'WFH' THEN 1 else 0 end))  AS employee_wfh
				,al.date
			FROM 
				employees_attendance_employeesattendancelabel AS al 
				
			WHERE 
				al.is_active = True 
				AND al.date >=%s 
				AND al.date <=%s
			group by al.employee_id , al.date
		) as ea  
		group by ea.employee_id
    ) AS attendance_data ON e.id = attendance_data.employee_id
    LEFT JOIN (
        SELECT 
		 COALESCE(SUM(CASE WHEN tl.title = 'Casual Leaves' THEN el.duration  ELSE 0 END), 0) AS total_casual_leaves,
         COALESCE(SUM(CASE WHEN tl.title = 'Annual Leaves' THEN el.duration ELSE 0 END), 0) AS total_annual_leaves,
--             COALESCE(SUM(el.duration), 0) AS total_durations,
            el.employee_id
            
        FROM 
            reimbursements_employeesleaves AS el
        JOIN 
            reimbursements_leavetypes AS tl ON tl.id = el.leave_types_id
        WHERE 
            el.is_active = True 
            AND el.status = 'approved'
            AND el.created_at >=%s::timestamp 
            AND el.created_at <=%s::timestamp
        GROUP BY 
            el.employee_id
    ) AS leaves_data ON leaves_data.employee_id = e.id 
    WHERE 
        e.is_active = True 
    GROUP BY 
        e.id
	,stf.title,ept.title,project_data.projects,edu.degree_title,wrok_experience.total_work_experience_years
        
) AS emp_data ON emp_data.dp_id = d.id
WHERE  
    d.is_active = True  
    AND org.id = %s
GROUP BY 
    d.id,
    org.id
HAVING 
    COALESCE(COUNT(DISTINCT emp_data.id), 0) > 0;
        """, [start_date,end_date,start_date1,end_date2,organization_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Parse the employees_data field into a list of dictionaries
        for row in rows:
            row['employees_data'] = parse_employees_data(row['employees_data'])

        return rows

def parse_employees_data(employees_data):
    # Parse the employees_data string into a list of dictionaries
    return json.loads("[" + employees_data + "]")

def custom_query_employee(start_date,end_date,start_date1,end_date2,emp_id,organization_id):
    # print(ep_yearly_segmentation, ep_batch,organization_id)
    with connection.cursor() as cursor:
        cursor.execute("""

    SELECT 
        e.id,
	    e.name as employee_name,
	    e.official_email as email,
        e.department_id AS dp_id,
		d.title as dp_name,
	    e.joining_date as joining_date,
	    e.current_salary as salary,
	    stf.title as desgination,
	    ept.title as status,
	    project_data.projects AS projects,
	    edu.degree_title as degree_title,
	CASE 
    WHEN wrok_experience.total_work_experience_years IS NULL THEN '0'
    ELSE CONCAT(
        FLOOR(wrok_experience.total_work_experience_years), 
        '.', 
        FLOOR((wrok_experience.total_work_experience_years - FLOOR(wrok_experience.total_work_experience_years)) * 10)
    )
END AS total_work_experience_years_months,
	    EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.dob)) AS age,
	    coalesce(sum(leaves_data.total_casual_leaves)) as total_casual_leaves,
		coalesce(sum(leaves_data.total_annual_leaves)) as total_annual_leaves,
		
        COALESCE(SUM(attendance_data.etotal_presents), 0) AS total_presents,
        COALESCE(SUM(attendance_data.etotal_wfh), 0) AS total_wfh
        
    FROM 
        employees_employees AS e
	INNER JOIN departments_departments as d on e.department_id=d.id and d.is_active=True
	LEFT JOIN (
		select ARRAY_AGG(DISTINCT CONCAT(pp.id, ':', pp.name))  AS projects,eep.employee_id
		from
	employees_employeeprojects AS eep  
	JOIN projects_projects AS pp ON eep.project_id = pp.id
	Where eep.is_active=True and pp.is_active=True
		group by eep.employee_id
	) as project_data on e.id=project_data.employee_id

	LEFT JOIN organizations_staffclassification as stf ON e.staff_classification_id=stf.id and stf.is_active=True
    LEFT JOIN employees_employeetypes as ept ON e.employee_type_id=ept.id and ept.is_active=True
	LEFT JOIN (
    SELECT 
        ed.employee_id,
        ed.degree_title,
        ROW_NUMBER() OVER (PARTITION BY ed.employee_id ORDER BY id DESC) AS row_num
    FROM 
        institutes_employeeeducations as ed
    WHERE 
        ed.is_active = True
	
) AS edu ON e.id = edu.employee_id AND edu.row_num = 1
	
Left Join (
	select we.employee_id,   (SUM(
    (DATE_PART('year', age(we.leaving_date, we.joining_date)) * 12) +
    DATE_PART('month', age(we.leaving_date, we.joining_date))
) / 10.0) AS total_work_experience_years
	from companies_employeeworkexperience as we
	GROUP BY we.employee_id
)as wrok_experience on wrok_experience.employee_id=e.id

	LEFT JOIN (
		select ea.employee_id, 

		
			COALESCE(SUM(CASE WHEN ea.employee_presents > 0 THEN 1 ELSE 0 END), 0) AS etotal_presents,
			COALESCE(SUM(CASE WHEN ea.employee_presents =0 AND ea.employee_wfh > 0 THEN 1 ELSE 0 END), 0) AS etotal_wfh
		from (
			SELECT 
				al.employee_id
-- 				,coalesce(sum(CASE WHEN al.attendance_status = 'L' THEN 1 else 0 end))  AS employee_leaves,
-- 				coalesce(sum(CASE WHEN al.attendance_status = 'H' THEN 1 else 0 end))  AS employee_holidays,
-- 				coalesce(sum(CASE WHEN al.attendance_status = 'W' THEN 1 else 0 end))  AS employee_weekends,
				,coalesce(sum(CASE WHEN al.attendance_status = 'P' THEN 1 else 0 end))  AS employee_presents
				,coalesce(sum(CASE WHEN al.attendance_status = 'WFH' THEN 1 else 0 end))  AS employee_wfh
				,al.date
			FROM 
				employees_attendance_employeesattendancelabel AS al 
				
			WHERE 
				al.is_active = True 
				AND al.date >=%s
				AND al.date <=%s
			group by al.employee_id , al.date
		) as ea  
		group by ea.employee_id
    ) AS attendance_data ON e.id = attendance_data.employee_id
    LEFT JOIN (
        SELECT 
		 COALESCE(SUM(CASE WHEN tl.title = 'Casual Leaves' THEN el.duration  ELSE 0 END), 0) AS total_casual_leaves,
         COALESCE(SUM(CASE WHEN tl.title = 'Annual Leaves' THEN el.duration ELSE 0 END), 0) AS total_annual_leaves,
            el.employee_id
            
        FROM 
            reimbursements_employeesleaves AS el
        JOIN 
            reimbursements_leavetypes AS tl ON tl.id = el.leave_types_id
        WHERE 
            el.is_active = True 
            AND el.status = 'approved'
            AND el.created_at >=%s::timestamp 
            AND el.created_at <=%s::timestamp
        GROUP BY 
            el.employee_id
    ) AS leaves_data ON leaves_data.employee_id = e.id 
    WHERE 
        e.is_active = True and e.id=%s and e.organization_id=%s
    GROUP BY 
        e.id
	,stf.title,ept.title,project_data.projects,d.title,edu.degree_title,wrok_experience.total_work_experience_years
        """, [start_date,end_date,start_date1,end_date2,emp_id,organization_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows

def custom_query_working_hours(current_month,current_year,organization_id):
    # print(ep_yearly_segmentation, ep_batch,organization_id)
    with connection.cursor() as cursor:
        cursor.execute("""
WITH DailyHours AS (
    SELECT 
        al.employee_id,
        al.date,
        SUM(al.check_out - al.check_in) AS hours_worked
    FROM 
        employees_attendance_employeesattendance AS al
    WHERE 
        al.is_active = True
        AND EXTRACT(MONTH FROM al.date) = %s
        AND EXTRACT(YEAR FROM al.date) = %s
        AND al.is_check_in = False
        AND al.is_check_out = True
    GROUP BY 
        al.employee_id, al.date
),
TotalHours AS (
    SELECT
        employee_id,
        SUM(hours_worked) AS total_interval
    FROM 
        DailyHours
    GROUP BY 
        employee_id
)
SELECT 
    e.id,
    e.emp_code,
    e.name AS employee_name,
    -- Conditional output for total monthly hours
    CASE
        WHEN t.total_interval IS NULL THEN NULL
        ELSE CONCAT(
            (EXTRACT(DAY FROM t.total_interval) * 24) + EXTRACT(HOUR FROM t.total_interval),
            'h ',
            EXTRACT(MINUTE FROM t.total_interval),
            'm'
        )
    END AS total_monthly_hours,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'date', dh.date,
            'hours', CASE
                WHEN dh.hours_worked IS NULL THEN NULL
                ELSE CONCAT(
                    EXTRACT(HOUR FROM dh.hours_worked),
                    'h ',
                    EXTRACT(MINUTE FROM dh.hours_worked),
                    'm'
                )
            END
        )
        ORDER BY dh.date  -- Sorting daily hours by date
    ) AS daily_hours
FROM 
    employees_employees AS e
LEFT JOIN 
    TotalHours AS t ON e.id = t.employee_id
LEFT JOIN 
    DailyHours AS dh ON e.id = dh.employee_id
WHERE 
    e.is_active = True 
    AND e.organization_id = %s
GROUP BY 
    e.id, e.emp_code, e.name, t.total_interval
ORDER BY 
    e.id
         """, [current_month,current_year,organization_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows

    
def custom_query_employee_overall_attendance_count(start_date,end_data,employee_id,organization_id):
    # print(ep_yearly_segmentation, ep_batch,organization_id)
    with connection.cursor() as cursor:
        cursor.execute("""
WITH date_ranges AS (
    SELECT 
        %s::date AS start_date,
        %s::date AS end_date
)
SELECT 
    e.id,
    e.name AS employee_name,
    e.official_email AS email,
    e.department_id AS dp_id,
    d.title AS dp_name,
    e.joining_date AS joining_date,
    stf.title AS designation,
    ept.title AS status,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.dob)) AS age,
    COALESCE(workdays.total_weekdays, 0) AS total_working_days,
    COALESCE(workdays.total_weekends, 0) AS total_weekends,
    COALESCE(leaves_data.total_weekday_leaves, 0) AS total_leaves,
    COALESCE(leaves_data.total_weekend_leaves, 0) AS total_weekend_leaves,
    COALESCE(attendance_data.total_weekday_presents, 0) AS total_presents,
    COALESCE(attendance_data.total_weekend_presents, 0) AS total_weekend_presents,
    COALESCE(attendance_data.total_weekday_wfh, 0) AS total_wfh,
    COALESCE(attendance_data.total_weekend_wfh, 0) AS total_weekend_wfh,
    COALESCE(holidays.total_weekdays, 0) AS total_weekday_holidays,
    COALESCE(holidays.total_weekends, 0) AS total_weekend_holidays,
    CASE
        WHEN (workdays.total_weekdays - COALESCE(holidays.total_weekdays, 0) - COALESCE(attendance_data.total_weekday_presents, 0) - COALESCE(leaves_data.total_weekday_leaves, 0) - COALESCE(attendance_data.total_weekday_wfh, 0)) < 0 
        THEN 0
        ELSE (workdays.total_weekdays - COALESCE(holidays.total_weekdays, 0) - COALESCE(attendance_data.total_weekday_presents, 0) - COALESCE(leaves_data.total_weekday_leaves, 0) - COALESCE(attendance_data.total_weekday_wfh, 0))
    END AS total_absent
FROM 
    employees_employees AS e
INNER JOIN 
    departments_departments AS d ON e.department_id = d.id AND d.is_active = True
LEFT JOIN 
    organizations_staffclassification AS stf ON e.staff_classification_id = stf.id AND stf.is_active = True
LEFT JOIN 
    employees_employeetypes AS ept ON e.employee_type_id = ept.id AND ept.is_active = True
LEFT JOIN (
    SELECT 
        ea.employee_id, 
        COALESCE(SUM(CASE WHEN ea.is_weekday AND ea.employee_presents > 0 THEN 1 ELSE 0 END), 0) AS total_weekday_presents,
        COALESCE(SUM(CASE WHEN NOT ea.is_weekday AND ea.employee_presents > 0 THEN 1 ELSE 0 END), 0) AS total_weekend_presents,
        COALESCE(SUM(CASE WHEN ea.is_weekday AND ea.employee_wfh > 0 THEN 1 ELSE 0 END), 0) AS total_weekday_wfh,
        COALESCE(SUM(CASE WHEN NOT ea.is_weekday AND ea.employee_wfh > 0 THEN 1 ELSE 0 END), 0) AS total_weekend_wfh
    FROM (
        SELECT 
            al.employee_id,
            COALESCE(SUM(CASE WHEN al.attendance_status = 'P' THEN 1 ELSE 0 END), 0) AS employee_presents,
            COALESCE(SUM(CASE WHEN al.attendance_status = 'WFH' THEN 1 ELSE 0 END), 0) AS employee_wfh,
            EXTRACT(ISODOW FROM al.date) < 6 AS is_weekday,
            al.date
        FROM 
            employees_attendance_employeesattendancelabel AS al 
        WHERE 
            al.is_active = True 
            AND al.date >= (SELECT start_date FROM date_ranges)
            AND al.date <= (SELECT end_date FROM date_ranges)
        GROUP BY 
            al.employee_id, al.date
    ) AS ea  
    GROUP BY 
        ea.employee_id
) AS attendance_data ON e.id = attendance_data.employee_id
LEFT JOIN (
    SELECT 
        SUM(CASE WHEN EXTRACT(ISODOW FROM date) < 6 THEN 1 ELSE 0 END) AS total_weekdays,
        SUM(CASE WHEN EXTRACT(ISODOW FROM date) >= 6 THEN 1 ELSE 0 END) AS total_weekends
    FROM 
        reimbursements_employeesofficialholidays
    WHERE 
        is_active = True
        AND date >= (SELECT start_date FROM date_ranges)
        AND date <= (SELECT end_date FROM date_ranges)
) AS holidays ON TRUE
LEFT JOIN (
    SELECT 
        el.employee_id,
        COALESCE(SUM(CASE WHEN EXTRACT(ISODOW FROM el.start_date) < 6 THEN el.duration ELSE 0 END), 0) AS total_weekday_leaves,
        COALESCE(SUM(CASE WHEN EXTRACT(ISODOW FROM el.start_date) >= 6 THEN el.duration ELSE 0 END), 0) AS total_weekend_leaves
    FROM 
        reimbursements_employeesleaves AS el
    WHERE 
        el.is_active = True 
        AND el.status = 'approved'
        AND el.start_date >= (SELECT start_date FROM date_ranges)::timestamp 
        AND el.end_date <= (SELECT end_date FROM date_ranges)::timestamp
    GROUP BY 
        el.employee_id
) AS leaves_data ON leaves_data.employee_id = e.id 
CROSS JOIN (
    SELECT 
        SUM(CASE WHEN EXTRACT(ISODOW FROM gs) < 6 THEN 1 ELSE 0 END) AS total_weekdays,
        SUM(CASE WHEN EXTRACT(ISODOW FROM gs) >= 6 THEN 1 ELSE 0 END) AS total_weekends
    FROM 
        generate_series((SELECT start_date FROM date_ranges), (SELECT end_date FROM date_ranges), '1 day') gs
) AS workdays
WHERE 
    e.is_active = True 
    AND e.id = %s
    AND e.organization_id = %s
GROUP BY 
    e.id, stf.title, ept.title, d.title, leaves_data.total_weekday_leaves, leaves_data.total_weekend_leaves, attendance_data.total_weekday_presents, attendance_data.total_weekend_presents, attendance_data.total_weekday_wfh, attendance_data.total_weekend_wfh, workdays.total_weekdays, workdays.total_weekends, holidays.total_weekdays, holidays.total_weekends;
    """, [start_date,end_data,employee_id,organization_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows

def custom_query_get_wfh_count(employee_id, month, year):
    with connection.cursor() as cursor:
        cursor.execute("""
SELECT 
    COUNT(DISTINCT al.date) AS wfh_count
FROM 
    employees_attendance_employeesattendancelabel AS al
WHERE 
    al.is_active = TRUE 
    AND al.attendance_status = 'WFH'
    AND al.employee_id = %s  -- Placeholder for employee ID
    AND EXTRACT(MONTH FROM al.date) = %s  -- Placeholder for month number (1-12)
    AND EXTRACT(YEAR FROM al.date) =%s   -- Placeholder for year
    AND NOT EXISTS (
        SELECT 1
        FROM employees_attendance_employeesattendancelabel AS o
        WHERE 
            o.is_active = TRUE
            AND o.attendance_status = 'P'  -- Assuming 'P' indicates an office presence
            AND o.date = al.date
            AND o.employee_id = al.employee_id
    )
GROUP BY 
    DATE_TRUNC('month', al.date)
""", [employee_id, month, year])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows
    
def parse_attendance(data):
    # Split the data into user_id and the rest
    user_id, rest = data.split(":", 1)
    # Further split the remaining data into date_time and other_info
    date_time, other_info = rest.split("(", 1)
    # Convert user_id to integer
    user_id = int(user_id.strip())
    # Separate date and time
    date, time = date_time.strip().split()
    # Extract mode and state from the other_info
    mode, state = map(int, other_info.strip(")").split(","))
    # Return a dictionary with parsed attendance details
    return {
        "user_id": user_id,
        "date": date,
        "time": time,
        "mode": mode,
        "state": state,
    }

def create_attendance_log(emp_id, result, status,ser_no):
        # Create a new attendance machine log
        AttendanceMachineslogs.objects.create(
            employee=emp_id,
            date=result['date'],
            time=result['time'],
            status=status,
            mode=result['mode'],
            state=result['state'],
            machine_serial_number=ser_no,
            is_active=True
        )

def log_to_file(message,filename):
    # Ensure the static folder exists
    static_folder_path = os.path.join(settings.BASE_DIR, "static")
    os.makedirs(static_folder_path, exist_ok=True)

    file_name=f'{filename}.txt'

    # File to log job runs
    log_file_path = os.path.join(static_folder_path,file_name)

    # Append message to log file
    with open(log_file_path, 'a') as f:
        f.write(f"{datetime.datetime.now()}: {message}\n")







def _to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes')
    return bool(value)
# ---------------- Upload Screenshot ----------------
from .models import Screenshot, Heartbeat  # Add Heartbeat import
@api_view(['POST'])
def upload_screenshot(request):
    try:
        attendance_id = request.data.get('attendance_id')
        timestamp = request.data.get('timestamp')
        is_heartbeat = _to_bool(request.data.get('is_heartbeat', False))

        if not attendance_id:
            return Response({'error': 'attendance_id is required'}, status=400)

        attendance = get_object_or_404(EmployeesAttendance, id=attendance_id, is_active=True)

        # Parse timestamp
        try:
            ts = parser.isoparse(timestamp) if timestamp else timezone.now()
        except:
            ts = timezone.now()

        # -------------------------
        # 🩺 HEARTBEAT PROCESSING 
        # -------------------------
        if is_heartbeat:
            tracker_status = request.data.get('tracker_status', 'STARTED')
            machine_info_str = request.data.get('machine_info')
            
            # Parse machine_info
            machine_info = None
            if machine_info_str:
                try:
                    machine_info = json.loads(machine_info_str) if isinstance(machine_info_str, str) else machine_info_str
                except:
                    machine_info = None

            # Create heartbeat record
            heartbeat_obj = Heartbeat.objects.create(
                attendance=attendance,
                timestamp=ts,
                tracker_status=tracker_status,
                machine_info=machine_info,
                is_active=True
            )

            return Response({
                'status': 'heartbeat_received',
                'timestamp': ts.isoformat(),
                'heartbeat_id': heartbeat_obj.id,
                'tracker_status': tracker_status
            }, status=200)

        # -------------------------
        # 🖼 SCREENSHOT + HEARTBEAT PROCESSING
        # -------------------------
        screenshot_file = request.FILES.get('screenshot')
        
        if not screenshot_file:
            return Response({'error': 'screenshot file is required for screenshot uploads'}, status=400)

        # Process screenshot data
        window_title = request.data.get('window_title', 'Unknown')
        is_idle = _to_bool(request.data.get('is_idle', False))
        idle_duration_seconds = int(request.data.get('idle_duration_seconds', 0) or 0)
        is_productive = _to_bool(request.data.get('is_productive', False))
        productive_time_min = float(request.data.get('productive_time_min', 0.0))

        # Productivity score
        productivity_score = (100 if is_productive else 0 if is_idle else 50)

        # Create screenshot object
        screenshot_obj = Screenshot.objects.create(
            attendance=attendance,
            timestamp=ts,
            window_title=window_title,
            is_idle=is_idle,
            idle_duration_seconds=idle_duration_seconds,
            is_productive=is_productive,
            productivity_score=productivity_score,
            productive_time_min=productive_time_min,
            deleted_by_user=False,
            is_active=True
        )

        # Save screenshot file
        folder = f"{attendance_id}/"
        filename = f"screenshot_{ts.strftime('%Y-%m-%d_%H-%M-%S')}.png"
        full_path = folder + filename

        screenshot_obj.screenshot.save(full_path, screenshot_file, save=True)

        # Also create a heartbeat record for screenshot activity
        tracker_status = request.data.get('tracker_status', 'ACTIVE')
        machine_info_str = request.data.get('machine_info')
        
        machine_info = None
        if machine_info_str:
            try:
                machine_info = json.loads(machine_info_str) if isinstance(machine_info_str, str) else machine_info_str
            except:
                machine_info = None

        heartbeat_obj = Heartbeat.objects.create(
            attendance=attendance,
            timestamp=ts,
            tracker_status=tracker_status,
            machine_info=machine_info,
            is_active=True
        )

        return Response({
            'status': 'success',
            'screenshot_id': screenshot_obj.id,
            'heartbeat_id': heartbeat_obj.id,
            'file_url': request.build_absolute_uri(screenshot_obj.screenshot.url),
            'timestamp': ts.isoformat(),
            'productivity_score': productivity_score,
            'productive_time_min': productive_time_min,
            'tracker_status': tracker_status
        }, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
    
    
    
#--------------------------------------------------WFH_UPLOAD_Screenshot------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_WFH_screenshot(request):
    try:
        attendance_id = request.data.get('attendance_id')
        timestamp = request.data.get('timestamp')
        is_heartbeat = _to_bool(request.data.get('is_heartbeat', False))

        if not attendance_id:
            return Response({'error': 'attendance_id is required'}, status=400)

        attendance = get_object_or_404(EmployeesAttendance, id=attendance_id, is_active=True)

        # Parse timestamp
        try:
            ts = parser.isoparse(timestamp) if timestamp else timezone.now()
        except:
            ts = timezone.now()

        # -------------------------
        # 🩺 HEARTBEAT PROCESSING 
        # -------------------------
        if is_heartbeat:
            tracker_status = request.data.get('tracker_status', 'STARTED')
            machine_info_str = request.data.get('machine_info')
            
            # Parse machine_info
            machine_info = None
            if machine_info_str:
                try:
                    machine_info = json.loads(machine_info_str) if isinstance(machine_info_str, str) else machine_info_str
                except:
                    machine_info = None

            # Create heartbeat record
            heartbeat_obj = Heartbeat.objects.create(
                attendance=attendance,
                timestamp=ts,
                tracker_status=tracker_status,
                machine_info=machine_info,
                is_active=True
            )

            return Response({
                'status': 'heartbeat_received',
                'timestamp': ts.isoformat(),
                'heartbeat_id': heartbeat_obj.id,
                'tracker_status': tracker_status
            }, status=200)

        # -------------------------
        # 🖼 SCREENSHOT + HEARTBEAT PROCESSING
        # -------------------------
        screenshot_file = request.FILES.get('screenshot')
        
        if not screenshot_file:
            return Response({'error': 'screenshot file is required for screenshot uploads'}, status=400)

        # Process screenshot data
        window_title = request.data.get('window_title', 'Unknown')
        is_idle = _to_bool(request.data.get('is_idle', False))
        idle_duration_seconds = int(request.data.get('idle_duration_seconds', 0) or 0)
        is_productive = _to_bool(request.data.get('is_productive', False))
        productive_time_min = float(request.data.get('productive_time_min', 0.0))

        # Productivity score
        productivity_score = (100 if is_productive else 0 if is_idle else 50)

        # Create screenshot object
        screenshot_obj = Screenshot.objects.create(
            attendance=attendance,
            timestamp=ts,
            window_title=window_title,
            is_idle=is_idle,
            idle_duration_seconds=idle_duration_seconds,
            is_productive=is_productive,
            productivity_score=productivity_score,
            productive_time_min=productive_time_min,
            deleted_by_user=False,
            is_active=True
        )

        # Save screenshot file
        folder = f"{attendance_id}/"
        filename = f"screenshot_{ts.strftime('%Y-%m-%d_%H-%M-%S')}.png"
        full_path = folder + filename

        screenshot_obj.screenshot.save(full_path, screenshot_file, save=True)

        # Also create a heartbeat record for screenshot activity
        tracker_status = request.data.get('tracker_status', 'ACTIVE')
        machine_info_str = request.data.get('machine_info')
        
        machine_info = None
        if machine_info_str:
            try:
                machine_info = json.loads(machine_info_str) if isinstance(machine_info_str, str) else machine_info_str
            except:
                machine_info = None

        heartbeat_obj = Heartbeat.objects.create(
            attendance=attendance,
            timestamp=ts,
            tracker_status=tracker_status,
            machine_info=machine_info,
            is_active=True
        )

        return Response({
            'status': 'success',
            'screenshot_id': screenshot_obj.id,
            'heartbeat_id': heartbeat_obj.id,
            'file_url': request.build_absolute_uri(screenshot_obj.screenshot.url),
            'timestamp': ts.isoformat(),
            'productivity_score': productivity_score,
            'productive_time_min': productive_time_min,
            'tracker_status': tracker_status
        }, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=400)

# ---------------------------------------------------------
# 1️⃣ GET SCREENSHOTS BY EMPLOYEE (DATE or MONTH)
# ---------------------------------------------------------
@api_view(['GET'])
def screenshots_by_employee_date(request):
    employee_id = request.GET.get('employee_id')
    date = request.GET.get('date')
    month = request.GET.get('month')

    if not employee_id:
        return Response({'error': 'employee_id is required'}, status=400)

    qs = Screenshot.objects.filter(attendance__employee_id=employee_id, is_active=True)

    if date:
        qs = qs.filter(attendance__date=date)
    elif month:
        qs = qs.filter(attendance__date__startswith=month)

    data = []
    for ss in qs.order_by('attendance__date', 'attendance__check_in', 'timestamp'):
        data.append({
            'attendance_id': ss.attendance.id,
            'slot_check_in': ss.attendance.check_in,
            'slot_check_out': ss.attendance.check_out,
            'date': ss.attendance.date,
            'timestamp': ss.timestamp,
            'window_title': ss.window_title,
            'screenshot_url': request.build_absolute_uri(ss.screenshot.url) if ss.screenshot else None,
            'is_idle': ss.is_idle,
            'is_productive': ss.is_productive,
            'productivity_score': ss.productivity_score or 0.0,
        })

    return Response(data)

# ---------------------------------------------------------
# 3️⃣ GET SCREENSHOTS BY ATTENDANCE ID
# ---------------------------------------------------------
from django.db.models import Count, Sum
from helpers.custom_permissions import IsAuthenticated

# @api_view(['GET'])
# def get_screenshots_by_attendance(request, attendance_id):
#     attendance = get_object_or_404(EmployeesAttendance, id=attendance_id)

#     # Active screenshots only
#     screenshots = Screenshot.objects.filter(
#         attendance=attendance,
#         deleted_by_user=False,
#         is_active=True
#     ).order_by('timestamp')

#     serializer = ScreenshotSerializer(screenshots, many=True, context={'request': request})
#     screenshots_data = serializer.data

#     total_idle_time = sum(ss['idle_duration_seconds'] / 60 for ss in screenshots_data)
#     total_productive_time = sum(ss.get('productive_time_min', 0.0) for ss in screenshots_data)
#     total_time = total_idle_time + total_productive_time

#     overall_productivity_percentage = (
#         round((total_productive_time / total_time * 100), 2)
#         if total_time > 0 else 0.0
#     )

#     # Deleted screenshots summary
#     deleted_info = Screenshot.objects.filter(
#         attendance=attendance,
#         deleted_by_user=True
#     ).aggregate(
#         count=Count('id'),
#         deducted_min=Sum('productive_time_min')  # Or use a separate field if you store actual deducted minutes
#     )

#     deleted_count = deleted_info['count'] or 0
#     deleted_deducted_min = round(deleted_info['deducted_min'] or 0, 2)

#     result = {
#         "attendance_id": attendance.id,
#         "employee_id": attendance.employee_id,
#         "check_in": attendance.check_in,
#         "check_out": attendance.check_out,
#         "session_duration_minutes": round(total_time, 2),
#         "total_screenshots": screenshots.count(),
#         "total_idle_time_min": round(total_idle_time, 2),
#         "total_productive_time_min": round(total_productive_time, 2),
#         "overall_productivity_percentage": overall_productivity_percentage,
#         "deleted_screenshots_count": deleted_count,
#         "deleted_screenshots_deducted_min": deleted_deducted_min,
#         "screenshots": screenshots_data,
#     }

#     return Response(result, status=status.HTTP_200_OK)

#--------------------------------------------------------------------------------------------------------------

@api_view(['GET'])
def get_screenshots_by_attendance(request, attendance_id):
    attendance = get_object_or_404(EmployeesAttendance, id=attendance_id)

    local_tz = pytz.timezone('Asia/Karachi')
    now_local = timezone.now().astimezone(local_tz)

    screenshots_qs = Screenshot.objects.filter(
        attendance=attendance,
        deleted_by_user=False,
        is_active=True
    ).order_by('timestamp')

    serializer = ScreenshotSerializer(
        screenshots_qs, many=True, context={'request': request}
    )
    screenshots_data = serializer.data

    # ---------- SESSION DURATION ----------
    if attendance.check_in:
        check_in_dt = datetime.datetime.combine(
            attendance.date, attendance.check_in
        )
        if timezone.is_naive(check_in_dt):
            check_in_dt = local_tz.localize(check_in_dt)

        if attendance.check_out:
            check_out_dt = datetime.datetime.combine(
                attendance.date, attendance.check_out
            )
            if timezone.is_naive(check_out_dt):
                check_out_dt = local_tz.localize(check_out_dt)
        else:
            check_out_dt = now_local

        session_duration_sec = max(
            (check_out_dt - check_in_dt).total_seconds(), 0
        )
    else:
        session_duration_sec = 0

    session_duration_min = session_duration_sec / 60

    # ---------- INTERVAL-BASED CALCULATION ----------
    total_idle_min = 0
    total_productive_min = 0

    timestamps = [
        timezone.localtime(ss.timestamp, local_tz)
        for ss in screenshots_qs
    ]

    for i, ss in enumerate(screenshots_qs):
        current_ts = timestamps[i]

        # interval end
        if i + 1 < len(timestamps):
            next_ts = timestamps[i + 1]
        else:
            break
            # next_ts = (
            #     timezone.localtime(check_out_dt, local_tz)
            #     if attendance.check_out
            #     else now_local
            # )

        interval_sec = max((next_ts - current_ts).total_seconds(), 0)
        interval_min = interval_sec / 60

        idle_min = (ss.idle_duration_seconds or 0) / 60
        idle_min = min(idle_min, interval_min)

        productive_min = max(interval_min - idle_min, 0)

        total_idle_min += idle_min
        total_productive_min += productive_min

    # ---------- PRODUCTIVITY ----------
    overall_productivity_percentage = (
        round((total_productive_min / session_duration_min) * 100, 2)
        if session_duration_min > 0 else 0.0
    )

    # ---------- DELETED SCREENSHOTS ----------
    deleted_info = Screenshot.objects.filter(
        attendance=attendance,
        deleted_by_user=True
    ).aggregate(
        count=Count('id'),
        deducted_min=Sum('productive_time_min')
    )

    result = {
        "attendance_id": attendance.id,
        "employee_id": attendance.employee_id,
        "check_in": attendance.check_in,
        "check_out": attendance.check_out,
        "session_duration_minutes": round(session_duration_min, 2),
        "total_screenshots": screenshots_qs.count(),
        "total_idle_time_min": round(total_idle_min, 2),
        "total_productive_time_min": round(total_productive_min, 2),
        "overall_productivity_percentage": overall_productivity_percentage,
        "deleted_screenshots_count": deleted_info["count"] or 0,
        "deleted_screenshots_deducted_min":
            round(deleted_info["deducted_min"] or 0, 2),
        "screenshots": screenshots_data,
    }

    return Response(result, status=status.HTTP_200_OK)














# ---------------------------------------------------------
# 4️⃣ ANALYTICS BY EMPLOYEE + DATE / MONTH
# ---------------------------------------------------------




# @api_view(['GET'])
# def analytics_by_employee_date(request):
#     employee_id = request.GET.get('employee_id')
#     date = request.GET.get('date')
#     month = request.GET.get('month')

#     if not employee_id:
#         return Response({'error': 'employee_id is required'}, status=400)

#     qs = EmployeesAttendance.objects.filter(employee_id=employee_id)

#     if date:
#         qs = qs.filter(date=date)
#     elif month:
#         qs = qs.filter(date__startswith=month)

#     summary_list = []
#     hourly_productivity = defaultdict(list)

#     overall_productive_seconds = 0
#     overall_idle_seconds = 0
#     overall_total_seconds = 0
#     weighted_overall_productivity = 0

#     local_tz = pytz.timezone('Asia/Karachi')
#     now_local = timezone.now().astimezone(local_tz)

#     for att in qs.order_by('date', 'check_in'):
#         screenshots = Screenshot.objects.filter(
#             attendance=att,
#             is_active=True,
#             deleted_by_user=False
#         ).order_by('timestamp')

#         deleted_screenshots = Screenshot.objects.filter(
#             attendance=att,
#             is_active=False,
#             deleted_by_user=True
#         )
#         deleted_count = deleted_screenshots.count()
#         deleted_deducted_min = sum(
#             (ss.productive_time_min or 0) + (ss.idle_duration_seconds or 0)/60
#             for ss in deleted_screenshots
#         )

#         # compute productivity from active screenshots
#         total_prod = 0
#         total_idle = 0
#         for ss in screenshots:
#             idle = (ss.idle_duration_seconds or 0) / 60
#             prod = ss.productive_time_min or 0
#             total_idle += idle
#             total_prod += prod

#             hour = ss.timestamp.astimezone(local_tz).strftime("%H:00")
#             total = prod + idle
#             p = round((prod / total * 100), 2) if total > 0 else 0
#             hourly_productivity[hour].append(p)

#         total_time = total_prod + total_idle
#         productivity = round((total_prod / total_time * 100), 2) if total_time else 0

#         overall_productive_seconds += total_prod * 60
#         overall_idle_seconds += total_idle * 60
#         weighted_overall_productivity += productivity * (total_time * 60)

#         # 🍀 LIVE DURATION HERE
#         if att.check_in:
#             check_in_dt = datetime.datetime.combine(att.date, att.check_in)
#             if timezone.is_naive(check_in_dt):
#                 check_in_dt = local_tz.localize(check_in_dt)

#             if att.check_out:
#                 check_out_dt = datetime.datetime.combine(att.date, att.check_out)
#                 if timezone.is_naive(check_out_dt):
#                     check_out_dt = local_tz.localize(check_out_dt)
#             else:
#                 check_out_dt = now_local  # <-- LIVE DURATION

#             duration_sec = (check_out_dt - check_in_dt).total_seconds()
#         else:
#             duration_sec = 0

#         overall_total_seconds += duration_sec

#         summary_list.append({
#             "attendance_id": att.id,
#             "date": att.date,
#             "check_in": att.check_in.strftime('%H:%M:%S') if att.check_in else None,
#             "check_out": att.check_out.strftime('%H:%M:%S') if att.check_out else None,
#             "screenshots_count": screenshots.count(),
#             "slot_duration_min": round(duration_sec / 60, 2),
#             "productive_time_min": round(total_prod, 2),
#             "idle_time_min": round(total_idle, 2),
#             "productivity_percentage": productivity,
#             "deleted_screenshots": deleted_count,
#             "deleted_deducted_min": round(deleted_deducted_min, 2),
#         })

#     hourly_graph = []
#     for h in range(24):
#         label = f"{h:02d}:00"
#         values = hourly_productivity.get(label, [])
#         avg = round(sum(values) / len(values), 2) if values else 0
#         hourly_graph.append({
#             "hour": label,
#             "productivity_percentage": avg,
#             "data_points": len(values)
#         })

#     result = {
#         "employee_id": employee_id,
#         "date": date,
#         "summary": summary_list,
#         "hourly_graph": hourly_graph,
#         "overall": {
#             "total_duration_min": round(overall_total_seconds / 60, 2),
#             "total_productive_time_min": round(overall_productive_seconds / 60, 2),
#             "total_idle_time_min": round(overall_idle_seconds / 60, 2),
#             "overall_productivity_percentage":
#                 round(weighted_overall_productivity / overall_total_seconds, 2) if overall_total_seconds else 0
#         }
#     }

#     return Response(result)


from collections import defaultdict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
import pytz
import datetime


from collections import defaultdict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
import datetime
import pytz


@api_view(['GET'])
def analytics_by_employee_date(request):
    employee_id = request.GET.get('employee_id')
    date = request.GET.get('date')
    month = request.GET.get('month')

    if not employee_id:
        return Response({'error': 'employee_id is required'}, status=400)

    qs = EmployeesAttendance.objects.filter(employee_id=employee_id)

    if date:
        qs = qs.filter(date=date)
    elif month:
        qs = qs.filter(date__startswith=month)

    local_tz = pytz.timezone('Asia/Karachi')
    now_local = timezone.now().astimezone(local_tz)

    summary_list = []
    hourly_productivity = defaultdict(list)

    overall_total_seconds = 0
    overall_productive_seconds = 0
    overall_idle_seconds = 0

    for att in qs.order_by('date', 'check_in'):

        screenshots = Screenshot.objects.filter(
            attendance=att,
            is_active=True,
            deleted_by_user=False
        ).order_by('timestamp')

        deleted_screenshots = Screenshot.objects.filter(
            attendance=att,
            deleted_by_user=True
        )

        deleted_count = deleted_screenshots.count()
        deleted_deducted_min = sum(
            ss.productive_time_min or 0 for ss in deleted_screenshots
        )

        # ---------- SESSION DURATION ----------
        if att.check_in:
            check_in_dt = datetime.datetime.combine(att.date, att.check_in)
            if timezone.is_naive(check_in_dt):
                check_in_dt = local_tz.localize(check_in_dt)

            if att.check_out:
                check_out_dt = datetime.datetime.combine(att.date, att.check_out)
                if timezone.is_naive(check_out_dt):
                    check_out_dt = local_tz.localize(check_out_dt)
            else:
                check_out_dt = now_local

            duration_sec = max((check_out_dt - check_in_dt).total_seconds(), 0)
        else:
            duration_sec = 0

        slot_duration_min = duration_sec / 60

        overall_total_seconds += duration_sec

        # ---------- INTERVAL-BASED CALCULATION ----------
        total_idle_min = 0
        total_productive_min = 0

        timestamps = [
            timezone.localtime(ss.timestamp, local_tz)
            for ss in screenshots
        ]

        for i, ss in enumerate(screenshots):
            current_ts = timestamps[i]

            if i + 1 < len(timestamps):
                next_ts = timestamps[i + 1]
            else:
                break
                # next_ts = (
                #     timezone.localtime(check_out_dt, local_tz)
                #     if att.check_out else now_local
                # )

            interval_sec = max((next_ts - current_ts).total_seconds(), 0)
            interval_min = interval_sec / 60

            idle_min = (ss.idle_duration_seconds or 0) / 60
            idle_min = min(idle_min, interval_min)

            productive_min = max(interval_min - idle_min, 0)

            total_idle_min += idle_min
            total_productive_min += productive_min

            # ---------- HOURLY GRAPH ----------
            hour_label = current_ts.strftime("%H:00")
            p = (
                round((productive_min / interval_min) * 100, 2)
                if interval_min > 0 else 0
            )
            hourly_productivity[hour_label].append(p)

        overall_idle_seconds += total_idle_min * 60
        overall_productive_seconds += total_productive_min * 60

        productivity_percentage = (
            round((total_productive_min / slot_duration_min) * 100, 2)
            if slot_duration_min > 0 else 0
        )

        summary_list.append({
            "attendance_id": att.id,
            "date": att.date,
            "check_in": att.check_in.strftime('%H:%M:%S') if att.check_in else None,
            "check_out": att.check_out.strftime('%H:%M:%S') if att.check_out else None,
            "screenshots_count": screenshots.count(),
            "slot_duration_min": round(slot_duration_min, 2),
            "productive_time_min": round(total_productive_min, 2),
            "idle_time_min": round(total_idle_min, 2),
            "productivity_percentage": productivity_percentage,
            "deleted_screenshots": deleted_count,
            "deleted_deducted_min": round(deleted_deducted_min, 2),
        })

    # ---------- HOURLY GRAPH FINAL ----------
    hourly_graph = []
    for h in range(24):
        label = f"{h:02d}:00"
        values = hourly_productivity.get(label, [])
        hourly_graph.append({
            "hour": label,
            "productivity_percentage":
                round(sum(values) / len(values), 2) if values else 0,
            "data_points": len(values)
        })

    # ---------- FINAL RESPONSE ----------
    result = {
        "employee_id": employee_id,
        "date": date,
        "summary": summary_list,
        "hourly_graph": hourly_graph,
        "overall": {
            "total_duration_min": round(overall_total_seconds / 60, 2),
            "total_productive_time_min":
                round(overall_productive_seconds / 60, 2),
            "total_idle_time_min":
                round(overall_idle_seconds / 60, 2),
            "overall_productivity_percentage":
                round(
                    (overall_productive_seconds / overall_total_seconds) * 100,
                    2
                ) if overall_total_seconds > 0 else 0
        }
    }

    return Response(result)





#-------------------------------------------------------------------------------------------------------------
@api_view(["DELETE"])
def delete_screenshot(request, attendance_id, screenshot_id):
    """
    Employee deletes a screenshot.
    Deducts actual logged time of that screenshot from attendance.
    """
    try:
        screenshot = (
            Screenshot.objects.filter(
                id=screenshot_id,
                attendance_id=attendance_id,
                is_active=True,
                deleted_by_user=False,
            )
            .select_related("attendance")
            .first()
        )

        if not screenshot:
            return Response(
                {"error": "Screenshot not found or already deleted."}, status=404
            )

        attendance = screenshot.attendance

        # Calculate actual screenshot duration for deduction (same)
        prev_ss = Screenshot.objects.filter(
            attendance=attendance,
            timestamp__lt=screenshot.timestamp,
            is_active=True,
            deleted_by_user=False,
        ).order_by("-timestamp").first()

        next_ss = Screenshot.objects.filter(
            attendance=attendance,
            timestamp__gt=screenshot.timestamp,
            is_active=True,
            deleted_by_user=False,
        ).order_by("timestamp").first()

        if prev_ss and next_ss:
            gap_before = (screenshot.timestamp - prev_ss.timestamp).total_seconds() / 60.0
            gap_after = (next_ss.timestamp - screenshot.timestamp).total_seconds() / 60.0
            deducted_minutes = round((gap_before + gap_after) / 2.0, 2)
        elif prev_ss:
            deducted_minutes = round((screenshot.timestamp - prev_ss.timestamp).total_seconds() / 60.0, 2)
        elif next_ss:
            deducted_minutes = round((next_ss.timestamp - screenshot.timestamp).total_seconds() / 60.0, 2)
        else:
            deducted_minutes = 10.0  # fallback

        # Save delete info
        screenshot.deleted_by_user = True
        screenshot.is_active = False
        screenshot.deducted_minutes = deducted_minutes      # NEW
        screenshot.deleted_at = timezone.now()              # NEW
        screenshot.save(update_fields=[
            "deleted_by_user",
            "is_active",
            "deducted_minutes",
            "deleted_at"
        ])

        # Deduct from attendance total_tracked_time
        if hasattr(attendance, "total_tracked_time") and attendance.total_tracked_time:
            attendance.total_tracked_time = max(
                datetime.timedelta(seconds=0),
                attendance.total_tracked_time - datetime.timedelta(minutes=deducted_minutes)
            )
            attendance.save(update_fields=["total_tracked_time", "updated_at"])

        return Response({
            "status": "success",
            "message": "Screenshot deleted successfully.",
            "deducted_minutes": deducted_minutes,
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)


    
#-----------------------------------------------------------------    ---------------------------------
    
@api_view(['GET'])
def generate_tracker_script(request, attendance_id):
    attendance = get_object_or_404(EmployeesAttendance, id=attendance_id)

    if not attendance.date or not attendance.check_in:
        return HttpResponse("❌ Attendance record missing date or check-in time.", status=400)

    # Combine date + check_in into full datetime - FIXED: use datetime.datetime.combine
    check_in_dt = datetime.datetime.combine(attendance.date, attendance.check_in)
    
    # Make timezone aware
    if timezone.is_naive(check_in_dt):
        pk_tz = pytz.timezone('Asia/Karachi')
        check_in_dt = pk_tz.localize(check_in_dt)

    check_in_iso = check_in_dt.isoformat()
    
    # Get the API URL dynamically
    api_url = request.build_absolute_uri('/api/attendance/upload_screenshot/')

    # Platform detection
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    
    if 'windows' in user_agent:
        platform_type = 'windows'
        filename = f"start_KavSync_{attendance_id}.bat"
        content_type = "application/octet-stream"
        content = generate_windows_bat(attendance_id, check_in_iso, api_url, request)
    elif 'mac' in user_agent or 'darwin' in user_agent:
        platform_type = 'macos'
        filename = f"start_KavSync_{attendance_id}.command"
        content_type = "application/x-shellscript"
        content = generate_macos_script(attendance_id, check_in_iso, api_url, request)
    else:
        platform_type = 'linux'
        filename = f"start_KavSync_{attendance_id}.py"
        content_type = "text/x-python"
        content = generate_linux_script(attendance_id, check_in_iso, api_url, request)

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    # Add instructions header for Linux
    if platform_type == 'linux':
        response['X-Instructions'] = 'After downloading, right-click the file, select "Properties", go to "Permissions" tab, and check "Allow executing file as program". Then double-click to run.'
    
    return response

#---------------------------------------------------------------------------------------------------------

def generate_windows_bat(attendance_id, check_in_iso, api_url, request):
    tracker_url = request.build_absolute_uri(settings.MEDIA_URL + "tracker/tracker.exe")
    tracker_do = "https://universal-hrms-live.sgp1.digitaloceanspaces.com/tracker/tracker.exe"
    return f"""@echo off
setlocal
set ATT_ID={attendance_id}
set CHECKIN="{check_in_iso}"
set API_URL="{api_url}"
set TRACKER_URL="{tracker_url}"
set tracker_do ="{tracker_do}"
set DEST=%APPDATA%\\UniversalHRMS

echo ======================================================
echo [Universal HRMS Tracker - Windows]
echo Attendance ID: %ATT_ID%
echo Check-in: %CHECKIN%


echo ======================================================
echo Creating local directory...
mkdir "%DEST%" >nul 2>&1

if not exist "%DEST%\\tracker.exe" (
    echo Downloading tracker.exe ...
    powershell -Command "Invoke-WebRequest -Uri '%TRACKER_URL%' -OutFile '%DEST%\\tracker.exe' -UseBasicParsing"
)

echo Starting tracker...
start "" "%DEST%\\tracker.exe" %ATT_ID% %CHECKIN% "%API_URL%"

echo Tracker started successfully!
exit
endlocal
"""

def generate_macos_script(attendance_id, check_in_iso, api_url, request):
    tracker_url = request.build_absolute_uri(settings.MEDIA_URL + "tracker/tracker_mac")
    return f"""#!/bin/bash
ATT_ID={attendance_id}
CHECKIN="{check_in_iso}"
API_URL="{api_url}"
TRACKER_URL="{tracker_url}"
DEST="$HOME/Library/Application Support/UniversalHRMS"

echo "======================================================"
echo "[Universal HRMS Tracker - macOS]"
echo "Attendance ID: $ATT_ID"
echo "Check-in: $CHECKIN"

echo "======================================================"
echo "Creating local directory..."
mkdir -p "$DEST"

if [ ! -f "$DEST/tracker_mac" ]; then
    echo "Downloading tracker..."
    curl -L "$TRACKER_URL" -o "$DEST/tracker_mac"
    chmod +x "$DEST/tracker_mac"
fi

echo "Requesting necessary permissions..."
echo "⚠️ Please grant Screen Recording permission in System Preferences > Security & Privacy"

echo "Starting tracker..."
"$DEST/tracker_mac" "$ATT_ID" "$CHECKIN" "$API_URL" &

echo "Tracker started successfully!"
echo "You can close this terminal window."
"""

def generate_linux_script(attendance_id, check_in_iso, api_url, request):
    tracker_url = request.build_absolute_uri(settings.MEDIA_URL + "tracker/tracker_linux")
    
    # Create a Python script that can be executed directly
    python_script = f"""#!/usr/bin/env python3
import os
import subprocess
import sys
import urllib.request

def main():
    ATT_ID = "{attendance_id}"
    CHECKIN = "{check_in_iso}"
    API_URL = "{api_url}"
    TRACKER_URL = "{tracker_url}"
    DEST = os.path.expanduser("~/.universal_hrms")
    
    print("======================================================")
    print("[Universal HRMS Tracker - Linux]")
    print(f"Attendance ID: {{ATT_ID}}")
    print(f"Check-in: {{CHECKIN}}")
    print("======================================================")
    
    # Create directory
    os.makedirs(DEST, exist_ok=True)
    
    tracker_path = os.path.join(DEST, "tracker_linux")
    
    # Download tracker if needed
    if not os.path.exists(tracker_path):
        print("Downloading tracker...")
        try:
            urllib.request.urlretrieve(TRACKER_URL, tracker_path)
            os.chmod(tracker_path, 0o755)
            print("✅ Tracker downloaded successfully!")
        except Exception as e:
            print(f"❌ Download failed: {{e}}")
            sys.exit(1)
    
    # Start tracker
    print("Starting tracker...")
    try:
        subprocess.Popen([tracker_path, ATT_ID, CHECKIN, API_URL])
        print("✅ Tracker started successfully!")
        print("You can close this window.")
    except Exception as e:
        print(f"❌ Failed to start tracker: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""

    return python_script

#----------------------------------------------------------------------------------------------------
@api_view(['GET'])
def generate_stop_tracker_script(request, attendance_id):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    
    if 'windows' in user_agent:
        filename = f"stop_KavSync_{attendance_id}.bat"
        content_type = "application/octet-stream"
        content = f"""@echo off
set ATT_ID={attendance_id}
echo ======================================================
echo [Universal HRMS Tracker Stopper - Windows]
echo Stopping tracker for attendance ID: %ATT_ID%
echo ======================================================
echo Sending stop signal to tracker...
echo Please wait 10 seconds for tracker to update status...
timeout /t 10 /nobreak >nul
taskkill /f /im tracker.exe >nul 2>&1
echo ✅ Tracker stopped successfully (if it was running).
echo You can now close this window.
pause
"""
    elif 'mac' in user_agent or 'darwin' in user_agent:
        filename = f"stop_KavSync_{attendance_id}.command"
        content_type = "application/x-shellscript"
        content = f"""#!/bin/bash
ATT_ID={attendance_id}
echo "======================================================"
echo "[Universal HRMS Tracker Stopper - macOS]"
echo "Stopping tracker for attendance ID: $ATT_ID"
echo "======================================================"
echo "Sending stop signal to tracker..."
echo "Please wait 10 seconds for tracker to update status..."
sleep 10
pkill -f "tracker_mac.*$ATT_ID"
echo "✅ Tracker stopped successfully (if it was running)."
echo "You can now close this window."
read -p "Press Enter to close..."
"""
    else:
        filename = f"stop_Kavsync_{attendance_id}.sh"
        content_type = "application/x-shellscript"
        content = f"""#!/bin/bash
ATT_ID={attendance_id}
echo "======================================================"
echo "[Universal HRMS Tracker Stopper - Linux]"
echo "Stopping tracker for attendance ID: $ATT_ID"
echo "======================================================"
echo "Sending stop signal to tracker..."
echo "Please wait 10 seconds for tracker to update status..."
sleep 10
pkill -f "tracker_linux.*$ATT_ID"
echo "✅ Tracker stopped successfully (if it was running)."
echo "You can now close this window."
read -p "Press Enter to close..."
"""

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response

#---------------------------------------------------------------------------------------------

from .models import Heartbeat  # Add this import

# @api_view(['GET'])
# def tracker_status(request, attendance_id):
#     """Check if tracker is running based on heartbeat"""
#     # Get all heartbeats for this attendance
#     heartbeats = Heartbeat.objects.filter(
#         attendance_id=attendance_id,
#         is_active=True
#     ).order_by('timestamp')
    
#     if not heartbeats.exists():
#         return Response({
#             'status': 'not_started',
#             'message': 'No heartbeat found for this attendance'
#         })
    
#     last_heartbeat = heartbeats.last()
#     diff = (timezone.now() - last_heartbeat.timestamp).total_seconds()
    
#     # Find start time (first heartbeat with tracker_status='STARTED')
#     start_heartbeat = heartbeats.filter(tracker_status='STARTED').first()
    
#     # Find stop time (last heartbeat with tracker_status='STOPPED')
#     stop_heartbeat = heartbeats.filter(tracker_status='STOPPED').last()
    
#     response_data = {
#         'tracker_status': last_heartbeat.tracker_status,
#         'last_seen': last_heartbeat.timestamp,
#         'seconds_ago': int(diff),
#         'machine_info': last_heartbeat.machine_info
#     }
    
#     # Add start time if available
#     if start_heartbeat:
#         response_data['started_at'] = start_heartbeat.timestamp
    
#     # Add stop time if available
#     if stop_heartbeat:
#         response_data['stopped_at'] = stop_heartbeat.timestamp
    
#     # If heartbeat is within last 60 seconds, tracker is running
#     if diff <= 60:
#         response_data['status'] = 'running'
#     else:
#         response_data['status'] = 'stopped'
#         response_data['message'] = f'Last heartbeat was {int(diff)} seconds ago'
    
#     return Response(response_data)

@api_view(['GET'])
def tracker_status(request, attendance_id):
    """Check if tracker is running with 30-minute timeout"""
    # Get all heartbeats for this attendance
    heartbeats = Heartbeat.objects.filter(
        attendance_id=attendance_id,
        is_active=True
    ).order_by('timestamp')
    
    if not heartbeats.exists():
        return Response({
            'status': 'not_started',
            'message': 'No heartbeat found for this attendance'
        })
    
    last_heartbeat = heartbeats.last()
    diff = (timezone.now() - last_heartbeat.timestamp).total_seconds()
    
    # Find start time (first STARTED/ACTIVE heartbeat)
    start_heartbeat = heartbeats.filter(
        tracker_status__in=['STARTED', 'ACTIVE']
    ).first()
    
    # Find stop time (last STOPPED heartbeat)
    stop_heartbeat = heartbeats.filter(tracker_status='STOPPED').last()
    
    response_data = {
        'tracker_status': last_heartbeat.tracker_status,
        'last_seen': last_heartbeat.timestamp,
        'seconds_ago': int(diff),
        'machine_info': last_heartbeat.machine_info
    }
    
    # Add start time if available
    if start_heartbeat:
        response_data['started_at'] = start_heartbeat.timestamp
    
    # Add stop time if available
    if stop_heartbeat:
        response_data['stopped_at'] = stop_heartbeat.timestamp
    
    # Determine status with 30-minute timeout logic
    TIMEOUT_SECONDS = 900  # 30 minutes
    
    if last_heartbeat.tracker_status == 'STOPPED':
        # Tracker explicitly stopped
        response_data['status'] = 'stopped'
        response_data['message'] = 'Tracker has been stopped'
    
    elif last_heartbeat.tracker_status in ['STARTED', 'ACTIVE']:
        if diff > TIMEOUT_SECONDS:  # More than 30 minutes
            response_data['status'] = 'stopped'
            response_data['message'] = f'No heartbeat received for {int(diff/60)} minutes'
            response_data['timeout'] = True
            response_data['timeout_minutes'] = 30
        else:
            # Still within 30 minutes
            response_data['status'] = 'running'
            response_data['message'] = f'Last heartbeat was {int(diff)} seconds ago'
            
            # Optional: Add warning after 5 minutes
            if diff > 300:  # 5 minutes
                response_data['warning'] = 'Heartbeat delayed'
    
    else:
        # Handle any other tracker_status values
        response_data['status'] = last_heartbeat.tracker_status.lower()
        response_data['message'] = f'Tracker status: {last_heartbeat.tracker_status}'
    
    return Response(response_data)







# Added for generating detailed employee attendance report by date range on admin site _ 20-Jan-2026
class CustomAttendanceReportViewSet(viewsets.ViewSet):
    def generate_report(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            
            # Get request data
            employee_id = request.data.get('employee_id')
            start_date_str = request.data.get('start_date')
            end_date_str = request.data.get('end_date')
            
            # Validate required fields
            if not all([employee_id, start_date_str, end_date_str]):
                return Response({
                    'status': 400,
                    'message': 'employee_id, start_date and end_date are required'
                }, status=400)
            
            # Parse dates
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # Validate date range
            if start_date > end_date:
                return Response({
                    'status': 400,
                    'message': 'start_date must be before end_date'
                }, status=400)
            
            # Get employee
            try:
                employee = Employees.objects.get(
                    id=employee_id,
                    organization_id=organization_id,
                    is_active=True
                )
            except Employees.DoesNotExist:
                return Response({
                    'status': 404,
                    'message': 'Employee not found'
                }, status=404)
            
            # Generate all dates in range
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date)
                current_date += datetime.timedelta(days=1)
            
            # Get all attendance labels for the date range
            attendance_labels = EmployeesAttendanceLabel.objects.filter(
                employee=employee,
                date__range=[start_date, end_date],
                is_active=True
            )
            # Convert to dictionary for easy lookup
            label_dict = {label.date: label for label in attendance_labels}
            
            # Get all attendance records for the date range
            attendance_records = EmployeesAttendance.objects.filter(
                employee=employee,
                date__range=[start_date, end_date]
            ).filter(
                Q(is_active=True) | Q(is_check_out=True)
            ).order_by('date', 'check_in')
            
            # Group attendance records by date
            attendance_by_date = {}
            for record in attendance_records:
                if record.date not in attendance_by_date:
                    attendance_by_date[record.date] = []
                attendance_by_date[record.date].append(record)
            
            # Get holidays in the date range
            holidays = EmployeesOfficialHolidays.objects.filter(
                organization=organization_id,
                date__range=[start_date, end_date],
                is_active=True
            )
            # Create a dictionary for holiday titles
            holiday_dict = {holiday.date: holiday.title for holiday in holidays}
            
            # Prepare response data
            report_data = []
            
            for date in date_range:
                # Initialize day data with arrays for multiple entries
                day_data = {
                    'date': date.strftime('%Y-%m-%d'),
                    'day_name': date.strftime('%A'),
                    'employee_id': employee.id,
                    'employee_name': employee.name,
                    'emp_code': employee.emp_code,
                    'attendance_status': 'A',  # Default: Absent
                    'attendance_type': 'Absent',
                    'attendance_details': [],  # List to hold multiple attendance entries
                    'check_in': None,
                    'check_out': None,
                    'duration': '0 hours',
                    'total_duration_seconds': 0,
                    'comments': '',
                    'is_weekend': date.weekday() in [5, 6],  # 5=Saturday, 6=Sunday
                    'is_holiday': date in holiday_dict,
                    'holiday_title': holiday_dict.get(date, ''),
                    'has_multiple_entries': False,
                    'wfh_reasons': []
                }
                
                # Check if it's a weekend
                if date.weekday() in [5, 6]:
                    day_data['attendance_status'] = 'W'
                    day_data['attendance_type'] = 'Weekend'
                    day_data['comments'] = 'Weekend'
                
                # Check if it's a holiday (but don't override attendance data)
                elif date in holiday_dict:
                    day_data['is_holiday'] = True
                    day_data['holiday_title'] = holiday_dict[date]
                
                # Check attendance label (for manual overrides)
                if date in label_dict:
                    label = label_dict[date]
                    day_data['attendance_status'] = label.attendance_status
                    day_data['comments'] = label.comments or ''
                    
                    # Map status to type
                    status_mapping = {
                        'P': 'Present',
                        'WFH': 'Work From Home',
                        'L': 'Leave',
                        'A': 'Absent',
                        'W': 'Weekend',
                        'H': 'Holiday'
                    }
                    day_data['attendance_type'] = status_mapping.get(
                        label.attendance_status, 
                        label.attendance_status
                    )
                
                # Process attendance records for the day
                if date in attendance_by_date:
                    records = attendance_by_date[date]
                    
                    # Set flag if multiple entries
                    if len(records) > 1:
                        day_data['has_multiple_entries'] = True
                    
                    total_seconds = 0
                    attendance_types = set()
                    wfh_reasons = []
                    
                    # Process each attendance record
                    for record in records:
                        entry_data = {
                            'id': record.id,
                            'check_in': record.check_in.strftime('%H:%M:%S') if record.check_in else None,
                            'check_out': record.check_out.strftime('%H:%M:%S') if record.check_out else None,
                            'attendance_type': record.attendance_type or 'Present',
                            'is_custom_time_set': record.is_custom_time_set,
                            'wfh_reason': record.wfh_reason,
                            'duration': '0 hours',
                            'duration_seconds': 0
                        }
                        
                        # Store WFH reason if exists
                        if record.wfh_reason:
                            wfh_reasons.append(record.wfh_reason)
                        
                        # Calculate duration for this entry
                        if record.check_in and record.check_out:
                            try:
                                check_in_dt = datetime.datetime.combine(date, record.check_in)
                                check_out_dt = datetime.datetime.combine(date, record.check_out)
                                
                                # Handle overnight shifts (check_out < check_in)
                                if check_out_dt < check_in_dt:
                                    check_out_dt += datetime.timedelta(days=1)
                                
                                duration = check_out_dt - check_in_dt
                                entry_duration_seconds = duration.seconds
                                total_seconds += entry_duration_seconds
                                entry_data['duration_seconds'] = entry_duration_seconds
                                
                                hours = entry_duration_seconds // 3600
                                minutes = (entry_duration_seconds % 3600) // 60
                                seconds = entry_duration_seconds % 60
                                
                                entry_data['duration'] = f"{hours} hours, {minutes} minutes, {seconds} seconds"
                            except Exception:
                                # If duration calculation fails, continue without it
                                pass
                        
                        # Track attendance types
                        if record.attendance_type:
                            attendance_types.add(record.attendance_type)
                        
                        day_data['attendance_details'].append(entry_data)
                    
                    # Determine overall attendance type for the day
                    if attendance_types:
                        # Handle hybrid cases
                        has_present_or_office = any(t in ['Present', 'office'] for t in attendance_types)
                        has_wfh = any(t in ['Work From Home', 'WFH'] for t in attendance_types)
                        
                        if has_present_or_office and has_wfh:
                            day_data['attendance_type'] = 'Hybrid'
                            original_status = 'P'
                        elif len(attendance_types) == 1:
                            attendance_type = next(iter(attendance_types))
                            day_data['attendance_type'] = attendance_type
                            
                            # Set status based on type
                            if attendance_type in ['Work From Home', 'WFH']:
                                original_status = 'WFH'
                            elif attendance_type == 'Leave':
                                original_status = 'L'
                            elif attendance_type == 'Absent':
                                original_status = 'A'
                            else:
                                original_status = 'P'
                        else:
                            # Combine multiple types
                            day_data['attendance_type'] = ', '.join(sorted(attendance_types))
                            original_status = 'P'
                    
                    # Set first check-in and last check-out for backward compatibility
                    if records:
                        # Get first check-in
                        valid_checkin_records = [r for r in records if r.check_in]
                        if valid_checkin_records:
                            first_record = valid_checkin_records[0]
                            day_data['check_in'] = first_record.check_in.strftime('%H:%M:%S') if first_record.check_in else None
                            day_data['is_custom_time_set'] = first_record.is_custom_time_set
                        
                        # Get last check-out
                        valid_checkout_records = [r for r in records if r.check_out]
                        if valid_checkout_records:
                            last_record = valid_checkout_records[-1]
                            day_data['check_out'] = last_record.check_out.strftime('%H:%M:%S') if last_record.check_out else None
                        
                        day_data['wfh_reasons'] = wfh_reasons
                    
                    # Calculate total duration for the day
                    if total_seconds > 0:
                        day_data['total_duration_seconds'] = total_seconds
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        day_data['duration'] = f"{hours} hours, {minutes} minutes, {seconds} seconds"
                    
                    if records and date not in label_dict:
                        # If it's a holiday but employee worked, show both
                        if date in holiday_dict:
                            day_data['attendance_status'] = 'P'  # Mark as present
                            day_data['attendance_type'] = f"Holiday - {day_data['attendance_type']}"
                            day_data['comments'] = f"{holiday_dict[date]} - Worked"
                        else:
                            # Use the original status determined from records
                            if 'original_status' in locals():
                                day_data['attendance_status'] = original_status
                            elif day_data['attendance_type'] in ['Work From Home', 'WFH']:
                                day_data['attendance_status'] = 'WFH'
                            else:
                                day_data['attendance_status'] = 'P'  # Fallback to Present
                
                # If no attendance records but it's a holiday, set holiday status
                # Only if no label exists (labels take precedence)
                elif date in holiday_dict and date not in label_dict and date not in attendance_by_date:
                    day_data['attendance_status'] = 'H'
                    day_data['attendance_type'] = 'Holiday'
                    day_data['comments'] = holiday_dict[date]
                
                report_data.append(day_data)
            
            # Calculate summary statistics
            working_days = [d for d in report_data if d['attendance_details'] and not d['is_weekend']]
            present_days = [d for d in report_data if d['attendance_status'] == 'P' and not d['is_weekend']]
            wfh_days = [d for d in report_data if (d['attendance_status'] == 'WFH' or 'Work From Home' in d['attendance_type']) and not d['is_weekend']]
            hybrid_days = [d for d in report_data if d['attendance_type'] == 'Hybrid' and not d['is_weekend']]
            
            total_seconds_all = sum(d['total_duration_seconds'] for d in report_data)
            total_hours = total_seconds_all // 3600
            total_minutes = (total_seconds_all % 3600) // 60
            
            summary = {
                'total_days': len(date_range),
                'total_working_days': len(working_days),
                'total_present': len(present_days),
                'total_wfh': len(wfh_days),
                'total_hybrid': len(hybrid_days),
                'total_office_only': len([d for d in working_days if d['attendance_type'] in ['Present', 'office'] and not d['is_holiday']]),
                'total_leaves': len([d for d in report_data if d['attendance_status'] == 'L']),
                'total_absents': len([d for d in report_data if d['attendance_status'] == 'A' and not d['is_weekend'] and not d['is_holiday']]),
                'total_holidays': len([d for d in report_data if d['is_holiday']]),
                'total_holiday_work': len([d for d in report_data if d['is_holiday'] and d['attendance_details']]),
                'total_weekends': len([d for d in report_data if d['is_weekend']]),
                'total_hours_worked': total_seconds_all / 3600,
                'total_hours_worked_formatted': f"{total_hours} hours, {total_minutes} minutes",
            }
            
            # Get employee details
            department_title = str(employee.department) if employee.department else None
            position_title = str(employee.position) if employee.position else None
            
            return Response({
                'status': 200,
                'message': 'Success',
                'employee_info': {
                    'id': employee.id,
                    'name': employee.name,
                    'emp_code': employee.emp_code,
                    'department': department_title,
                    'position': position_title,
                    'has_department': bool(employee.department),
                    'has_position': bool(employee.position),
                    'work_mode': employee.work_mode
                },
                'date_range': {
                    'start_date': start_date_str,
                    'end_date': end_date_str,
                    'total_days': len(date_range)
                },
                'summary': summary,
                'data': report_data
            })
            
        except ValueError as e:
            return Response({
                'status': 400,
                'message': 'Invalid date format. Use YYYY-MM-DD format',
                'error': str(e)
            }, status=400)
            
        except Exception as e:
            # Log the error for server-side debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in generate_report: {str(e)}", exc_info=True)
            
            return Response({
                'status': 500,
                'message': 'Internal server error',
                'error': str(e)
            }, status=500)