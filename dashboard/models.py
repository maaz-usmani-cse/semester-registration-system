from django.db import models
from app.models import UserProfile


class Examform(models.Model):

    SEMESTER_CHOISES=[

        ('ist', 'ist semester'),
        ('2nd', '2nd semester'),
        ('3rd', '3rd semester'),
        ('4th', '4th semester'),
        ('5th', '5th Semester'),
        ('6th', '6th Semester'),
        ('7th', '7th Semester'),
        ('8th', '8th Semester'),

    ]




    YEAR_CHOISES=[


        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),


    ]




    user_profile=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    enrollment_no=models.CharField(max_length=50)
    semester=models.CharField(max_length=10,choices=SEMESTER_CHOISES)
    year=models.CharField(max_length=20,choices=YEAR_CHOISES)
    subject = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=20, default='Regular')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.semester} - {self.enrollment_no}'
