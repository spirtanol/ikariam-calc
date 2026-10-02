from enum import StrEnum


class Resource(StrEnum):
    """Ресурсы строительства войск. Мрамора нет. Золото сюда не входит."""

    WOOD = "wood"  # дерево
    WINE = "wine"  # вино
    CRYSTAL = "crystal"  # хрусталь
    SULFUR = "sulfur"  # сера
