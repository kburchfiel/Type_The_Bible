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


verse = "God made the two great lights: the greater light to rule the day, and the lesser light to rule the night. He also made the stars."
print(verse)


# The following block of code derives from the v2 code found in
# run_typing_test.


verse_response = '' # This string will store the player's 
# response.
local_start_time = datetime.now().isoformat()
utc_start_time = datetime.now(timezone.utc).isoformat()
typing_start_time = time.time()
while True: # This while loop allows the player to enter
    # multiple characters.
    # to allow the player to enter 
    character = getch() # getch() allows each character to be 
    # checked, making it easier to identify mistyped words.
    if character == b'\x08': 
        # This will return True if the user hits backspace.
        # In this case, we'll want to remove the latest character
        # from verse_response in order to keep that value
        # in sync with what the player sees on the screen.
        # Calling print(character) after
        # hitting backspace revealed that b'\x08' was the code
        # associated with the backspace key. 
        verse_response = verse_response[:-1] # Trims the last
        # value off verse_response.
    elif character == b'`':
        print(Style.RESET_ALL) # Resets the color of the text.
        # See https://pypi.org/project/colorama/
        break
    else: 
        # The following line adds the latest character typed
        # to verse_response.
        verse_response += character.decode('ascii')  
        # See https://stackoverflow.com/questions/17615414/how-to-convert-binary-string-to-normal-string-in-python3

    # Determining which color to use for the text:
    if verse[0:len(verse_response)] == verse_response:
        text_color = Fore.GREEN
    else:
        text_color = Fore.RED 
    
    # Printing the player's response so far: (Note that 
    # verse_response gets printed instead of the last character.)

    # The addition of 'end = "\r", which comes from Sencer H at
    #  https://stackoverflow.com/a/69030559/13097194,
    #  allows characters to get 
    # displayed immediately
    # after one another rather than on separate lines. It also
    # prevents a new line from appearing whenever the user 
    # types an entry.

    line_count = ((len(verse_response)-1) // column_width) + 1
    # Calculates the number of lines that are 
    # being displayed so far. 

    up_command = f"\033[{line_count}A"
    # This value, based on Richard's response at
    # https://stackoverflow.com/a/33206814/13097194 ,
    # will move the cursor up up_count number of times.

    print(f"{text_color}{verse_response.ljust(column_width*line_count + 1)}{up_command}", end = "\r")
    # I had also added in flush = True, but this didn't appear
    # to affect the output. 
    # .ljust() pads the string with ASCII spaces on the right
    # (see https://docs.python.org/3/library/stdtypes.html#str.ljust).
    # I added this in so that, if the user needed to hit backspace,
    # the deleted characters would no longer appear within the string.
    # For the use of Colorama to produce red and green text, see
    # https://pypi.org/project/colorama/
    # and https://stackoverflow.com/a/3332860/13097194

    if verse_response == verse: # Note that, unlike with version
        # v1, the player does not need to hit 'Enter' in order
        # to end the typing test after writing a completed
        # verse. This should speed up his/her WPM as a result.
        typing_end_time = time.time()
        typing_time = typing_end_time - typing_start_time
        print("\nSuccess!")
        print(Style.RESET_ALL)
        break