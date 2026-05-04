from __future__ import annotations

import argparse
import base64
import json
from typing import Any

import httpx
from pydantic import TypeAdapter

from kaufland.config import KauflandSettings, get_settings
from kaufland.models import KauflandAPIError, Offer, OffersResponse, Store


class Kaufland:
    def __init__(
        self,
        *,
        settings: KauflandSettings | None = None,
        user: str | None = None,
        password: str | None = None,
        timeout: float | None = None,
        language: str | None = None,
    ) -> None:
        settings = settings or get_settings()

        self.user = user if user is not None else settings.app_basic_user
        self.password = (
            password if password is not None else settings.app_basic_password
        )

        app_version = settings.app_version

        self._client = httpx.Client(
            base_url=settings.app_base_url,
            timeout=timeout if timeout is not None else settings.timeout,
            headers={
                "Accept": "application/json",
                "Accept-Language": (
                    language if language is not None else settings.language
                ),
                "App-Version": app_version,
                "User-Agent": f"Kaufland/{app_version} Android",
            },
        )

    def __enter__(self) -> Kaufland:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def _auth_headers(self) -> dict[str, str]:
        raw = f"{self.user}:{self.password}".encode()
        token = base64.b64encode(raw).decode("ascii")
        return {"Authorization": f"Basic {token}"}

    def _get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        try:
            response = self._client.get(
                path, params=params, headers=self._auth_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500]
            raise KauflandAPIError(
                f"GET {path} failed with HTTP {exc.response.status_code}: {body}"
            ) from exc
        except httpx.HTTPError as exc:
            raise KauflandAPIError(f"GET {path} failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise KauflandAPIError(f"GET {path} did not return valid JSON") from exc

    def stores(
        self,
        *,
        country: str | None = "DE",
        latitude: float | None = None,
        longitude: float | None = None,
        limit: int | None = None,
    ) -> list[Store]:
        params = {
            key: value
            for key, value in {
                "country": country,
                "latitude": latitude,
                "longitude": longitude,
                "limit": limit,
            }.items()
            if value is not None
        }

        data = self._get("/api/v4/stores", params=params)
        stores = TypeAdapter(list[Store]).validate_python(data)

        if country:
            normalized_country = country.upper()
            stores = [
                store
                for store in stores
                if (store.country or "").upper() == normalized_country
            ]

        if latitude is not None and longitude is not None:
            stores.sort(
                key=lambda store: (
                    store.distance_to(latitude, longitude)
                    if store.distance_to(latitude, longitude) is not None
                    else float("inf")
                )
            )

        if limit is not None:
            stores = stores[:limit]

        return stores

    def find_stores(
        self,
        query: str,
        *,
        country: str | None = "DE",
        limit: int = 10,
    ) -> list[Store]:
        needle = query.casefold().strip()

        matches: list[Store] = []
        for store in self.stores(country=country):
            searchable = " ".join(
                value
                for value in (
                    store.store_id,
                    store.name,
                    store.street,
                    store.zipcode,
                    store.city,
                )
                if value
            ).casefold()

            if needle in searchable:
                matches.append(store)

        return matches[:limit]

    def find_store(self, query: str, *, country: str | None = "DE") -> Store:
        matches = self.find_stores(query, country=country, limit=1)
        if not matches:
            raise LookupError(f"No Kaufland store found for {query!r}")
        return matches[0]

    def offers(self, store_id: str) -> list[Offer]:
        data = self._get(f"/data/api/v7/offers/{store_id}")
        return OffersResponse.model_validate(data).all_offers()


def _format_opening_hours(store: Store) -> tuple[list[str], list[str]]:
    if not store.opening_hours:
        return [], []

    open_days: list[str] = []
    closed_days: list[str] = []

    for row in store.opening_hours:
        weekday = row.get("weekday") or row.get("dayOfWeek") or row.get("day")
        if weekday is None:
            continue

        opens = row.get("open")
        closes = row.get("close")

        if opens is None:
            opens = row.get("opensAt")
        if closes is None:
            closes = row.get("closesAt")

        if opens == 0 and closes == 0:
            closed_days.append(str(weekday))
        else:
            open_days.append(str(weekday))

    return open_days, closed_days


def print_store(store: Store) -> None:
    print(f"{store.title} ({store.store_id})")
    print(store.address or "-")

    if store.latitude is not None and store.longitude is not None:
        print(f"{store.latitude}, {store.longitude}")

    if store.phone:
        print(store.phone)

    if store.features:
        print(", ".join(store.features))

    open_days, closed_days = _format_opening_hours(store)

    if open_days:
        print("Open: " + ", ".join(open_days))
    if closed_days:
        print("Closed: " + ", ".join(closed_days))


def _ellipsize(value: str | None, width: int) -> str:
    text = value or "-"
    if len(text) <= width:
        return text
    if width <= 3:
        return "." * width
    return text[: width - 3] + "..."


def print_offers(offers: list[Offer], *, limit: int) -> None:
    print(f"Offers: {len(offers)}")

    for offer in offers[:limit]:
        name = _ellipsize(f"{offer.name}:", 10)
        subtitle = _ellipsize(offer.subtitle, 36)
        price = _ellipsize(offer.price, 8)
        base_price = _ellipsize(offer.base_price, 18)
        loyalty_price = _ellipsize(offer.loyalty_price, 8)
        period = _ellipsize(offer.period, 23)

        print(
            f"  {name:<13} "
            f"{subtitle:<36} | "
            f"{price:>8} | "
            f"{base_price:<18} | "
            f"loyalty {loyalty_price:>8} | "
            f"{period}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find a Kaufland store and print current offers."
    )

    parser.add_argument(
        "query",
        help="Store search query, e.g. Frankfurt, Lübeck, Farmsen",
    )
    parser.add_argument(
        "--country",
        default="DE",
        help="Country filter, default: DE",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of offers to print, default: 10",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Accept-Language override, e.g. de or en",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="HTTP timeout override in seconds",
    )
    parser.add_argument(
        "--user",
        default=None,
        help="Basic auth user override",
    )
    parser.add_argument(
        "--password",
        default=None,
        help="Basic auth password override",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.limit < 1:
        print("Error: --limit must be at least 1")
        return 2

    try:
        with Kaufland(
            user=args.user,
            password=args.password,
            timeout=args.timeout,
            language=args.language,
        ) as kaufland:
            store = kaufland.find_store(args.query, country=args.country)
            offers = kaufland.offers(store.store_id)

        print_store(store)
        print_offers(offers, limit=args.limit)
        return 0

    except LookupError as exc:
        print(f"Error: {exc}")
        return 1
    except KauflandAPIError as exc:
        print(f"API error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
