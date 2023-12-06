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


verse = "There is no fear in love; but perfect love casts out fear, because fear has punishment. He who fears is not made perfect in love." # 1 John 4:18
print(verse)

# Creating a list of words within the verse that we can use for
# word-based typing test analyses:
# We could use verse.split(' ') to create a list of words. However,
# since our goal is to build a list that can then serve as the basis
# of analyses, we'll want to create a list that includes:
# 1. The starting and finishing index of each word within the verse. This will
# allow us to determine when the player has arrived at and completed
# that word.
# 2. Words without any spacing or punctuation attached. (Learning how fast
# you wrote 'they' is more interesting than is learning how fast 
# you wrote '"that' or 'that,'.)
# Therefore, the following code is more complex than a simple split()
# operation.

first_character_index_list = []
# Determining the indices of the verse that contain starting letters of
# words: 
# (We can find these indices by searching for characters that are preceded
# by a non-alphabetic character *or* an alphabetic character that is also
# the first character in the verse.
for i in range(1, len(verse)):
    if ((verse[i].isalpha()) & (verse[i-1].isalpha() == False)):
        first_character_index_list.append(i)
    if (verse[i].isalpha() & ((verse[i-1].isalpha() == True) & (i == 1))):
        first_character_index_list.append(i-1) # In this case, the
        # character preceding i is the starting character rather than i itself.

first_character_index_list


df_word_index_list = []

for index in first_character_index_list:
    first_character = verse[index]
    # Initializing the word started by this character with 
    # the starting character:
    word = first_character
    i = 1
    while True:
        next_character = verse[index + i]
        if next_character.isalpha() == True: # 
            word += next_character
            i += 1
        else:
            last_character_index = index + i -1
            break
    df_word_index_list.append({'first_character_index':index, 
        'last_character_index': last_character_index,
        'word':word})
    # print(index, last_character_index, word)

df_word_index_list = pd.DataFrame(df_word_index_list)
df_word_index_list['previous_character_index'] = np.where(df_word_index_list['first_character_index'] != 0,  df_word_index_list['first_character_index'] - 1, np.NaN)





# The following block of code derives from the v2 code found in
# run_typing_test.


# This version of the test checks the player's input after
# each character is typed. If the player's input is correct
# so far, the text will be highlighted green; otherwise,
# it will be highlighted red. (This allows the player to be 
# notified of an error without the need for a line break
# in the console, which could prove distracting.)
# This function has been tested on Windows, but not yet 
# on Mac or Linux. The use of the Colorama library should
# make it cross-platform, however.
verse_response = '' # This string will store the player's 
# response.
no_mistakes = 1 # This flag will get set to 0 if the player makes
# a mistake. If it remains at 1 throughout the race, then
# a mistake-free race will get logged in results_table.
previous_line_count = 1
backspace_count = 0
incorrect_character_count = 0
correct_consecutive_entries = 0 # Keeps track of the number
# of correct characters typed in a row. Both incorrect characters
# and backspace keypresses will reset this value to 0.
character_timestamp_list = []
character_time_list = []
character_stats_list = []
word_stats_list = []
code_execution_time_list = []
unix_start_time = time.time()
local_start_time = pd.Timestamp.now()
utc_start_time = pd.Timestamp.now(timezone.utc)
first_keypress = 1 # Designates whether or not the player is 
# currently making his or her first keypress. This flag, which
# will be set to 0 after the first keypress is made,
# will help determine whether or not to begin timing the player's
# first word.
typing_start_time = time.perf_counter_ns()
# Using perf_counter_ns() allows for more accurate time duration
# calculations than does time.time(). See
# https://docs.python.org/3/library/time.html#time.perf_counter_ns
last_character_index = -1 # Initializing this variable with a number
# that will never occur within the game so that this value won't
# get interpreted as an actual value

