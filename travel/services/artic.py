"""Art Institute of Chicago API — валидация и загрузка данных о произведениях."""
import requests

ARTWORK_DETAIL_URL = 'https://api.artic.edu/api/v1/artworks/{id}'


def fetch_artwork(external_id: str) -> dict | None:
    """
    Возвращает payload произведения или None, если API вернуло 404/ошибку.
    """
    url = ARTWORK_DETAIL_URL.format(id=external_id)
    try:
        r = requests.get(url, timeout=10)
    except requests.RequestException:
        return None
    if r.status_code != 200:
        return None
    data = r.json()
    return data.get('data')
