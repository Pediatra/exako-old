from functools import wraps


def enum_dispatch(func):
    func._registry = {}

    @wraps(func)
    def wrapper(enum_value, *args, **kwargs):
        if enum_value in func._registry:
            return func._registry[enum_value](*args, **kwargs)
        return func(*args, **kwargs)

    def register(enum_value):
        if not isinstance(enum_value, list):
            enum_value = [enum_value]

        def inner(f):
            for value in enum_value:
                func._registry[value] = f
            return f

        return inner

    wrapper.register = register
    return wrapper


def validate(func):
    func._registry = {}

    @wraps(func)
    def wrapper(value, *args, **kwargs):
        if value in func._registry:
            for validation_func in func._registry[value]:
                validation_func(*args, **kwargs)

    def register(value_list):
        if not isinstance(value_list, list):
            value_list = [value_list]

        def inner(f):
            for value in value_list:
                func._registry.setdefault(value, []).append(f)
            return f

        return inner

    wrapper.register = register
    return wrapper
