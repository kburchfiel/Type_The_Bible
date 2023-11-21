# %% [markdown]
# # Type Through The Bible
# 
# By Kenneth Burchfiel
# 
# Code is released under the MIT license; Bible verses are from the Web English Bible (Catholic Edition)* and are in the public domain.
# 
# \* Genesis was not found within the original WEB Catholic Edition folder, so I copied in files from another Web English Bible translation instead. I imagine, but am not certain, that these files are the same as the actual Catholic Edition Genesis files.

# %% [markdown]
# # Instructions for getting started:
# 
# If you have just downloaded this game, you'll want to create new copies of the **WEB_Catholic_Version_for_game_updated.csv**, **results.csv**, and **character_stats.csv** files. That way, the files will show your results and progress, not mine. You can do so using the following steps:
# 
# 1. Rename the existing versions of these files as **WEB_Catholic_Version_for_game_updated_sample.csv**, **results_sample.csv**, and **character_stats_sample.csv**.
# 
# 2. Make a copy of **WEB_Catholic_Version_for_game.csv** and rename it **WEB_Catholic_Version_for_game_updated.csv**.
# 
# 3. Make a copy of **blank_results_file.csv** and rename it **results.csv**.
# 
# 4. Make a copy of **blank_character_sttats_file.csv** and rename it **character_stats.csv**.
# 
# 
# You're now ready to play!

# %% [markdown]
# ## More documentation to come!

# %% [markdown]
# Next steps: (Not necessarily in order of importance)
# 
# * Finish documenting your v2 print code and the variables/ANSI escape codes that it uses
# * Improve chart formatting (e.g. add titles, legend names, etc.)
# * Add documentation to other parts of the code as well
# * Revise verse numbering for chapters that have lots of verses grouped together. (You can use the PDF version of the WEB as a guide for this)
# * Add in WPM comparisons by accuracy (in both scatterplot and bar chart form. You can create accuracy bins for the bar chart; these bins could be created automatically or specified ahead of time)

# %%
import pandas as pd
pd.set_option('display.max_columns', 1000)
import time
import plotly.express as px
from getch import getch # Installed this library using pip install py-getch, not
# pip install getch. See https://github.com/joeyespo/py-getch
import numpy as np
from datetime import datetime, date, timezone # Based on 
# https://docs.python.org/3/library/datetime.html
import os
from colorama import just_fix_windows_console, Fore, Back, Style
# From https://github.com/tartley/colorama/blob/master/demos/demo01.py
just_fix_windows_console() # From https://github.com/tartley/colorama/blob/master/demos/demo01.py


# %%
extra_analyses = False

# %% [markdown]
# Checking whether the program is currently running on a Jupyter notebook:
# 
# (The program normally uses getch() to begin typing tests; however, I wasn't able to enter input after getch() got called within a Jupyter notebook and thus couldn't begin a typing test in that situation. Therefore, the program will use input() instead of getch() to start tests when running within a notebook.)

# %%
# The following method of determining whether the code is running
# within a Jupyter notebook is based on Gustavo Bezerra's response
# at https://stackoverflow.com/a/39662359/13097194 . I found that
# just calling get_ipython() was sufficient, at least on Windows and within
# Visual Studio Code; his answer is more complex.

try: 
    get_ipython()
    run_on_notebook = True
except:
    run_on_notebook = False

# print(run_on_notebook)

# %%
df_Bible = pd.read_csv('WEB_Catholic_Version_for_game_updated.csv')
df_Bible

# %%
df_results = pd.read_csv('results.csv', index_col='Test_Number')
df_results

# %% [markdown]
# Importing character-level stats: 

# %%
df_character_stats = pd.read_csv('character_stats.csv')
df_character_stats

# %%
for column in ['Local_Start_Time', 'UTC_Start_Time']:
    df_results[column] = pd.to_datetime(df_results[column])
df_results['WPM'] = df_results['WPM'].astype('float') # Prevents a glitch
# that can be caused when this column is stored as an object. The WPM
# column should only be in object format when the results table is blank.
df_results

# %%
# # If you accidentally overwrite your Unix_Start_Time values with something else,
# # you can recreate them using UTC_Start_Time values as follows:
# # (This code is based on that shown in
# # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#from-timestamps-to-epoch )
# df_results['Unix_Start_Time'] = ((df_results['UTC_Start_Time'] - pd.Timestamp(
# "1970-01-01", tz = 'utc')) // pd.Timedelta("1ns") / 1000000000)
# df_results

# %%
# If you ever need to drop a particular result,
# you can do so as follows:
# df_results.drop(17, inplace = True)
# df_results.to_csv('results.csv') # We want to preserve the index so as not
# to lose our 'Test_Number' values
# df_results

# %%
# Creating an RNG seed:
# In order to make the RNG values a bit more random, the following code will
# derive the RNG seed from the decimal component of the current timestamp.
# This seed will change 1 million times each second.

# Using the decimal component of time.time() to select an RNG seed:
current_time = time.time()
decimal_component = current_time - int(current_time) # This 
# line retrieves the decimal component of current_time. int() is used instead
# of np.round() so that the code won't ever round current_time up prior
# to the subtraction operation, which would return a different value.
# I don't think that converting current_time to an integer (e.g. via
# np.int64(current_time)) is necessary, as int() appears to handle at least 
# some integers larger than 32 bits in size just fine.
decimal_component
random_seed = round(decimal_component * 1000000)
decimal_component, random_seed

# %%
rng = np.random.default_rng(random_seed) # Based on
# https://numpy.org/doc/stable/reference/random/index.html?highlight=random#module-numpy.random

# %%
df_Bible

# %% [markdown]
# [This fantastic answer](https://stackoverflow.com/a/23294659/13097194) by Kevin at Stack Overflow proved helpful in implementing user validation code within this program. 

# %%
def select_verse():
    print("Select a verse to type! Enter 0 to receive a random verse\n\
or enter a verse number (see 'Verse_Order column of\n\
the WEB_Catholic_Version.csv spreadsheet for a list of numbers to enter)\n\
to select a specific verse.\n\
You can also enter -2 to receive a random verse that you haven't yet typed\n\
or -3 to choose the first Bible verse that hasn't yet been typed.")
    while True:
        try:
            response = int(input())
        except:
            print("Please enter an integer corresponding to a particular Bible \
verse or 0 for a randomly selected verse.")
            continue # Allows the user to retry entering a number

        if response == 0:
            return rng.integers(1, 35380) # Selects any verse within the Bible.
            # there are 35,379 verses present, so we'll pass 1 (the first verse)
            # and 35,380 (1 more than the last verse, as rng.integers won't 
            # include the final number within the range) to rng.integers().
        # The next two elif statements will require us to determine which 
        # verses haven't yet been typed. We can do so by filtering df_Bible
        # to include only untyped verses.
        elif response == -2:
            verses_not_yet_typed = list(
                df_Bible.query("Typed == 0")['Verse_Order'].copy())
            if len(verses_not_yet_typed) == 0:
                print("Congratulations! You have typed all verses from \
the Bible, so there are no new verses to type! Try selecting another option \
instead.")
                continue
            print(f"{len(verses_not_yet_typed)} verses have not yet \
been typed.")
            return rng.choice(verses_not_yet_typed) # Chooses one of these
            # untyped verses at random
        elif response == -3:
            verses_not_yet_typed = list(
                df_Bible.query("Typed == 0")['Verse_Order'].copy())
            if len(verses_not_yet_typed) == 0:
                print("Congratulations! You have typed all verses from \
the Bible, so there are no new verses to type! Try selecting another option \
instead.")
                continue
            print(f"{len(verses_not_yet_typed)} verses have not yet \
been typed.")
            verses_not_yet_typed.sort() # Probably not necessary, as df_Bible
            # is already sorted from the first to the last verse.
            return verses_not_yet_typed[0]
        
        else:
            if ((response >= 1) 
            & (response <= 35379)): # Making sure that the response is 
                # an integer between 1 and 35,379 (inclusive) so that it 
                # matches one of the Bible verse numbers present:                    
                return response
            else: # Will be called if a non-integer number was passed
                    # or if the integer didn't correspond to a Bible verse
                    # number. 
                print("Please enter an integer between 1 and 35,379.") # Since
                # we're still within a While loop, the user will be returned
                # to the initial try/except block.


# %%
column_width = 120
column_width - (55 % column_width)

