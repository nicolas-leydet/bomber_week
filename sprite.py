@dataclass
class Frame:
    __slots__ = 'image', 'duration', 'is_loop', 'is_still'

    image: Optional[Image]
    duration: float
    loop: bool = False
    has_looped: bool = False


class Animation:
    def __init__(self, frames):
        self.frames = frames
        self.current_frame = Frame(None, 0)
        self.start_animation()

    def start_animation(self):
        self._iter_frame = iter(self.frames)

    def next_frame(self, dt):
        prev_frame = self.current_frame
        next_frame = next(self._iter_frame, None)
        if not next_frame:
            return None

        if next_frame.loop:
            self.start_animation()

        duration = (
            -1 if next_frame.duration == -1
            else next_frame.duration + prev_frame.duration - dt
        )

        self.current_frame = Frame(
            image=next_frame.image,
            duration=duration,
            has_looped=prev_frame.loop,
        )

        return self.current_frame


class Sprite(pyglet.Sprite):

    def __init__(self,
                 img, x=0, y=0,
                 blend_src=GL_SRC_ALPHA,
                 blend_dest=GL_ONE_MINUS_SRC_ALPHA,
                 batch=None,
                 group=None,
                 usage='dynamic',
                 subpixel=False):

        self._x = x
        self._y = y
        self._batch = batch
        self._group = SpriteGroup(self._texture, blend_src, blend_dest, group)
        self._usage = usage
        self._subpixel = subpixel

        self.image = img

    def _animate(self, dt=0):
        frame = self._animation.next_frame(dt)
        if frame == None:
            self.dispatch_event("on_animation_end")

        frame.image.get_texture()

        if frame.duration == -1:
            return

        if frame.has_looped():
            self.dispatch_event("on_animation_loop")

        clock.schedule_once(self._animate, frame.duration)

    @image.setter
    def image(self, image):
        if self._animation is not None:
            clock.unschedule(self._animate)
            self._animation = None

        if isinstance(img, image.Animation):
            self._animation = animation
            self._animate()
        else:
            self._set_texture(img.get_texture())

        self._update_position()

    def __del__(self):
        try:
            if self._vertex_list is not None:
                self._vertex_list.delete()
        except:
            pass

    def delete(self):
        """Force immediate removal of the sprite from video memory.

        This is often necessary when using batches, as the Python garbage
        collector will not necessarily call the finalizer as soon as the
        sprite is garbage.
        """
        if self._animation:
            clock.unschedule(self._animate)
        self._vertex_list.delete()
        self._vertex_list = None
        self._texture = None

        # Easy way to break circular reference, speeds up GC
        self._group = None

    def _animate(self, dt):
        self._frame_index += 1
        if self._frame_index >= len(self._animation.frames):
            self._frame_index = 0
            self.dispatch_event('on_animation_end')
            if self._vertex_list is None:
                return  # Deleted in event handler.

        frame = self._animation.frames[self._frame_index]
        self._set_texture(frame.image.get_texture())

        if frame.duration is not None:
            duration = frame.duration - (self._next_dt - dt)
            duration = min(max(0, duration), frame.duration)
            clock.schedule_once(self._animate, duration)
            self._next_dt = duration
        else:
            self.dispatch_event('on_animation_end')

    @property
    def batch(self):
        """Graphics batch.

        The sprite can be migrated from one batch to another, or removed from
        its batch (for individual drawing).  Note that this can be an expensive
        operation.

        :type: :py:class:`pyglet.graphics.Batch`
        """
        return self._batch

    @batch.setter
    def batch(self, batch):
        if self._batch == batch:
            return

        if batch is not None and self._batch is not None:
            self._batch.migrate(self._vertex_list, GL_QUADS, self._group, batch)
            self._batch = batch
        else:
            self._vertex_list.delete()
            self._batch = batch
            self._create_vertex_list()

    @property
    def group(self):
        """Parent graphics group.

        The sprite can change its rendering group, however this can be an
        expensive operation.

        :type: :py:class:`pyglet.graphics.Group`
        """
        return self._group.parent

    @group.setter
    def group(self, group):
        if self._group.parent == group:
            return
        self._group = SpriteGroup(self._texture,
                                  self._group.blend_src,
                                  self._group.blend_dest,
                                  group)
        if self._batch is not None:
            self._batch.migrate(self._vertex_list, GL_QUADS, self._group,
                                self._batch)

    @property
    def image(self):
        """Image or animation to display.

        :type: :py:class:`~pyglet.image.AbstractImage` or
               :py:class:`~pyglet.image.Animation`
        """
        if self._animation:
            return self._animation
        return self._texture

    def _set_texture(self, texture):
        if texture.id is not self._texture.id:
            self._group = SpriteGroup(texture,
                                      self._group.blend_src,
                                      self._group.blend_dest,
                                      self._group.parent)
            if self._batch is None:
                self._vertex_list.tex_coords[:] = texture.tex_coords
            else:
                self._vertex_list.delete()
                self._texture = texture
                self._create_vertex_list()
        else:
            self._vertex_list.tex_coords[:] = texture.tex_coords
        self._texture = texture

    def _create_vertex_list(self):
        if self._subpixel:
            vertex_format = 'v2f/%s' % self._usage
        else:
            vertex_format = 'v2i/%s' % self._usage
        if self._batch is None:
            self._vertex_list = graphics.vertex_list(
                4, vertex_format, 'c4B', ('t3f', self._texture.tex_coords))
        else:
            self._vertex_list = self._batch.add(
                4, GL_QUADS, self._group, vertex_format, 'c4B', ('t3f', self._texture.tex_coords))
        self._update_position()
        self._update_color()

    def _update_position(self):
        img = self._texture
        scale_x = self._scale * self._scale_x
        scale_y = self._scale * self._scale_y
        if not self._visible:
            vertices = (0, 0, 0, 0, 0, 0, 0, 0)
        elif self._rotation:
            x1 = -img.anchor_x * scale_x
            y1 = -img.anchor_y * scale_y
            x2 = x1 + img.width * scale_x
            y2 = y1 + img.height * scale_y
            x = self._x
            y = self._y

            r = -math.radians(self._rotation)
            cr = math.cos(r)
            sr = math.sin(r)
            ax = x1 * cr - y1 * sr + x
            ay = x1 * sr + y1 * cr + y
            bx = x2 * cr - y1 * sr + x
            by = x2 * sr + y1 * cr + y
            cx = x2 * cr - y2 * sr + x
            cy = x2 * sr + y2 * cr + y
            dx = x1 * cr - y2 * sr + x
            dy = x1 * sr + y2 * cr + y
            vertices = (ax, ay, bx, by, cx, cy, dx, dy)
        elif scale_x != 1.0 or scale_y != 1.0:
            x1 = self._x - img.anchor_x * scale_x
            y1 = self._y - img.anchor_y * scale_y
            x2 = x1 + img.width * scale_x
            y2 = y1 + img.height * scale_y
            vertices = (x1, y1, x2, y1, x2, y2, x1, y2)
        else:
            x1 = self._x - img.anchor_x
            y1 = self._y - img.anchor_y
            x2 = x1 + img.width
            y2 = y1 + img.height
            vertices = (x1, y1, x2, y1, x2, y2, x1, y2)
        if not self._subpixel:
            vertices = (int(vertices[0]), int(vertices[1]),
                        int(vertices[2]), int(vertices[3]),
                        int(vertices[4]), int(vertices[5]),
                        int(vertices[6]), int(vertices[7]))
        self._vertex_list.vertices[:] = vertices

    def _update_color(self):
        r, g, b = self._rgb
        self._vertex_list.colors[:] = [r, g, b, int(self._opacity)] * 4

    @property
    def position(self):
        """The (x, y) coordinates of the sprite, as a tuple.

        :Parameters:
            `x` : int
                X coordinate of the sprite.
            `y` : int
                Y coordinate of the sprite.
        """
        return self._x, self._y

    @position.setter
    def position(self, pos):
        self._x, self._y = pos
        self._update_position()

    @property
    def x(self):
        """X coordinate of the sprite.

        :type: int
        """
        return self._x

    @x.setter
    def x(self, x):
        self._x = x
        self._update_position()

    @property
    def y(self):
        """Y coordinate of the sprite.

        :type: int
        """
        return self._y

    @y.setter
    def y(self, y):
        self._y = y
        self._update_position()

    @property
    def rotation(self):
        """Clockwise rotation of the sprite, in degrees.

        The sprite image will be rotated about its image's (anchor_x, anchor_y)
        position.

        :type: float
        """
        return self._rotation

    @rotation.setter
    def rotation(self, rotation):
        self._rotation = rotation
        self._update_position()

    @property
    def scale(self):
        """Base Scaling factor.

        A scaling factor of 1 (the default) has no effect.  A scale of 2 will
        draw the sprite at twice the native size of its image.

        :type: float
        """
        return self._scale

    @scale.setter
    def scale(self, scale):
        self._scale = scale
        self._update_position()

    @property
    def scale_x(self):
        """Horizontal scaling factor.

         A scaling factor of 1 (the default) has no effect.  A scale of 2 will
         draw the sprite at twice the native width of its image.

        :type: float
        """
        return self._scale_x

    @scale_x.setter
    def scale_x(self, scale_x):
        self._scale_x = scale_x
        self._update_position()

    @property
    def scale_y(self):
        """Vertical scaling factor.

         A scaling factor of 1 (the default) has no effect.  A scale of 2 will
         draw the sprite at twice the native height of its image.

        :type: float
        """
        return self._scale_y

    @scale_y.setter
    def scale_y(self, scale_y):
        self._scale_y = scale_y
        self._update_position()

    def update(self, x=None, y=None, rotation=None, scale=None, scale_x=None, scale_y=None):
        """Simultaneously change the position, rotation or scale.

        This method is provided for performance. In cases where
        multiple Sprite attributes need to be updated at the same
        time, it is more efficent to update them together using
        the update method, rather than modifying them one by one.

        :Parameters:
            `x` : int
                X coordinate of the sprite.
            `y` : int
                Y coordinate of the sprite.
            `rotation` : float
                Clockwise rotation of the sprite, in degrees.
            `scale` : float
                Scaling factor.
            `scale_x` : float
                Horizontal scaling factor.
            `scale_y` : float
                Vertical scaling factor.
        """
        if x is not None:
            self._x = x
        if y is not None:
            self._y = y
        if rotation is not None:
            self._rotation = rotation
        if scale is not None:
            self._scale = scale
        if scale_x is not None:
            self._scale_x = scale_x
        if scale_y is not None:
            self._scale_y = scale_y
        self._update_position()

    @property
    def width(self):
        """Scaled width of the sprite.

        Read-only.  Invariant under rotation.

        :type: int
        """
        if self._subpixel:
            return self._texture.width * abs(self._scale_x) * abs(self._scale)
        else:
            return int(self._texture.width * abs(self._scale_x) * abs(self._scale))

    @property
    def height(self):
        """Scaled height of the sprite.

        Read-only.  Invariant under rotation.

        :type: int
        """
        if self._subpixel:
            return self._texture.height * abs(self._scale_y) * abs(self._scale)
        else:
            return int(self._texture.height * abs(self._scale_y) * abs(self._scale))

    @property
    def opacity(self):
        """Blend opacity.

        This property sets the alpha component of the colour of the sprite's
        vertices.  With the default blend mode (see the constructor), this
        allows the sprite to be drawn with fractional opacity, blending with the
        background.

        An opacity of 255 (the default) has no effect.  An opacity of 128 will
        make the sprite appear translucent.

        :type: int
        """
        return self._opacity

    @opacity.setter
    def opacity(self, opacity):
        self._opacity = opacity
        self._update_color()

    @property
    def color(self):
        """Blend color.

        This property sets the color of the sprite's vertices. This allows the
        sprite to be drawn with a color tint.

        The color is specified as an RGB tuple of integers '(red, green, blue)'.
        Each color component must be in the range 0 (dark) to 255 (saturated).

        :type: (int, int, int)
        """
        return self._rgb

    @color.setter
    def color(self, rgb):
        self._rgb = list(map(int, rgb))
        self._update_color()

    @property
    def visible(self):
        """True if the sprite will be drawn.

        :type: bool
        """
        return self._visible

    @visible.setter
    def visible(self, visible):
        self._visible = visible
        self._update_position()

    def draw(self):
        """Draw the sprite at its current position.

        See the module documentation for hints on drawing multiple sprites
        efficiently.
        """
        self._group.set_state_recursive()
        self._vertex_list.draw(GL_QUADS)
        self._group.unset_state_recursive()

    if _is_epydoc:
        def on_animation_end(self):
            """The sprite animation reached the final frame.

            The event is triggered only if the sprite has an animation, not an
            image.  For looping animations, the event is triggered each time
            the animation loops.

            :event:
            """


Sprite.register_event_type('on_animation_end')
