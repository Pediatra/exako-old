from functools import wraps


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
