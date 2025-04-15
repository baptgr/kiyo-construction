from django.core.management.base import BaseCommand
from langsmith import Client

from leveling.modules.evaluation.dataset import create_evaluation_dataset

class Command(BaseCommand):
    help = 'Create a dataset for evaluating the construction agent'

    def add_arguments(self, parser):
        parser.add_argument(
            '--template-name',
            type=str,
            default='template-1',
            help='Name of the template to create'
        )

    def handle(self, *args, **options):
        # Initialize LangSmith client
        client = Client()
        
        # Create the dataset
        dataset = create_evaluation_dataset(
            client=client,
            template_name=options['template_name']
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created dataset: {dataset.name}')
        ) 