"""
This module provides some base definitions and functions used by
other model modules.
"""
from peewee import Model

class BaseModel(Model):
    """Recommended practice is to have a base model that
    your tables inherit from."""
    pass


def register(array):
    """A decorator register a class or function by appending
    it to an array.
    """
    def wrapper(cls):
        array.append(cls)
        return cls

    return wrapper
