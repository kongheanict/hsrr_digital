from import_export import resources
from .models import Student, Enrollment

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ('student_id',)
        fields = ('student_id', 'family_name', 'given_name', 'major', 'phone_number', 'student_type')