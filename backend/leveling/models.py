from django.db import models
from django.utils import timezone
import uuid

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

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.CharField(max_length=255, null=True, blank=True)  # Optional for now
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation {self.id} - User: {self.user_id or 'Anonymous'}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=[
        ('user', 'User'),
        ('assistant', 'Assistant')
    ])
    content = models.TextField()
    item_type = models.CharField(max_length=50, null=True, blank=True)  # For storing RunItem type
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
