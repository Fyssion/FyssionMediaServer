"""
This source code was responsibly sourced from Rapptz/discord.py
Original: https://github.com/Rapptz/discord.py/blob/a8f44174bafed3989ec2959a62b89006f4a9e9a1/discord/flags.py

The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""


class flag_value:
    def __init__(self, func):
        self.flag = func(None)
        self.__doc__ = func.__doc__

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance._has_flag(self.flag)

    def __set__(self, instance, value):
        instance._set_flag(self.flag, value)

    def __repr__(self):
        return "<flag_value flag={.flag!r}>".format(self)


class alias_flag_value(flag_value):
    pass


def fill_with_flags(*, inverted=False):
    def decorator(cls):
        cls.VALID_FLAGS = {
            name: value.flag
            for name, value in cls.__dict__.items()
            if isinstance(value, flag_value)
        }

        if inverted:
            max_bits = max(cls.VALID_FLAGS.values()).bit_length()
            cls.DEFAULT_VALUE = -1 + (2 ** max_bits)
        else:
            cls.DEFAULT_VALUE = 0

        return cls
    return decorator


# n.b. flags must inherit from this and use the decorator above
class BaseFlags:
    __slots__ = ("value",)

    def __init__(self, **kwargs):
        self.value = self.DEFAULT_VALUE
        for key, value in kwargs.items():
            if key not in self.VALID_FLAGS:
                raise TypeError(f"{key:r} is not a valid flag name.")
            setattr(self, key, value)

    @classmethod
    def _from_value(cls, value):
        self = cls.__new__(cls)
        self.value = value
        return self

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return f"<{self.__class__.__name__} value={self.value}>"

    def __iter__(self):
        for name, value in self.__class__.__dict__.items():
            if isinstance(value, alias_flag_value):
                continue

            if isinstance(value, flag_value):
                yield (name, self._has_flag(value.flag))

    def _has_flag(self, o):
        return (self.value & o) == o

    def _set_flag(self, o, toggle):
        if toggle is True:
            self.value |= o
        elif toggle is False:
            self.value &= ~o
        else:
            raise TypeError(f"Value to set for {self.__class__.__name__} must be a bool.")
