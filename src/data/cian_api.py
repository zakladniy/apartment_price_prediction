"""Tools for extract data from CIAN by API."""
from datetime import datetime
from typing import Union, Any, List, Optional, Dict

import requests
from nested_lookup import nested_lookup

from .cian_config import headers, api_url
from .cian_html import get_data_from_html


def nested_check(key: str, source_dict: dict) -> Optional[Any]:
    """Get data by key from nested dicts/json.

    @param key: target key
    @param source_dict: nested dict
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


def get_ads_by_page_number(
        target: str,
        page: int,
        url: str = api_url
) -> Dict[Any, Any]:
    """Get ads with apartments by page number from API.

    @param target: ad type
    @param page: page number
    @param url: API url
    @return: json with ads
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
        return {}
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
    """Get apartment info from API json.

    @param json_data: raw data
    @return: clean data
    """
    # Apartment properties from API
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
    # Apartment properties from HTML
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


def get_ad_info_from_json(json_data: dict) -> Dict[str, Union[str, Any]]:
    """Get common ad info from json.

    @param json_data: raw json data
    @return: clean data
    """
    # Ad params
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


def get_building_info_from_json(json_data: dict) -> dict:
    """Get building info from json data.

    @param json_data: raw data
    @return: clean data
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


def get_location_info_from_json(
        json_data: dict
) -> Dict[str, Union[Union[str, int, List[str]], Any]]:
    """Get apartment location info from json.

    @param json_data: raw data
    @return: clean data
    """
    # Location params
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


def get_all_apartment_info_from_json(json_data: dict) -> dict:
    """Get all apartment info from json.

    @param json_data: raw data
    @return: clean data
    """
    all_data = get_apartment_info_from_json(json_data)
    all_data.update(get_building_info_from_json(json_data))
    all_data.update(get_location_info_from_json(json_data))
    all_data.update(get_ad_info_from_json(json_data))
    return all_data
