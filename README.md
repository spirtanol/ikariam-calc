# Ikariam battle calc

Симулятор боя Ikariam. Стороны и поле описываются в YAML, на выходе YAML: ход боя по раундам, победитель, стоимость и содержание потерь. Отдельная команда считает стоимость и содержание состава, не запуская бой.

Это библиотека расчёта и тонкий CLI. Сервиса, базы и подбора состава нет. Один запуск — один бой.

Рабочий запуск — Docker и Make, Python 3.13 внутри образа.

## Подготовка

Нужны Docker и Docker Compose. В `.env` в корне репозитория задайте пользователя, от которого пишутся файлы в смонтированный каталог:

```
UID=1000
GID=1000
```

Первый `make battle` или `make cost` соберёт образ `ikariam-calc`.

## Команды

По умолчанию вход — `example.yml`, копия результата — `result.yml`. Тот же YAML печатается в stdout. Пути считаются от корня репозитория.

```bash
make battle
make cost
```

Свой файл и свой путь вывода:

```bash
make battle FILE=example.yml OUT=result.yml
make cost FILE=example.yml OUT=cost.yml
```

Оболочка в контейнере:

```bash
make shell
```

Внутри контейнера те же команды напрямую:

```bash
python -m app battle example.yml --output result.yml
python -m app cost example.yml --output cost.yml
```

`--output` необязателен. Без него результат только в stdout.

## Вход

Имена полей английские. `type` — `army` или `navy`. Под `attacker` и `defender` — имя юнита и количество, не меньше 1. Пустая сторона допустима.

Для боя обязателен `level`, целое от 1 до 5. Команда стоимости уровень не читает.

`example.yml`:

```yaml
defender:
  barbarian_club: 35
attacker:
  phalanx: 30
level: 1
type: army
```

Имена сухопутных юнитов — ключи `UNITS` в `src/app/defs/army.py`: `phalanx`, `steam_giant`, `spearman`, `swordsman`, `shooter`, `slinger`, `archer`, `gyrocopter`, `bomber`, `ram`, `catapult`, `mortar`, а также варвары `barbarian_club`, `barbarian_axe`, `barbarian_steam_giant`, `barbarian_knife`, `barbarian_axe_thrower`, `barbarian_ram`, `barbarian_catapult`, `barbarian_gyrocopter`, `barbarian_bomber`.

Имена кораблей — ключи `UNITS` в `src/app/defs/navy.py`: `flamethrower_ship`, `steam_ram_ship`, `ram_ship`, `ballista_ship`, `catapult_ship`, `mortar_ship`, `rocket_ship`, `submarine`, `steam_ship`, `carrier_ship`.

Неизвестное имя и количество меньше 1 — ошибка.

## Бой

`make battle` крутит раунды, пока не появится победитель, и печатает `winner`, список `rounds` и `totals`.

В раунде у каждой стороны:

- `field` — кто стоит на линиях до залпов этого раунда: `count`, `health` как доля от полного здоровья и, если у типа есть снаряжение, среднее `ammo`
- `losses` — потери за раунд
- `reserve` — кто не встал на поле
- `resources` и `upkeep` — цена этих потерь

В `totals` у каждой стороны только сумма цены потерь за весь бой: `resources` и `upkeep`. Ресурсы — `wood`, `wine`, `crystal`, `sulfur`. Золото туда не входит, содержание лежит в `upkeep`.

Фрагмент результата `example.yml`:

```yaml
winner: attacker
rounds:
- attacker:
    field:
      melee:
        phalanx:
          count: 30
          health: 1.0
    losses:
      phalanx: 2
    reserve: {}
    resources:
      wood: 80
      sulfur: 60
    upkeep: 6
  defender:
    field:
      melee:
        barbarian_club:
          count: 35
          health: 1.0
    losses:
      barbarian_club: 30
    reserve: {}
    resources: {}
    upkeep: 0
totals:
  attacker:
    resources:
      wood: 80
      sulfur: 60
    upkeep: 6
  defender:
    resources: {}
    upkeep: 0
```

`winner` — `attacker`, `defender` или `draw`. Ничья не останавливает бой: следующий раунд идёт с остатков. Сторону держат ближний бой, фланги, дальний бой и артиллерия. Одни истребители и бомбардировщики сторону не держат.

## Стоимость

`make cost` считает строительство и содержание обеих сторон по тому же файлу. Поле боя не нужно.

Для `example.yml`:

```yaml
attacker:
  resources:
    wood: 1200
    sulfur: 900
  upkeep: 90
defender:
  resources: {}
  upkeep: 0
```
