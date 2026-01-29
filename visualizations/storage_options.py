import intake
import requests
from intake.source import base

class StorageOptionsDataSource(base.DataSource):
    name = 'storage_options'
    version = '0.0.1'
    container = 'python'
    
    # Cache to prevent infinite calls
    _cached_data = None
    _cache_initialized = False

    visualization_label = 'Storage Type'
    visualization_type = 'variable_input'
    visualization_group = 'Custom Intake Plugins'
    visualization_args = {}

    def __init__(self, metadata=None, **kwargs):
        super().__init__(metadata=metadata)

    def read(self):
        # Return cached data if available to prevent infinite calls
        if self._cache_initialized and self._cached_data is not None:
            return self._cached_data
            
        url = 'http://ggst-api.geoglows.org/api/getStorageOptions'
        response = requests.get(url)

        if response.status_code != 200:
            options = []
        else:
            options = response.json().get("storage_options", [])

        result = {
            "variable_name": "Storage Type",
            "initial_value": options[0]["value"] if options else None,
            "variable_options_source": options
        }
        
        # Cache the result
        self._cached_data = result
        self._cache_initialized = True
        
        return result

# intake.register_driver(StorageOptionsDataSource.name, StorageOptionsDataSource)