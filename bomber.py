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

BB = namedtuple('BB', ['x', 'y', 'rx', 'ry'])
Vec2 = namedtuple('Vec2', ['x', 'y'])


class Obj:
    pass


class World:
    def __init__(self, center_x, center_y, level):
        self.objects = defaultdict(set)
        self.all_objects = set()

        self.center_x = center_x
        self.center_y = center_y
        self.origin_x = center_x - level['width'] * 8
        self.origin_y = center_y - level['height'] * 8

        self.create_level(level['objects'])

    def __init__(self, window):
        self.window = window


    def create_level(self, ):




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


def intersect(, b):
    dcx = b.x - a.x
    dcy = b.y - a.y

    penetration_x = abs(dcx) - a.rx - b.rx
    penetration_y = abs(dcy) - a.ry - b.ry
    if penetration_x > 0 or penetration_y > 0:
        return None

    return copysign(penetration_x, dcx), copysign(penetration_y, dcy)


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


def apply_time_rules(dt):


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




if __name__ == "__main__":
    wnd = pyglet.window.Window()
    game = game(steps=[update)
    .init()
    keys = pyglet.window.key.KeyStateHandler()
    wnd.push_handlers(keys)

    pyglet.clock.schedule_interval(update, 0.015)
    pyglet.app.run()


"""
    def amend_move(self, penetrations):
        keep_biggest_px = max if self.dx > 0 else min
        keep_biggest_py = max if self.dy > 0 else min

        correction_dx = 0.0
        correction_dy = 0.0

        penetrations_left = []

        for px, py in penetrations:
            if not is_penetration_caused_by_move(px, self.dx):
                dy_correction = keep_biggest_py(py, dy_correction)
                break

            if not is_penetration_caused_by_move(py, self.dy):
                dx_correction = keep_biggest_px(px, dx_correction)
                break

            penetrations_left.append((px, py))

        for px, py in penetrations_left:
            if px == py:
                dx_correction = keep_biggest_px(px, dx_correction)
                dy_correction = keep_biggest_py(py, dy_correction)
            elif px > py:
                dy_correction = keep_biggest_py(py, dy_correction)
            else:
                dx_correction = keep_biggest_px(px, dx_correction)

        self.x += correction_dx
        self.y += correction_dy

    def advance(self, dt):
        last_index = len(self.delayed) - 1
        for index, delayed_action in enumerate(reversed(self.delayed)):
            delayed_action['delay'] -= dt
            if delayed_action['delay'] <= 0:
                self.update_aspects(delayed_action['actions'])
                self.delayed.pop(last_index - index)

    def amend_move(self, penetrations):
        keep_biggest_px = max if self.dx > 0 else min
        keep_biggest_py = max if self.dy > 0 else min

        correction_dx = 0.0
        correction_dy = 0.0

        penetrations_left = []

        for px, py in penetrations:
            if not is_penetration_caused_by_move(px, self.dx):
                dy_correction = keep_biggest_py(py, dy_correction)
                break

            if not is_penetration_caused_by_move(py, self.dy):
                dx_correction = keep_biggest_px(px, dx_correction)
                break

            penetrations_left.append((px, py))

        for px, py in penetrations_left:
            if px == py:
                dx_correction = keep_biggest_px(px, dx_correction)
                dy_correction = keep_biggest_py(py, dy_correction)
            elif px > py:
                dy_correction = keep_biggest_py(py, dy_correction)
            else:
                dx_correction = keep_biggest_px(px, dx_correction)

        self.x += correction_dx
        self.y += correction_dy

    def advance(self, dt):
        last_index = len(self.delayed) - 1
        for index, delayed_action in enumerate(reversed(self.delayed)):
            delayed_action['delay'] -= dt
            if delayed_action['delay'] <= 0:
                self.update_aspects(delayed_action['actions'])
                self.delayed.pop(last_index - index)

def is_penetration_caused_by_move(p, m):
    if m < 0:  # negative move
        if p > 0:
            return False
        if p < m:
            return False
    else:  # positive move
        if p < 0:
            return False
        if p > m:
            return False
    return True




"""
