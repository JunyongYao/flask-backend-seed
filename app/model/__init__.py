# -*- coding: utf-8 -*-
# Model module should not import cache module to avoid circle reference.
import enum


class DBEnum(enum.Enum):
    """
    Used for have enumerate data supported in sqlalchemy
    """
    @classmethod
    def get_enum_labels(cls):
        return [i.value for i in cls]
