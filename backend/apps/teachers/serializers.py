from rest_framework import serializers
from .models import LeaveRequest, Teacher

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['id', 'start_date', 'end_date', 'reason', 'status', 'teacher']
        read_only_fields = ['id', 'status', 'teacher']

        
class TeacherLeaveSerializer(serializers.ModelSerializer):
    leave_requests = LeaveRequestSerializer(many=True, read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['id', 'user', 'leave_requests']