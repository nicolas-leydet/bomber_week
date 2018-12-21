import pyglet
from pyglet.image import Animation, ImageGrid, TextureGrid, load as load_image
from dataclasses import dataclass


class WrongGridMappingError:
    pass


@dataclass
class Img:
    name: str


@dataclass
class Anim:
    name: str
    nb_frame: int
    period: float
    loop: bool = True


@dataclass
class Skip:
    nb_skip: int


mobs = pyglet.graphics.Batch()
statics = pyglet.graphics.Batch()


def load_sprites(filename, row, col, grid_mapping):
    grid = TextureGrid(ImageGrid(load_image(filename), row, col))
    sprites = {}
    index = 0

    for item in grid_mapping:
        if isinstance(item, Img):
            grid_index = get_grid_index(index, row, col)
            sprites[item.name] = grid[grid_index]
            index += 1
        elif isinstance(item, Anim):
            sprites[item.name] = Animation.from_image_sequence(
                [
                    grid[get_grid_index(index + offset, row, col)]
                    for offset in range(item.nb_frame)
                ],
                item.period,
                item.loop,
            )
            index += item.nb_frame
        elif isinstance(item, Skip):
            index += item.skip_nb
        else:
            raise WrongGridMappingError(item)

    return sprites


def get_grid_index(index, row, col):
    x = index // col
    y = index - x * col
    return (row - y) * col + x


sprite_repo = load_sprites('bomber.py', 4, 14, [
    Img('wall.strong'), Img('weak.wall'), Skip(2),
    Anim('bomb', 10, 0.1, False), Skip(2),
    Img('player.down.static'), Anim('player.down.walk', 2, 0.2), Skip(),
    Img('player.up.static'), Anim('player.up.walk', 2, 0.2), Skip(),
    Img('player.right.static'), Anim('player.right.walk', 2, 0.2), Skip(),
    Img('player.left.static'), Anim('player.left.walk', 2, 0.2), Skip(),
    Anim('explosion', 2, 0.2, False), Img('flame.v'), Img('flame.h'),
    Img('flame.down'), Img('flame.up'), Img('flame.left'), Img('flame.right'),
    Img('bonus.bomb'), Img('bonus.flame'), Img('bonus.speed'), Skip(''),
    Img('exit'),
])


class Obj:
    def __init__(self, **aspects):
        self.aspects = aspects

    def clone(self, **aspects_override):
        return Obj(**self.aspects, **aspects_override)

    def __call__(self, **aspects_override):
        return _Obj(**self.aspects, **aspects_override)


class _Obj:
    def __init__(self, **aspects):
        self.tags = []
        aspects.pop()
        for aspect, value in aspects.items():
            setattr(self, aspect, value)

        if getattr(self, "sprite", None):
            self.create_graphic()
            self.update_position()

    def create_graphic(self):
        is_mobile = 'player' in self.tags or 'monster' in self.is_monster
        batch = mobs if is_mobile else statics

        self._graphic = pyglet.sprite.Sprite(
            sprite_repo[self.sprite], batch=batch
        )
        self.update_bb()

    def update_sprite(self, sprite):
        self.sprite = sprite
        self._graphic.image = sprite_repo[sprite]
        self.update_bb()

    def update_bb(self):
        self.height = self._graphic.height
        self.width = self._graphic.width
        bb_width, bb_height = getattr(
            self, 'bb', (self.width, self.height)
        )
        self.rx = bb_width / 2.0
        self.ry = bb_height / 2.0

    def move(self, x, y):
        self.x = x
        self.y = y
        graphic_x = x - self.width / 2
        graphic_y = y - self.height / 2
        self._graphic.update(x=graphic_x, y=graphic_y)

    def destroy(self):
        self._graphic.delete()



class Trait:
    def __init__(self, name, selectable, depends_on, attributes):
        self.name = name
        self.selectable = selectable
        self.depends_on = depends_on
        self.attributes = attributes

    def __call__(self, **attributes):
        return Trait(self.name, self.selectable, self.depends_on, attributes)


def update_sprite(world, dt):
    for entity in world.get_entities_with(Sprite):
        new_sprite = entity.get_sprite()
        if entity.graphic.image != new_sprite:
            entity.graphic.image = sprite


def lay_bomb(world, dt):
    bombs = world.get_entities_with(Explosive)
    nb_bombs = len(bombs)

    for entity in world.get_entities_with(BombLayer):

        if nb_bombs >= entity.max_bomb:
            continue  # Max bomb reached

        cell = world.get_cell(entity.position)

    for bomb in bombs:
        if bomb.cell == cell:
            continue  # Bomb already layed

    position = world.get_coord(cell)
    new_bomb = Bomb(position=position, cell=cell)
    world.add(new_bomb)
    world.delay(4.0, explode, new_bomb)


