from abc import ABCMeta, ABC
from numpy import int32


class _IDMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        dct['_next_id'] = 1
        return super().__new__(cls, name, bases, dct)


class IDNumerator(ABC, metaclass=_IDMeta):
    def __init__(self):
        self._id = self.__class__._next_id
        self.__class__._next_id += 1

    @property
    def id(self) -> int32:
        return self._id


# Пример использования
# class TestClass(IDnumerator):
#     pass
#
#
# class AnotherClass(IDnumerator):
#     pass
#
# if __name__ == "__main__":
#     obj1 = TestClass()
#     obj2 = AnotherClass()
#     obj3 = TestClass()
#
#     print(f"ID объекта 1 (TestClass): {obj1.id}")
#     print(f"ID объекта 2 (AnotherClass): {obj2.id}")
#     print(f"ID объекта 3 (TestClass): {obj3.id}")
#
#     try:
#         obj1.id = 100
#     except AttributeError as e:
#         print(f"Ошибка при попытке изменить id: {e}")