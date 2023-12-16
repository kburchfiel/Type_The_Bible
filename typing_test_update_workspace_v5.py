# This file makes it easier to test out updates to V2
# of the typing test in Type Through the Bible.

import os
terminal_width, terminal_height = os.get_terminal_size()
# print(terminal_width, terminal_height)

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

# I found that Backspace and Ctrl + Backspace mapped to different bytestrings
# on Windows and on Linux. Therefore, the following code checks the user's
# operating system, then uses that information to choose which
# bytestrings to assign to character_backspace and word_backspace.
# When character_backspace is detected within V2 of the typing test, 
# a single character will be removed; meanwhile, when word_backspace 
# is detected, a whole word
# will be removed.
import platform
if platform.system() == 'Linux':
    character_backspace = b'\x7f'
    word_backspace = b'\x08'
else:
    character_backspace = b'\x08'
    word_backspace = b'\x7f'


verse = "There is no fear in love; but perfect love casts out fear, because fear has punishment. He who fears is not made perfect in love." # 1 John 4:18
print(verse)

from blessed import Terminal # Blessed is a variant of the Blessings library 
# that also works on Windows. See
# https://blessed.readthedocs.io/en/latest/intro.html
term = Terminal()



def create_word_table(verse):
    '''Creating a list of words within the verse that we can use for
    word-based typing test analyses:
    We could use verse.split(' ') to create a list of words. However,
    since our goal is to build a list that can then serve as the basis
    of analyses, we'll want to create a list that includes:
    1. The starting and finishing index of each word within the verse. This will
    allow us to determine when the player has arrived at and completed
    that word.
    2. Words without any spacing or punctuation attached. (Learning how fast
    you wrote 'they' is more interesting than is learning how fast 
    you wrote '"that' or 'that,'.)
    Therefore, the following code is more complex than a simple split()
    operation.
    This function also counts contractions ('don't', 'can't,
    etc.) as individual words. Some care is needed to distinguish between
    apostrophes/single quotes that begin contractions and those that start
    or end single quotes.'''

    first_letter_index_list = []
    # Determining the indices of the verse that contain starting letters of
    # words: 
    # (We can find these indices by searching for characters that are preceded
    # by a non-alphabetic character *or* an alphabetic character that is also
    # the first character in the verse.
    for i in range(1, len(verse)): # Starting at 1 rather than 0 because
        # we'll sometimes need to reference the preceding character
        # (which wouldn't be possible if i were 0)

        if i == 1:
            if ((verse[i].isalpha()) & (verse[i-1].isalpha() == False)): 
                # This if statement addresses a special case
                # in which a verse begins with ' and a letter. In this 
                # case, because there are no letters preceding the ' 
                # (since i is 1), we'll assume that the ' is the start of 
                # a single quote rather than the beginning of a contraction
                # and will thus add the letter to our starting letters list.
                # print("Found first letter of word (Part A)")
                first_letter_index_list.append(i)
                continue # Now that we've added i to the list, we can 
                # return to the top of the for loop. (This will prevent the
                # code from adding duplicate copies of a starting letter
                # to first_letter_index_list.

            if (verse[i-1].isalpha()):
                # print("Found first letter of word (Part B)")
                first_letter_index_list.append(i-1) # In this case, the
            # character preceding i is the starting letter 
            # rather than i itself (which may or may not be a letter).
                continue

        if ((verse[i].isalpha()) & 
        ((verse[i-1].isalpha() == False) & (verse[i-1] != "'"))): # If 
            # the current character is a letter (e.g. isalpha() is True)
            # and the character behind it isn't a letter *and* also isn't
            # "'" (which is found in contractions), we'll assume that we
            # have found the start of a word.
            # This if statement will fail to detect the first word in a verse
            # if it gets preceded by a single quote (e.g. 'Hello' in 
            # 'Hello there'), but a previous if statement
            # will have already detected it.
            # print("Found first letter of word (Part C)")
            first_letter_index_list.append(i)
            continue
    
        if i >= 2:
            if ((verse[i].isalpha()) & 
            ((verse[i-1].isalpha() == False)) &
            (verse[i-2].isalpha() == False)): # In this case,
                # if both of the characters preceding a letter
                # aren't letters, then we'll assume that
                # this letter begins a word. (This was added in
                # to account for words that are preceded by a single
                # quote. Checking the character before that single quote
                # helps us distinguish apostrophes that begin quotes (which
                # won't be preceded by a letter)
                # from apostrophes that form part of contractions (which
                # will be).
                # print("Found first letter of word (Part D)")
                first_letter_index_list.append(i)
                continue


    # print(first_letter_index_list)


    # Now that we've determined the index of each word's starting letter,
    # we will go through the verse again to locate the final letter
    # within each word.
    df_word_index_list = []

    for index in first_letter_index_list: # This code iterates through
        # each word's starting character.
        first_letter = verse[index]
        # Initializing the word started by this character with 
        # the starting character:
        word = first_letter
        i = 0
        while True:
            i += 1
            position_within_verse = index + i
            # print("i is now", i)
            if position_within_verse < (len(verse) -1): # If this is False,
                # then there are at least two characters left in the verse.
                # We need to perform this check so that an upcoming if
                # statement that reads two characters ahead won't go
                # out of bounds.
                next_character = verse[position_within_verse]
                # print(f"Next character: '{next_character}'")
                if (next_character.isalpha() == True) | (
                    (next_character == "'") & 
                    (verse[position_within_verse + 1].isalpha() == True)): 
                    # Here, the next character will be added to the word if
                    # (1) it's a letter or (2) it's an apostrophe followed
                    # by a letter (which indicates that the apostrophe
                    # is part of a contraction).
                    word += next_character
                else:
                    last_letter_index = position_within_verse -1
                    break # Now that we've found the last letter, we can
                    # exit out of the while loop and begin to evaluate
                    # the next first index in first_letter_index_list.

            elif position_within_verse < len(verse): # In this case, 
                # we haven't yet made it to the very end of the verse.
                # We need to use elif here rather than 'if' so that
                # the preceding block of if statements and this one
                # will not both return True.
                next_character = verse[position_within_verse]
                if next_character.isalpha() == True: # 
                    word += next_character
                else:
                    last_letter_index = position_within_verse -1
                    break
            else: # In this case, we're already at the end of the verse,
                # so we can instead store the previous index position
                # within last_letter_index.
                last_letter_index = position_within_verse -1
                break

        df_word_index_list.append({'first_letter_index':index, 
            'last_letter_index': last_letter_index,
            'word':word})
        # print(index, last_letter_index, word)

    df_word_index_list = pd.DataFrame(df_word_index_list)
    df_word_index_list['previous_character_index'] = np.where(
        df_word_index_list['first_letter_index'] != 0,  
        df_word_index_list['first_letter_index'] - 1, np.NaN)
    df_word_index_list
    print("Words identified by create_word_table():",df_word_index_list['word'].to_list())
    return df_word_index_list


