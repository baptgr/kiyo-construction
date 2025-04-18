from django.core.management.base import BaseCommand
from langsmith import Client
import os
import pandas as pd
from typing import Dict, Any, List

from leveling.modules.evaluation.evaluation import run_evaluation_pipeline
from leveling.modules.config.model_configs import get_config, get_config_names

class Command(BaseCommand):
    help = 'Evaluate the construction agent using LangSmith'

    def add_arguments(self, parser):
        parser.add_argument(
            '--google-token',
            type=str,
            help='Google access token'
        )
        parser.add_argument(
            '--dataset-name',
            type=str,
            default='template-1',
            help='Name of the dataset to create/use'
        )
        parser.add_argument(
            '--config',
            type=str,
            help='Name of the specific configuration to use',
            default='default'
        )
        parser.add_argument(
            '--configs',
            type=str,
            nargs='+',
            help='List of configuration names to run experiments with',
            default=[]
        )
        parser.add_argument(
            '--all-configs',
            action='store_true',
            help='Run experiments with all available configurations',
            default=False
        )
        parser.add_argument(
            '--repetitions',
            type=int,
            default=1,
            help='Number of repetitions per configuration'
        )

    def handle(self, *args, **options):
        # Get OpenAI API key from arguments or environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.stderr.write(self.style.ERROR('OpenAI API key is required. Set OPENAI_API_KEY environment variable'))
            return

        # Get Google credentials
        google_access_token = options['google_token'] or os.getenv('DEV_GOOGLE_ACCESS_TOKEN')

        # Initialize LangSmith client
        client = Client()
        
        configs_to_run = self._get_configs_to_run(options)
        
        # Run evaluations for each configuration
        results = {}
        for config_name in configs_to_run:
            self.stdout.write(f"Running evaluation for configuration: {config_name}")
            
            try:
                # Get the configuration
                config = get_config(config_name)
                
                # Run evaluation for this configuration
                experiment_results = run_evaluation_pipeline(
                    client=client,
                    dataset_name=options['dataset_name'],
                    google_access_token=google_access_token,
                    num_repetitions=options['repetitions'],
                    config=config,
                    experiment_prefix=config_name
                )
                
                # Store results
                results[config_name] = experiment_results
                
                # Log completion
                self.stdout.write(self.style.SUCCESS(f"Completed evaluation for {config_name}"))
                
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error running evaluation for {config_name}: {str(e)}"))
            

    def _get_configs_to_run(self, options: Dict[str, Any]) -> List[str]:
        """Get the configurations to run based on the command options."""
        configs_to_run = []
        
        if options['all_configs']:
            # Run all configs
            configs_to_run = get_config_names()
            self.stdout.write(self.style.SUCCESS(f"Running experiments with all configurations: {', '.join(configs_to_run)}"))
        
        elif options['configs']:
            # Run specific list of configs
            configs_to_run = options['configs']
            self.stdout.write(self.style.SUCCESS(f"Running experiments with configurations: {', '.join(configs_to_run)}"))
        
        elif options['config']:
            # Run a single config
            configs_to_run = [options['config']]
            self.stdout.write(self.style.SUCCESS(f"Running experiment with configuration: {options['config']}"))
        
        else:
            # Default to single default config
            configs_to_run = ["default"]
            self.stdout.write(self.style.SUCCESS("Running experiment with default configuration"))
            
        return configs_to_run