#!"c:\users\75165\documents\course\csci 571\hw6\venv\scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'pipreq==0.4','console_scripts','pipreq'
__requires__ = 'pipreq==0.4'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('pipreq==0.4', 'console_scripts', 'pipreq')()
    )
