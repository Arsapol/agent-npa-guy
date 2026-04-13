"""Pydantic v2 models for landsmaps.dol.go.th deed → GPS lookup."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Amphur registry ---


class Amphur(BaseModel):
    model_config = ConfigDict(frozen=True)

    pvcode: str
    amcode: str
    amnamethai: str
    amnameeng: str


class AmphurResponse(BaseModel):
    status: int
    result: list[Amphur]


class AmphurRegistry:
    """Load amphur.json once, provide fast lookups by code or name."""

    def __init__(self, path: Path | None = None) -> None:
        if path is None:
            path = Path(__file__).parent / "amphur.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        parsed = AmphurResponse.model_validate(raw)
        # Filter out placeholder entries (amcode "00")
        self._entries = [a for a in parsed.result if a.amcode != "00"]
        # Index by (pvcode, amcode)
        self._by_code: dict[tuple[str, str], Amphur] = {
            (a.pvcode, a.amcode): a for a in self._entries
        }

    def get_by_code(self, pvcode: str, amcode: str) -> Amphur | None:
        return self._by_code.get((pvcode, amcode))

    def search_by_thai_name(self, name: str, pvcode: str | None = None) -> list[Amphur]:
        results = []
        for a in self._entries:
            if pvcode and a.pvcode != pvcode:
                continue
            if name in a.amnamethai:
                results.append(a)
        return results

    def search_by_eng_name(self, name: str, pvcode: str | None = None) -> list[Amphur]:
        needle = name.lower()
        results = []
        for a in self._entries:
            if pvcode and a.pvcode != pvcode:
                continue
            if needle in a.amnameeng.lower():
                results.append(a)
        return results

    def list_by_province(self, pvcode: str) -> list[Amphur]:
        return [a for a in self._entries if a.pvcode == pvcode]


# --- Deed query ---


class DeedQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    province_code: str = Field(description="2-digit province code, e.g. '90'")
    amphur_code: str = Field(description="2-digit amphur code, e.g. '01'")
    parcel_no: str = Field(description="Parcel/deed number, e.g. '83776'")


# --- API response models ---


class LandsStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    obligation: Optional[str] = None
    freeze: Optional[str] = None
    not_transfer: Optional[str] = None


class ParcelResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    # GPS
    parcellat: str
    parcellon: str

    # Parcel identifiers
    landno: str = ""
    parcelno: str = ""
    surveyno: str = ""
    parcel_type: str = ""
    parcel_seq: str = ""

    # Location names
    tumbolname: str = ""
    tumbolname_en: str = ""
    amphurname: str = ""
    amphurname_en: str = ""
    provname: str = ""
    provname_en: str = ""

    # Location codes
    provid: str = ""
    amphurid: str = ""
    tambol_id: str = ""

    # Area
    rai: str = "0"
    ngan: str = "0"
    wa: str = "0"
    subwa: str = "0"

    # Land price (per rai, baht string with commas)
    landprice: str = ""

    # UTM
    utm: str = ""
    utm1: str = ""
    utm2: str = ""
    utm3: str = ""
    utm4: str = ""
    utmscale: str = ""
    n: str = ""
    e: str = ""
    zone: str = ""
    parcelzone: str = ""

    # Land office
    landoffice: str = ""
    landoffice_en: str = ""
    landofficelat: str = ""
    landofficelon: str = ""
    landoffice_id: str = ""
    landoffice_seq: str = ""
    org_tel: str = ""

    # Status
    lands_status: Optional[LandsStatus] = None
    lands_owner: Optional[str] = None
    lands_allocation: Optional[str] = None

    # Links
    qrcode_link: str = ""
    surveyprice_link: str = ""
    lecs_weblink: str = ""
    treasury_weblink: str = ""

    # Misc
    isfavorite: bool = False
    queuesurvey: str = ""
    parcelbound: str = ""
    reg_seq: str = ""
    dpt1: str = ""
    dpt2: str = ""
    dpt3: str = ""
    dptid: str = ""

    @property
    def lat(self) -> float:
        return float(self.parcellat)

    @property
    def lon(self) -> float:
        return float(self.parcellon)

    @property
    def area_sqm(self) -> float:
        """Convert rai-ngan-wa to square meters. 1 rai = 1600 sqm, 1 ngan = 400 sqm, 1 wa = 4 sqm."""
        r = int(self.rai) if self.rai else 0
        n = int(self.ngan) if self.ngan else 0
        w = int(self.wa) if self.wa else 0
        sw = int(self.subwa) if self.subwa else 0
        return r * 1600.0 + n * 400.0 + w * 4.0 + sw * 0.04


class ApiResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: int
    result: list[ParcelResult] = Field(default_factory=list)
    message: str = ""
    message_en: Optional[str] = None
    error: bool = False
