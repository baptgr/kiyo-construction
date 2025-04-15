from django.core.management.base import BaseCommand
from kiyo_agents.construction_agent import ConstructionAgent
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

    def handle(self, *args, **options):
        # Get OpenAI API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.stderr.write(self.style.ERROR('OPENAI_API_KEY environment variable is not set'))
            return

        google_access_token = "123"

        # Initialize the agent
        agent = ConstructionAgent(api_key=api_key, google_access_token=google_access_token)

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