# %%
def run_typing_test(verse_number, results_table, character_stats_table, test_type = 'v2'):
    '''This function calculates how quickly the user types the characters
    passed to the Bible verse represented by verse_number, then saves those 
    results to the DataFrame passed to results_table.'''

    # Retrieving the verse to be typed:
    # The index begins at 0 whereas the list of verse numbers begins at 1,
    # so we'll need to subtract 1 from verse_number in order to obtain
    # the verse's index.
    verse = df_Bible.iloc[verse_number-1]['Verse']
    book = df_Bible.iloc[verse_number-1]['Book_Name']
    chapter = df_Bible.iloc[verse_number-1]['Chapter_Name']
    verse_number_within_chapter = df_Bible.iloc[verse_number-1]['Verse_#']
    verse_number_within_Bible = df_Bible.iloc[
        verse_number-1]['Verse_Order']
    
    # I moved these introductory comments out of the following while loop
    # in order to simplify the dialogue presented to users during retest
    # attempts.
    print(f"Welcome to the typing test! Your verse to type is {book} \
{chapter}:{verse_number_within_chapter} (verse {verse_number_within_Bible} \
within the Bible .csv file).\n")
    if run_on_notebook == False:
        print("Press any key to begin typing!")
    else:
        print("Press Enter to begin the test!")
    
    complete_flag = 0
    while complete_flag == 0:
        print(f"Here is the verse:\n\n{verse}") 

        if run_on_notebook == False: # In this case, we can use getch()
            # to begin the test.
        # time.sleep(3) # I realized that players could actually begin typing
        # during this sleep period, thus allowing them to complete the test
        # faster than intended. Therefore, I'm now having the test start
        # after the player hits a character of his/her choice. getch()
        # accomplishes this task well.
        # A simpler approach would be to add in an additional input block
        # and have the player begin after he/she presses Enter, but that would
        # cause the player's right hand to leave the default home row position,
        # which could end up slowing him/her down. getch() allows any character
        # to be pressed (such as the space bar) and thus avoids this issue.

            start_character = getch() # See https://github.com/joeyespo/py-getch
        
        else: # When running the program within a Jupyter notebook, I wasn't
            # able to enter input after getch() was called, so I created
            # an alternative start method below that simply uses input().
            input()

        # The following line determines the width of the terminal just before
        # the beginning of the typing test. This width will help determine
        # when a line has been completed, which will in turn inform
        # when to move the cursor up and how many lines to fill with
        # blank spaces.

        if run_on_notebook == False: # The following line crashed for me
            # when running the program within a notebook.
            column_width = os.get_terminal_size().columns
        # get_terminal_size() is cross-platform. See
        # https://docs.python.org/3.8/library/os.html?highlight=get_terminal_size#os.get_terminal_size
        else:
            column_width = 120 # The default column width for my
            # terminal

        # print(f"Column width is {column_width}")
        print("Start!")      
        if test_type == 'v1': 
            # This is a simple typing test setup that receives input from
            # the user when 'Enter' is pressed, then checks that input
            # against the verse. Because it doesn't check the response
            # for accuracy as the player types, the player might not realize
            # a character was mistyped until the very end, which can get
            # frustrating. Therefore, I've now added in a new version
            # of the test (called 'v2') that can be used instead. 
            no_mistakes = np.NaN
            backspaces_as_pct_of_length = np.NaN
            incorrect_characters_as_pct_of_length = np.NaN
            min_character_time = np.NaN
            median_character_time = np.NaN
            max_character_time = np.NaN
            local_start_time = pd.Timestamp.now()
            utc_start_time = pd.Timestamp.now(timezone.utc)
            character_stats_for_latest_test = pd.DataFrame(
                {'Character': {},
                'Time Used to Type Last Character (ms)': {},
                'Last 2 Characters': {},
                'Time Used to Type Last 2 Characters (ms)': {}}
                )

            # I used to use ISO8601-compatible timestamps via the following
            # lines, but decided to switch to a value that Pandas would 
            # immediately recognize as a datetime.
            # local_start_time = datetime.now().isoformat()
            # utc_start_time = datetime.now(timezone.utc).isoformat()

            typing_start_time = time.time()
            verse_response = input() 
            # The following code will execute once the player finishes typing and
            # hits Enter. (Having the program evaluate the player's entry only after
            # 'Enter' is pressed isn't the best option, as the time required to
            # hit Enter will reduce the player's reported WPM. Version v2, 
            # shown below, stops the test right when the final correct
            # character is typed, which will make the final WPM slightly faster.
            typing_end_time = time.time()
            typing_time = typing_end_time - typing_start_time

        elif test_type == 'v2':
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
            local_start_time = pd.Timestamp.now()
            utc_start_time = pd.Timestamp.now(timezone.utc)
            typing_start_time = time.time()
            while True: # This while loop allows the player to enter
                # multiple characters.
                character = getch() # getch() allows each character to be 
                # checked, making it easier to identify mistyped words.
                character_press_time = time.time()

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
                    # Adding the time it took to type the last character
                    # to the list: (Note that the time it takes to 
                    # enter a backspace won't be included.)
                    if character != b'\x08':
                        character_timestamp_list.append(character_press_time)
                        correct_consecutive_entries += 1

                        if correct_consecutive_entries >= 2:
                            # Limiting the additions to character_time_list
                            # to cases in which 2+ characters have been
                            # typed correctly in a row will prevent the data 
                            # from getting skewed by incorrect results. 
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
                            'Time Used to Type Last Character (ms)': 1000 * (
                                character_timestamp_list[-1] - 
                                character_timestamp_list[-2]),
                                'Last 2 Characters':verse_response[-2:],
                                'Time Used to Type Last 2 Characters (ms)':
                                1000 * (character_timestamp_list[-1] - 
                                character_timestamp_list[-3])}
                            )

                else:
                    no_mistakes = 0 # This flag will remain at 0 for the 
                    # rest of the race.
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
                    typing_end_time = time.time()
                    typing_time = typing_end_time - typing_start_time
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
                    # Note that each value will be converted from
                    # seconds to milliseconds.
                    min_character_time = 1000*min(character_time_list)
                    median_character_time = 1000*np.median(character_time_list)
                    max_character_time= 1000*max(character_time_list)

                    character_stats_for_latest_test = pd.DataFrame(
                        character_stats_list)
                    break

        if verse_response == verse:
            print(f"Well done! You typed the verse correctly.")
            complete_flag = 1 # Setting this flag to 1 allows the player to exit
            # out of the while statement.
        elif (verse_response.lower() == 'exit') or ('`' in verse_response):
            print("Exiting typing test.")
            return results_table # Exits the function without saving the 
            # current test to results_table or df_Bible. This function has
            # been updated to work with both versions of the typing
            # test.
        else:
            print("Sorry, that wasn't the correct input.")   
            # Identifying incorrectly typed words:
            verse_words = verse.split(' ')
            verse_response_words = verse_response.split(' ')[0:len(verse_words)]
            # I added in the [0:len(verse_words)] filter so that the following
            # for loop would not attempt to access more words that were 
            # present in the original verse (which would cause the game
            # to crash with an IndexError).
            for i in range(len(verse_response_words)):
                if verse_response_words[i] != verse_words[i]:
                    print(f"Word number {i} ('{verse_words[i]}') \
was typed '{verse_response_words[i]}'.")
                    # If the response has more or fewer words than the original
                    # verse, some correctly typed words might appear within
                    # this list also.
            print("Try again!") # complete_flag will still be 0 in this case,
            # so the while loop will continue back to the beginning.

    # Calculating typing statistics and storing them within a single-row
    # DataFrame:

    cps = len(verse) / typing_time # Calculating characters per second
    wpm = cps * 12 # Multiplying by 60 to convert from characters to minutes, 
    # then dividing by 5 to convert from characters to words.
    wpm

    # print(min_character_time, median_character_time, max_character_time)

    character_stats_table = pd.concat(
        [character_stats_table, character_stats_for_latest_test]).reset_index(
            drop=True)

    # Creating a single-row DataFrame that stores the player's results:
    df_latest_result = pd.DataFrame(index = [
        len(results_table)+1], data = {'Unix_Start_Time':typing_start_time, 
    'Local_Start_Time':local_start_time,
    'UTC_Start_Time':utc_start_time,
    'Characters':len(verse),
    'Seconds':typing_time, 
    'CPS': cps,
    'WPM':wpm,
    'Mistake_Free_Test':no_mistakes,
    'Backspaces as % of Verse Length': backspaces_as_pct_of_length,
    'Incorrect Characters as % of Verse Length': \
incorrect_characters_as_pct_of_length,
    'Min Character Time (ms)': min_character_time,
    'Median Character Time (ms)': median_character_time,
    'Max Character Time (ms)': max_character_time,
    'Book': book,
    'Chapter': chapter,
    'Verse #': verse_number_within_chapter,
    'Verse':verse, 
    'Verse_Order':verse_number_within_Bible})
    df_latest_result.index.name = 'Test_Number'
    df_latest_result

    # Adding this new row to results_table:
    results_table = pd.concat([results_table, df_latest_result])
    # Note: I could also have used df.at or df.iloc to add a new row
    # to df_latest_result, but I chose a pd.concat() setup in order to ensure
    # that the latest result would never overwrite an earlier result.
    

    # Rank and percentile data needs to be recalculated after each test,
    # as later results can affect the rank and percentile of earlier results.
    # I could compute these statistics later, but calculating them here
    # allows the player to view his/her statistics after each test.

    results_table['WPM_Rank'] = results_table['WPM'].rank(
    ascending = False, method = 'min').astype('int')
    results_table['WPM_Percentile'] = results_table['WPM'].rank(pct=True)*100
    latest_rank = results_table.iloc[-1]['WPM_Rank']
    # Note: These percentile results may differ from the results
    # calculated by np.quartile later in this function, likely a result of
    # different calculation methodologies. These differences should narrow
    # as more tests are completed.

    latest_percentile = results_table.iloc[-1]['WPM_Percentile'].round(3)
    number_of_tests = len(results_table)
    last_10_avg = results_table['WPM'].rolling(10).mean().iloc[-1]
    
    # The player's rolling 10-race average will be NaN until he/she has
    # completed 10 tests. Therefore, the following if statement will 
    # return a blank last 10 races report unless at least 10 tests
    # are present in results_table.
    if len(results_table) >= 10:
        last_10_report = f' You have averaged \
{last_10_avg.round(3)} WPM over your last 10 tests.' # The space
    # space before 'You' separates this text from the rest of
    # the print statement below.
    else:
        last_10_report = ''

    print(f"Your CPS and WPM were {round(cps, 3)} and {round(wpm, 3)}, \
respectively. Your WPM percentile was {latest_percentile} \
({latest_rank} out of {number_of_tests} tests).{last_10_report}")  

    # Updating df_Bible to store the player's results: (This will allow the
    # player to track how much of the Bible he/she has typed so far)
    df_Bible.at[verse_number-1, 'Typed'] = 1 # Denotes that this verse
    # has now ben typed
    df_Bible.at[verse_number-1, 'Tests'] += 1 # Keeps track of how 
    # many times this verse has been typed
    fastest_wpm = df_Bible.at[verse_number-1, 'Fastest_WPM']
    if ((pd.isna(fastest_wpm) == True) | (wpm > fastest_wpm)): 
        # In these cases, we should replace the pre-existing Fastest_WPM value
        # with the WPM the player just achieved.
        # I found that 5 > np.NaN returned False, so if I only checked for
        # wpm > fastest_wpm, blank fastest_wpm values would never get overwritten.
        # Therefore, I chose to also check for NaN values 
        # in the above if statement.
        df_Bible.at[verse_number-1, 'Fastest_WPM'] = wpm

    # Autosaving results as separate files: (That way, if the script crashes,
    # the player won't lose all of his/her progress.)
    try:
        results_table.to_csv('df_results_autosave.csv', index = False)
        df_Bible.to_csv('WEB_Catholic_Version_for_game_updated_autosave.csv')
        character_stats_table.to_csv('character_stats_autosave.csv', index = False)
    except:
        print("At least one of the autosave files could not be saved. Close \
out of any open autosave files before starting the next test \
so that they can be updated.")
    return (results_table, character_stats_table)


