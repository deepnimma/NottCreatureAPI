from __future__ import annotations

from pydantic import BaseModel

from app.models.common import PaginationMeta

__all__ = [
    "Ability",
    "Attack",
    "Card",
    "CardListResponse",
    "CardSummary",
    "CardVariant",
    "CardVariantResolved",
    "Legality",
    "Translation",
    "WeaknessResistance",
]


class Attack(BaseModel):
    name: str
    cost: list[str]
    converted_energy_cost: int
    damage: str | None = None
    description: str | None = None


class Ability(BaseModel):
    name: str
    type: str
    description: str


class WeaknessResistance(BaseModel):
    type: str
    value: str


class Legality(BaseModel):
    standard: bool
    expanded: bool
    unlimited: bool


class Translation(BaseModel):
    name: str | None = None
    description: str | None = None
    flavor_text: str | None = None


class Card(BaseModel):
    id: str
    name: str
    supertype: str
    subtypes: list[str] = []
    hp: int | None = None
    types: list[str] = []
    evolves_from: str | None = None
    evolves_to: list[str] = []
    rules: list[str] = []
    abilities: list[Ability] = []
    attacks: list[Attack] = []
    weaknesses: list[WeaknessResistance] = []
    resistances: list[WeaknessResistance] = []
    retreat_cost: list[str] = []
    converted_retreat_cost: int = 0
    set_id: str
    number: str
    artist: str | None = None
    rarity: str | None = None
    flavor_text: str | None = None
    national_pokedex_numbers: list[int] = []
    legalities: Legality
    image_url: str | None = None
    translations: dict[str, Translation] = {}


class CardSummary(BaseModel):
    id: str
    name: str
    supertype: str
    types: list[str] = []
    set_id: str
    number: str
    rarity: str | None = None
    image_url: str | None = None


class CardListResponse(BaseModel):
    data: list[CardSummary]
    pagination: PaginationMeta


class CardVariant(BaseModel):
    id: str
    card_id: str
    name: str | None = None
    image_url: str | None = None


class CardVariantResolved(CardVariant):
    effective_image_url: str