df_word_index_list = create_word_table(verse)

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
word_stats_list = []
# code_execution_time_list = []

# The following two lists will keep track of first- and last-letter
# indices that have already been reached by the player. These lists
# will be incorporated into if statements so that (1) timing for a
# word will begin only if that word's first letter index is not in 
# first_letter_indices_reached and (2) timing for a word will end
# only if that word's last letter index is not in
# last_letter_indices_reached. This will prevent duplicate 
# timing entries for the same word from getting added to the word
# stats list; in addition, it will prevent the player from
# 'resetting' the timing for a given word by returning to its index.
first_letter_indices_reached = []
last_letter_indices_reached = []

first_keypress = 1 # Designates whether or not the player is 
# currently making his or her first keypress. This flag, which
# will be set to 0 after the first keypress is made,
# will help determine whether or not to begin timing the player's
# first word.
last_letter_index = -1 # Initializing this variable with a number
# that will never occur within the game so that this value won't
# get interpreted as an actual word starting point.

get_location_start_time = time.perf_counter_ns()
cursor_y_pos, cursor_x_pos = term.get_location()

# get_location() retrieves the text cursor's current location. I wasn't
# able to find a way to do this within colorama, but thankfully this 
# solution works great. See
# https://blessed.readthedocs.io/en/latest/location.html for more details.
# print(cursor_y_pos)
get_location_end_time = time.perf_counter_ns()
# print(cursor_y_pos, cursor_x_pos)
# print((get_location_end_time - get_location_start_time)/1000000)
# print("Now printing cursor position:")

