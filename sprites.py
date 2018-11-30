import pyglet


atlas_img = pyglet.image.load('bomber16.png')
atlas_grid = pyglet.image.ImageGrid(atlas_img, 6, 6)
atlas = pyglet.image.TextureGrid(atlas_grid)

def sprite(atlas_col, atlas_row, size = None):
    sprite = {'sprite': atlas[atlas_col, atlas_row]}
    if size:
        sprite['bb_size'] = size
    return sprite


player = sprite(3, 0, size=(14, 14))
wall = sprite(5, 0, size=(14, 14))
weak_wall = sprite(5, 1, size=(14, 14))
bomb = sprite(5, 2)
explosion = sprite(3, 3)
flame_h = sprite(2, 1)
flame_v = sprite(3, 4)
bonus_bomb = sprite(2, 2)
bonus_flame = sprite(2, 3)
bonus_speed = sprite(2, 4)
trap = sprite(1, 2)
