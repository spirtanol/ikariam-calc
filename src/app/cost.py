from dataclasses import dataclass

from app.defs.base import Unit
from app.defs.resources import Resource


@dataclass(frozen=True)
class ArmyCost:
    """Стоимость состава: ресурсы строительства и содержание в золоте."""

    resources: dict[Resource, int]
    upkeep: int


def army_cost(composition: dict[str, int], units: dict[str, Unit]) -> ArmyCost:
    """Сумма цены и содержания юнитов по словарю. Поле боя не нужно."""
    resources: dict[Resource, int] = {}
    upkeep = 0
    for key, count in composition.items():
        try:
            unit = units[key]
        except KeyError:
            raise ValueError(f"unknown unit: {key}") from None
        if count < 1:
            raise ValueError(f"unit count must be at least 1: {key}")
        for resource, amount in unit.cost.items():
            resources[resource] = resources.get(resource, 0) + amount * count
        upkeep += unit.upkeep * count
    return ArmyCost(resources=resources, upkeep=upkeep)
