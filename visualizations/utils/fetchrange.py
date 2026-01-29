import requests

_RANGE_CACHE = {}


def fetch_range(region_name, storage_type=None):
    key = (region_name, storage_type)

    if key in _RANGE_CACHE:
        return _RANGE_CACHE[key]

    base_url = "http://ggst-api.geoglows.org"
    url = f"{base_url}/api/fetch_range?storage_type={storage_type}"

    if region_name != "global":
        url = f"{url}&region_name={region_name}"

    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    result = {
        "min": float(data.get("min")),
        "max": float(data.get("max")),
    }

    _RANGE_CACHE[key] = result
    return result
