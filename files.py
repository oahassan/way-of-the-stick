import os
import string
import unicodedata

_HOME_DIR = ''

if 'HOME' in os.environ:
    _HOME_DIR = os.environ["HOME"]
elif 'USERPROFILE' in os.environ:
    _HOME_DIR = os.environ["USERPROFILE"]
else:
    _HOME_DIR = "."

_WOTS_DIR = os.path.join(_HOME_DIR, 'wots')

def removeDisallowedFilenameChars(filename):
    
    return ''.join(c for c in filename if c in validFilenameChars)

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
