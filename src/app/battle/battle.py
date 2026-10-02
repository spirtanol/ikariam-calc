from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from app.battle.accuracy import AccuracyBuffer
from app.defs.base import Battlefield, Forces, Line, LineLayout, Unit

if TYPE_CHECKING:
    from app.battle.line import BattlefieldLine

# Эти линии удерживают сторону. Истребители и бомбардировщики не удерживают.
HOLDING_LINES = frozenset({Line.MELEE, Line.FLANK, Line.LONG_RANGE, Line.ARTILLERY})

# Порядок пар — порядок хода в раунде, не порядок описания поля.
ATTACKS: tuple[tuple[Line, tuple[Line, ...]], ...] = (
    (Line.FIGHTER, (Line.BOMBER, Line.FIGHTER)),
    (Line.BOMBER, (Line.ARTILLERY, Line.LONG_RANGE, Line.MELEE, Line.FLANK)),
    (Line.FLANK, (Line.FLANK, Line.LONG_RANGE, Line.ARTILLERY, Line.MELEE)),
    (Line.ARTILLERY, (Line.MELEE, Line.FLANK)),
    (Line.LONG_RANGE, (Line.MELEE, Line.FLANK, Line.LONG_RANGE)),
    (Line.MELEE, (Line.MELEE, Line.LONG_RANGE, Line.ARTILLERY, Line.FLANK)),
)


@dataclass
class UnitState:
    """Текущие здоровье и снаряжение одного экземпляра юнита."""

    health: int
    ammo: int | None


@dataclass
class Field:
    """Линии одной стороны и резерв: сколько экземпляров типа ещё не на линии."""

    lines: dict[Line, BattlefieldLine]
    reserve: dict[Unit, int]


@dataclass(frozen=True)
class Snapshot:
    """Тип на линии до залпов: число, доля здоровья и средний запас."""

    count: int
    health: float
    ammo: float | None


class Winner(StrEnum):
    """Исход раунда. Ничья оставляет бой в том же Battle."""

    ATTACKER = "attacker"
    DEFENDER = "defender"
    DRAW = "draw"


@dataclass
class Round:
    """Снимок до залпов, поле после чистки, потери и победитель."""

    attacker: Field
    defender: Field
    attacker_losses: dict[Unit, int]
    defender_losses: dict[Unit, int]
    winner: Winner
    attacker_before: dict[Line, dict[Unit, Snapshot]]
    defender_before: dict[Line, dict[Unit, Snapshot]]


