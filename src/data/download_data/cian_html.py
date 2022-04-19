"""Tools for extract data from CIAN html pages."""
import re
from typing import Dict, List, Union, Any

import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

from cian_config import headers, target_params, base_url


def get_apartment_info_from_string(param: str, target_string: str) -> str:
    """Get param from target string.

    @param param: param for search
    @param target_string: target string
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
        base_url: str = base_url,
        headers: Headers = headers,
        target_params: List[str] = target_params,
) -> Dict[Union[str, Any], Union[Union[str, List[str]], Any]]:
    """Get data of apartment from html-page with ad.

    @param target_params: params for search in html-page
    @param headers: headers
    @param base_url: CIAN base url
    @param ad_id: ad id
    @return: apartment info
    """
    # Raw data
    url = f"{base_url}{ad_id}/"
    html = requests.get(url, headers=headers.generate()).text
    soup = BeautifulSoup(html, features="html.parser")
    raw_data = [str(item) for item in soup.findAll("li")]
    raw_data = [item for item in raw_data if "AdditionalFeatureItem" in item]
    # Params for search
    dct = dict(zip(target_params, [""] * len(target_params)))
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
