from abc import abstractmethod

class Bad:
    def __repr__(self) -> str:  # Y029 Defining __repr__ or __str__ in a stub is almost always redundant
        ...

    def __str__(self) -> str:  # Y029 Defining __repr__ or __str__ in a stub is almost always redundant
        ...


class Good:
    @abstractmethod
    def __str__(self) -> str:
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...


class AlsoGood(str):
    def __str__(self) -> AlsoGood:
        ...

    def __repr__(self) -> AlsoGood:
        ...
