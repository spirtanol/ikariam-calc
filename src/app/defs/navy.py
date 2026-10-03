from traceback import extract_stack
from app.battle import accuracy
from app.defs.base import Battlefield, Catalog, Forces, Line, LineLayout, Unit, Attack
from app.defs.resources import Resource


def _layout(cell_count: int, cell_size: int) -> LineLayout:
    return LineLayout(cell_count=cell_count, cell_size=cell_size)


BATTLEFIELDS: dict[int, Battlefield] = {
    1: Battlefield(
        melee=_layout(3, 15),
        long_range=_layout(3, 15),
        artillery=_layout(1, 15),
        fighter=_layout(1, 10),
        bomber=_layout(1, 10),
    ),
    2: Battlefield(
        melee=_layout(5, 15),
        flank=_layout(2, 15),
        long_range=_layout(5, 15),
        artillery=_layout(2, 15),
        fighter=_layout(1, 10),
        bomber=_layout(1, 10),
    ),
    3: Battlefield(
        melee=_layout(7, 15),
        flank=_layout(4, 15),
        long_range=_layout(7, 15),
        artillery=_layout(3, 15),
        fighter=_layout(1, 15),
        bomber=_layout(1, 15),
    ),
    4: Battlefield(
        melee=_layout(7, 20),
        flank=_layout(6, 15),
        long_range=_layout(7, 20),
        artillery=_layout(4, 15),
        fighter=_layout(2, 10),
        bomber=_layout(2, 10),
    ),
    5: Battlefield(
        melee=_layout(7, 20),
        flank=_layout(6, 15),
        long_range=_layout(7, 20),
        artillery=_layout(4, 15),
        fighter=_layout(2, 10),
        bomber=_layout(2, 10),
    ),
}

UNITS: dict[str, Unit] = {
    unit.name: unit
    for unit in (
        Unit(
            name="flamethrower_ship",
            line=Line.MELEE,
            cost={Resource.WOOD: 80, Resource.SULFUR: 230},
            upkeep=25,
            health=4380,
            armor=160,
            attack=Attack(damage=1640, accuracy=50),
            size=2,
        ),
        Unit(
            name="steam_ram_ship",
            line=Line.MELEE,
            cost={Resource.WOOD: 400, Resource.SULFUR: 800},
            upkeep=45,
            health=11520,
            armor=320,
            attack=Attack(damage=3320, accuracy=90),
            size=5,
        ),
        Unit(
            name="ram_ship",
            line=Line.FLANK,
            cost={Resource.WOOD: 250},
            upkeep=15,
            health=3080,
            armor=180,
            attack=Attack(damage=1500, accuracy=80),
            size=3,
        ),
        Unit(
            name="ballista_ship",
            line=Line.LONG_RANGE,
            cost={Resource.WOOD: 180, Resource.SULFUR: 160},
            upkeep=20,
            health=3080,
            armor=280,
            attack=Attack(damage=1020, accuracy=70),
            extra_attack=Attack(damage=560, accuracy=50),
            size=2,
            ammo=7
        ),
        Unit(
            name="catapult_ship",
            line=Line.LONG_RANGE,
            cost={Resource.WOOD: 180, Resource.SULFUR: 140},
            upkeep=35,
            health=2960,
            armor=200,
            attack=Attack(damage=620, accuracy=70),
            extra_attack=Attack(damage=900, accuracy=30),
            size=3,
            ammo=6
        ),
        Unit(
            name="mortar_ship",
            line=Line.LONG_RANGE,
            cost={Resource.WOOD: 220, Resource.SULFUR: 900},
            upkeep=50,
            health=3080,
            armor=120,
            attack=Attack(damage=740, accuracy=50),
            extra_attack=Attack(damage=1380, accuracy=10),
            size=4,
            ammo=5
        ),
        Unit(
            name="rocket_ship",
            line=Line.ARTILLERY,
            cost={Resource.WOOD: 200, Resource.SULFUR: 1200},
            upkeep=55,
            health=1300,
            armor=120,
            attack=Attack(damage=400, accuracy=70),
            extra_attack=Attack(damage=7600, accuracy=20),
            size=4,
            ammo=2
        ),
        Unit(
            name="submarine",
            line=Line.ARTILLERY,
            cost={Resource.WOOD: 160, Resource.SULFUR: 100, Resource.CRYSTAL: 750},
            upkeep=50,
            health=2200,
            armor=120,
            attack=Attack(damage=1800, accuracy=80),
            extra_attack=Attack(damage=2460, accuracy=80),
            size=3,
            ammo=4
        ),
        Unit(
            name="steam_ship",
            line=Line.FIGHTER,
            cost={Resource.WOOD: 40, Resource.SULFUR: 280},
            upkeep=5,
            health=400,
            armor=0,
            attack=Attack(damage=240, accuracy=90),
            size=1,
            ammo=5
        ),
        Unit(
            name="carrier_ship",
            line=Line.BOMBER,
            cost={Resource.WOOD: 700, Resource.SULFUR: 700},
            upkeep=100,
            health=2800,
            armor=0,
            attack=Attack(damage=2000, accuracy=50),
            size=5,
            ammo=5
        ),
    )
}

ORDERS: dict[Line, tuple[str, ...]] = {
    Line.MELEE: (
        "steam_ram_ship", "flamethrower_ship", "ram_ship", "ballista_ship", "catapult_ship", "mortar_ship"
        # Варвары
    ),
    Line.FLANK: (
        "ram_ship",
        # Варвары
    ),
    Line.LONG_RANGE: (
        "mortar_ship", "catapult_ship", "ballista_ship"
        # Варвары
    ),
    Line.ARTILLERY: (
        "rocket_ship", "submarine"
        # Варвары
    ),
    Line.FIGHTER: (
        "steam_ship",
        # Варвары
    ),
    Line.BOMBER: (
        "carrier_ship",
        # Варвары
    ),
}

CATALOG = Catalog(
    forces=Forces(units=UNITS, orders=ORDERS),
    battlefields=BATTLEFIELDS,
)
