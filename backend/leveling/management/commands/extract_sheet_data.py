"""Extract data from a Google Sheet."""

import os
import logging
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from leveling.modules.evaluation.data_extraction.data_extraction import EXTRACTION_FUNCTIONS
import json

load_dotenv()

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Extract data from a Google Sheet using the specified template'

    def add_arguments(self, parser):
        parser.add_argument(
            '--spreadsheet-id',
            type=str,
            required=True,
            help='The ID of the Google Spreadsheet to extract data from'
        )
        parser.add_argument(
            '--range',
            type=str,
            help='The range to read in A1 notation (e.g., Sheet1!A1:D10)',
            default='Bid Comparison!A1:Z100'
        )
        parser.add_argument(
            '--access-token',
            type=str,
            help='Google OAuth access token with Sheets scope',
            default=os.getenv('DEV_GOOGLE_ACCESS_TOKEN')
        )

    def handle(self, *args, **options):
        spreadsheet_id = options['spreadsheet_id']
        range_name = options['range']
        access_token = options['access_token']

        logger.info(f"Attempting to read spreadsheet ID: {spreadsheet_id}")
        logger.info(f"Range: {range_name}")
        logger.info(f"Access token present: {'Yes' if access_token else 'No'}")

        if not access_token:
            self.stdout.write(
                self.style.ERROR('No access token provided. Please set DEV_GOOGLE_ACCESS_TOKEN in your .env file or provide it via --access-token')
            )
            return

        try:
            # Use the template-1 extraction function
            structured_data = EXTRACTION_FUNCTIONS["template-1"](
                spreadsheet_id=spreadsheet_id,
                access_token=access_token,
                range_name=range_name
            )
            
            # Output the results
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully extracted and transformed data:\n{json.dumps(structured_data, indent=2)}'
                )
            )
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error extracting data: {error_message}", exc_info=True)
            
            if "400" in error_message:
                self.stdout.write(
                    self.style.ERROR(
                        'Bad Request (400) error. This could be due to:\n'
                        '1. Invalid spreadsheet ID\n'
                        '2. Invalid range format\n'
                        '3. Insufficient permissions\n'
                        '4. Invalid access token\n\n'
                        f'Full error: {error_message}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Error extracting data: {error_message}')
                )