# print(term.get_location())
# print("Printed cursor position.")


unix_start_time = time.time()
local_start_time = pd.Timestamp.now()
utc_start_time = pd.Timestamp.now(timezone.utc)
typing_start_time = time.perf_counter_ns()
# Using perf_counter_ns() allows for more accurate time duration
# calculations than does time.time(). See
# https://docs.python.org/3/library/time.html#time.perf_counter_ns


while True: # This while loop allows the player to 
    # enter multiple characters.
    # The following if statement determines whether to 
    # begin timing the player's first word. Timing will only
    # begin
    if (len(verse_response) == 0) & (
        0 in df_word_index_list['first_letter_index'].to_list()
        ) & (first_keypress == 1):
        word_start_time = typing_start_time
        last_letter_index = df_word_index_list.query(
            'first_letter_index == 0').copy().iloc[0][
                'last_letter_index']
        word = df_word_index_list.query(
            'first_letter_index == 0').copy().iloc[0][
                'word']
        first_letter_indices_reached.append(0)
        # print(f" Started typing {word}.")
        typed_word_without_mistakes = 1
        # print(f" {last_letter_index}")
    # code_execution_end_time = time.perf_counter_ns()
    # if first_keypress == 0: 
    #     code_execution_time_list.append((code_execution_end_time - character_press_time) / 1000000)
        # We divide by 1,000,000 to convert from nanoseconds (the output
        # of perf_counter_ns() to milliseconds.
    character = getch() # getch() allows each character to be 
    # checked, making it easier to identify mistyped words.
    # The following lines assume that character is stored as a bytestring
    # rather than as a string. (I initially developed this game within
    # Windows, in which getch() returns a bytestring.) However, I found
    # that getch() returned strings when I tested out the code in Linux.
    # Therefore, the following if statement was added in to convert
    # these strings to bytestrings.
    if type(character) == str:
        character = character.encode()
    character_press_time = time.perf_counter_ns()
    first_keypress = 0

    if character == character_backspace: 
        # In this case, we'll want to remove the latest character
        # from verse_response in order to keep that value
        # in sync with what the player sees on the screen.
        backspace_count += 1
        verse_response = verse_response[:-1] # Trims the last
        # value off verse_response.
        typed_word_without_mistakes = 0
    elif character == word_backspace: 
        # The following code allows this sequence to remove the last
        # word typed, which is often a faster deletion method than
        # pressing the backspace key repeatedly.
        verse_response = ' '.join(verse_response.rstrip().split(' ')[:-1])
        # The above line first removes all spaces from the right of the last
        # word typed so that they won't interfere with the split() call.
        # It then splits the response into individual words; deselects
        # the last word; and joins the response back together.
        if len(verse_response) != 0: # As long as we're not at the start
            # of the console, it will be useful to add the space after
            # the last word back in so that the player doesn't need
            # to retype it.
            verse_response += ' '
        backspace_count += 1 # I was considering increasing backspace_count
        # here by the number of characters removed through Ctrl + Backspace,
        # but since the player still only has to press Backspace once
        # in this operation, I decided to still increment it by one.
        # This means that backspace_count may diverge significantly
        # from incorrect_character_count and thus be a poorer measure
        # of accuracy.
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
            # arrow keys, could cause the above line to crash. Therefore,
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
        
        if (character != character_backspace) & (character != word_backspace):

            # Checking whether a word has begun or ended:
            # We're placing these checks within the correct response and
            # no backspace clauses so that a typo or backspace won't
            # count as having correctly begun or ended a word. (I'm not sure
            # it would actually be possible to trigger the word start or 
            # end checks with Ctrl + Backspace, but I'll include it here
            # just in case a clever user figures out how.)
            # Note that last_letter_indices_reached and 
            # first_letter_indices_reached will be checked for the
            # presence of verse_response_minus_one. If it's already
            # there, then no action will be taken, as timing
            # for that word has already ended or started.

            # Checking whether the player has finished typing a word:
            if (verse_response_minus_one == last_letter_index) & (
                last_letter_index not in last_letter_indices_reached):
                word_end_time = character_press_time
                # print(f"Finished typing {word} in \
