import pyglet

from __future__ import import annotations


game_window = pyglet.window.Window()


board: dict[Union[Tuple[int, int], Tuple[float, float]], Union[Wall, Player, Mob]]= {
    ( 1,  1): WeakWall(contains=BONUS_BOMB),
    ( 1,  2): WALL,
    ( 2,  3): WeakWall(contains=MOB_SPAWN),
    ( 3, 10): Player(),
    ( 5, 10): Mob(BALLON),
    ( 7,  5): WeakWall(contains=EXIT),
    ...
}


@dataclass
class World:



@dataclass
class Level:
    """ Definition of a level """
    pass


@dataclass
class Board:
    """ A level being played """
    objects: dict[
        Tuple[int, int],
        Union[Wall, Bonus, Exit, Explosive, Mob, Player, Fire]
    ]
    mobs: List[Tuple[int, int]]
    player: Tuple[int, int],
    bomb: dict[
        tuple[int, int],
        Fire

    ]


class GameObject:
    position
    bb
    direction
    velocity



class World:
    rules:








@dataclass
class Player:
    position: Tuple[float, float]
    max_bombs: int
    speed: int
    fire_size: int
    pass_wall: bool
    pass_bomb: bool
    detonator: bool
    bomb_left: int
    score: int
    sprite: SpriteMap


@dataclass
class Mob:
    position: Tuple[float, float]
    brain: Brain
    speed: int
    pass_wall: bool
    pass_bomb: bool
    sprite: SpriteMap


@dataclass
class Wall:
    position: Tuple[int, int]
    content: Union[Bonus, Exit, Mob]
    toughness: int


@dataclass
class SpriteMap:
    pass












def manage_input():
    pass



def update_positions():
    """
    dumb move without collision check
     * player
     * Mob using brain

    """
    pass

def update_collisions():

    """
    for each entity checked for collision
       collect entities in neighbour cell
       check distance

    player
        wall, explosive -> move back (except pass thru)
        enemy -> dead (except immunity)
        hazard -> dead (except immunity)

    hazard
        wall -> destroyed (if weak wall) -> Spawn
        mob -> destroyed
        explosive -> detonate
    """
    pass


def update_state():
    pass


def update_lifespan():
    pass


def update_graphics():
    pass


def draw():
    pass


"""
Mobile
  pos
  direction
  speed


Transient
  timeleft



"""

def sense(objs):
    pass


def age(states):
    pass


def spawn(states):
    pass


def move(mobs):
    pass


def calculate_colision():
    pass


def resolve_penetration():
    pass


def resolve_collision():
    pass



'''


Rules actions:
    * Attribute (aspect) add / remove / modify
    * Entity add / remove

Aging rules:
    * update all age attributes
    * trigger actions

Sensor rules:
    * check sensor collisions
    * trigger actions

Collision Rules = collision resolution
    * rule per shape type pair
    * trigger actions


Correction for forbidden moves ? (cancel)

Action Reversal in case of a object creation in a forbidden position
(alternative is checking for that before creation)


testing world
* character
* walls (collision with position correction)
* traps (collision -> death)
* enemies (moving trap) simple move
* character drop bomb (object creation)
* aging bomb (-> disappear)
* explosion (aging object)



attribute



spawn_point:
    spawn_content: [
        {type: bear, qty: 1, chance: 1}
        {type: wolf,  qty: 3, chance: 2}
        {type: rabbit, qty: INF, chance: 3}
    ]


@resolve("spawn_content")
def resolve_spawn_content(entity, world):
    pass


entity:
    position
    orientation

    sensors: [shapes]
    body: [shapes]



    targets: [
        {shape: circle(1), type: body},
        {shape: sector(10, -60, 60), type: vision}
        {shape: circle(3), type: earing}
    ]




@resolve_colision()



@resolve('destroyed')


@resolve('')

'''



if __name__ == '__main__':
    pyglet.app.run()


"""
circle rectangle intersect:
    // clamp(value, min, max) - limits value to the range min..max

    // Find the closest point to the circle within the rectangle
    float closestX = clamp(circle.X, rectangle.Left, rectangle.Right);
    float closestY = clamp(circle.Y, rectangle.Top, rectangle.Bottom);

    // Calculate the distance between the circle's center and this closest point
    float distanceX = circle.X - closestX;
    float distanceY = circle.Y - closestY;

    // If the distance is less than the circle's radius, an intersection occurs
    float distanceSquared = (distanceX * distanceX) + (distanceY * distanceY);
    return distanceSquared < (circle.Radius * circle.Radius);


bool intersects(CircleType circle, RectType rect)
{
    circleDistance.x = abs(circle.x - rect.x);
    circleDistance.y = abs(circle.y - rect.y);

    if (circleDistance.x > (rect.width/2 + circle.r)) { return false; }
    if (circleDistance.y > (rect.height/2 + circle.r)) { return false; }

    if (circleDistance.x <= (rect.width/2)) { return true; }
    if (circleDistance.y <= (rect.height/2)) { return true; }

    cornerDistance_sq = (circleDistance.x - rect.width/2)^2 +
                         (circleDistance.y - rect.height/2)^2;

    return (cornerDistance_sq <= (circle.r^2));
}

import math

def collision(rleft, rtop, width, height,   # rectangle definition
              center_x, center_y, radius):  # circle definition

    # complete boundbox of the rectangle
    rright, rbottom = rleft + width/2, rtop + height/2

    # bounding box of the circle
    cleft, ctop     = center_x-radius, center_y-radius
    cright, cbottom = center_x+radius, center_y+radius

    # trivial reject if bounding boxes do not intersect
    if rright < cleft or rleft > cright or rbottom < ctop or rtop > cbottom:
        return False  # no collision possible

    # check whether any point of rectangle is inside circle's radius
    for x in (rleft, rleft+width):
        for y in (rtop, rtop+height):
            # compare distance between circle's center point and each point of
            # the rectangle with the circle's radius
            if math.hypot(x-center_x, y-center_y) <= radius:
                return True  # collision detected

    # check if center of circle is inside rectangle
    if rleft <= center_x <= rright and rtop <= center_y <= rbottom:
        return True  # overlaid

    return False  # no collision detected


simple quadtree impl.

https://github.com/karimbahgat/Pyqtree/blob/master/pyqtree.py

"""
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
