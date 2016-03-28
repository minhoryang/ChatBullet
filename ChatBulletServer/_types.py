from sqlalchemy_utils import UUIDType as _UUIDType


class UUIDType(_UUIDType):
    def __init__(self, *args, **kwargs):
        if 'length' in kwargs:
            kwargs.pop('length')
        return super().__init__(*args, **kwargs)
