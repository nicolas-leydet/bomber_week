import sprites


class Obj:
    pass


def create_object(*, sprite, tags=None, **aspects):
    obj = Obj()
    obj.sprite_update_on = []

    bb_height = aspects.pop('bb_height', sprites.HEIGHT)
    bb_width = aspects.pop('bb_width', sprites.WIDTH)
    obj.rx = bb_width / 2.0
    obj.ry = bb_height / 2.0

    for aspect, value in aspects.items():
        setattr(obj, aspect, value)

    for tag in getattr(obj, "tags", []):
        setattr(obj, f"is_{tag}", True)

    obj.sprite_update_on = set(obj.sprite_update_on)



PLAYER = create_object(
    **sprite.player,
    max_bomb=1,
    flame=1,
    speed=35,
    tags=['player', 'mob'],


    **sprites.player,
    'max_bomb': 1, 'flame': 1, 'speed': 25,
    'groups': ['player']
}
WALL = {**sprites.wall, 'fireproof': True, 'groups': ['obstruction']}
WEAK_WALL = {**sprites.weak_wall, 'groups': ['obstruction']}
TRAP = {**sprites.trap, 'groups': ['monster']}
EXPLOSION = {**sprites.explosion, 'power': 1, 'life': 1.0, 'delay': 0.1, 'groups': ['lethal', 'explosion']}
FLAME = {**sprites.explosion, 'delay': 0.1, 'groups': ['lethal', 'flame']}
BOMB = {**sprites.bomb, 'delay': 3.0, 'contains': EXPLOSION, 'groups': ['bomb', 'just_layed']}
BONUS_BOMB = {**sprites.bonus_bomb, 'bonus': ('max_bomb', 1), 'groups': ['bonus']}
BONUS_FLAME = {**sprites.bonus_flame, 'bonus': ('flame', 1), 'groups': ['bonus']}
BONUS_SPEED = {**sprites.bonus_speed, 'bonus': ('speed', 7), 'groups': ['bonus']}

translation = {
    'X': PLAYER,
    '#': WALL,
    '.': WEAK_WALL,
    'b': {**WEAK_WALL, 'contains': BONUS_BOMB},
    'f': {**WEAK_WALL, 'contains': BONUS_FLAME},
    's': {**WEAK_WALL, 'contains': BONUS_SPEED},
}

levels = {
    'level1': """
        #########################
        #X   b#. .#. b#. .#. .#.#
        #.b.#.b.#...#.s.#.b.#...#
        ##f .#. .#f .#. .#. .#. #
        ###.###.###.###e###.###.#
        ##. .#. .#. .#. .#. .#. #
        #..#.b.#.s.#..f#...#..s##
        ## # # # # # # # # # # ##
        #.s#...#..b#...#.b.#...##
        #########################
    """
}


def parse_level(level_name):
    objects = []
    rows = levels[level_name].strip().split('\n')
    h = len(rows)
    w = len(rows[0].strip())
    for y, row in enumerate(reversed(rows)):
        for x, cell in enumerate(row.strip()):
            obj = translation.get(cell)
            if obj:
                objects.append((x, y, translation[cell]))

    return {'board_w': w, 'board_h': h, 'objects': objects}
