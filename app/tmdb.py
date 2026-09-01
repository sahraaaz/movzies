import random
from datetime import date
from typing import Any

import aiohttp


TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


class TMDBError(RuntimeError):
    pass


class TMDBClient:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self._genre_cache: dict[str, dict[int, str]] = {}

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "accept": "application/json",
        }

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout, headers=self.headers) as session:
            async with session.get(f"{TMDB_BASE_URL}{path}", params=params) as response:
                if response.status != 200:
                    body = await response.text()
                    raise TMDBError(f"TMDB request failed ({response.status}): {body[:300]}")
                return await response.json()

    async def get_genres(self, media_type: str) -> dict[int, str]:
        if media_type in self._genre_cache:
            return self._genre_cache[media_type]

        endpoint = "/genre/movie/list" if media_type == "movie" else "/genre/tv/list"
        data = await self._get(endpoint, {"language": "en-US"})
        genres = {item["id"]: item["name"] for item in data.get("genres", [])}
        self._genre_cache[media_type] = genres
        return genres

    async def _normalize_item(self, item: dict[str, Any], media_type: str) -> dict[str, Any]:
        genres_map = await self.get_genres(media_type)

        if item.get("genres"):
            genre_names = [genre.get("name") for genre in item["genres"] if genre.get("name")]
        else:
            genre_names = [genres_map[g] for g in item.get("genre_ids", []) if g in genres_map]

        title = item.get("title") if media_type == "movie" else item.get("name")
        release_date = item.get("release_date") if media_type == "movie" else item.get("first_air_date")
        year = release_date[:4] if release_date else "—"
        poster_path = item.get("poster_path")

        return {
            "id": item["id"],
            "media_type": media_type,
            "title": title or "Unknown title",
            "year": year,
            "rating": float(item.get("vote_average") or 0),
            "vote_count": int(item.get("vote_count") or 0),
            "genres": genre_names,
            "overview": (item.get("overview") or "No synopsis is available yet.").strip(),
            "poster_url": f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None,
            "tmdb_url": f"https://www.themoviedb.org/{'movie' if media_type == 'movie' else 'tv'}/{item['id']}",
        }

    async def _random_from_discover(
        self,
        media_type: str,
        extra_params: dict[str, Any] | None = None,
        max_pages: int = 100,
    ) -> dict[str, Any]:
        if media_type not in {"movie", "tv"}:
            raise ValueError("media_type must be 'movie' or 'tv'")

        endpoint = "/discover/movie" if media_type == "movie" else "/discover/tv"
        params: dict[str, Any] = {
            "language": "en-US",
            "include_adult": "false",
            "sort_by": "popularity.desc",
            "vote_count.gte": 100,
            "page": 1,
        }
        if media_type == "movie":
            params["include_video"] = "false"
        if extra_params:
            params.update(extra_params)

        first_page = await self._get(endpoint, params)
        total_pages = min(int(first_page.get("total_pages", 1) or 1), max_pages)
        page = random.randint(1, max(total_pages, 1))

        if page == 1:
            data = first_page
        else:
            data = await self._get(endpoint, {**params, "page": page})

        candidates = [item for item in data.get("results", []) if item.get("id")]
        if not candidates:
            raise TMDBError("No recommendation candidates were returned by TMDB.")

        return await self._normalize_item(random.choice(candidates), media_type)

    async def random_recommendation(self, media_type: str) -> dict[str, Any]:
        return await self._random_from_discover(
            media_type,
            {"vote_average.gte": 6.0, "vote_count.gte": 150},
        )

    async def filtered_recommendation(
        self,
        media_type: str,
        genre_id: int | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        min_rating: float | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"vote_count.gte": 80}

        if genre_id:
            params["with_genres"] = str(genre_id)
        if min_rating is not None:
            params["vote_average.gte"] = min_rating

        if media_type == "movie":
            if year_from:
                params["primary_release_date.gte"] = f"{year_from}-01-01"
            if year_to:
                params["primary_release_date.lte"] = f"{year_to}-12-31"
        else:
            if year_from:
                params["first_air_date.gte"] = f"{year_from}-01-01"
            if year_to:
                params["first_air_date.lte"] = f"{year_to}-12-31"

        # Avoid future-dated entries if no explicit upper bound was selected.
        if not year_to:
            current_year = date.today().year
            key = "primary_release_date.lte" if media_type == "movie" else "first_air_date.lte"
            params[key] = f"{current_year}-12-31"

        return await self._random_from_discover(media_type, params, max_pages=60)

    async def movie_by_title(self, title: str, year: int | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {
            "query": title,
            "include_adult": "false",
            "language": "en-US",
            "page": 1,
        }
        if year:
            params["year"] = year

        data = await self._get("/search/movie", params)
        results = [item for item in data.get("results", []) if item.get("id")]
        if not results:
            raise TMDBError(f"Movie not found: {title}")

        return await self._normalize_item(results[0], "movie")
