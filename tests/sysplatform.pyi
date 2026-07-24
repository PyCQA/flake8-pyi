import sys

if sys.platform > 3: ...  # Y007 Unrecognized sys.platform check
if sys.platform == 10.12: ...  # Y007 Unrecognized sys.platform check
if sys.platform == 'linus': ...  # Y008 Unrecognized platform "linus"
if sys.platform != 'linux': ...
if sys.platform == 'win32': ...

if sys.platform == 'win32':
    platform_specific: str
    platform_same: float
else:
    platform_specific: int
    platform_same: float  # Y069 Definition "platform_same" is identical in multiple sys.version_info/sys.platform branches
