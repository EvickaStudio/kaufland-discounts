from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from kaufland.utils import distance_km


class KauflandAPIError(RuntimeError):
    pass


class KauflandModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class Store(KauflandModel):
    store_id: str = Field(alias="storeId")
    country: str | None = None
    name: str | None = None
    street: str | None = None
    zipcode: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    features: list[str] | None = None
    opening_hours: list[dict[str, Any]] | None = Field(
        default=None, alias="openingHours"
    )

    @property
    def address(self) -> str:
        parts = [
            self.street,
            " ".join(value for value in (self.zipcode, self.city) if value) or None,
            self.country,
        ]
        return ", ".join(value for value in parts if value)

    @property
    def title(self) -> str:
        return self.name or f"Kaufland {self.store_id}"

    def distance_to(self, latitude: float, longitude: float) -> float | None:
        if self.latitude is None or self.longitude is None:
            return None
        return distance_km(latitude, longitude, self.latitude, self.longitude)


class Offer(KauflandModel):
    offer_id: str | None = Field(default=None, alias="offerId")
    store_id: str | None = Field(default=None, alias="storeId")
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    brand: str | None = None
    formatted_price: str | None = Field(default=None, alias="formattedPrice")
    formatted_base_price: str | None = Field(default=None, alias="formattedBasePrice")
    loyalty_formatted_price: str | None = Field(
        default=None, alias="loyaltyFormattedPrice"
    )
    date_from: str | None = Field(default=None, alias="dateFrom")
    date_to: str | None = Field(default=None, alias="dateTo")
    image_url: str | None = Field(default=None, alias="imageUrl")

    @property
    def name(self) -> str:
        return " ".join(value for value in (self.brand, self.title) if value) or "-"

    @property
    def period(self) -> str:
        if self.date_from and self.date_to:
            return f"{self.date_from} – {self.date_to}"
        return self.date_from or self.date_to or "-"

    @property
    def price(self) -> str:
        return self.formatted_price or "-"

    @property
    def loyalty_price(self) -> str:
        return self.loyalty_formatted_price or "-"

    @property
    def base_price(self) -> str:
        return self.formatted_base_price or "-"


class OffersBucket(KauflandModel):
    offers: list[Offer] = Field(default_factory=list)


class OffersResponse(KauflandModel):
    offers: list[Offer] = Field(default_factory=list)
    loyalty: OffersBucket | None = None

    def all_offers(self) -> list[Offer]:
        result = list(self.offers)
        if self.loyalty:
            result.extend(self.loyalty.offers)
        return result
