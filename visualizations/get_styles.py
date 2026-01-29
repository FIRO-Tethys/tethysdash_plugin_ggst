import intake
import requests

class FetchStyles(intake.source.base.DataSource):
    name = 'fetch_styles'
    version = '0.0.1'
    container = 'python'

    visualization_label = 'Styles'
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
        self.data = None

    def update_config(self, region_name, storage_type):
        self.region_name = region_name
        self.storage_type = storage_type
        self.data = None
        return self.read()

    def read(self):
        """
        Returns configuration for a UI variable input
        """
        if self.region_name != "global":
            url = f"http://13.201.155.87:4000/thredds/wms/regions/data/{self.region_name}/{self.region_name}_{self.storage_type}.nc?request=GetMetadata&item=layerDetails&layerName=lwe_thickness"
        else:
            url = f"http://13.201.155.87:4000/thredds/wms/regions/data/GRC_{self.storage_type}.nc?request=GetMetadata&item=layerDetails&layerName=lwe_thickness"

        response = requests.get(url)
        if response.status_code != 200:
            styles = []
        else:
            styles = response.json().get('palettes', [])
        return {
            "variable_name": "Styles",
            "initial_value": styles[0],
            "variable_options_source": styles
        }