def explose(world, bomb):
    world.add(Explosion(position=bomb.position))
    world.remove(bomb)
    world.delay(0.1, create_flame, bomb.position, direction=(-1, 0), power - 1)
    world.delay(0.1, create_flame, bomb.position, direction=(+1, 0), power - 1)
    world.delay(0.1, create_flame, bomb.position, direction=(0, -1), power - 1)
    world.delay(0.1, create_flame, bomb.position, direction=(0, +1), power - 1)


def create_flame(world, origin, direction, power):
    position = origin[0] + direction[0] * 16, origin[1] + direction[1] * 16
    world.add(Flame(position, direction=direction))
    if power > 0:
        delay(0.1, create_flame, position, direction, power - 1)


class ShapeType(Enum):
    CIRCLE = 1
    RECT = 2


def trait(
        cls_or_name=None, *,
        name: str = None,
        selectable: bool = True,
        depends_on: List[Trait] = None):
    if isinstance(cls_or_name, str):  # Name
        return None
    elif isinstance(cls_or_name, type):  # Class
        return make_trait(cls_or_name)


# Traits
@trait
class Position:
    position: Vec2 = Vec2(0.0, 0.0)
    cell: Optional[Vec2] = None


@trait(depend_on=[Position])
class Mobile:
    direction: Vec2 = Vec2(0.0, 0.0)
    speed: int = 32


@trait
class Collidable:
    shape: ShapeType = ShapeType.RECT
    radius: Vec2 = Vec2(16, 16)


@trait
class BombLayer:
    max_bomb: int = 1
    bomb_power: int = 1


@trait(name="drawable", depends_on=[Position])
class Sprite:
    ephemeral: bool = False

    def finalize(self, entity):
        entity.graphic = pyglet.Sprite(entity.get_sprite(), entity.position
                                       ephemeral=ephemeral)




@trait
class Explosive:
    explosion_power: int


@trait
class flame:
    explosion_power: int


Obstruction = trait("obstruction")
Fireproof = trait("fireproof")


# Entity Types
Player = Entity(position, movement, player_sprite, bomb_layer)
StrongWall = Entity()
StupidMonster = Entity(
    position, movement(speed=25),
    sprite(monster_sprite('stupid')),
)


class Entity:
    def __init__(self, **overrides):
        attributes = {}
        for trait in self.traits:
            attributes.update(trait.attributes)
        self.__dict__.update(attributes)
        self.__dict__.update(overrides)
        for trait in self.traits:
            trait.finalize(self)


class Player(Entity):
    traits = [Position, Mobile, Sprite, BombLayer, Collidable, Controlled]
    get_sprite =


class Wall(Entity):
    traits = [Position, StaticSprite('wall.weak'), Collidable, Obstruction]


class StrongWall(Entity):
    traits = [Position, StaticSprite('wall.strong'), Collidable, Obstruction, Fireproof]


class Controller:




class BomberMan(Entity):



StrongWall = Obj(sprite='wall.strong', fireproof=True, tags=['obstruction'])
WeakWall = Obj(sprite="wall.weak", tags=['obstruction'])

Explosion = Obj(sprite="explosion", delay=0.1, tags=['lethal', 'explosion'])
Flame = Obj(sprite="flame", delay=0.1, tags=['lethal', 'flame'])
Bomb = Obj(sprite="bomb", tags=['bomb', 'just_layed'])

BonusBomb = Obj(sprite="bonus.bomb", bonus=('max_bomb', 1), tags=['bonus'])
BonusFlame = Obj(sprite="bonus.flame", bonus=('flame', 1), tags=['bonus'])
BonusSpeed = Obj(sprite="bonus.speed", bonus=('speed', 7), tags=['bonus'])

Exit = Obj(sprite="exit", tag=['exit'])

translation = {
    'X': Player,
    '#': StrongWall,
    '.': WeakWall,
    'b': WeakWall.clone(contains=BonusBomb),
    'f': WeakWall.clone(contains=BonusFlame),
    's': WeakWall.clone(contains=BonusSpeed),
    'e': WeakWall.clone(contains=Exit),

    'B': BonusBomb,
    'F': BonusFlame,
    'S': BonusSpeed,

    '1': WeakWall,
    '2': WeakWall,
    '3': WeakWall,
}

levels = {
    'level1': """
        ################
        #X   ..1...  .1#
        ####.b####f.####
        #  .1..  s...  #
        #.f####..####b.#
        #  s...  ..1.  #
        ####..####..####
        #..  1.e..1  .1#
        ################
    """,
    'level10': """
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
        for x, char in enumerate(row.strip()):
            obj = translation.get(char)
            if obj:
                objects.append((x, y, char))

    return {'board_w': w, 'board_h': h, 'objects': objects}
