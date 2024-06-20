from django.db import models
from django.urls import reverse

class Certificate(models.Model):
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    certificate_number = models.CharField(max_length=50)
    roll_no = models.CharField(max_length=50)
    certificate_type = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')])
    issue_date = models.DateField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('verify_certificate', args=[str(self.id)])

    def __str__(self):
        return self.certificate_number