"""Configs for parsing CIAN by bs4 or API."""
from environs import Env
from fake_headers import Headers

env = Env()
env.read_env()

headers = Headers(
    browser="chrome",
    os="win",
    headers=True,
)

base_url = env("BASE_URL")

api_url = env("API_URL")

target_params = [
    "Тип жилья",
    "Планировка",
    "Высота потолков",
    "Санузел",
    "Ремонт",
    "Вид из окон",
    "Балкон/лоджия",
    "Площадь комнат",
    "Отделка",
]
