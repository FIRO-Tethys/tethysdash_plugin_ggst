import io
import requests
import xml.etree.ElementTree as ET
import dateparser
from datetime import timedelta
from typing import List
from intake.source import base


def format_to_iso(dt):
    return dt.strftime("%Y-%m-%d")


def expand_interval(interval: str) -> List[str]:
    start, end, *_ = interval.split("/")
    start_dt = dateparser.parse(start)
    end_dt = dateparser.parse(end)

    dates = []
    cur = start_dt
    while cur <= end_dt:
        dates.append(format_to_iso(cur))
        cur = cur + timedelta(days=1)  # Use timedelta instead of replace
    return dates


def parse_dates_for_layer(xml_text: str, layer_name: str) -> List[str]:
    root = ET.fromstring(xml_text)

    # Detect namespace
    if root.tag.startswith("{"):
        ns_uri = root.tag.split("}")[0][1:]
        ns = {"wms": ns_uri}
        layer_path = ".//wms:Layer"
        name_tag = "wms:Name"
        title_tag = "wms:Title"
        dim_path = "wms:Dimension"
        ext_path = "wms:Extent"
    else:
        ns = {}
        layer_path = ".//Layer"
        name_tag = "Name"
        title_tag = "Title"
        dim_path = "Dimension"
        ext_path = "Extent"

    layer = None
    for lyr in root.findall(layer_path, ns):
        name_elem = lyr.find(name_tag, ns)
        title_elem = lyr.find(title_tag, ns)
        if (
            (name_elem is not None and name_elem.text == layer_name)
            or (title_elem is not None and title_elem.text == layer_name)
        ):
            layer = lyr
            break

    if layer is None:
        return []

    def extract_dates(text: str) -> List[str]:
        items = (d.strip() for d in text.split(","))
        out: List[str] = []
        for item in items:
            if not item:
                continue
            if "/" in item:
                out.extend(expand_interval(item))
            else:
                parsed = dateparser.parse(item)
                if parsed:
                    out.append(format_to_iso(parsed))
        return out

    for dim in layer.findall(dim_path, ns):
        if dim.get("name", "").lower() == "time" and dim.text:
            return extract_dates(dim.text.strip())

    for ext in layer.findall(ext_path, ns):
        if ext.get("name", "").lower() == "time" and ext.text:
            return extract_dates(ext.text.strip())

    return []


class FetchDatesDataSource(base.DataSource):
    name = "fetch_dates"
    version = "0.0.1"
    container = "python"

    visualization_label = "Select Date"
    visualization_type = "variable_input"
    visualization_group = "GGST"

    visualization_args = {
        "region_name": {
            "type": "string",
            "description": "Name of the region",
            "required": False,
        },
        "storage_type": {
            "type": "string",
            "description": "Storage type",
            "required": True,
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
        if not self.storage_type:
            return {
                "variable_name": "Date",
                "initial_value": None,
                "variable_options_source": [],
            }

        if self.region_name != "global":
            file_path = f"{self.region_name}/{self.region_name}_{self.storage_type}.nc"
        else:
            file_path = f"GRC_{self.storage_type}.nc"

        wms_url = (
            f"http://13.201.155.87:4000/thredds/wms/regions/data/{file_path}"
            "?service=WMS&version=1.3.0&request=GetCapabilities"
        )

        try:
            resp = requests.get(wms_url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException:
            return {
                "variable_name": "Date",
                "initial_value": None,
                "variable_options_source": [],
            }

        dates = parse_dates_for_layer(resp.text, "lwe_thickness")

        self.data = {
            "variable_name": "Date",
            "initial_value": dates[0] if dates else None,
            "variable_options_source": dates,
        }

        return self.data

# intake.register_driver(FetchDatesDataSource.name, FetchDatesDataSource)
