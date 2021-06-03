from functools import wraps


def memoize(func):
    """
    The memoize decorator will cache the result of a function and store it
    in a cache dictionary using its arguments and keywords arguments as a key.
    The cache can be cleared by calling the cache_clear function on the
    decorated function. If only a certain key needs to be removed the pop
    function can be used.
    """
    cache = {}

    def construct_key(*args, **kwargs):
        """
        The constructing of the key is a bit more elaborate than it might need
        to be. The reason for making sure that everything is converted into a
        string separately is to make sure that if raw or unicode string are
        provided in either the arguments or keyword arguments they are not
        cached separately.
        """
        key = ""
        for arg in args:
            key += str(arg)
        for key, value in kwargs.items():
            key += str(key) + str(value)

        return key

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = construct_key(*args, **kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    def clear():
        cache.clear()

    def pop(*args, **kwargs):
        key = construct_key(*args, **kwargs)
        cache.pop(key, None)

    wrapper.clear = clear
    wrapper.pop = pop
    return wrapper