# %%
# run_typing_test(1, results_table=df_results)

# %%
def select_subsequent_verse(previous_verse_number):
    '''This function allows the player to specify which verse to
    type next, or, alternatively, to exit the game.'''
    print("Press 0 to retry the verse you just typed; \
1 to type the next verse; 2 to type the next verse that hasn't yet been typed; \
3 to select a different verse; \
-1 to save your results and exit; \
and -2 to save your results without running the analysis \
portion of the script.") # The analysis portion can take a decent amount of
# time to run, which is why an option to save without running these analyses
# was added in. These analyses can then get updated during a later session.
    while True: 
            try:
                response = int(input())
            except: # The user didn't enter a number.
                print("Please enter a number.")      
                continue
            if response == 0:
                return previous_verse_number
            elif response == 1:
                if previous_verse_number == 35379: # The verse order value
                    # corresponding to the final verse of Revelation
                    print("You just typed the last verse in the Bible, so \
there's no next verse to type! Please enter an option other than 1.\n")
                    continue
                else:
                    return previous_verse_number + 1
            elif response == 2:
                # In this case, we'll retrieve a list of verses that haven't
                # yet been typed; filter that list to include only verses
                # greater than previous_verse_number; and then select
                # the first verse within that list (i.e. the next 
                # untyped verse).
                verses_not_yet_typed = list(df_Bible.query(
                    "Typed == 0")['Verse_Order'].copy())
                if len(verses_not_yet_typed) == 0:
                    print("Congratulations! You have typed all verses from \
the Bible, so there are no new verses to type! Try selecting another option \
instead.")
                    continue
                print(f"{len(verses_not_yet_typed)} verses have not yet \
been typed.")
                verses_not_yet_typed.sort() 
                next_untyped_verses = [verse for verse in verses_not_yet_typed 
                if verse > previous_verse_number]
                return next_untyped_verses[0]
            elif response == 3:
                return select_verse()
            elif response in [-1, -2]:
                return response
            else: # A number other than -2, -1, 0, 1, 2, or 3 was passed.
                print("Please enter either -2, -1, 0, 1, 2, or 3.\n")  

# %%
def calculate_current_day_results(df):
    ''' This function reports the number of characters, total verses, and 
    unique verses that the player has typed so far today.'''
    df_current_day_results = df[pd.to_datetime(
        df['Local_Start_Time']).dt.date == datetime.today().date()].copy()
    if len(df_current_day_results) == 0:
        result_string = "You haven't typed any Bible verses yet today."
    else:
        characters_typed_today = df_current_day_results['Characters'].sum()
        total_verses_typed_today = len(df_current_day_results)

        # Allowing for both singular and plural versions of 'verse' to 
        # be displayed:
        if total_verses_typed_today == 1:
            total_verses_string = 'verse'
        else:
            total_verses_string = 'verses'

        unique_verses_typed_today = len(df_current_day_results[
            'Verse_Order'].unique())

        if unique_verses_typed_today == 1:
            unique_verses_string = 'verse'
        else:
            unique_verses_string = 'verses'

        average_wpm_today = round(df_current_day_results['WPM'].mean(), 3)
        median_wpm_today = round(df_current_day_results['WPM'].median(), 3)
        result_string = f"So far today, you have typed \
{characters_typed_today} characters from {total_verses_typed_today} Bible \
{total_verses_string} (including {unique_verses_typed_today} unique \
{unique_verses_string}). Your mean and median WPM today are \
{average_wpm_today} and {median_wpm_today}, respectively."
    return result_string