# {(word_end_time - word_start_time) / 1000000} ms. typed_word_without_mistakes \
# is set to {typed_word_without_mistakes}.")
                word_stats_list.append({"word":word, 
                "word_duration (ms)": (word_end_time - 
                word_start_time) / 1000000, 
                "typed_word_without_mistakes":typed_word_without_mistakes})
                last_letter_indices_reached.append(last_letter_index)
                # Other analyses can be added to our 
                # word stats table later on, so we don't
                # need to compute them now.

            # Checking whether the player has started typing a word:
            if (verse_response_minus_one in df_word_index_list[
                'previous_character_index'].to_list()) & (
                verse_response_minus_one not in first_letter_indices_reached):
                # If this returns true, we know we're
                # at the starting point of a new word.
                # print(verse_response_minus_one, df_word_index_list['previous_character_index'])
                # print("Start of new word detected (Point A).")
                typed_word_without_mistakes = 1
                verse_response_minus_one = len(verse_response) -1
                word_start_time = character_press_time # The start time of 
                # this new word is defined as the time that the character 
                # preceding the word was pressed.
                last_letter_index = df_word_index_list.query(
                "previous_character_index == @verse_response_minus_one").iloc[
                0]['last_letter_index']
                word = df_word_index_list.query(
                "previous_character_index == @verse_response_minus_one").iloc[
                0]['word']
                # print(f" Started typing {word}.")
                first_letter_indices_reached.append(
                verse_response_minus_one)

    else:
        no_mistakes = 0 # This flag will remain at 0 for the 
        # rest of the race.
        typed_word_without_mistakes = 0 
        text_color = Fore.RED 
        if (character != character_backspace) & (character != word_backspace): 
            # Backspaces won't be counted as part of the 
            # incorrect character tally so that
            # players won't be double-penalized for mistyping
            # a character.
            incorrect_character_count += 1
    
    # Printing the player's response so far: 
    
    # This process will involve printing the entirety of verse_response
    # after each character is pressed rather than 
    # just the most recent character. 
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


    line_count = ((len(verse_response)) // terminal_width) + 1
    # Calculates the number of lines on which the player's
    # response appears.

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

    previous_line_count = line_count # Updates the value of 
    # previous_line_count

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

    clear_text_to_right_command = '\033[0K' # This code clears out all text
    # to the right of the cursor. This will allow us to make text disappear
    # after the user hits Backspace or Ctrl + Backspace.
    # Based on
    # https://en.wikipedia.org/wiki/ANSI_escape_code
    # and on https://pypi.org/project/colorama/

    # In order to make the cursor appear on a new line when the player
    # has reached the end of a line, a space will get added to the verse
    # after it is printed (see below for more details). To compensate for 
    # this space, the ANSI escape code '\033[D' will usually get printed;
    # this code will then move the cursor one column back. However, 
    # if the verse is one column away from the end of the line, this
    # step won't be necessary, so an empty string can get passed
    # to left_cursor_shift instead.
    if terminal_width - (len(verse_response) % terminal_width) == 1:
        left_cursor_shift = ''
    else:
        left_cursor_shift = '\033[D'

    # Printing out various variables related to
    # the subsequent print statement can be useful for debugging.
    # print("\033A",line_count, len(verse_response), terminal_width, 
    # terminal_width - (len(verse_response) % terminal_width) == 1)


    # The following print statement displays the latest version
    # of verse_response on the screen. It does so using the following steps:
    # (Note: Many of these items are ANSI escape codes rather than
    # text.)

    # 1. \r (carriage return) moves
    # the cursor to the left of the line. 
    
    # 2. clear_text_to_right_command,
    # an ANSI escape code, is printed; this clears out all text
    # to the right of the cursor (which, due to the cursor's positioning,
    # equals all of the line's text).
    # This command also appears at the end of the print statement;
    # however, both commands are necessary. If the player's use of 
    # Ctrl + Backspace causes the end of the output to move up one line,
    # the first clear_text_to_right command will remove deleted text
    # on the lower line, and the last one will remove deleted text on the 
    # upper line.
    
    # 3. line_change_shift_command is printed in order to adjust for
    # changes in the output's line count. (See notes above for more details.)
    
    # 4. up_command is printed so that the cursor will be high enough to 
    # print all of the response's lines without creating an unnecessary
    # extra line.
    
    # 5. text_color gets printed; this will make the verse red if a mistake
    # is present and green otherwise.

    # 6. Finally, the verse itself gets printed, followed by a space (in order
    # to make a new line appear if the player has reached the end of the line).
    # Note that no other spaces are present within the print statement.

    # 7. In order to compensate for this space, left_cursor_shift is called,
    # which usually moves the cursor back one column. (See above for more
    # details.)

    # 8. Finally, clear_text_to_right_command is printed once again.

    # 9. End is set to '' so that the cursor will not move to a new line
    # after the string is printed.
    if (cursor_y_pos + (line_count - 1)) == terminal_height: # In this case, we'll print
        # a newline to make more room, then reduce the cursor y position by 1.
        bottom_line_newline = 'Hello!\n'
        cursor_y_pos -= 1
    else:
        bottom_line_newline = 'Hithere'
    cursor_reposition_code = f'\033[{cursor_y_pos};{cursor_x_pos}H'
    print(f"{clear_text_to_right_command}{bottom_line_newline}{cursor_reposition_code}{text_color}\
{verse_response}{cursor_y_pos + (line_count - 1)}{terminal_height}{clear_text_to_right_command}", end = '', flush=True)




#     print(f"\r{clear_text_to_right_command}\
# {line_change_shift_command}{up_command}{text_color}\
# {verse_response} {left_cursor_shift}{clear_text_to_right_command}", end = '')
    # For the use of Colorama to produce red and green text, see
    # https://pypi.org/project/colorama/
    # and https://stackoverflow.com/a/3332860/13097194
    
    if verse_response == verse: # Note that, unlike with version
        # v1, the player does not need to hit 'Enter' in order
        # to end the typing test after writing a completed
        # verse. This should speed up his/her WPM as a result.
        typing_end_time = time.perf_counter_ns()
        typing_time = (
            typing_end_time - typing_start_time) / 1000000000
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
        print("Backspace count and incorrect character count:",
        backspace_count, incorrect_character_count)
    
        # Calculating timing statistics at the word level:
        word_stats_for_latest_test = pd.DataFrame(word_stats_list)
        # print(word_stats_for_latest_test)
        # print(f"Code execution stats: Median: {np.median(
        # code_execution_time_list)}, Mean: {np.mean(
        # code_execution_time_list)}, Max: {max(
        # code_execution_time_list)}, Min: {min(
        # code_execution_time_list)}. All execution times: {
        # code_execution_time_list}")
        break