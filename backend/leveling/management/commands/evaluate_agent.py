from django.core.management.base import BaseCommand
from kiyo_agents.construction_agent import ConstructionAgent
from langsmith import Client
import os
import pandas as pd

from leveling.modules.evaluation.evaluation import run_evaluation_pipeline

class Command(BaseCommand):
    help = 'Evaluate the construction agent using LangSmith'

    def add_arguments(self, parser):
        parser.add_argument(
            '--spreadsheet-id',
            type=str,
            help='Google Spreadsheet ID to use'
        )
        parser.add_argument(
            '--google-token',
            type=str,
            help='Google access token'
        )
        parser.add_argument(
            '--dataset-name',
            type=str,
            default='sample-dataset',
            help='Name of the dataset to create/use'
        )

    def handle(self, *args, **options):
        # Get OpenAI API key from arguments or environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.stderr.write(self.style.ERROR('OpenAI API key is required. Set OPENAI_API_KEY environment variable'))
            return

        # Get Google credentials
        google_access_token = options['google_token'] or os.getenv('DEV_GOOGLE_ACCESS_TOKEN')
        spreadsheet_id = options['spreadsheet_id'] or os.getenv('DEV_SPREADSHEET_ID')

        if not google_access_token or not spreadsheet_id:
            self.stderr.write(self.style.WARNING('Warning: No Google credentials provided. The agent will not be able to access Google Sheets.'))

        # Initialize the agent
        agent = ConstructionAgent(
            api_key=api_key,
            google_access_token=google_access_token,
            spreadsheet_id=spreadsheet_id
        )

        # Initialize LangSmith client
        client = Client()

        # Run the evaluation pipeline
        experiment_results = run_evaluation_pipeline(
            client=client,
            agent=agent,
            dataset_name=options['dataset_name']
        )
        
        # Process and display results
        self.stdout.write(self.style.SUCCESS("Successfully ran the evaluation pipeline"))