# %%
def run_game(results_table, character_stats_table):
    '''This function runs Type Through the Bible by 
    calling various other functions. It allows users to select
    verses to type, then runs typing tests and stores the results in
    the DataFrame passed to results_table.'''
    
    print("Welcome to Type Through the Bible!")
    # The game will now share the player's progress for the current day:
    print(calculate_current_day_results(results_table))

    if run_on_notebook == True: # I haven't been able to get version
        # v2 of the typing test to work within a Jupyter notebook, 
        # so the following line forces notebook-based runs to use version v1.
        typing_test_version = 'v1'
    else: # In this case, the user gets to choose whether to to use 
        # v1 or v2.
        print("To switch to a simpler typing test method that doesn't \
check your input as you type, enter v1. Otherwise, to stick with the \
recommended version, press Enter.")
        response = input()
        if (response == 'v1') or (run_on_notebook == True): # Version 2 likely
            # won't work within Jupyter notebooks, 
            # so the version will always be kept as v1 for notebook users.
            typing_test_version = 'v1'
        else:
            typing_test_version = 'v2'

    # The method for exiting a test in progress differs by typing test
    # version, so the game will now explain how the player can exit out of 
    # his/her version of the test.
    if typing_test_version == 'v1':
        print("Version 1 selected. Note that you can exit a test in \
progress by typing 'exit' and then hitting Enter.")
    if typing_test_version == 'v2':
        print("Version 2 selected. Note that you can exit a test in progress \
by hitting the ` (backtick) key.")
              
              

    verse_number = select_verse()
    

    while True: # Allows the game to continue until the user exits
        results_table, character_stats_table = run_typing_test(
            verse_number=verse_number, 
        results_table=results_table, 
        character_stats_table=character_stats_table,
        test_type = typing_test_version)
        # The game will next share an updated progress report:
        print(calculate_current_day_results(results_table))
        
        # The player will now be prompted to select a new verse number 
        # (or to save and quit). This verse_number, provided it is not -1,
        # will then be passed back to run_typing_test().
        verse_number = select_subsequent_verse(
            previous_verse_number=verse_number)
        if verse_number == -1: # In this case, the game will quit and the 
            # user's new test results will be saved to results_table.
            run_analyses = 1
            return (results_table, character_stats_table, run_analyses)
        if verse_number == -2: # In this case, the game will quit and the 
            # user's new test results will be saved to results_table.
            # However, the analysis portion of the script will be skipped 
            # in order to save time.
            run_analyses = 0
            return (results_table, character_stats_table, run_analyses)


# %%
df_results, df_character_stats, run_analyses = run_game(results_table = df_results, character_stats_table=df_character_stats)

# %%
df_results

# %% [markdown]
# If df_results is blank (e.g. because the player exited out of his/her first typing test during his/her first game), some of the following code will likely crash, because they are expecting results to be present within df_results. Therefore, the program will exit out early instead of continuing on.

# %%
if len(df_results) == 0:
    print("No results have been entered, so there is nothing to save or \
analyze. Exiting program in 5 seconds.")
    time.sleep(5) # Allows the user to view the above message
    raise SystemExit # See https://stackoverflow.com/a/19747562/13097194

# %%
# Updating certain df_Bible columns to reflect new results:

# %%
df_Bible['Characters_Typed'] = df_Bible['Characters'] * df_Bible['Typed']
df_Bible['Total_Characters_Typed'] = df_Bible['Characters'] * df_Bible['Tests']
df_Bible

# %%
characters_typed_sum = df_Bible['Characters_Typed'].sum()
proportion_of_Bible_typed = characters_typed_sum / df_Bible['Characters'].sum()

print(f"You have typed {characters_typed_sum} characters so far, \
which represents {round(100*proportion_of_Bible_typed, 4)}% of the Bible.")

# %% [markdown]
# # Adding in additional values and statistics to df_results:
# 
# (The following cell was derived from [this script](https://github.com/kburchfiel/typeracer_data_analyzer/blob/master/typeracer_data_analyzer_v2.ipynb) that I wrote.)
# 
# These statistics will get recreated whenever the script is run; this approach allows for the results to be revised as needed (e.g. if certain rows are removed from the dataset).

# %%
df_results['Last 10 Avg'] = df_results['WPM'].rolling(10).mean()
df_results['Last 100 Avg'] = df_results['WPM'].rolling(100).mean()
df_results['Last 1000 Avg'] = df_results['WPM'].rolling(1000).mean()


df_results['Local_Start_Year'] = df_results['Local_Start_Time'].dt.year
df_results['Local_Start_Month'] = df_results['Local_Start_Time'].dt.month
df_results['Local_Start_Date'] = df_results['Local_Start_Time'].dt.date
df_results['Local_Start_Hour'] = df_results['Local_Start_Time'].dt.hour
df_results['Local_Start_Minute'] = df_results['Local_Start_Time'].dt.minute
df_results['Local_Start_10_Minute_Block'] = df_results[
'Local_Start_Minute'] // 10 + 1
df_results['Local_Start_15_Minute_Block'] = df_results[
'Local_Start_Minute'] // 15 + 1
df_results['Local_Start_30_Minute_Block'] = df_results[
'Local_Start_Minute'] // 30 + 1

df_results['Count'] = 1 # Useful for pivot tables that analyze test counts
# by book, month, etc.

# In order to more accurately calculate the largest number of characters 
# typed within a given block of time, we'll want to know the end time
# of each test. This can be calculated as the sum of the local start time
# and the number of seconds each test took.
df_results['Local_End_Time'] = df_results[
'Local_Start_Time'] + pd.to_timedelta(df_results['Seconds'], unit = 's')

df_results['Local_End_Year'] = df_results['Local_End_Time'].dt.year
df_results['Local_End_Month'] = df_results['Local_End_Time'].dt.month
df_results['Local_End_Date'] = df_results['Local_End_Time'].dt.date
df_results['Local_End_Hour'] = df_results['Local_End_Time'].dt.hour
df_results['Local_End_Minute'] = df_results['Local_End_Time'].dt.minute
df_results['Local_End_15_Minute_Block'] = df_results[
'Local_End_Minute'] // 15 + 1
df_results['Local_End_10_Minute_Block'] = df_results[
'Local_End_Minute'] // 10 + 1
df_results['Local_End_30_Minute_Block'] = df_results[
'Local_End_Minute'] // 30 + 1

# The following line uses a list comprehension to generate a cumulative average
# of all WPM scores up until the current race. .iloc searches from 0 to i+1 for
# each row so that that row is included in the calculation.
df_results['cumulative_avg'] = [round(np.mean(df_results.iloc[0:i+1]['WPM']),
3) for i in range(len(df_results))]
df_results

# %%
df_character_stats['Count'] = 1 # Will be useful when analyzing character
# statistics

# %%
print("Saving results:")

# %%
def attempt_save(df, filename, index):
    '''This function attempts to save the DataFrame passed to df to the file
    specified by filename. It allows players to retry the save operation
    if it wasn't initially successful (e.g. because the file was open at 
    the time), thus preventing them from losing their latest progress.
    The index parameter determines whether or not the DataFrame's index
    will be included in the .csv export. Set to True for results.csv
    but False for Web_Catholic_Version_for_game_updated.csv.'''
    while True:
        try: 
            df.to_csv(filename, index = index)
            return
        except:
            print("File could not be saved, likely because it is currently open. \
Try closing the file and trying again. Press Enter to retry.")
            input()

# %%
attempt_save(df_results, 'results.csv', index = True)

# %%
attempt_save(df_Bible, 'WEB_Catholic_Version_for_game_updated.csv', index = False)

# %%
attempt_save(df_character_stats, 'character_stats.csv', index = False)

# %%
print("Successfully saved updated copies of the Results, Character Stats, \
and Bible .csv files.")

# %%
if run_analyses == 0: # In this case, the analysis portion of the script will
    # be skipped. These analyses can be updated when the game is next played.
    print("Analyses won't be updated during this session. \
Exiting program in 3 seconds.")
    time.sleep(3) # Allows the user to view the above message
    raise SystemExit # See https://stackoverflow.com/a/19747562/13097194

# %% [markdown]
# # Visualizing the player's progress in typing the entire Bible:

# %%
analysis_start_time = time.time() # Allows us to determine how long the
# analyses took
print("Updating analyses:")

# %%
df_Bible['Count'] = 1

# %% [markdown]
# ### Creating a tree map within Plotly that visualizes the player's progress in typing the entire Bible:

# %%
# This code is based on https://plotly.com/python/treemaps/
# It's pretty amazing that such a complex visualization can be created using
# just one line of code. Thanks Plotly!
fig_tree_map_books_chapters_verses = px.treemap(
    df_Bible, path = ['Book_Name', 'Chapter_Name', 'Verse_#'], 
    values = 'Characters', color = 'Typed')
# fig_verses_typed

# %%
fig_tree_map_books_chapters_verses.write_html(
    'Analyses/tree_map_books_chapters_verses.html')

# %%
# # A similar chart that doesn't use the Typed column for color coding:
# (This chart, unlike fig_verses_typed above, won't change unless edits are 
# made to the code itself, so it can be 
# commented out after being run once.)
# fig_Bible_verses.write_html('Bible_tree_map.html')
# fig_Bible_verses = px.treemap(df_Bible, path = ['Book_Name', 
# 'Chapter_Name', 'Verse_#'], values = 'Characters')
# fig_Bible_verses

