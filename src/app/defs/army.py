from app.defs.base import Attack, Battlefield, Catalog, Forces, Line, LineLayout, Unit
from app.defs.resources import Resource


def _layout(cell_count: int, cell_size: int) -> LineLayout:
    return LineLayout(cell_count=cell_count, cell_size=cell_size)


BATTLEFIELDS: dict[int, Battlefield] = {
    1: Battlefield(
        melee=_layout(3, 30),
        long_range=_layout(3, 30),
        artillery=_layout(1, 30),
        fighter=_layout(1, 10),
        bomber=_layout(1, 10),
    ),
    2: Battlefield(
        melee=_layout(5, 30),
        flank=_layout(2, 30),
        long_range=_layout(5, 30),
        artillery=_layout(2, 30),
        fighter=_layout(1, 20),
        bomber=_layout(1, 20),
    ),
    3: Battlefield(
        melee=_layout(7, 30),
        flank=_layout(4, 30),
        long_range=_layout(7, 30),
        artillery=_layout(3, 30),
        fighter=_layout(1, 30),
        bomber=_layout(1, 30),
    ),
    4: Battlefield(
        melee=_layout(7, 40),
        flank=_layout(6, 30),
        long_range=_layout(7, 40),
        artillery=_layout(4, 30),
        fighter=_layout(2, 20),
        bomber=_layout(2, 20),
    ),
    5: Battlefield(
        melee=_layout(7, 50),
        flank=_layout(6, 40),
        long_range=_layout(7, 50),
        artillery=_layout(5, 30),
        fighter=_layout(2, 30),
        bomber=_layout(2, 30),
    ),
}

