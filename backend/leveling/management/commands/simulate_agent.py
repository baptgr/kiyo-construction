from django.core.management.base import BaseCommand
from leveling.modules.kiyo_agents.construction_agent import ConstructionAgent
import os

class Command(BaseCommand):
    help = 'Simulate the construction agent with a simple message'

    def add_arguments(self, parser):
        parser.add_argument(
            '--message',
            type=str,
            default='Hello, can you help me with bid leveling?',
            help='Message to send to the agent'
        )
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

    def handle(self, *args, **options):
 
        # Get Google credentials
        google_access_token = options['google_token'] or os.getenv('DEV_GOOGLE_ACCESS_TOKEN')
        spreadsheet_id = options['spreadsheet_id'] or os.getenv('DEV_SPREADSHEET_ID')

        if not google_access_token or not spreadsheet_id:
            self.stderr.write(self.style.WARNING('Warning: No Google credentials provided. The agent will not be able to access Google Sheets.'))

        # Initialize the agent
        agent = ConstructionAgent(
            google_access_token=google_access_token,
            spreadsheet_id=spreadsheet_id
        )

        # Get the message from arguments
        message = options['message']
        self.stdout.write(self.style.SUCCESS(f'Sending message: {message}'))

        # Process the message and stream the response
        try:
            accumulated_text = ""
            for chunk in agent.process_message_stream(message, conversation_id="simulation"):
                if chunk.get('type') == 'message':
                    # Only write the new part of the text
                    new_text = chunk['text']
                    if new_text.startswith(accumulated_text):
                        new_part = new_text[len(accumulated_text):]
                        if new_part:
                            self.stdout.write(new_part, ending='')
                            self.stdout.flush()
                    else:
                        # If the text doesn't start with accumulated text, write the whole thing
                        self.stdout.write(new_text, ending='')
                        self.stdout.flush()
                    accumulated_text = new_text
                elif chunk.get('type') == 'tool_call':
                    self.stdout.write(self.style.WARNING(f'\nTool call: {chunk["tool_calls"]}'))
            self.stdout.write('\n')
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error occurred: {str(e)}')) 