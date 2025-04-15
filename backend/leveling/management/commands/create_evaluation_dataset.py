from django.core.management.base import BaseCommand
from langsmith import Client

from leveling.modules.evaluation.dataset import create_evaluation_dataset

class Command(BaseCommand):
    help = 'Create a dataset for evaluating the construction agent'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dataset-name',
            type=str,
            default='sample-dataset',
            help='Name of the dataset to create'
        )

    def handle(self, *args, **options):
        # Initialize LangSmith client
        client = Client()
        
        # Create the dataset
        dataset = create_evaluation_dataset(
            client=client,
            dataset_name=options['dataset_name']
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created dataset: {dataset.name}')
        ) 