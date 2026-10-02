from collections.abc import Iterator

from app.battle.battle import UnitState
from app.defs.base import Unit


class BattlefieldLine:
    """Одна линия поля. Клетку открывает сама, типы внутри клетки не смешивает."""

    def __init__(self, cell_count: int, cell_size: int) -> None:
        self._cell_size = cell_size
        self._cells_left = cell_count
        self._slots_left = 0
        self._last: Unit | None = None
        self.units: dict[Unit, list[UnitState]] = {}

    def place(self, unit: Unit, state: UnitState) -> bool:
        """Поставить один экземпляр. True — юнит встал на линию."""
        if self._last is not unit:
            if not self._open(unit):
                return False
        elif self._slots_left == 0 and not self._open(unit):
            return False
        self._slots_left -= 1
        self.units.setdefault(unit, []).append(state)
        return True

    def _open(self, unit: Unit) -> bool:
        if self._cells_left == 0:
            return False
        self._cells_left -= 1
        self._slots_left = self._cell_size // unit.size
        self._last = unit
        return True

    def get_target(self) -> Iterator[tuple[Unit, UnitState]]:
        """Круг живых целей. За проход без выживших генератор заканчивается."""
        while True:
            has_alive = False
            for unit, states in self.units.items():
                for state in states:
                    if state.health <= 0:
                        continue
                    yield unit, state
                    has_alive = has_alive or state.health > 0
            if not has_alive:
                return

