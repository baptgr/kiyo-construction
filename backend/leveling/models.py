from django.db import models
from django.utils import timezone

class Project(models.Model):
    """
    Model representing a construction project
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Document(models.Model):
    """
    Model representing a bid document (PDF)
    """
    project = models.ForeignKey(Project, related_name='documents', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

class Spreadsheet(models.Model):
    """
    Model representing a leveled spreadsheet
    """
    project = models.ForeignKey(Project, related_name='spreadsheets', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    google_sheet_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