# %%
df_Bible

# %%
# This variant of the treemap shows chapters and verses rather than books,
# chapters, and verses.
if (run_on_notebook == True) & (extra_analyses == True):
    fig_tree_map_chapters_verses = px.treemap(df_Bible, path = [
        'Book_and_Chapter', 'Verse_#'], values = 'Characters', color = 'Typed')
    fig_tree_map_chapters_verses.write_html(
        'Analyses/tree_map_chapters_verses.html')
    fig_tree_map_chapters_verses.write_image(
        'Analyses/tree_map_chapters_verses.png', width = 7680, height = 4320)

# %%
# This variant of the treemap shows each verse as its own box, which results in 
# a very busy graph that takes a while to load within a web browser
# (if it even loads at all).

if (run_on_notebook == True) & (extra_analyses == True):
    fig_tree_map_verses = px.treemap(df_Bible, path = ['Verse_Order'], 
                                     values = 'Characters', color = 'Typed')
    fig_tree_map_verses.write_html('Analyses/tree_map_verses.html')
    fig_tree_map_verses.write_image('Analyses/tree_map_verses_8K.png', 
                                    width = 7680, height = 4320) 
    fig_tree_map_verses.write_image('Analyses/tree_map_verses_16K.png', 
                                    width = 15360, height = 8640) 
# fig_tree_map_verses.write_image('Analyses/tree_map_verses.png', width = 30720, 
# height = 17280) # Didn't end up rendering successfully, probably 
# because the dimensions were absurdly large!

# %% [markdown]
# ### Creating a bar chart that shows the proportion of each book that has been typed so far:

# %%
df_characters_typed_by_book = df_Bible.pivot_table(index = ['Book_Order', 
'Book_Name'], values = ['Characters', 'Characters_Typed'], 
aggfunc = 'sum').reset_index()
# Adding 'Book_Order' as the first index value allows for the pivot tables
# and bars to be ordered by that value.
df_characters_typed_by_book['proportion_typed'] = df_characters_typed_by_book[
    'Characters_Typed'] / df_characters_typed_by_book['Characters']
df_characters_typed_by_book.to_csv(
    'Analyses/characters_typed_by_book.csv')
df_characters_typed_by_book

# %%
fig_proportion_of_each_book_typed = px.bar(df_characters_typed_by_book, 
x = 'Book_Name', y = 'proportion_typed')
fig_proportion_of_each_book_typed.update_yaxes(range = [0, 1]) # Setting
# the maximum y value as 1 better demonstrates how much of the Bible
# has been typed so far
fig_proportion_of_each_book_typed.write_html(
    'Analyses/proportion_of_each_book_typed.html')