UNITS: dict[str, Unit] = {
    unit.name: unit
    for unit in (
        Unit(
            name="phalanx",
            line=Line.MELEE,
            cost={Resource.WOOD: 40, Resource.SULFUR: 30},
            upkeep=3,
            health=1120,
            armor=20,
            attack=Attack(damage=360, accuracy=90),
            size=1,
        ),
        Unit(
            name="steam_giant",
            line=Line.MELEE,
            cost={Resource.WOOD: 130, Resource.SULFUR: 180},
            upkeep=12,
            health=3680,
            armor=60,
            attack=Attack(damage=840, accuracy=80),
            size=3,
        ),
        Unit(
            name="spearman",
            line=Line.FLANK,
            cost={Resource.WOOD: 30},
            upkeep=1,
            health=260,
            armor=0,
            attack=Attack(damage=80, accuracy=70),
            size=1,
        ),
        Unit(
            name="swordsman",
            line=Line.FLANK,
            cost={Resource.WOOD: 30, Resource.SULFUR: 30},
            upkeep=4,
            health=360,
            armor=0,
            attack=Attack(damage=200, accuracy=90),
            size=1,
        ),
        Unit(
            name="shooter",
            line=Line.LONG_RANGE,
            cost={Resource.WOOD: 50, Resource.SULFUR: 150},
            upkeep=3,
            health=240,
            armor=0,
            attack=Attack(damage=60, accuracy=60),
            extra_attack=Attack(damage=580, accuracy=70),
            size=4,
            ammo=3
        ),
        Unit(
            name="slinger",
            line=Line.LONG_RANGE,
            cost={Resource.WOOD: 20},
            upkeep=2,
            health=160,
            armor=0,
            attack=Attack(damage=40, accuracy=60),
            extra_attack=Attack(damage=60, accuracy=20, ammo=5),
            size=1,
        ),
        Unit(
            name="archer",
            line=Line.LONG_RANGE,
            cost={Resource.WOOD: 30, Resource.SULFUR: 25},
            upkeep=4,
            health=320,
            armor=0,
            attack=Attack(damage=100, accuracy=60),
            extra_attack=Attack(damage=100, accuracy=40, ammo=3),
            size=1,
        ),
        Unit(
            name="gyrocopter",
            line=Line.FIGHTER,
            cost={Resource.WOOD: 25, Resource.SULFUR: 100},
            upkeep=15,
            health=580,
            armor=0,
            attack=Attack(damage=340, accuracy=80),
            ammo=4,
            size=1,
        ),
        Unit(
            name="bomber",
            line=Line.BOMBER,
            cost={Resource.WOOD: 40, Resource.SULFUR: 250},
            upkeep=45,
            health=800,
            armor=0,
            attack=Attack(damage=960, accuracy=20),
            ammo=2,
            size=2,
        ),
        Unit(
            name="ram",
            line=Line.ARTILLERY,
            cost={Resource.WOOD: 220},
            upkeep=15,
            health=1760,
            armor=20,
            attack=Attack(damage=240, accuracy=70),
            extra_attack=Attack(damage=1600, accuracy=10),
            size=5,
        ),
        Unit(
            name="catapult",
            line=Line.ARTILLERY,
            cost={Resource.WOOD: 260, Resource.SULFUR: 300},
            upkeep=25,
            health=1080,
            armor=0,
            attack=Attack(damage=80, accuracy=20),
            extra_attack=Attack(damage=2660, accuracy=10, ammo=5),
            size=5,
        ),
        Unit(
            name="mortar",
            line=Line.ARTILLERY,
            cost={Resource.WOOD: 300, Resource.SULFUR: 1250},
            upkeep=30,
            health=640,
            armor=0,
            attack=Attack(damage=200, accuracy=20),
            extra_attack=Attack(damage=5400, accuracy=10, ammo=3),
            size=5,
        ),
        # Варвары
        Unit(
            name="barbarian_club",
            line=Line.MELEE,
            cost={},
            upkeep=0,
            health=240,
            armor=20,
            attack=Attack(damage=100, accuracy=85),
            size=1,
        ),
        Unit(
            name="barbarian_axe",
            line=Line.MELEE,
            cost={},
            upkeep=0,
            health=1120,
            armor=20,
            attack=Attack(damage=360, accuracy=90),
            size=1,
        ),
        Unit(
            name="barbarian_steam_giant",
            line=Line.MELEE,
            cost={},
            upkeep=0,
            health=3680,
            armor=60,
            attack=Attack(damage=840, accuracy=80),
            size=3,
        ),
        Unit(
            name="barbarian_knife",
            line=Line.FLANK,
            cost={},
            upkeep=0,
            health=360,
            armor=0,
            attack=Attack(damage=200, accuracy=90),
            size=1,
        ),
        Unit(
            name="barbarian_axe_thrower",
            line=Line.LONG_RANGE,
            cost={},
            upkeep=0,
            health=320,
            armor=0,
            attack=Attack(damage=100, accuracy=60),
            extra_attack=Attack(damage=200, accuracy=30, ammo=7),
            size=1,
        ),
        Unit(
            name="barbarian_ram",
            line=Line.ARTILLERY,
            cost={},
            upkeep=0,
            health=1400,
            armor=20,
            attack=Attack(damage=200, accuracy=20),
            extra_attack=Attack(damage=2100, accuracy=20),
            size=5,
        ),
        Unit(
            name="barbarian_catapult",
            line=Line.ARTILLERY,
            cost={},
            upkeep=0,
            health=640,
            armor=0,
            attack=Attack(damage=200, accuracy=20),
            extra_attack=Attack(damage=5400, accuracy=20, ammo=5),
            size=5,
        ),
        Unit(
            name="barbarian_gyrocopter",
            line=Line.FIGHTER,
            cost={},
            upkeep=0,
            health=580,
            armor=0,
            attack=Attack(damage=340, accuracy=80),
            ammo=4,
            size=1,
        ),
        Unit(
            name="barbarian_bomber",
            line=Line.BOMBER,
            cost={},
            upkeep=0,
            health=800,
            armor=0,
            attack=Attack(damage=960, accuracy=20),
            ammo=2,
            size=2,
        ),
    )
}

ORDERS: dict[Line, tuple[str, ...]] = {
    Line.MELEE: (
        "phalanx", "steam_giant", "swordsman", "spearman", "shooter", "archer", "slinger",
        # Варвары
        "barbarian_club", "barbarian_axe", "barbarian_steam_giant", "barbarian_knife", "barbarian_axe_thrower"
    ),
    Line.FLANK: (
        "swordsman", "spearman",
        # Варвары
        "barbarian_knife"
    ),
    Line.LONG_RANGE: (
        "shooter", "archer", "slinger",
        # Варвары
        "barbarian_axe_thrower"
    ),
    Line.ARTILLERY: (
        "mortar", "catapult", "ram",
        # Варвары
        "barbarian_catapult", "barbarian_ram"
    ),
    Line.FIGHTER: (
        "gyrocopter",
        # Варвары
        "barbarian_gyrocopter"
    ),
    Line.BOMBER: (
        "bomber",
        # Варвары
        "barbarian_bomber"
    ),
}

CATALOG = Catalog(
    forces=Forces(units=UNITS, orders=ORDERS),
    battlefields=BATTLEFIELDS,
)
