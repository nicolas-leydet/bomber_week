import pyglet


wnd = pyglet.window.Window()
keys = pyglet.window.key.KeyStateHandler()
wnd.push_handlers(keys)


def update(dt):
    if keys:
        print(dt, keys)

pyglet.clock.schedule_interval(update, 0.05)
pyglet.app.run()