fig_proportion_of_each_book_typed.write_image(
    'Analyses/proportion_of_each_book_typed.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_proportion_of_each_book_typed

# %% [markdown]
# ### Creating a chart that compares the number of characters in each book with the number that have been typed:
# 
# This provides a clearer view of the player's progress in typing the Bible, as each bar's height is based on the number of characters. (In contrast, bars for fully typed small books will be just as high in fig_proportion_of_each_book_typed as those for fully typed large books.)

# %%
fig_characters_typed_in_each_book = px.bar(df_characters_typed_by_book, 
x = 'Book_Name', y = ['Characters', 'Characters_Typed'], barmode = 'overlay')
fig_characters_typed_in_each_book.write_html(
    'Analyses/characters_typed_by_book.html')
fig_characters_typed_in_each_book.write_image(
    'Analyses/characters_typed_by_book.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_characters_typed_in_each_book

# %% [markdown]
# ## Creating charts that show both book- and chapter-level data:

# %%
df_characters_typed_by_book_and_chapter = df_Bible.pivot_table(index = [
'Book_Order', 'Book_Name', 'Book_and_Chapter'], values = [
    'Characters', 'Characters_Typed'], aggfunc = 'sum').reset_index()
df_characters_typed_by_book_and_chapter[
'proportion_typed'] = df_characters_typed_by_book_and_chapter[
'Characters_Typed'] / df_characters_typed_by_book_and_chapter['Characters']
df_characters_typed_by_book_and_chapter.to_csv(
    'Analyses/characters_typed_by_book_and_chapter.csv')
df_characters_typed_by_book_and_chapter

# %% [markdown]
# The following chart shows both books (as bars) and chapters (as sections of these bars). These sections are also color coded by the proportion of each chapter that has been typed.

# %%
fig_characters_typed_in_each_book_and_chapter = px.bar(
df_characters_typed_by_book_and_chapter, x = 'Book_Name', y = [
    'Characters'], color = 'proportion_typed')
fig_characters_typed_in_each_book_and_chapter.write_html(
    'Analyses/characters_typed_by_book_and_chapter.html')
fig_characters_typed_in_each_book_and_chapter.write_image(
    'Analyses/characters_typed_by_book_and_chapter.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_characters_typed_in_each_book_and_chapter

# %% [markdown]
# ## Creating similar charts at the chapter level:
# 
# These proved difficult to interpret due to the narrowness of the bars, so I'm commenting this code out for now.

# %%
# fig_proportion_of_each_chapter_typed = px.bar(df_characters_typed_by_chapter, 
# x = 'Book_and_Chapter', y = 'proportion_typed')
# fig_proportion_of_each_chapter_typed.update_yaxes(range = [0, 1]) # Setting
# # the maximum y value as 1 better demonstrates how much of the Bible
# # has been typed so far
# fig_proportion_of_each_chapter_typed.write_html(
# 'Analyses/proportion_of_each_chapter_typed.html')
# fig_proportion_of_each_chapter_typed

# fig_characters_typed_in_each_chapter = px.bar(df_characters_typed_by_chapter, 
# x = 'Book_and_Chapter', y = ['Characters', 'Characters_Typed'], 
# barmode = 'overlay')
# fig_characters_typed_in_each_chapter.write_html(
# 'Analyses/characters_typed_by_chapter.html')
# fig_characters_typed_in_each_chapter

# %% [markdown]
# # Endurance statistics (e.g. most characters/verses typed over a given time period):

# %% [markdown]
# ## Calculating the dates with the most characters and verses typed:
# 
# Note: In order to create more accurate analyses, I will filter the results to only include values with the same start and end periods. (For instance, if a given test began at 9:59 p.m. on 2023-11-17 but ended after 10 p.m., that test would get filtered out of a 'top hours by characters typed' report, since including it would extend the time frame analyzed beyond a 60-minute window.)

# %%
df_top_dates_by_characters = df_results.pivot_table(
    index = ['Local_Start_Date', 'Local_End_Date'], values = 'Characters', aggfunc = 'sum').reset_index(
    ).sort_values('Characters', ascending = False)
# By using both the start and end dates as pivot index values, we've already 
# separated results with different start and end dates from ones whose 
# start and end dates are the same. (This will prevent the tests included
# in a given date's calculation from extending beyond just that date.)
# We'll also filter the DataFrame to exclude any results whose start
# and end dates differ:
df_top_dates_by_characters = df_top_dates_by_characters.query("Local_Start_Date == Local_End_Date").head(50).copy()
df_top_dates_by_characters['Rank'] = df_top_dates_by_characters[
    'Characters'].rank(ascending = False, method = 'min').astype('int')
# Creating a column that shows both the rank and date: (This also prevents
# Plotly from converting the x axis to a date range, which would interfere
# with the order of the chart items)
df_top_dates_by_characters['Rank and Date'] = '#'+df_top_dates_by_characters[
    'Rank'].astype('str') + ': ' + df_top_dates_by_characters[
        'Local_Start_Date'].astype('str')
df_top_dates_by_characters.reset_index(drop=True,inplace=True)
df_top_dates_by_characters.to_csv(
    'Analyses/top_dates_by_characters.csv', index = False)
df_top_dates_by_characters

# %%
fig_top_dates_by_characters = px.bar(df_top_dates_by_characters, 
x = 'Rank and Date', y = 'Characters', text = 'Characters')
fig_top_dates_by_characters.update_xaxes(tickangle = 90)
fig_top_dates_by_characters.write_html('Analyses/top_dates_by_characters.html')
fig_top_dates_by_characters.write_image(
    'Analyses/top_dates_by_characters.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_dates_by_characters

# %%
df_top_dates_by_verses = df_results.pivot_table(
    index = ['Local_Start_Date', 'Local_End_Date'], 
    values = 'Count', aggfunc = 'sum').reset_index(
    ).rename(columns = {'Count':'Verses'}).sort_values(
        'Verses', ascending = False)
df_top_dates_by_verses = df_top_dates_by_verses.query(
    "Local_Start_Date == Local_End_Date").head(50).copy()
df_top_dates_by_verses['Rank'] = df_top_dates_by_verses['Verses'].rank(
    ascending = False, method = 'min').astype('int')
df_top_dates_by_verses['Rank and Date'] = '#'+df_top_dates_by_verses[
    'Rank'].astype('str') + ': ' + df_top_dates_by_verses[
        'Local_Start_Date'].astype('str')
df_top_dates_by_verses.reset_index(drop=True,inplace=True)
df_top_dates_by_verses.to_csv('Analyses/top_dates_by_verses.csv', index = False)
df_top_dates_by_verses

# %%
fig_top_dates_by_verses = px.bar(df_top_dates_by_verses, 
x = 'Rank and Date', y = 'Verses', text = 'Verses')
fig_top_dates_by_verses.update_xaxes(tickangle = 90)
fig_top_dates_by_verses.write_html('Analyses/top_dates_by_verses.html')
fig_top_dates_by_verses.write_image(
    'Analyses/top_dates_by_verses.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_dates_by_verses

# %% [markdown]
# ## Performing similar analyses by month:

# %%
df_top_months_by_characters = df_results.pivot_table(
    index = ['Local_Start_Year', 'Local_End_Year', 
    'Local_Start_Month', 'Local_End_Month'], 
    values = 'Characters', aggfunc = 'sum').reset_index(
    ).sort_values('Characters', ascending = False)
df_top_months_by_characters = df_top_months_by_characters.query(
    "Local_Start_Year == Local_End_Year & \
Local_Start_Month == Local_End_Month").head(50).copy()

df_top_months_by_characters['Rank'] = df_top_months_by_characters[
'Characters'].rank(ascending = False, method = 'min').astype('int')
df_top_months_by_characters['Rank and Month'] = '#'+df_top_months_by_characters[
    'Rank'].astype('str') + ': ' + df_top_months_by_characters[
        'Local_Start_Year'].astype('str') + '-' + df_top_months_by_characters[
            'Local_Start_Month'].astype('str')
df_top_months_by_characters.reset_index(drop=True,inplace=True)
df_top_months_by_characters.to_csv('Analyses/top_months_by_characters.csv', index = False)
df_top_months_by_characters

# %%
fig_top_months_by_characters = px.bar(df_top_months_by_characters, 
x = 'Rank and Month', y = 'Characters', text = 'Characters')
fig_top_months_by_characters.update_xaxes(tickangle = 90)
fig_top_months_by_characters.write_html(
    'Analyses/top_months_by_characters.html')
fig_top_months_by_characters.write_image(
    'Analyses/top_months_by_characters.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_months_by_characters

# %%
df_top_months_by_verses = df_results.pivot_table(
    index = ['Local_Start_Year', 'Local_Start_Month', 
    'Local_End_Year', 'Local_End_Month'], 
    values = 'Count', aggfunc = 'sum').reset_index(
    ).rename(columns={'Count':'Verses'}).sort_values(
        'Verses', ascending = False)
df_top_months_by_verses = df_top_months_by_verses.query(
    "Local_Start_Year == Local_End_Year & \
Local_Start_Month == Local_End_Month").head(50).copy()

df_top_months_by_verses['Rank'] = df_top_months_by_verses['Verses'].rank(
    ascending = False, method = 'min').astype('int')
df_top_months_by_verses['Rank and Month'] = '#'+df_top_months_by_verses[
    'Rank'].astype('str') + ': ' + df_top_months_by_verses[
        'Local_Start_Year'].astype('str') + '-' + df_top_months_by_verses[
            'Local_Start_Month'].astype('str')
df_top_months_by_verses.reset_index(drop=True,inplace=True)
df_top_months_by_verses.to_csv('Analyses/top_months_by_verses.csv', index = False)
df_top_months_by_verses

# %%
fig_top_months_by_verses = px.bar(df_top_months_by_verses, 
x = 'Rank and Month', y = 'Verses', text = 'Verses')
fig_top_months_by_verses.update_xaxes(tickangle = 90)
fig_top_months_by_verses.write_html('Analyses/top_months_by_verses.html')
fig_top_months_by_verses.write_image(
    'Analyses/top_months_by_verses.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_months_by_verses

# %% [markdown]
# ## Performing similar analyses for hours and for 30-, 15-, and 10-minute blocks:

# %%
df_top_hours_by_characters = df_results.pivot_table(index = ['Local_Start_Date', 
'Local_End_Date', 'Local_Start_Hour', 'Local_End_Hour'], values = 'Characters', 
aggfunc = 'sum').reset_index().sort_values('Characters', ascending = False)
df_top_hours_by_characters = df_top_hours_by_characters.query(
"Local_Start_Date == Local_End_Date & \
Local_Start_Hour == Local_End_Hour").head(100).copy()
df_top_hours_by_characters['Hour'] = df_top_hours_by_characters[
'Local_Start_Date'].astype('str') + ' ' + df_top_hours_by_characters[
'Local_Start_Hour'].astype('str') 
df_top_hours_by_characters.to_csv('Analyses/top_hours_by_characters.csv', index = False)
df_top_hours_by_characters

# %%
fig_top_hours_by_characters = px.bar(df_top_hours_by_characters, 
x = 'Hour', y = 'Characters', text = 'Characters')
fig_top_hours_by_characters.update_xaxes(type = 'category')
fig_top_hours_by_characters.write_html('Analyses/top_hours_by_characters.html')
fig_top_hours_by_characters.write_image(
    'Analyses/top_hours_by_characters.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_hours_by_characters

# %%
df_top_30m_by_characters = df_results.pivot_table(index = ['Local_Start_Date', 
'Local_End_Date', 'Local_Start_Hour', 'Local_End_Hour', 
'Local_Start_30_Minute_Block', 'Local_End_30_Minute_Block'], 
values = 'Characters', aggfunc = 'sum').reset_index().sort_values(
'Characters', ascending = False)
df_top_30m_by_characters = df_top_30m_by_characters.query(
"Local_Start_Date == Local_End_Date & Local_Start_Hour == Local_End_Hour \
& Local_Start_30_Minute_Block == Local_End_30_Minute_Block").head(100).copy()
df_top_30m_by_characters['30-Minute Block'] = df_top_30m_by_characters[
'Local_Start_Date'].astype('str') + ' ' + df_top_30m_by_characters[
'Local_Start_Hour'].astype('str') + '_' + df_top_30m_by_characters[
'Local_Start_30_Minute_Block'].astype('str')
df_top_30m_by_characters.to_csv('Analyses/top_30m_by_characters.csv', index = False)
df_top_30m_by_characters

# %%
fig_top_30m_by_characters = px.bar(df_top_30m_by_characters, 
x = '30-Minute Block', y = 'Characters', text = 'Characters')
fig_top_30m_by_characters.update_xaxes(type = 'category')
fig_top_30m_by_characters.write_html(
'Analyses/top_30m_blocks_by_characters.html')
fig_top_30m_by_characters.write_image(
    'Analyses/top_30m_blocks_by_characters.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_30m_by_characters

# %%
df_top_15m_by_characters = df_results.pivot_table(index = [
'Local_Start_Date', 'Local_End_Date', 'Local_Start_Hour', 'Local_End_Hour', 
'Local_Start_15_Minute_Block', 'Local_End_15_Minute_Block'], 
values = 'Characters', aggfunc = 'sum').reset_index().sort_values(
'Characters', ascending = False)
# print(len(df_top_15m_by_characters))
df_top_15m_by_characters = df_top_15m_by_characters.query(
"Local_Start_Date == Local_End_Date & Local_Start_Hour == Local_End_Hour & \
Local_Start_15_Minute_Block == Local_End_15_Minute_Block").head(100).copy()
df_top_15m_by_characters['15-Minute Block'] = df_top_15m_by_characters[
'Local_Start_Date'].astype('str') + ' ' + df_top_15m_by_characters[
'Local_Start_Hour'].astype('str') + '_' + df_top_15m_by_characters[
'Local_Start_15_Minute_Block'].astype('str')
# print(len(df_top_15m_by_characters))
df_top_15m_by_characters.to_csv('Analyses/top_15m_by_characters.csv', index = False)
df_top_15m_by_characters

# %%
fig_top_15m_by_characters = px.bar(df_top_15m_by_characters, 
x = '15-Minute Block', y = 'Characters', text = 'Characters')
fig_top_15m_by_characters.update_xaxes(type = 'category')
fig_top_15m_by_characters.write_html(
'Analyses/top_15m_blocks_by_characters.html')
fig_top_15m_by_characters.write_image(
    'Analyses/top_15m_blocks_by_characters.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_15m_by_characters

# %%
df_top_10m_by_characters = df_results.pivot_table(index = ['Local_Start_Date', 
'Local_End_Date', 'Local_Start_Hour', 'Local_End_Hour', 
'Local_Start_10_Minute_Block', 'Local_End_10_Minute_Block'], 
values = 'Characters', aggfunc = 'sum').reset_index().sort_values(
'Characters', ascending = False)
# print(len(df_top_10m_by_characters))
df_top_10m_by_characters = df_top_10m_by_characters.query(
"Local_Start_Date == Local_End_Date & Local_Start_Hour == Local_End_Hour \
& Local_Start_10_Minute_Block == Local_End_10_Minute_Block").head(100).copy()
df_top_10m_by_characters['10-Minute Block'] = df_top_10m_by_characters[
'Local_Start_Date'].astype('str') + ' ' + df_top_10m_by_characters[
'Local_Start_Hour'].astype('str') + '_' + df_top_10m_by_characters[
'Local_Start_10_Minute_Block'].astype('str')
# print(len(df_top_10m_by_characters))
df_top_10m_by_characters.to_csv('Analyses/top_10m_by_characters.csv', index = False)
df_top_10m_by_characters

# %%
fig_top_10m_by_characters = px.bar(df_top_10m_by_characters, 
x = '10-Minute Block', y = 'Characters', text = 'Characters')
fig_top_10m_by_characters.update_xaxes(type = 'category')
fig_top_10m_by_characters.write_html(
'Analyses/top_10m_blocks_by_characters.html')
fig_top_10m_by_characters.write_image(
    'Analyses/top_10m_blocks_by_characters.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_10m_by_characters

# %% [markdown]
# # Analyzing WPM data:
# 
# (Some of this section's code derives from my work in [this script](https://github.com/kburchfiel/typeracer_data_analyzer/blob/master/typeracer_data_analyzer_v2.ipynb).)
# 

# %% [markdown]
# Top 20 WPM results:

# %%
df_top_100_wpm = df_results.sort_values('WPM', ascending = False).head(
    100).copy()
df_top_100_wpm.insert(0, 'Rank', df_top_100_wpm['WPM'].rank(
    ascending = False, method = 'min').astype('int'))
# method = 'min' assigns the lowest rank to any rows that happen to have
# the same WPM. See 
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rank.html
df_top_100_wpm.to_csv('Analyses/top_100_wpm.csv')
df_top_100_wpm

# %%
fig_top_100_wpm = px.bar(df_top_100_wpm, x = 'Rank', y = 'WPM', 
text_auto = '.6s')
fig_top_100_wpm.write_html('Analyses/top_100_wpm.html')
fig_top_100_wpm.write_image('Analyses/top_100_wpm.png', 
width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_100_wpm

# %% [markdown]
# Top 'Last 10 Average' values:

# %%
if len(df_results) >= 10: # If fewer than 10 tests are present in df_results,
    # there won't be anything to graph (and the following code will raise
    # an error), so this section should be skipped.
    df_top_last_10_avg_results = df_results.sort_values(
    'Last 10 Avg', ascending = False).head(20).copy()
    df_top_last_10_avg_results.insert(0, 'Rank', 
    df_top_last_10_avg_results['Last 10 Avg'].rank(ascending = False, 
    method = 'min').astype('int'))
    df_top_last_10_avg_results.to_csv('Analyses/top_last_10_avg_results.csv', index = False)
    df_top_last_10_avg_results

# %%
if len(df_results) >= 10:
    fig_top_last_10_average_wpm = px.bar(df_top_last_10_avg_results, x = 'Rank', 
    y = 'Last 10 Avg', text_auto = '.6s')
    fig_top_last_10_average_wpm.write_html('Analyses/top_last_10_average_wpm.html')
    fig_top_last_10_average_wpm.write_image('Analyses/top_last_10_average_wpm.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
    fig_top_last_10_average_wpm

# %% [markdown]
# # Showing WPM results and moving averages by test number:

# %%
df_results

# %%
fig_df_results_by_test_number = px.line(df_results, x = df_results.index, 
y = ['WPM', 'Last 10 Avg', 'Last 100 Avg', 'Last 1000 Avg', 'cumulative_avg'])
fig_df_results_by_test_number.write_html('Analyses/results_by_test_number.html')
fig_df_results_by_test_number.write_image('Analyses/results_by_test_number.png', 
width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_df_results_by_test_number

# %% [markdown]
# ## Creating WPM histograms for (1) all tests and (2) the last 1000 tests:
# 
# (Until you've taken more than 1,000 tests, these histograms will have the same appearance.)

# %%
fig_wpm_histogram = px.histogram(x = df_results['WPM'], nbins = 50, 
text_auto = True)
fig_wpm_histogram.update_layout(bargroupgap = 0.1) # Adds a bit of space
# in between histogram bars. See https://stackoverflow.com/a/62925197/13097194
fig_wpm_histogram.write_html('Analyses/wpm_histogram.html')
fig_wpm_histogram.write_image('Analyses/wpm_histogram.png', 
width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_wpm_histogram


# %%
fig_wpm_histogram = px.histogram(x = df_results.tail(1000)['WPM'], nbins = 50, 
text_auto = True)
fig_wpm_histogram.update_layout(bargroupgap = 0.1) # Adds a bit of space
# in between histogram bars. See https://stackoverflow.com/a/62925197/13097194
fig_wpm_histogram.write_html('Analyses/wpm_histogram_last_1000.html')
fig_wpm_histogram.write_image('Analyses/wpm_histogram_last_1000.png', 
width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_wpm_histogram


# %% [markdown]
# ## Evaluating average results by month:

# %%
df_results_by_month = df_results.pivot_table(
    index = ['Local_Start_Year', 'Local_Start_Month'], values = [
'Count', 'WPM'], aggfunc = {'Count':'sum', 'WPM':'mean'}).reset_index()
df_results_by_month['Year/Month'] = df_results_by_month[
    'Local_Start_Year'].astype('str') + '-' + df_results_by_month[
    'Local_Start_Month'].astype('str')
df_results_by_month.to_csv('Analyses/results_by_month.csv', index = False)
df_results_by_month

# %%
fig_results_by_month = px.bar(df_results_by_month, x = 'Year/Month', 
y = 'WPM', color = 'Count', text_auto = '.6s')
fig_results_by_month.update_xaxes(type = 'category') # This line, based on
# Pracheta's response at https://stackoverflow.com/a/64424308/13097194,
# updates the axes to show the date-month pairs as strings rather than 
# as Plotly-formatted date values. This will also prevent missing
# months from appearing in the graph.
fig_results_by_month.write_html('Analyses/results_by_month.html')
fig_results_by_month.write_image('Analyses/results_by_month.png', 
width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_results_by_month

# %% [markdown]
# ## Evaluating average results by hour of day:

# %%
df_results_by_hour = df_results.pivot_table(index = ['Local_Start_Hour'], 
values = ['Count', 'WPM'], 
aggfunc = {'Count':'sum', 'WPM':'mean'}).reset_index()
df_results_by_hour.to_csv('Analyses/results_by_hour.csv')
df_results_by_hour

# %%
fig_results_by_hour = px.bar(df_results_by_hour, x = 'Local_Start_Hour', 
y = 'WPM', color = 'Count', text_auto = '.6s')
fig_results_by_hour.write_html('Analyses/results_by_hour.html')
fig_results_by_hour.write_image('Analyses/results_by_hour.png', 
width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_results_by_hour

# %% [markdown]
# # Comparing mean WPMs by Bible books:

# %%
df_wpm_by_book = df_results.pivot_table(index = 'Book', values = 'WPM', 
aggfunc = ['count', 'mean'], margins = True, 
margins_name = 'Total').reset_index()
df_wpm_by_book.columns = 'Book', 'Tests', 'WPM'
df_wpm_by_book.sort_values('WPM', ascending = False, inplace = True)
df_wpm_by_book.reset_index(drop=True,inplace=True)
df_wpm_by_book.to_csv('Analyses/mean_wpm_by_book.csv')
df_wpm_by_book


# %%
# The following chart will display a bar for each book for which at least one 
# test has been taken. It will also show a line that corresponds to the player's
# overall WPM across all books. The bars are colored by test count, making
# it easier to identify which bars might be skewed by a low number of results.
# The 'Total' value in df_wpm_by_book is displayed as a line instead of as
# a color so as not to interfere with the color gradient.

# Retrieving the total mean WPM value in df_wpm_by_book:
total_mean_wpm = df_wpm_by_book.query("Book == 'Total'").iloc[0]['WPM']
total_mean_wpm

fig_mean_wpm_by_book = px.bar(df_wpm_by_book.query("Book != 'Total'"), 
x = 'Book', y = 'WPM', color = 'Tests', text_auto = '.6s')
fig_mean_wpm_by_book.add_shape(type = 'line', x0 = -0.5, 
x1 = len(df_wpm_by_book) -1.5, y0 = total_mean_wpm, y1 = total_mean_wpm)
# See https://plotly.com/python/shapes/ for the add_shape() code.
# The use of -0.5 and len() - 1.5 is based on gleasocd's answer at 
# https://stackoverflow.com/a/40408960/13097194 . len(df) - 0.5 would normally
# work, except that I reduced the size of the DataFrame by 1 when excluding
# the 'Total' book.
fig_mean_wpm_by_book.write_html('Analyses/mean_wpm_by_book.html')
fig_mean_wpm_by_book.write_image('Analyses/mean_wpm_by_book.png', width = 1920, 
height = 1080, engine = 'kaleido', scale = 2)
fig_mean_wpm_by_book


# %% [markdown]
# ## Comparing mean WPM for error-free and non-error free tests:

# %%
# We'll only create the graph if there is at least one mistake-free
# result and one result with errors. (Otherwise, we won't be able to
# compare these two outcomes.)
if (len(df_results.query("Mistake_Free_Test == 0")) >= 1) & (
    len(df_results.query("Mistake_Free_Test == 1")) >= 1):
    df_wpm_by_mistake_free_status = df_results.pivot_table(index = 'Mistake_Free_Test', values = 'WPM', aggfunc = 'mean').reset_index()
    df_wpm_by_mistake_free_status['Mistake_Free_Test'].replace({0:'No', 1:'Yes'}, inplace = True)
    df_wpm_by_mistake_free_status.to_csv('Analyses/wpm_by_mistake_free_status.csv', index = False)
    df_wpm_by_mistake_free_status

# %%
# We'll only create the graph if there is at least one mistake-free
# result and one result with errors. (Otherwise, we won't be able
# to compare these two outcomes.)
if (len(df_results.query("Mistake_Free_Test == 0")) >= 1) & (
    len(df_results.query("Mistake_Free_Test == 1")) >= 1):
    fig_wpm_by_mistake_free_status = px.bar(df_wpm_by_mistake_free_status, x = 'Mistake_Free_Test', y = 'WPM', text_auto = '.6s')
    fig_wpm_by_mistake_free_status.write_html('Analyses/mean_wpm_by_mistake_free_status.html')
    fig_wpm_by_mistake_free_status.write_image('Analyses/mean_wpm_by_mistake_free_status.png', width = 1920, 
    height = 1080, engine = 'kaleido', scale = 2)
    fig_wpm_by_mistake_free_status

# %%
df_wpm_by_percentile = df_results['WPM'].quantile(q = np.arange(0, 1.05, 0.05)).transpose().reset_index()
df_wpm_by_percentile.columns = ['Percentile', 'WPM']
df_wpm_by_percentile['Percentile'] = (
df_wpm_by_percentile['Percentile']*100).astype('int')
# Some of the WPM values had additional decimal values (e.g. 15.000000000000002,
# might currently have additional decimal values, so rounding them as integers
# helps simplify them.
df_wpm_by_percentile.to_csv('Analyses/wpm_by_percentile.csv', index = False)
df_wpm_by_percentile

# %%
fig_wpm_by_percentile = px.bar(df_wpm_by_percentile, x = 'Percentile', y = 'WPM', text_auto = '.6s')
fig_wpm_by_percentile.update_xaxes(type = 'category')
fig_wpm_by_percentile.write_html('Analyses/wpm_by_percentile.html')
fig_wpm_by_percentile.write_image('Analyses/wpm_by_percentile.png', width = 1920, 
height = 1080, engine = 'kaleido', scale = 2)
fig_wpm_by_percentile

# %% [markdown]
# ## Analyzing character statistics:

# %%
# Calculating the fastest keypresses (in ms):
# Note: This analysis will only include characters that were preceded by at 
# least two correctly typed characters. (This is due to the code underlying
# the construction of the source table.)

df_fastest_keypresses = df_character_stats.sort_values('Time Used to Type Last Character (ms)').head(50).copy().reset_index(drop=True)
df_fastest_keypresses['Rank'] = df_fastest_keypresses.index + 1
df_fastest_keypresses.to_csv('Analyses/fastest_keypresses.csv')
df_fastest_keypresses

# %%
fig_fastest_keypresses = px.bar(df_fastest_keypresses, x = 'Rank', y = 'Time Used to Type Last Character (ms)', text_auto = '.3s', title = 'Fastest Keypresses (ms)<br><i>(Note: these values only include characters that were immediately preceded by<br>at least 2 correct keypresess)')
fig_fastest_keypresses.write_html('Analyses/fastest_keypresses.html')
fig_fastest_keypresses.write_image('Analyses/fastest_keypresses.png', width = 1920, 
height = 1080, engine = 'kaleido', scale = 2)

fig_fastest_keypresses

# %%
df_character_durations = df_character_stats.pivot_table(index = 'Character', values = ['Time Used to Type Last Character (ms)', 'Count'], aggfunc = {'Time Used to Type Last Character (ms)':np.median, 'Count':sum}).reset_index().sort_values('Time Used to Type Last Character (ms)').reset_index(drop=True)
df_character_durations['Character'] = df_character_durations['Character'].replace(' ', '_')
df_character_durations.to_csv('Analyses/median_character_durations.csv', index = False)
df_character_durations

# %%
fig_character_durations = px.bar(df_character_durations, x = 'Character', y = 'Time Used to Type Last Character (ms)', color = 'Count')
fig_character_durations.write_html('Analyses/median_character_durations.html')
fig_character_durations.write_image('Analyses/median_character_durations.png', width = 1920, 
height = 1080, engine = 'kaleido', scale = 2)
fig_character_durations

# %%
df_last_2_character_durations = df_character_stats.pivot_table(index = 'Last 2 Characters', values = ['Time Used to Type Last 2 Characters (ms)', 'Count'], aggfunc = {'Time Used to Type Last 2 Characters (ms)':np.median, 'Count':sum}).reset_index().sort_values('Time Used to Type Last 2 Characters (ms)').reset_index(drop=True)
df_last_2_character_durations.to_csv('Analyses/median_last_2_character_durations.csv', index = False)
# Replacing spaces with underscores to make them more visible:
df_last_2_character_durations['Last 2 Characters'] = \
df_last_2_character_durations['Last 2 Characters'].str.replace(' ', '_')
df_last_2_character_durations

# %%
fig_last_2_character_durations = px.bar(df_last_2_character_durations, x = 'Last 2 Characters', y = 'Time Used to Type Last 2 Characters (ms)', color = 'Count')
fig_last_2_character_durations.write_html('Analyses/median_character_pair_durations.html')
fig_last_2_character_durations.write_image('Analyses/median_character_pair_durations.png', width = 1920, 
height = 1080, engine = 'kaleido', scale = 2)
fig_last_2_character_durations

# %%
analysis_end_time = time.time()
analysis_time = analysis_end_time - analysis_start_time
print(f"Finished updating analyses in {round(analysis_time, 3)} seconds. \
Enter any key to exit.") # Allows the console to stay open when the
# .py version of the program is run

input()


