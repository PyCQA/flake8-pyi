import sys

if sys.platform > 3: ...  # Y007 Unrecognized sys.platform check
if sys.platform == 10.12: ...  # Y007 Unrecognized sys.platform check
if sys.platform == 'linus': ...  # Y008 Unrecognized platform "linus"
if sys.platform != 'linux': ...
if sys.platform == 'win32': ...
