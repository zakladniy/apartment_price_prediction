"""Tools for extract data from CIAN by API."""
from datetime import datetime
from typing import Any, Optional, Dict, Union, List

import requests
from fake_headers import Headers
from nested_lookup import nested_lookup

from cian_config import headers, base_url
from cian_html import get_data_from_html


def nested_check(key: str, source_dict: dict) -> Optional[Any]:
    """Search data in nested dicts or in json

    @param key: target key
    @param source_dict: source dict
    @return: search result
    """
    if source_dict is None:
        return None
    else:
        res = nested_lookup(key, source_dict)
        if res:
            return res
        else:
            return None


def get_raw_data_from_api(
        target: str,
        page: int,
        headers: Headers = headers,
        url: str = base_url
) -> Union[Optional[Dict[Any, Any]], Any]:
    """Get raw data from CIAN API by target for search.

    @param target: target for search
    @param page: page number
    @param headers: headers
    @param url: CIAN API url
    @return: data from API
    """
    if target == "all":
        payload = {
            "jsonQuery": {
                "region": {"type": "terms", "value": [2]},
                "_type": "flatsale",
                "room": {"type": "terms", "value": [1, 2, 3, 4, 5, 6, 9, 7]},
                "engine_version": {"type": "term", "value": 2},
                "page": {"type": "term", "value": page},
            }
        }
    elif target == "sobstv":
        payload = {
            "jsonQuery": {
                "region": {"type": "terms", "value": [2]},
                "_type": "flatsale",
                "room": {
                    "type": "terms",
                    "value": [1, 2, 3, 4, 5, 6, 9, 7],
                },
                "engine_version": {"type": "term", "value": 2},
                "page": {"type": "term", "value": page},
                "is_by_homeowner": {"type": "term", "value": True},
            }
        }
    else:
        return None
    response = requests.post(
        url=url,
        json=payload,
        headers=headers.generate()
    )
    if response.status_code == 200:
        return response.json()
    else:
        return {}


def get_apartment_info_from_json(
        json_data: dict
) -> Dict[str, Union[Union[int, str, List[Any]], Any]]:
    """Get apartment data from json-file.

    @param json_data: raw data from json
    @return: clean data
    """
    # Apartment features from API
    living_area = json_data.get("livingArea", 0) or 0
    kitchen_area = json_data.get("kitchenArea", 0) or 0
    total_area = json_data.get("totalArea", 0) or 0
    floor_number = json_data.get("floorNumber", 0) or 0
    rooms_count = json_data.get("roomsCount", 0) or 0
    description = json_data.get("description", "") or ""
    bargain_terms = json_data.get("bargainTerms", {}) or {}
    if bargain_terms:
        price = bargain_terms.get("price", 0) or 0
    else:
        price = 0
    photos = json_data.get("photos", {}) or {}
    if photos:
        photos_url_list = [item.get("fullUrl", "") for item in photos]
        photos_url_list = [item for item in photos_url_list if item]
    else:
        photos_url_list = []
    # Apartment features from HTML
    cian_id = json_data.get("cianId", 0) or 0
    if cian_id:
        part_of_apartment_data = get_data_from_html(cian_id)
    else:
        part_of_apartment_data = {
            "Тип жилья": "",
            "Планировка": "",
            "Высота потолков": "",
            "Санузел": "",
            "Ремонт": "",
            "Вид из окон": "",
            "Балкон/лоджия": "",
            "Площадь комнат": "",
            "Отделка": "",
        }
    apartment_data = {
        "Жилая площадь, м^2": living_area,
        "Площадь кухни, м^2": kitchen_area,
        "Общая площадь, м^2": total_area,
        "Этаж": floor_number,
        "Стоимость, р.": price,
        "Количество комнат": rooms_count,
        "Описание квартиры": description,
        "Фотографии": photos_url_list,
    }
    apartment_data.update(part_of_apartment_data)
    return apartment_data


