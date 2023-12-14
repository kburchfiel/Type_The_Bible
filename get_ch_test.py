# This file makes it easier to test out updates to V2
# of the typing test in Type Through the Bible.

import os
column_width = os.get_terminal_size().columns

import pandas as pd
pd.set_option('display.max_columns', 1000)
import time
import plotly.express as px
from getch import getch # Installed this library using pip install py-getch, not
# pip install getch. See https://github.com/joeyespo/py-getch
import numpy as np
from datetime import datetime, date, timezone # Based on 
# https://docs.python.org/3/library/datetime.html

from colorama import just_fix_windows_console, Fore, Back, Style, Cursor
# From https://github.com/tartley/colorama/blob/master/demos/demo01.py
just_fix_windows_console() # From https://github.com/tartley/colorama/blob/master/demos/demo01.py

# Using the following while loop, I determined that pressing 
# Ctrl + Backspace on Windows produces the value b'\x7f'.
while True:
    print("Enter a character.")
    char = getch()
    print(char)
    try:
        print(char.decode('ascii'))
    except:
        print("ASCII decoding failed.")