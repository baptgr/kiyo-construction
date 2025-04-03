from rest_framework import serializers
from .models import Project, Document, Spreadsheet

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'name', 'file', 'uploaded_at', 'project']

class SpreadsheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spreadsheet
        fields = ['id', 'name', 'google_sheet_id', 'created_at', 'updated_at', 'project']

class ProjectSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    spreadsheets = SpreadsheetSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'documents', 'spreadsheets'] 