while True: # This while loop allows the player to 
    # enter multiple characters.
    # The following if statement determines whether to 
    # begin timing the player's first word. Timing will only
    # begin
    if (len(verse_response) == 0) & (
        0 in df_word_index_list['first_character_index'].to_list()
        ) & (first_keypress == 1):
        word_start_time = typing_start_time
        last_character_index = df_word_index_list.query(
            'first_character_index == 0').copy().iloc[0][
                'last_character_index']
        word = df_word_index_list.query(
            'first_character_index == 0').copy().iloc[0][
                'word']
        # print(f" Started typing {word}.")
        typed_word_without_mistakes = 1
        # print(f" {last_character_index}")
    code_execution_end_time = time.perf_counter_ns()
    if first_keypress == 0: 
        code_execution_time_list.append((code_execution_end_time - character_press_time) / 1000000)
        # We divide by 1,000,000 to convert from nanoseconds (the output
        # of perf_counter_ns() to milliseconds.
    character = getch() # getch() allows each character to be 
    # checked, making it easier to identify mistyped words.
    character_press_time = time.perf_counter_ns()
    first_keypress = 0

    if character == b'\x08': 
        # This will return True if the user hits backspace.
        # In this case, we'll want to remove the latest character
        # from verse_response in order to keep that value
        # in sync with what the player sees on the screen.
        # Calling print(character) after
        # hitting backspace revealed that b'\x08' was the code
        # associated with the backspace key. 
        backspace_count += 1
        verse_response = verse_response[:-1] # Trims the last
        # value off verse_response.
        correct_consecutive_entries = 0 # Resets this value
        # so that a correct entry followed by a backspace and
        # another correct entry won't be counted as two
        # correct entries in a row.
        typed_word_without_mistakes = 0
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
    if verse[0:len(verse_response)] == verse_response: # If this returns
        # True, the player's response is correct so far.
        text_color = Fore.GREEN
        # Adding the time it took to type the last character
        # to the list: (Note that the time it takes to 
        # enter a backspace won't be included.)
        verse_response_minus_one = len(verse_response) -1 # The character
        # Index values in df_word_index_list start at 0, so this variable
        # will help us convert between verse lengths and index positions.        
        
        if character != b'\x08':
            character_timestamp_list.append(character_press_time)
            correct_consecutive_entries += 1

            if correct_consecutive_entries >= 2:
                # Limiting the additions to character_time_list
                # to cases in which 2+ characters have been
                # typed correctly in a row will prevent the data 
                # from getting skewed by incorrect output. 
                character_time_list.append(
                    character_timestamp_list[-1] - 
                    character_timestamp_list[-2])
                
            if correct_consecutive_entries >= 3:
                # We're using 3 as a threshold instead of 2 so
                # that our statistics on the time needed
                # to type the last 2 characters won't get skewed
                # by cases in which the 3rd-to-last character
                # was typed incorrectly.
                character_stats_list.append(
                {'Character': character.decode('ascii'),
                'Time Used to Type Last Character (ms)': (
                    character_timestamp_list[-1] - 
                    character_timestamp_list[-2]) / 1000000,
                    'Last 2 Characters':verse_response[-2:],
                    'Time Used to Type Last 2 Characters (ms)':
                    (character_timestamp_list[-1] - 
                    character_timestamp_list[-3]) / 1000000}
                )
                # print(f"Finished typing {character.decode('ascii')} in \
