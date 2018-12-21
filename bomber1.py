import pyglet
from math import copysign
from collections import defaultdict, namedtuple
from pyglet.window import key
from pyglet.sprite import Sprite
import levels


"""
TODO:
    X Remove cancel_move: check player collision when moving
    * Add exit -> next level
    * Add Kill Player function to terminate level (use end_animation_event)

"""


mobs = pyglet.graphics.Batch()
statics = pyglet.graphics.Batch()

BB = namedtuple('BB', ['position', 'radius'])


class Vec2:
    __slots__ = ['x', 'y']

    def __init__(self, x: float, y: float):
        self.x, self.y = x, y

    def apply(self, func):
        return Vec2(func(self.x), func(self.y))

    def abs(self):
        return Vec2(abs(self.x), abs(self.y))

    def copysign(self, signs):
        return Vec2(copysign(self.x, signs.x), copysign(self.y, signs.y))

    def __add__(self, other: Vec2):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, other: Vec2):
        return Vec2(self.x * other.x, self.y * other.y)

    def __truediv__(self, othe: Vec2):
        return Vec2(self.x / other.y, self.y / other.x)

    def __floordiv__(self, other: Vec2):
        return Vec2(self.x // other.y, self.y // other.x)

    def __repr__(self):
        return str((self.x, self.y))


class Grid:
    def __init__(self, size: Vec2, center: Vec2, cell_size: vec2 = (16, 16)):
        self.origin = center - (size * cell_size / 2)
        self.size = size
        self.cell_size = cell_size

    def get_cell(self, coord: Vec2):
        return coord - self.origin // self.cell_size

    def get_position(self, cell: Vec2):
        return self.origin + cell * self.cell_size


class World:
    def __init__(self, **fragments):
        self.window = pyglet.window.Window()
        self.clock = pyglet.clock
        self.entities = set()
        self.entities_by_trait = defaultdict(set)

    def add_fragments(**fragments):
        pass

    def remove_fragments(*fragments):
        pass

    def add_entities(self, entities):
        pass

    def step(self, dt):
        for layer in self.layers:

    def delay(self, delay, func, *args, **kwargs):
        self.clock.schedule_once(func, delay, *args, **kwargs)


    def create_level(self, objects):
        for col, row, obj in objects:
            x, y = self.get_xy_coord(col, row)
            obj.move(x, y)
            self.register_obj(obj)

    def get_cell(self, x, y):
        return (x - self.origin_x) // 16, (y - self.origin_y) // 16

    def get_coord(self, col, row):
        return self.origin_x + col * 16, self.origin_y + row * 16

    def add(self, obj):
        for tag in obj.tags:
            self.objects[tag].add(obj)
        self.all_objects.add(obj)

    def remove(self, obj, reveal=True):
        if reveal and hasattr(obj, 'contains'):
            self.create(obj.x, obj.y, obj.contains)

        if obj in self.all_objects:
            obj.destroy()
            self.all_objects.remove(obj)

        for group in self.objects.values():
            group.discard(obj)

    def update(self, obj):
        for group in self.objects.values():
            group.discard(obj)
        for tag in obj.tags:
            self.objects[tag].add(obj)



keys = pyglet.window.key.KeyStateHandler()
wnd.push_handlers(keys)




board = Board(wnd.width / 2, wnd.height / 2, levels.parse_level('level1'))
player = next(iter(board.objects['player']))  # first elem of player set


def explose(x, y, power):
    board.add(Explosion(x=x, y=y))
    delay(0.1, create_flame, x, y, direction=(-1, 0), power - 1)
    delay(0.1, create_flame, x, y, direction=(+1, 0), power - 1)
    delay(0.1, create_flame, x, y, direction=(0, -1), power - 1)
    delay(0.1, create_flame, x, y, direction=(0, +1), power - 1)

def create_flame(x, y, dir, power):
    x +=  dir[0] * 16
    y +=  dir[1] * 16
    board.add(Flame(x=x, y=y, direction=direction))
    if power > 0:
        delay(0.1, create_flame, x, y, direction=(-1, 0), power - 1)


def update_mobs(dt):
    for monster in board.objects['monster']:
        monster.move(dt)
    player.move(dt)


def intersect(a, b):
    center_delta = b.position - a.position
    penetration = center_delta.apply(abs) - a.radius - b.radius
    if penetration.x > 0 or penetration.y > 0:
        return None

    return penetration.copysign(center_delta)


def lay_bomb():
    if not keys[key.A]:
        return

    bombs = board.objects['bomb']
    nb_bombs = len(bombs)

    if nb_bombs >= player.max_bomb:
        return  # Max bomb reached

    col, row = board.get_cell_coord(player.x, player.y)

    for bomb in bombs:
        if col == bomb.col and row == bomb.row:
            return  # Bomb already layed

    x, y = board.get_xy_coord(col, row)
    world.add(Bomb(x=x, y=y, col=col, row=row))
    bomb.when_animation_ends(explode, bomb, player.flame)


WALK_SPRITE_GIVEN_DIRECTION = {
    (0, 1): "player.up.walk",
    (0, -1): "player.down.walk",
    (1, 0): "player.right.walk",
    (-1, 0): "player.left.walk",
    (1, 1): "player.right.walk",
    (-1, 1): "player.left.walk",
    (1, -1): "player.right.walk",
    (-1, -1): "player.left.walk",
}


def flame_sprite(obj):
    obj.direction



def update_player_sprite(direction):
    if player.direction == direction:
        return
    player.direction = direction

    if direction == (0, 0):
        new_sprite = player.sprite.replace('walk', 'static')
    else:
        new_sprite = WALK_SPRITE_GIVEN_DIRECTION[direction]

    player.update_sprite(new_sprite)


def move_player(world, dt):
    direction = Vec2(
        keys[key.LEFT] * -1.0 + keys[key.RIGHT] * 1.0
        keys[key.DOWN] * -1.0 + keys[key.UP] * 1.0
    )

    if direction == (0.0, 0.0):
        return

    if direction.x and direction.y:
        direction.x *= 0.7071
        direction.y *= 0.7071

    new_x = player.position.x + direction.x * dt * player.speed
    new_y = player.position.y + direction.y * dt * player.speed
    bb = BB(new_x, new_y, player.rx, player.ry)

    for obstruction in board.objects['obstruction']:
        if intersect(bb, obstruction):
            return

    player.x = new_x
    player.y = new_y
    player.graphic.update(
        new_x - player.graphic.width / 2,
        new_y - player.graphic.height / 2,
    )

    # Manage bomb the player just dropped
    just_layed = next(iter(board.objects['just_layed']), None)
    if just_layed and not intersect(player, just_layed):
        board.update_groups(just_layed, ['bomb', 'obstruction'])



def manage_collisions():
    obstructions = board.objects['obstruction']
    monsters = board.objects['monster']
    lethals = board.objects['lethal']
    bonuses = board.objects['bonus']

    to_remove = []

    # Player's collisions
    for monster in monsters:
        if intersect(player, monster):
            print('ouch monster')
            # board.remove(player)

    for bonus in bonuses:
        if intersect(player, bonus):
            aspect, increment = bonus.bonus
            setattr(player, aspect, getattr(player, aspect) + increment)
            to_remove.append(bonus)

    for lethal in lethals:
        if intersect(player, lethal):
            print('ouch flame')
            # board.remove(player)

    # generic mob collision
    for monster in monsters:
        for lethal in lethals:
            if intersect(monster, lethal):
                to_remove.append(monster)

    # Wall/Bomb destruction
    for obstruction in obstructions:
        for lethal in lethals:
            if intersect(obstruction, lethal):
                if not hasattr(obstruction, 'fireproof'):
                    to_remove.append(obstruction)
                to_remove.append(lethal)

    for obj in to_remove:
        board.remove(obj)


def update_graphic_positions():
    for monster in board.objects['monster']:
        monster.update_graphic_position()
    player.update_graphic_position()


def draw_graphics():
    wnd.clear()
    mobs.draw()
    statics.draw()


class BomberGame(Game):

    def step(self, dt):
        lay_bomb()
        move_player(dt)
        update_mobs(dt)
        update_flames(dt)
        update_explosions(dt)
        update_bombs(dt)
        manage_collisions()
        update_graphic_positions()
        draw_graphics()


class Fragment:
    def initialize(self):
        pass

    def get_batches(self):
        pass

    def update(self, dt):
        pass

    def draw(self, dt):
        pass

    def destroy(self, dt):
        pass



def


class SceneManager:
    def __init__(self):
        self.world = None

    def slash(self):
        pass

    def menu(self):
        pass

    def level(self, level):
        pass


class Game:
    def __init__(self):
        self.wnd = pyglet.window.Window()
        self.entities = defaultdict(set)
        self.framents = {}
        self.step_fragment = []

    def add_fragment(name, fragment, before=None):
        setattr(self, name, fragment)
        if hasattr('step', fragment):
            self.step_fragment.append(fragment.step)



    def add_entity(self, entity, groups):
        for group in groups:
            self.entities[group].add(entity)
        self.entities[...].add(entity)

    def remove_entity(self, entity):
        for group in self.entities.values():
            group.discard(obj)

    def update_entity(self, entity, groups):
        for group in self.objects.values():
            group.discard(obj)
        for tag in obj.tags:
            self.objects[tag].add(obj)

    def switch_mode(self, systems):
        pass

    def run(self, ):
        pass



class Game():
    def __init__(self):

    def step(self, dt):
        pass



class Bomberman(Game):
    def configure(self):
        pass

    def step(self, dt):
        pass



if __name__ == "__main__":
    Bombermam().run()