def get_common_info_from_ad(json_data: dict) -> Dict[str, Union[str, Any]]:
    """Get common info from ad.

    @param json_data: ad json-data
    @return: clear data
    """
    # Ad features
    apartment_url = json_data.get("fullUrl", "")
    added_timestamp = json_data.get("addedTimestamp", "")
    user = json_data.get("user", {})
    if user:
        user_type = user.get("userType", "")
    else:
        user_type = ""
    ad_data = {
        "Ссылка на объявление": apartment_url,
        "Дата публикации объявления": datetime.fromtimestamp(
            added_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        "Тип автора объявления": user_type,
    }
    return ad_data


def get_building_info(
        json_data: dict
) -> Dict[str, Union[Union[str, int], Any]]:
    """Get building info from json-data.

    @param json_data: raw json-data
    @return: clear data
    """
    # Building properties
    building = json_data.get("building", {}) or {}
    if building:
        passenger_lifts_count = building.get("passengerLiftsCount", 0) or 0
        build_year = building.get("buildYear", "") or ""
        cargo_lifts_count = building.get("cargoLiftsCount", 0) or 0
        floors_count = building.get("floorsCount", 0) or 0
        material_type = building.get("materialType", "") or ""
    else:
        passenger_lifts_count = 0
        build_year = ""
        cargo_lifts_count = 0
        floors_count = 0
        material_type = ""
    building_data = {
        "Количество пассажирских лифтов": passenger_lifts_count,
        "Год постройки": build_year,
        "Количество грузовых лифтов": cargo_lifts_count,
        "Количество этажей": floors_count,
        "Технология строительства": material_type,
    }
    return building_data


def get_apartment_location_info(
        json_data: dict
) -> Dict[str, Union[Union[str, int, List[str]], Any]]:
    """Get apartment location info from json-file.

    @param json_data: raw json-data
    @return: clear data
    """
    # Apartment location
    geo = json_data.get("geo", {}) or {}
    if geo:
        user_input = geo.get("userInput", "")
        coordinates = geo.get("coordinates", {}) or {}
        address = geo.get("address", []) or []
        if coordinates:
            lng = coordinates.get("lng", 0) or 0
            lat = coordinates.get("lat", 0) or 0
        else:
            lng = 0
            lat = 0
        if address:
            location_flag = False
            okrug_flag = False
            raion_flag = False
            street_flag = False
            house_flag = False
            metro_station_flag = False
            for item in address:
                if "type" in item:
                    if item["type"] == "location":
                        location = item["name"]
                        location_flag = True
                    if item["type"] == "okrug":
                        okrug = item["name"]
                        okrug_flag = True
                    if item["type"] == "raion":
                        raion = item["name"]
                        raion_flag = True
                    if item["type"] == "street":
                        street = item["name"]
                        street_flag = True
                    if item["type"] == "house":
                        house = item["name"]
                        house_flag = True
                    if item["type"] == "metro":
                        metro_station = item["name"]
                        metro_station_flag = True
                else:
                    location = ""
                    district = ""
                    raion = ""
                    street = ""
                    house = ""
                    metro_station = ""
            if not location_flag:
                location = ""
            if not okrug_flag:
                okrug = ""
            if not raion_flag:
                raion = ""
            if not street_flag:
                street = ""
            if not house_flag:
                house = ""
            if not metro_station_flag:
                metro_station = ""
        else:
            location = ""
            district = ""
            raion = ""
            street = ""
            house = ""
            metro_station = ""
    else:
        user_input = ""
        lng = 0
        lat = 0
        location = ""
        okrug = ""
        raion = ""
        street = ""
        house = ""
        metro_station = ""
    transport_type = {"walk": "пешком", "transport": "на транспорте"}
    if geo:
        undergrounds = geo.get("undergrounds", []) or []
        if undergrounds:
            undergrounds_proximity = []
            for item in undergrounds:
                if "name" in item and "transportType" in item \
                        and "time" in item:
                    line = f"{item['name']}, " \
                           f"{item['time']} минут(ы) " \
                           f"{transport_type[item['transportType']]}"
                    undergrounds_proximity.append(line)
        else:
            undergrounds_proximity = []
    else:
        undergrounds_proximity = []
    location_data = {
        "Широта": lat,
        "Долгота": lng,
        "Адрес, введенный пользователем": user_input,
        "Город": location,
        "Округ": okrug,
        "Район": raion,
        "Улица": street,
        "Дом": house,
        "Станция метро": metro_station,
        "Близость к метро": undergrounds_proximity,
    }
    return location_data


def get_all_apartment_info_from_json(
        json_data: dict
) -> Dict[str, Union[Union[int, str, List[Any]], Any]]:
    """Get all apartment data.

    @param json_data: json-data
    @return: clear data
    """
    all_data = get_apartment_info_from_json(json_data)
    all_data.update(get_building_info(json_data))
    all_data.update(get_apartment_location_info(json_data))
    all_data.update(get_common_info_from_ad(json_data))
    return all_data
