import intake
import requests

class GeoSLineChart(intake.source.base.DataSource):
    name = 'geoslinechart'
    version = '0.0.1'
    container = 'python'
    partition_access = True

    visualization_label = 'GeoS Line Chart'
    visualization_type = 'plotly'
    visualization_group = 'GeoGloWS'
    visualization_args = {
        'region': {
            'type': 'string',
            'description': 'Region to fetch data for',
            'default': 'katherine_nt',
        },
        'storage_type': {
            'type': 'string',
            'description': 'Type of storage data to fetch',
            'default': 'grace',
        }
    }
    visualization_tags = ['plot', 'geoglows']
    visualization_description = 'GeoGloWS storage values as a Plotly line chart'

    def __init__(self, region='katherine_nt', storage_type='grace', metadata=None):
        super().__init__(metadata=metadata)
        self.region = region
        self.storage_type = storage_type
        self._data = None

    def _get_schema(self):
        return intake.source.base.Schema(datashape=None, dtype=None, shape=None, npartitions=1, extra_metadata={})

    def _get_partition(self, _):
        if self._data is None:
            self._load_data()
        return self._data

    def read(self):
        return self._get_partition(None)

    def _load_data(self):
        response = requests.post('https://ggst-api.geoglows.org/api/getRegionSummary',
                                 data={
                                     'region': self.region,
                                     'storage_type': self.storage_type,
                                     },
                                 headers={
                                     'accept': 'application/json',
                                     'Content-Type': 'application/x-www-form-urlencoded',
                                    },
                                 )
        response.raise_for_status()
        data = response.json()
        timestamps = [item[0] for item in data['values']]
        values = [item[1] for item in data['values']]
        self._data = {
            'data': [
                {
                    'x': timestamps,
                    'y': values,
                    'mode': 'lines',
                    'type': 'scatter',
                    'name': f'{self.storage_type.upper()} Values',
                }
            ],
            'layout': {
                'title': f'{self.storage_type.upper()} Values for {self.region.upper()}',
                'xaxis': {'title': 'Timestamp', 'type': 'date'},
                'yaxis': {'title': f'{self.storage_type.upper()} Value'},
            },
        }

# intake.register_driver(GeoSLineChart.name, GeoSLineChart)

