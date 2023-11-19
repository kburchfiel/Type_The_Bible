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
no_mistakes = 1 # This flag will get set to 0 if the player makes
# a mistake. If it remains at 1 throughout the race, then
# a mistake-free race will get logged in results_table.
previous_line_count = 1

local_start_time = pd.Timestamp.now()
utc_start_time = pd.Timestamp.now(timezone.utc)

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
        verse_response += character.decode('ascii') # The presence
        # of this character within verse_response will instruct
        # the program to exit the user out of this test later on.
        # See https://pypi.org/project/colorama/
        break
    else: 
        # The following line adds the latest character typed
        # to verse_response.
        try:
            verse_response += character.decode('ascii')  
            # See https://stackoverflow.com/questions/17615414/how-to-convert-binary-string-to-normal-string-in-python3
        except: # Keys that fall out of the ascii subset, such as 
            # arrow keys, would cause the above line to crash. Therefore,
            # when the above line fails to work, the following 'continue'
            # statement will allow the program to ignore the key and move
            # back to the beginning of the loop.
            continue

    # Determining which color to use for the text:
    if verse[0:len(verse_response)] == verse_response:
        text_color = Fore.GREEN
    else:
        no_mistakes = 0 # This flag will remain at 0 for the 
        # rest of the race.
        text_color = Fore.RED 
    
    # Printing the player's response so far: 
    
    # This process will involve printing the entirety of verse_response
    # after each character is pressed than just the most recent character. 
    # This code is more complex than a regular print statement, but it has
    # several advantages:
    # 1. It allows the player to quickly determine when a typo has 
    # occurred (as the text will show up in red rather than in green).
    # 2. It supports the use of backspace to correct responses on 
    # previous lines. (I wasn't able to navigate to a previous line 
    # using backspace when printing single characters at a time.)
    # 3. It allows the cursor to always appear to the right of the most
    # recent character. If the latest typed line takes up the entire
    # width of the console, the cursor will appear on the left of 
    # the following line.
    # The development of this code involved a decent amount of trial and 
    # error, but I'll try to explain the function of each line in order to
    # make the final result more intuitive.


    line_count = (len(verse_response) // column_width) + 1
    # Calculates the number of lines on which the player's
    # response appears. The inclusion of the max() function ensures
    # that line_count will always be at least 1.
    # 1 is added to verse_response because, if the response has extended
    # to the right side of the terminal, another line will get added
    # in (via code below) to make room for the cursor. Thus, line_count
    # needs to be incremented by 1 in that case to reflect the terminal's
    # output.

    # The following code adjusts to changes in the response's line count.
    # If the line count goes up (as indicated by line_count's exceeding
    # previous_line_count), the response printout will be preceded
    # by a newline so that more space is available to print the longer
    # text. If the line count goes down (e.g. due to a backspace),
    # the the printout will be preceded by an up cursor statement
    # since less space will be needed to print the line.
    if line_count > previous_line_count:
        line_change_shift_command = '\n'
    elif line_count < previous_line_count: 
        line_change_shift_command = "\033[A"
        # "\033[A" is an ANSI escape code that moves the cursor 
        # up by one line. See
        # at https://pypi.org/project/colorama/
    else: # No command is necessary if the number of lines is the same 
        # as before
        line_change_shift_command = ''

    previous_line_count = line_count 

    # If more than one line is present, we'll need to move the cursor
    # up by the number of lines -1. Otherwise, an extra line will get
    # printed for each character.
    if line_count > 1:
        up_command = f"\033[{line_count - 1}A"
    # This ANSI escape code, based on Richard's response at
    # https://stackoverflow.com/a/33206814/13097194 ,
    # will move the cursor up line_count -1 times.
    else:
        up_command = '' # If the response is still on the first line,
        # there's no need to move the cursor up, as its vertical
        # position won't shift in the process of writing the response.

    chars_right_of_response = column_width - (
        len(verse_response) % column_width)
    if chars_right_of_response == 1:
        left_cursor_shift = '' # No cursor shift is needed in this case.
    else:
        left_cursor_shift = f"\033[{chars_right_of_response -1}D"
        # Based on https://pypi.org/project/colorama/


    ljust_compensation = '\033[A'


    # print(line_count, len(verse_response), column_width, chars_right_of_response)
    print(f"\r{line_change_shift_command}{up_command}{text_color}{verse_response.ljust(column_width*(line_count + 1))}{left_cursor_shift}{ljust_compensation}", end = '')
    # print(f"\r{text_color}{verse_response.ljust(column_width*(line_count + 1))}{up_command}", end = '')
    # .ljust() pads the string with ASCII spaces on the right
    # (see https://docs.python.org/3/library/stdtypes.html#str.ljust).
    # I added this in so that, if the user needed to hit backspace,
    # the deleted characters would no longer appear within the string.
    # For the use of Colorama to produce red and green text, see
    # https://pypi.org/project/colorama/
    # and https://stackoverflow.com/a/3332860/13097194
    
    # cursor_position = "\033[1C" 
    # # See cursor positioning section within
    # # https://pypi.org/project/colorama/
    # print(cursor_position)

    if verse_response == verse: # Note that, unlike with version
        # v1, the player does not need to hit 'Enter' in order
        # to end the typing test after writing a completed
        # verse. This should speed up his/her WPM as a result.
        typing_end_time = time.time()
        typing_time = typing_end_time - typing_start_time
        print('\n'*line_count+'Success!') # The cursor
        # needs to be moved past the lines already printed
        # so that 'Success' won't overwrite any of the words.
        print(Style.RESET_ALL)
        break