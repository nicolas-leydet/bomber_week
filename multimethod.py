def multi(selector_fn):
    def _dispatch_fn(*args, **kwargs):
        return _dispatch_fn.__multi__.get(
            selector_fn(*args, **kwargs),
            _dispatch_fn.__multi_default__
        )(*args, **kwargs)

    _dispatch_fn.__multi__ = {}
    _dispatch_fn.__multi_default__ = lambda *args, **kwargs: None
    return _dispatch_fn


def method(dispatch_fn, dispatch_key=None):
    def register_method(method):
        if dispatch_key is None:
            dispatch_fn.__multi_default__ = method
        else:
            dispatch_fn.__multi__[dispatch_key] = method
        return dispatch_fn
    return register_method



if __name__ == '__main__':


    @multi
    def die(obj):
        return obj['type']

    @method(die, 'A')
    def _(obj):
        print('death of type A')

    @method(die, 'B')
    def _(obj):
        print('death of type B')

    @method(die)
    def _(obj):
        print('default death')


    die({'type': 'A'})
    die({'type': 'B'})
    die({'type': 'C'})