class Battle:
    """Один бой: поле, две стороны и буфер точности у каждой."""

    def __init__(
        self,
        battlefield: Battlefield,
        attacker: dict[str, int],
        defender: dict[str, int],
        forces: Forces,
    ) -> None:
        self.battlefield = battlefield
        self.forces = forces
        self.attacker = self._side(attacker)
        self.defender = self._side(defender)
        self._attacker_buffer = AccuracyBuffer()
        self._defender_buffer = AccuracyBuffer()

    def play_round(self) -> Round:
        """Собрать поле и провести линии: залп атакующего, ответ защитника, чистка."""
        attacker = self._field(self.attacker)
        defender = self._field(self.defender)
        attacker_before = self._snapshot(attacker)
        defender_before = self._snapshot(defender)
        attacker_losses: dict[Unit, int] = {}
        defender_losses: dict[Unit, int] = {}
        for attack_line, target_names in ATTACKS:
            self._volley(
                attacker,
                defender,
                self._attacker_buffer,
                defender_losses,
                attack_line,
                target_names,
            )
            self._volley(
                defender,
                attacker,
                self._defender_buffer,
                attacker_losses,
                attack_line,
                target_names,
            )
            self._purge(attacker, self.attacker)
            self._purge(defender, self.defender)
        return Round(
            attacker,
            defender,
            attacker_losses,
            defender_losses,
            self._winner(),
            attacker_before,
            defender_before,
        )

    def _snapshot(self, field: Field) -> dict[Line, dict[Unit, Snapshot]]:
        shot: dict[Line, dict[Unit, Snapshot]] = {}
        for line, battle_line in field.lines.items():
            units: dict[Unit, Snapshot] = {}
            for unit, states in battle_line.units.items():
                count = len(states)
                if count == 0:
                    continue
                health = sum(state.health for state in states) / count
                health = health / unit.health
                ammo = None
                if unit.ammo is not None:
                    ammo = sum(state.ammo or 0 for state in states) / count
                units[unit] = Snapshot(count, health, ammo)
            if units:
                shot[line] = units
        return shot

    def _winner(self) -> Winner:
        if not self._holds(self.attacker):
            return Winner.DEFENDER
        if not self._holds(self.defender):
            return Winner.ATTACKER
        return Winner.DRAW

    def _holds(self, side: dict[Unit, list[UnitState]]) -> bool:
        return any(unit.line in HOLDING_LINES for unit in side)

    def _field(self, side: dict[Unit, list[UnitState]]) -> Field:
        engaged: dict[Unit, int] = {}
        lines: dict[Line, BattlefieldLine] = {Line.MELEE: self._fill_melee(side, engaged)}
        if self.battlefield.flank is not None:
            lines[Line.FLANK] = self._fill(side, engaged, self.battlefield.flank, Line.FLANK)
        lines[Line.LONG_RANGE] = self._fill(side, engaged, self.battlefield.long_range, Line.LONG_RANGE)
        lines[Line.ARTILLERY] = self._fill(side, engaged, self.battlefield.artillery, Line.ARTILLERY)
        lines[Line.FIGHTER] = self._fill(side, engaged, self.battlefield.fighter, Line.FIGHTER)
        lines[Line.BOMBER] = self._fill(side, engaged, self.battlefield.bomber, Line.BOMBER)
        return Field(lines=lines, reserve=self._reserve(side, engaged))

    def _volley(
        self,
        attackers: Field,
        defenders: Field,
        buffer: AccuracyBuffer,
        losses: dict[Unit, int],
        attack_line: Line,
        target_names: tuple[Line, ...],
    ) -> None:
        if attack_line not in attackers.lines:
            return
        streams = [
            defenders.lines[name].get_target()
            for name in target_names
            if name in defenders.lines
        ]
        index = 0
        wounded: deque[tuple[Unit, UnitState]] = deque()
        for unit, states in attackers.lines[attack_line].units.items():
            for state in states:
                focus = buffer.strike(unit.attack.accuracy)
                while index < len(streams):
                    target_unit = None
                    while focus and wounded and target_unit is None:
                        target_unit, target_state = wounded[0]
                        if target_state.health <= 0:
                            wounded.popleft()
                            target_unit = None

                    if target_unit is None:
                        try:
                            target_unit, target_state = next(streams[index])
                        except StopIteration:
                            index += 1
                            continue
                    blow = unit.attack
                    if unit.extra_attack is not None and (state.ammo is None or state.ammo > 0):
                        blow = unit.extra_attack
                    damage = max(0, blow.damage - target_unit.armor)
                    if damage > 0:
                        target_state.health -= damage
                        if target_state.health <= 0:
                            losses[target_unit] = losses.get(target_unit, 0) + 1
                            if focus and wounded:
                                wounded.popleft()
                        elif all(state is not target_state for _, state in wounded):
                            wounded.append((target_unit, target_state))
                    break

    def _purge(self, field: Field, side: dict[Unit, list[UnitState]]) -> None:
        for line in field.lines.values():
            alive = {
                unit: [state for state in states if state.health > 0]
                for unit, states in line.units.items()
            }
            line.units = {unit: states for unit, states in alive.items() if states}
        for unit in list(side):
            survivors = [state for state in side[unit] if state.health > 0]
            if survivors:
                side[unit] = survivors
            else:
                del side[unit]

    def _reserve(self, side: dict[Unit, list[UnitState]], engaged: dict[Unit, int]) -> dict[Unit, int]:
        reserve: dict[Unit, int] = {}
        for unit, states in side.items():
            waiting = len(states) - engaged.get(unit, 0)
            if waiting:
                reserve[unit] = waiting
        return reserve

    def _empty_line(self, layout: LineLayout) -> BattlefieldLine:
        from app.battle.line import BattlefieldLine

        return BattlefieldLine(layout.cell_count, layout.cell_size)

    def _fill_melee(
        self,
        side: dict[Unit, list[UnitState]],
        engaged: dict[Unit, int],
    ) -> BattlefieldLine:
        line = self._empty_line(self.battlefield.melee)
        for key in self.forces.orders[Line.MELEE]:
            unit = self.forces.units[key]
            states = side.get(unit, [])
            count = engaged.get(unit, 0)
            index = len(states) - 1 - count
            while index >= 0:
                state = states[index]
                if state.ammo not in (None, 0):
                    break
                if not line.place(unit, state):
                    return line
                count += 1
                engaged[unit] = count
                index -= 1
        return line

    def _fill(
        self,
        side: dict[Unit, list[UnitState]],
        engaged: dict[Unit, int],
        layout: LineLayout,
        line_name: Line,
    ) -> BattlefieldLine:
        line = self._empty_line(layout)
        for key in self.forces.orders[line_name]:
            unit = self.forces.units[key]
            states = side.get(unit, [])
            count = engaged.get(unit, 0)
            skipped = 0
            while True:
                index = len(states) - 1 - count - skipped
                if index < 0:
                    break
                state = states[index]
                if unit.ammo is not None and state.ammo in (None, 0):
                    skipped += 1
                    continue
                if not line.place(unit, state):
                    return line
                count += 1
                engaged[unit] = count
        return line

    def _side(self, composition: dict[str, int]) -> dict[Unit, list[UnitState]]:
        side: dict[Unit, list[UnitState]] = {}
        for key, count in composition.items():
            try:
                unit = self.forces.units[key]
            except KeyError:
                raise ValueError(f"unknown unit: {key}") from None
            if count < 1:
                raise ValueError(f"unit count must be at least 1: {key}")
            side[unit] = [
                UnitState(health=unit.health, ammo=unit.ammo) for _ in range(count)
            ]
        return side
