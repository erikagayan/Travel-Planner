"""Art Institute of Chicago API — валидация и загрузка произведений."""
from __future__ import annotations

import requests
from django.core.cache import cache
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout as RequestsTimeout

from .exceptions import ServiceUnavailableError

ARTWORK_CACHE_TTL = 3600  # 1 час
ARTWORK_CACHE_KEY = 'artic:artwork:{id}'


class ArticService:
    BASE = 'https://api.artic.edu/api/v1'
    ARTWORK_FIELDS = 'id,title,place_of_origin'
    TIMEOUT = 10.0

    def __init__(self, timeout: float | None = None):
        self.timeout = self.TIMEOUT if timeout is None else timeout

    def _get(self, url: str, *, params: dict | None = None) -> requests.Response:
        try:
            return requests.get(url, params=params, timeout=self.timeout)
        except (RequestsTimeout, RequestsConnectionError) as exc:
            raise ServiceUnavailableError(
                'Unable to reach Art Institute of Chicago API. Please try again later.'
            ) from exc

    def get_artwork(self, external_id: str) -> dict | None:
        """
        Валидация места: GET artworks/{id}?fields=...
        Возвращает dict с полями API или None при 404.
        """
        key = ARTWORK_CACHE_KEY.format(id=external_id)
        cached = cache.get(key)
        if cached is not None:
            return cached

        url = f'{self.BASE}/artworks/{external_id}'
        r = self._get(url, params={'fields': self.ARTWORK_FIELDS})
        if r.status_code == 404:
            return None
        if r.status_code != 200:
            return None

        payload = r.json().get('data')
        if isinstance(payload, dict):
            cache.set(key, payload, timeout=ARTWORK_CACHE_TTL)
        return payload if isinstance(payload, dict) else None

    def validate_artwork(self, external_id: str) -> bool:
        """Место существует во внешнем API."""
        return self.get_artwork(external_id) is not None

    def search_artworks(self, query: str) -> dict:
        """Поиск произведений (сырой ответ API)."""
        q = (query or '').strip()
        if not q:
            return {'data': [], 'pagination': {'total': 0, 'offset': 0, 'limit': 0}}

        url = f'{self.BASE}/artworks/search'
        r = self._get(
            url,
            params={'q': q, 'fields': self.ARTWORK_FIELDS},
        )
        if r.status_code == 200:
            return r.json()
        if r.status_code >= 500:
            raise ServiceUnavailableError(
                'Art Institute search is temporarily unavailable. Please try again later.'
            )
        return {'data': [], 'pagination': {'total': 0, 'offset': 0, 'limit': 0}}
