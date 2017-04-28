import sys
if sys.platform == 'win32':
    from tzlocals.win32 import get_localzone, reload_localzone
elif 'darwin' in sys.platform:
    from tzlocals.darwin import get_localzone, reload_localzone
else:
    from tzlocals.unix import get_localzone, reload_localzone
