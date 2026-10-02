from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.defs.resources import Resource


class Line(StrEnum):
    """Род войск. Порядок значений — порядок описания поля, не порядок хода в раунде."""

    MELEE = "melee"  # ближний бой
    FLANK = "flank"  # фланги
    LONG_RANGE = "long_range"  # дальний бой
    ARTILLERY = "artillery"  # артиллерия
    FIGHTER = "fighter"  # истребители
    BOMBER = "bomber"  # бомбардировщики


class LineLayout(BaseModel):
    """Клетки одного рода: сколько их и какая ёмкость у каждой."""

    model_config = ConfigDict(frozen=True)

    cell_count: int = Field(ge=0)
    cell_size: int = Field(ge=1)


class Battlefield(BaseModel):
    """Размер поля: по одному описанию клеток на каждый род. Флангов может не быть."""

    model_config = ConfigDict(frozen=True)

    melee: LineLayout
    flank: LineLayout | None = None
    long_range: LineLayout
    artillery: LineLayout
    fighter: LineLayout
    bomber: LineLayout


class Attack(BaseModel):
    """Урон и точность."""

    model_config = ConfigDict(frozen=True)

    damage: int = Field(ge=0)
    accuracy: int = Field(ge=0)


class Unit(BaseModel):
    """Общие характеристики сухопутного и морского юнита."""

    model_config = ConfigDict(frozen=True)

    name: str
    line: Line
    cost: dict[Resource, Annotated[int, Field(ge=1)]]
    upkeep: int
    health: int = Field(ge=0)
    armor: int = Field(ge=0)
    attack: Attack
    extra_attack: Attack | None = None
    ammo: int | None = Field(default=None, ge=1)
    size: int = Field(ge=1)

    def __hash__(self) -> int:
        return hash(self.name)


class Forces(BaseModel):
    """Юниты одного вида войск и порядок постановки на линии."""

    model_config = ConfigDict(frozen=True)

    units: dict[str, Unit]
    orders: dict[Line, tuple[str, ...]]


class Catalog(BaseModel):
    """Справочник вида боя: состав с расстановкой и размеры поля по уровням."""

    model_config = ConfigDict(frozen=True)

    forces: Forces
    battlefields: dict[int, Battlefield]
