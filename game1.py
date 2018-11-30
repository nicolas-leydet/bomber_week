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


wnd = pyglet.window.Window()
keys = pyglet.window.key.KeyStateHandler()
wnd.push_handlers(keys)

mobs = pyglet.graphics.Batch()
statics = pyglet.graphics.Batch()

BB = namedtuple('BB', ['x', 'y', 'rx', 'ry'])


class Obj:
    pass


class Board:
    def __init__(self, center_x, center_y, board_w, board_h, objects):
        self.objects = defaultdict(set)
        self.all_objects = {}
        self.center_x = center_x
        self.center_y = center_y
        self.origin_x = center_x - board_w * 8
        self.origin_y = center_y - board_h * 8
        for x, y, obj in objects:
            self.create_on_board(x, y, obj)

    def create_on_board(self, cell_x, cell_y, obj):
        x = self.origin_x + cell_x * 16
        y = self.origin_y + cell_y * 16
        self.create(x, y, obj)

    def get_cell_coord(self, x, y):
        return (x - self.origin_x) // 16, (y - self.origin_y) // 16

    def create(self, x, y, obj):
        if obj.is_player or obj.is_monster:
            batch = mobs
        else:
            batch = statics
        obj.x = x
        obj.y = y
        obj._graphic = Sprite(batch=batch)
        self._update_graphic(obj)

        obj = Obj(x, y, batch=batch, **kwargs)
        for group in groups:
            self.objects[group].add(obj)
        self.objects['all'].add(obj)


    def remove(self, obj, reveal=True):
        if reveal and hasattr(obj, 'contains'):
            self.create(obj.x, obj.y, **obj.contains)

        if obj in self.objects['all']:
            if obj.graphic:
                obj.graphic.delete()

        for group in self.objects.values():
            group.discard(obj)

    def update(self, obj, **aspects):
        for aspect, value in aspects.items():
            setattr(obj, aspect, value)
        aspects = set(aspects)

        if {"x", "y"} & aspects:
            self._update_position()

        if obj.sprite_update_on & aspects:
            self._update_sprite()

        if "tags" in aspects:
            self._update_tags()

    def _update_tags(self, obj, tags):
        for group in self.objects.values():
            group.discard(obj)
        for tag in tags:
            self.objects[tag].add(obj)

    def _update_position(self, obj, x, y):


    def _update_sprite(self, obj):
        obj.



board = Board(wnd.width / 2, wnd.height / 2, **levels.parse_level('level1'))
player = next(iter(board.objects['player']))  # first elem of player set


def update_bombs(dt):
    to_remove = []
    for bomb in board.objects['bomb']:
        bomb.delay -= dt
        if bomb.delay <= 0:
            to_remove.append(bomb)
    for bomb in to_remove:
        board.remove(bomb)


# TODO: separate spawning points
def update_explosions(dt):
    to_remove = []
    for explosion in board.objects['explosion']:
        explosion.life -= dt
        explosion.delay -= dt
        if explosion.life <= 0:
            to_remove.append(explosion)
        if explosion.delay <= 0 and not hasattr(explosion, 'flame_created'):
            print('boom')
            explosion.flame_created = True
            x = explosion.x
            y = explosion.y
            w = explosion.graphic.width
            h = explosion.graphic.height
            base = {'power': explosion.power - 1, 'life': explosion.life}
            board.create(x - w, y, direction=(-1, 0), **levels.FLAME, **base)
            board.create(x + w, y, direction=(1, 0),  **levels.FLAME, **base)
            board.create(x, y - h, direction=(0, -1), **levels.FLAME, **base)
            board.create(x, y + h, direction=(0, 1), **levels.FLAME, **base)

    for explosion in to_remove:
        board.remove(explosion)


def update_flames(dt):
    to_remove = []
    to_create = []
    for flame in board.objects['flame']:
        flame.life -= dt
        flame.delay -= dt
        if flame.life <= 0:
            to_remove.append(flame)
        if flame.power == 0:
            continue
        if flame.delay <= 0 and not hasattr(flame, 'flame_created'):
            print('flame')
            flame.flame_created = True
            to_create.append({
                'x': flame.x + flame.graphic.width * flame.direction[0],
                'y': flame.y + flame.graphic.height * flame.direction[1],
                'power': flame.power - 1, 'direction': flame.direction,
                'life': flame.life, **levels.FLAME,
            })

    for flame in to_remove:
        board.remove(flame)

    for flame in to_create:
        board.create(**flame)


def update_mobs(dt):
    for monster in board.objects['monster']:
        monster.move(dt)
    player.move(dt)


def intersect(a, b):
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
        return

    x, y = board.get_cell_coord(player.x, player.y)

    for bomb in bombs:
        if x == bomb.cell_x and y == bomb.cell_y:
            return

    bomb = {
        **levels.BOMB,
        'cell_x': x,
        'cell_y': y,
        'contains': {
            **levels.EXPLOSION, 'power': player.flame
        },
    }
    board.create_on_board(x, y, bomb)


def move_player(dt):
    dir_x = keys[key.LEFT] * -1.0 + keys[key.RIGHT] * 1.0
    dir_y = keys[key.DOWN] * -1.0 + keys[key.UP] * 1.0

    if not dir_x and not dir_y:
        return

    if dir_x and dir_y:
        dir_x *= 0.7071
        dir_y *= 0.7071

    new_x = player.x + dir_x * dt * player.speed
    new_y = player.y + dir_y * dt * player.speed
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
    update_mobs(dt)
    update_flames(dt)
    update_explosions(dt)
    update_bombs(dt)


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


def update(dt):
    lay_bomb()
    move_player(dt)
    apply_time_rules(dt)
    manage_collisions()
    update_graphic_positions()
    draw_graphics()


if __name__ == "__main__":
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
