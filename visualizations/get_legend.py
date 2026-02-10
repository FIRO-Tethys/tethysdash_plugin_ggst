import intake
import requests

class GetLegendGraphic(intake.source.base.DataSource):
    name='get_legend_graphic'
    version='0.0.1'
    container='python'
    visualization_tags = []
    visualization_label = 'Legend Graphic'
    visualization_type = 'image'
    visualization_description = 'Displays the legend from the thredds url'
    visualization_group = 'GGST'
    visualization_args = {
        'min': {
            'type': 'float'
        },
        'max': {
            'type': 'float'
        },
        'styles': {
            'type': 'string'
        },
        'region_name': {
            'type': 'string', 'description': 'Name of the region'
        },
        'storage_type': {
            'type': 'string', 'description': 'Name of the storage type'
        },

    }
    visualization_type = "image"

    def __init__(self, min=None, max=None, styles=None, region_name=None, storage_type=None, metadata=None, **kwargs):
        super().__init__(metadata=metadata)
        self.min = min
        self.max = max
        self.styles = styles
        self.region_name = region_name
        self.storage_type = storage_type

    def read(self):
        if self.region_name != "global":
            url = f'http://13.201.155.87:4000/thredds/wms/regions/data/{self.region_name}/{self.region_name}_{self.storage_type}.nc?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetLegendGraphic&LAYER=lwe_thickness&colorscalerange={self.min},{self.max}&STYLES=raster/{self.styles}&transparent=FALSE&WIDTH=40&HEIGHT=250'
        else: 
            url = f'http://13.201.155.87:4000/thredds/wms/regions/data/GRC_{self.storage_type}.nc?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetLegendGraphic&LAYER=lwe_thickness&colorscalerange={self.min},{self.max}&STYLES=raster/{self.styles}&transparent=FALSE&WIDTH=40&HEIGHT=250'
        return url

# http://13.201.155.87:4000/thredds/wms/regions/data/GRC_grace.nc?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetLegendGraphic&LAYER=lwe_thickness&colorscalerange=50,-50&STYLES=raster/default&transparent=FALSE&WIDTH=40&HEIGHT=250
# https://apps.geoglows.org/thredds/wms/geoglows_data/ggst/GRC_grace.nc?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetLegendGraphic&LAYER=lwe_thickness&colorscalerange=-50,50&STYLES=raster/default&transparent=FALSE&WIDTH=50&HEIGHT=300