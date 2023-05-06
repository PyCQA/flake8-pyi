# This checks that pyflakes emits F822 errors where appropriate,
# but doesn't emit false positives when checking stub files.
# flake8-pyi's monkeypatching of pyflakes impacts the way this check works.

__all__ = ["a", "b", "c", "Klass", "d", "e"]  # F822 undefined name 'e' in __all__

a: int
b: int = 42
c: int = ...
class Klass: ...
def d(): ...
