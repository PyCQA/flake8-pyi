import sys

if sys.version == 'Python 2.7.10': ...  # Y002 If test must be a simple comparison against sys.platform or sys.version_info
if 'linux' == sys.platform: ...  # Y002 If test must be a simple comparison against sys.platform or sys.version_info
if hasattr(sys, 'maxint'): ...  # Y002 If test must be a simple comparison against sys.platform or sys.version_info
if sys.maxsize == 42: ...  # Y002 If test must be a simple comparison against sys.platform or sys.version_info

if sys.version_info >= (3, 10) and sys.platform == "linux": ...
if sys.version_info >= (3, 15) and (sys.platform == "win32" or sys.platform == "linux"): ...
if (sys.platform == "win32" or sys.platform == "linux") and sys.version_info >= (3, 15): ...
if sys.version_info >= (3, 10) and (sys.platform == "linux" or sys.maxsize == 42): ...  # Y002 If test must be a simple comparison against sys.platform or sys.version_info
