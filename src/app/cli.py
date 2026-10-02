import importlib
from pathlib import Path

import typer
import yaml

from app.battle.battle import Battle, Field, Round, Snapshot, Winner
from app.cost import ArmyCost, army_cost
from app.defs.base import Catalog, Line, Unit

app = typer.Typer()

SIDES = ("attacker", "defender")


@app.callback()
def main() -> None:
    """Калькулятор Ikariam."""


def _load(file: Path) -> dict[str, object]:
    loaded = yaml.safe_load(file.read_text())
    if not isinstance(loaded, dict):
        raise typer.BadParameter("file must contain attacker or defender")
    return loaded


def _composition(raw: object) -> dict[str, int]:
    if raw is None or not isinstance(raw, dict):
        return {}
    composition: dict[str, int] = {}
    for key, count in raw.items():
        if not isinstance(key, str) or not isinstance(count, int) or isinstance(count, bool):
            raise typer.BadParameter("side must be a mapping of unit to count")
        composition[key] = count
    return composition


def _emit(text: str, output: Path | None) -> None:
    typer.echo(text, nl=False)
    if output is not None:
        output.write_text(text)


def _catalog(battle_type: object) -> Catalog:
    if battle_type not in ("army", "navy"):
        raise typer.BadParameter("type must be army or navy")
    module = importlib.import_module(f"app.defs.{battle_type}")
    catalog = getattr(module, "CATALOG", None)
    if catalog is None:
        raise typer.BadParameter(f"{battle_type} battlefield sizes are not recorded")
    return catalog


@app.command()
def cost(file: Path, output: Path | None = None) -> None:
    """Посчитать стоимость и содержание обеих сторон."""
    loaded = _load(file)
    units = _catalog(loaded.get("type")).forces.units
    result: dict[str, dict[str, object]] = {}
    for side in SIDES:
        try:
            priced = army_cost(_composition(loaded[side]), units)
        except ValueError as error:
            raise typer.BadParameter(str(error)) from None
        result[side] = _price_report(priced)
    _emit(yaml.safe_dump(result, sort_keys=False, allow_unicode=True), output)


def _price_report(priced: ArmyCost) -> dict[str, object]:
    return {
        "resources": {resource.value: amount for resource, amount in priced.resources.items()},
        "upkeep": priced.upkeep,
    }


def _add_losses(total: dict[str, int], losses: dict[Unit, int]) -> None:
    for unit, count in losses.items():
        total[unit.name] = total.get(unit.name, 0) + count


def _field_report(before: dict[Line, dict[Unit, Snapshot]]) -> dict[str, dict[str, dict[str, int | float]]]:
    report: dict[str, dict[str, dict[str, int | float]]] = {}
    for line in Line:
        units = before.get(line)
        if not units:
            continue
        report[line.value] = {}
        for unit, shot in units.items():
            row: dict[str, int | float] = {"count": shot.count, "health": shot.health}
            if shot.ammo is not None:
                row["ammo"] = shot.ammo
            report[line.value][unit.name] = row
    return report


def _side_round(
    field: Field,
    losses: dict[Unit, int],
    before: dict[Line, dict[Unit, Snapshot]],
    units: dict[str, Unit],
) -> dict[str, object]:
    lost = {unit.name: count for unit, count in losses.items()}
    priced = _price_report(army_cost(lost, units))
    return {
        "field": _field_report(before),
        "losses": lost,
        "reserve": {unit.name: count for unit, count in field.reserve.items()},
        "resources": priced["resources"],
        "upkeep": priced["upkeep"],
    }


@app.command()
def battle(file: Path, output: Path | None = None) -> None:
    """Прокрутить бой до победы и показать потери."""
    loaded = _load(file)
    catalog = _catalog(loaded.get("type"))
    level = loaded.get("level")
    if isinstance(level, bool) or not isinstance(level, int) or level not in catalog.battlefields:
        raise typer.BadParameter("level must be an integer from 1 to 5")
    units = catalog.forces.units
    try:
        fight = Battle(
            catalog.battlefields[level],
            _composition(loaded.get("attacker")),
            _composition(loaded.get("defender")),
            catalog.forces,
        )
    except ValueError as error:
        raise typer.BadParameter(str(error)) from None
    rounds: list[Round] = []
    winner = Winner.DRAW
    while winner is Winner.DRAW:
        fought = fight.play_round()
        rounds.append(fought)
        winner = fought.winner
    attacker_losses: dict[str, int] = {}
    defender_losses: dict[str, int] = {}
    report: list[dict[str, object]] = []
    for fought in rounds:
        _add_losses(attacker_losses, fought.attacker_losses)
        _add_losses(defender_losses, fought.defender_losses)
        report.append(
            {
                "attacker": _side_round(
                    fought.attacker, fought.attacker_losses, fought.attacker_before, units
                ),
                "defender": _side_round(
                    fought.defender, fought.defender_losses, fought.defender_before, units
                ),
            }
        )
    result = {
        "winner": winner.value,
        "rounds": report,
        "totals": {
            "attacker": _price_report(army_cost(attacker_losses, units)),
            "defender": _price_report(army_cost(defender_losses, units)),
        },
    }
    _emit(yaml.safe_dump(result, sort_keys=False, allow_unicode=True), output)
