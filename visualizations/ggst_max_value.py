import intake
import requests
from intake.source import base
from .utils.fetchrange import fetch_range


class FetchMaxValueDataSource(base.DataSource):
    name = 'fetch_max_value'
    version = '0.0.1'
    container = 'python'

    visualization_label = 'Maximum'
    visualization_type = 'variable_input'
    visualization_group = 'Custom Intake Plugins'

    visualization_args = {
        'region_name': {
            'type': 'string',
            'description': 'Name of the region',
            'required': False,
            'default': None
        },
        'storage_type': {
            'type': 'string',
            'description': 'Name of the storage type'
        },
    }

    def __init__(self, region_name=None, storage_type=None, metadata=None, **kwargs):
        super().__init__(metadata=metadata)
        self.region_name = region_name
        self.storage_type = storage_type

    def read(self):
        """
        Returns configuration for a UI variable input
        """
        if not self.region_name:
            return {
                "variable_name": "Max",
                "initial_value": None,
                "variable_options_source": []
            }

        max_value = fetch_range(self.region_name, self.storage_type)
        print(max_value)
        return {
            "variable_name": "Maximum",
            "initial_value": max_value["max"],
            "variable_options_source": "number",
            "metadata": {
                "step": 0.1
            },
        }

