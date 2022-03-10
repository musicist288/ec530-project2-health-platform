from peewee import Model

class BaseModel(Model):
    """Recommended practice is to have a base model that
    your tables inherit from."""
    pass


def register_table(array):
    def wrapper(cls):
        array.append(cls)
        return cls

    return wrapper
