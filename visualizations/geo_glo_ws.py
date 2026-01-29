import intake
import requests
import plotly.graph_objects as go

class GeoGloWSDataSource(intake.source.base.DataSource):
    name = 'geo_glo_ws'
    version = '0.0.1'
    container = 'python'
    partition_access = True

    visualization_label = 'GeoGloWS Storage Chart'
    visualization_type = 'geo_glo_ws'
    visualization_group = 'GeoGloWS'
    visualization_args = {
        'latitude': {'type': 'float', 'description': 'Latitude'},
        'longitude': {'type': 'float', 'description': 'Longitude'},
        'storage_type': {'type': 'string', 'description': 'Storage Type'}
    }
    visualization_tags = ['chart', 'plot', 'line', 'geoglows']
    visualization_description = 'Display storage values from GeoGloWS API'

    def __init__(self, metadata=None, latitude=None, longitude=None, lat=None, lon=None, region=None, storage_type=None):
        super().__init__(metadata=metadata)
        self.region = region or 'katherine_nt'
        self.storage_type = storage_type or 'grace'
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self._data = None

    def update_coordinates(self, latitude, longitude):
        """Update the coordinates and reset the data"""
        self.latitude = latitude
        self.longitude = longitude
        self._data = None
        return self.read()

    def _get_schema(self):
        return intake.source.base.Schema(
            datashape=None,
            dtype=None,
            shape=None,
            npartitions=1,
            extra_metadata={},
        )

    def _get_partition(self, _):
        if self._data is None:
            self._load_data()
        return self._data

    def read(self):
        """Read the data and return formatted for plotting"""

        # 🔒 Guard against missing or unresolved args
        if (
            self.latitude is None
            or self.longitude is None
            or not self.storage_type
            or (isinstance(self.storage_type, str) and self.storage_type.startswith("${"))
        ):
            raise ValueError("Latitude, longitude, and resolved storage_type must be provided")

        print(
            f"Reading data for lat: {self.latitude}, "
            f"lon: {self.longitude}, "
            f"storage type: {self.storage_type}"
        )

        if self._data is None:
            self._load_data()

        return {
            "data": [{
                "x": self._data['timestamp'],
                "y": self._data['value'],
                "type": "scatter",
                "mode": "lines",
                "name": f"{self.storage_type.upper()} Values"
            }],
            "layout": {
                "title": (
                    f"{self.storage_type.upper()} Values for "
                    f"lat: {self.latitude:.4f}, lon: {self.longitude:.4f}"
                ),
                "xaxis": {"title": "Timestamp", "type": "date"},
                "yaxis": {"title": f"{self.storage_type.upper()} Value"}
            }
        }

    def _load_data(self):
        if self.latitude is None or self.longitude is None:
            raise ValueError("Latitude and longitude must be provided")

        print(
            f"Fetching data for lat: {self.latitude}, "
            f"lon: {self.longitude}, "
            f"storage type: {self.storage_type}"
        )

        url = (
            f'http://ggst-api.geoglows.org/api/getPointValues'
            f'?latitude={self.latitude}'
            f'&longitude={self.longitude}'
            f'&storage_type={self.storage_type}'
        )

        try:
            response = requests.get(url, timeout=30)
        except requests.RequestException as e:
            raise Exception(f"GeoGloWS request failed: {e}") from e

        if response.status_code != 200:
            # Try to extract a user-friendly error message from the JSON response
            error_message = f"GeoGloWS API error (status {response.status_code})"
            try:
                error_data = response.json()
                if isinstance(error_data, dict):
                    # Extract common error fields
                    detail = error_data.get("detail") or error_data.get("error") or error_data.get("message")
                    if detail:
                        print(f"GeoGloWS: {detail}")
                        error_message = "GeoGloWS: Failed to Load the Data"
            except (ValueError, KeyError):
                # If JSON parsing fails, use a snippet of the raw text
                body_snippet = (response.text or "")[:200]
                if body_snippet:
                    error_message = f"GeoGloWS API error: {body_snippet}"
            
            raise Exception(error_message)

        data = response.json()
        if "values" not in data:
            raise Exception(
                f"GeoGloWS response missing 'values' key. url={url}, keys={list(data.keys())}"
            )

        timestamps = [item[0] for item in data["values"]]
        values = [item[1] for item in data["values"]]
        self._data = {"timestamp": timestamps, "value": values}

# Register with Intake
# intake.register_driver(GeoGloWSDataSource.name, GeoGloWSDataSource)

# http://ggst-api.geoglows.org