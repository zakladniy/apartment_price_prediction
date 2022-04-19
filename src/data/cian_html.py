"""Tools for extract data from CIAN html pages."""
import re
from typing import Dict, Union, Any, List

import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

from cian_config import base_url, headers, target_params


def get_apartment_info_from_string(param: str, target_string: str) -> str:
    """Get apartment param from target string.

    @param target_string: target string
    @param param: param for search
    @return: param value
    """
    if param in target_string:
        target_string_list = target_string.split("span")
        if len(target_string_list) >= 2:
            res = re.search(r">(.*)<", target_string_list[-2]).group()
            if res:
                res = re.sub(r"[><]", "", res)
                return res
            else:
                return ""
        else:
            return ""
    else:
        return ""


def get_data_from_html(
        ad_id: int,
        headers: Headers = headers,
        url: str = base_url,
        params: List[str] = target_params
) -> Dict[Any, Union[Union[str, List[str]], Any]]:
    """Get apartment data from HTML.

    @param ad_id: ad id
    @param headers: headers
    @param url: base url for html parse
    @param params: params for extract
    @return: data from html
    """
    # Raw data
    html = requests.get(f"{url}{ad_id}/", headers=headers.generate()).text
    soup = BeautifulSoup(html, features="html.parser")
    raw_data = [str(item) for item in soup.findAll("li")]
    raw_data = [item for item in raw_data if "AdditionalFeatureItem" in item]
    # Get params for search
    dct = dict(zip(params, [""] * len(params)))
    for key, _ in dct.items():
        res = []
        for string in raw_data:
            if key in string:
                res.append(get_apartment_info_from_string(key, string))
            else:
                res.append("")
            dct[key] = [item for item in res if item] or ""
            if isinstance(dct[key], list):
                dct[key] = dct[key][0]
    return dct
