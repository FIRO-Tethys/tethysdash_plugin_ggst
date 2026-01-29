import intake
import requests
from intake.source import base
from .utils.fetchrange import fetch_range


class FetchMinValueDataSource(base.DataSource):
    name = 'fetch_min_value'
    version = '0.0.1'
    container = 'python'

    visualization_label = 'Minimum'
    visualization_type = 'variable_input' 
    visualization_group = 'Custom Intake Plugins'

    visualization_args = {
        'region_name': {
            'type': 'string',
            'description': 'Name of the region'
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
        Returns a dict with a 'text' key for the JS 'number' viz
        """

        # When the region_name is missing, return an object with a text key
        if not self.region_name:
            return {
                "variable_name": "Min",
                "initial_value": None,
                "variable_options_source": []
            }

        min_value = fetch_range(self.region_name, self.storage_type)
        print(min_value)
        return {
            "variable_name": "Minimum",
            "initial_value": min_value["min"],
            "variable_options_source": "number",
            "metadata": {
                "step": 0.1
            },
        }