# {(character_timestamp_list[-1] - character_timestamp_list[-2]) / 1000000} ms.") 
#                 print(f"Finished typing {verse_response[-2:]} in \
# # {(character_timestamp_list[-1] - character_timestamp_list[-3]) / 1000000} ms.")

            # Checking whether a word has begun or ended:
            # We're placing these checks within the correct response and
            # no backspace clauses so that a typo or backspace won't
            # count as having correctly begun or ended a word.

            if verse_response_minus_one == last_character_index:
                word_end_time = character_press_time
                # print(f"Finished typing {word} in {(word_end_time - word_start_time) / 1000000} ms. typed_word_without_mistakes is set to {typed_word_without_mistakes}.")
                word_stats_list.append({"word":word, "word_duration (ms)": (word_end_time - word_start_time) / 1000000, "typed_word_without_mistakes":typed_word_without_mistakes}) 
                # Other analyses can be added to our 
                # word stats table later on, so we don't
                # need to compute them now.

            if verse_response_minus_one in df_word_index_list[
                'previous_character_index'].to_list():
                # If this returns true, we know we're
                # at the starting point of a new word.
                # print(verse_response_minus_one, df_word_index_list['previous_character_index'])
                # print("Start of new word detected (Point A).")
                typed_word_without_mistakes = 1
                verse_response_minus_one = len(verse_response) -1
                word_start_time = character_press_time # The start time of 
                # this new word is defined as the time that the character 
                # preceding the word was pressed.
                last_character_index = df_word_index_list.query(
                    "previous_character_index == @verse_response_minus_one").iloc[
                        0]['last_character_index']
                word = df_word_index_list.query(
                    'previous_character_index == @verse_response_minus_one').iloc[0][
                        'word']
                # print(f" Started typing {word}.")

    else:
        no_mistakes = 0 # This flag will remain at 0 for the 
        # rest of the race.
        typed_word_without_mistakes = 0 
        correct_consecutive_entries = 0
        text_color = Fore.RED 
        if character != b'\x08': # Backspaces won't be counted
            # towards the incorrect character count so that
            # players won't be double-penalized for mistyping
            # a character.
            incorrect_character_count += 1
    
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


    line_count = ((len(verse_response)) // column_width) + 1
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
    # printed with each character.
    if line_count > 1:
        up_command = f"\033[{line_count -1}A"
    # This ANSI escape code, based on Richard's response at
    # https://stackoverflow.com/a/33206814/13097194 ,
    # will move the cursor up line_count -1 times.
    else:
        up_command = '' # If the response is still on the first line,
    #     # there's no need to move the cursor up, as its vertical
    #     # position won't shift in the process of writing the response.

    clear_text_to_right_command = '\033[0K' # Based on
    # https://en.wikipedia.org/wiki/ANSI_escape_code
    # and on https://pypi.org/project/colorama/

    if column_width - (len(verse_response) % column_width) == 1:
        left_cursor_shift = ''
    else:
        left_cursor_shift = '\033[D'

    # Printing out various variables related to
    # the subsequent print statement can be useful for debugging.
    # print("\033A",line_count, len(verse_response), column_width, column_width - (len(verse_response) % column_width) == 1)
    print(f"\r{clear_text_to_right_command}{line_change_shift_command}{up_command}{text_color}{verse_response} {left_cursor_shift}", end = '')
    # For the use of Colorama to produce red and green text, see
    # https://pypi.org/project/colorama/
    # and https://stackoverflow.com/a/3332860/13097194
    
    if verse_response == verse: # Note that, unlike with version
        # v1, the player does not need to hit 'Enter' in order
        # to end the typing test after writing a completed
        # verse. This should speed up his/her WPM as a result.
        typing_end_time = time.perf_counter_ns()
        typing_time = (typing_end_time - typing_start_time) / 1000000000
        # Dividing by 1 billion to convert typing_time from nanoseconds
        # to seconds
        print('\n'*line_count+'Success!') # The cursor
        # needs to be moved past the lines already printed
        # so that 'Success' won't overwrite any of the words.
        print(Style.RESET_ALL)

        # Accuracy calculations:
        # Calculating backspaces as a percentage of verse length:
        backspaces_as_pct_of_length = (
            100 * backspace_count / len(verse)) # The 100* 
            # multiplier converts these values from 
            # proportions to percentages.

        # Calculating incorrect entries as a percentage of verse
        # length:
        incorrect_characters_as_pct_of_length = (
            100 * incorrect_character_count / len(verse))
    

        # Calculating timing statistics at the character level:
        # Note that this value will be converted from
        # nanoseconds to milliseconds.
        median_character_time = np.median(character_time_list) / 1000000

        # Calculating timing statistics at the word level:
        character_stats_for_latest_test = pd.DataFrame(
            character_stats_list)
        word_stats_for_latest_test = pd.DataFrame(word_stats_list)
        print(f"Code execution stats: Median: {np.median(code_execution_time_list)}, Mean: {np.mean(code_execution_time_list)}, Max: {max(code_execution_time_list)}, Min: {min(code_execution_time_list)}. All execution times: {code_execution_time_list}")
        # print("Typing time:",typing_time)
        # print("Character keypress times (in ms)",
        # [character_time / 1000000 for 
        # character_time in character_time_list])
        break