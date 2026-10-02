class AccuracyBuffer:
    """Накопитель точности одной стороны. Юнита не выбирает и урон не считает."""

    def __init__(self) -> None:
        self._value = 0

    def strike(self, accuracy: int) -> bool:
        """True — цель из уже повреждённых. False — цель любая."""
        if not isinstance(accuracy, int) or isinstance(accuracy, bool) or not 0 <= accuracy <= 100:
            raise ValueError(f"accuracy must be an integer from 0 to 100: {accuracy}")
        self._value += accuracy
        if self._value < 100:
            return False
        self._value -= 100
        return True
