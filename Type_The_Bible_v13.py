# %% [markdown]
# # Type Through The Bible
# 
# By Kenneth Burchfiel
# 
# *Code is released under the MIT license; Bible verses are from the Web English Bible (Catholic Edition)* and are in the public domain.*
# 
# \* Genesis was not found within the original WEB Catholic Edition folder, so I copied in files from another Web English Bible translation instead. I imagine, but am not certain, that these files are the same as the actual Catholic Edition Genesis files. In addition, to make it easier to type verses, I also replaced the em dashes in the original file with double hyphens and replaced curly single and double quotes with straight ones.

# %% [markdown]
# # Instructions for getting started:
# 
# If you have just downloaded the source code for this game through GitHub, you'll need to make certain updates to the folder directory so that you see your results instead of mine:
# 
# 1. Rename WEB_Catholic_Version_for_game_updated.csv as **WEB_Catholic_Version_for_game_updated_sample.csv**; results.csv as **results_sample.csv**; and word_stats.csv as **word_stats_sample.csv** (if these files are present in the directory).
# 
# 1. Make a copy of **WEB_Catholic_Version_for_game.csv** and rename it **WEB_Catholic_Version_for_game_updated.csv**.
# 
# 1. Delete the Analyses folder (if it already exists).
# 
# You're now ready to play!
# 
# Note: If you instead downloaded an executable copy of this game from Itch.io, the above steps aren't necessary.

# %% [markdown]
# Next steps for development: (Not necessarily in order of importance)
# 
# * Add documentation
# * Create a regression analysis that attempts to use data about the verse (length, number of capital letters, etc.)
# * Add in a help/disclaimer/credits/dedication section

# %% [markdown]
# This file shows the source code for Type Through The Bible. I am working to add in documentation to make the code more intuitive.

# %% [markdown]
# We'll first import a number of libraries:

# %%
import pandas as pd
pd.set_option('display.max_columns', 1000)
import time
import plotly.express as px
from getch import getch # Installed this library using pip install py-getch, not
# pip install getch. See https://github.com/joeyespo/py-getch
import numpy as np
# import statsmodels as sm
from datetime import datetime, date, timezone # Based on 
# https://docs.python.org/3/library/datetime.html
import os
from colorama import just_fix_windows_console
# From https://github.com/tartley/colorama/blob/master/demos/demo01.py
# The following line allows ANSI escape codes to display correctly on Windows.
# For more information, see # https://github.com/tartley/colorama .
just_fix_windows_console() 

# Note: You'll also need to have kaleido installed if you set 
# save_image_copies_of_charts (see below) to True, as it 
# will get called by Plotly later in the program.
# For Windows, I ran conda install python-kaleido=0.1.0, since a later
# version of Kaleido didn't work correctly for me. It wasn't necessary
# to specify the version of kaleido on Linux.

# %%
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


# %%
from blessed import Terminal # Blessed is a variant of the Blessings library 
# that also works on Windows. This library contains a very useful function
# for retrieving the current coordinates of the text cursor; this information
# will prove very useful during gameplay.
#  See https://blessed.readthedocs.io/en/latest/intro.html
term = Terminal()

# %%
extra_analyses = False # If set to True, additional analyses will be created, 
# but only when the program is run as a Jupyter notebook.
save_image_copies_of_charts = False # I had trouble getting Kaleido 
# (the package that Plotly uses by default to generate screenshots of
# charts) to run on pyinstaller-generated copies of Type Through The Bible,
# so I chose to disable image generation by default. (The HTML versions
# of these charts are more useful anyway, and disabling the screenshot
# generation also helps the program finish its analyses more quickly.)

# %% [markdown]
# Checking whether the program is currently running on a Jupyter notebook:
# 
# (The program normally uses getch() to begin typing tests; however, I wasn't able to enter input after getch() got called within a Jupyter notebook and thus couldn't begin a typing test in that situation. Therefore, the program will use input() instead of getch() to start tests when running within a notebook.)

# %%
# The following method of determining whether the code is running
# within a Jupyter notebook is based on Gustavo Bezerra's response
# at https://stackoverflow.com/a/39662359/13097194 . I found that
# just calling get_ipython() was sufficient, at least on Windows and within
# Visual Studio Code.

try: 
    get_ipython()
    run_on_notebook = True
except:
    run_on_notebook = False

# print(run_on_notebook)

# %% [markdown]
# Importing Bible verses into the program:
# 
# (This file derives from Bible_csv_generator.ipynb.)

# %%
df_Bible = pd.read_csv('WEB_Catholic_Version_for_game_updated.csv', 
index_col = 'Verse_Order') # Setting Verse_Order (the position of each verse
# within the entire Bible) as the index column will simplify the process
# of updating this file.
df_Bible.sort_index(inplace = True) # Helps ensure that
# any code that relies on df_Bible's being sorted from the first to the last
# verse will run correctly

df_Bible

# %% [markdown]
# The script will now search the local directory for 'results.csv' and 'word_stats.csv', files used to store various typing statistics. If the script doesn't find these, it will go ahead and create blank DataFrames that will be replaced with actual results after the player completes a typing test.
# 
# The script will also create an 'Analyses' folder for storing typing stats and visualizations if this folder does not already exist.

# %%
local_dir = os.listdir()
if 'Analyses' not in local_dir:
    print("Analyses folder was not found within the directory. Adding this \
folder now.")    
    os.mkdir('Analyses')
if 'results.csv' not in local_dir:
    print("results.csv was not found within the directory. A new copy \
will be created.")    
    df_results = pd.DataFrame() # This blank DataFrame will be passed
    # to various functions and later replaced with actual statistics.
else:
    df_results = pd.read_csv('results.csv', index_col='Test_Number')
    df_results.sort_index(inplace = True)

df_results


# %% [markdown]
# I encountered errors when trying to add new results to my pre-existing list of results; I found that these errors were caused by datetime type mismatches between df_results and the new results. The following cell resolves these issues by converting some of the datetime columns in df_results to microsecond types.

# %%
if len(df_results) > 0: # If df_results is empty, then there's
    # no need to attempt to convert its (non-existent) values.
    df_results['Local_Start_Time'] = pd.to_datetime(
    df_results['Local_Start_Time']).astype('datetime64[us]')
    df_results['UTC_Start_Time'] = pd.to_datetime(
    df_results['UTC_Start_Time']).astype('datetime64[us, UTC]')
    df_results['WPM'] = df_results['WPM'].astype('float') # Prevents a glitch
    # that can be caused when this column is stored as an object.
df_results

# %%
if 'word_stats.csv' not in local_dir:
    df_word_stats = pd.DataFrame() # Once again, the script will
    # create a blank DataFrame that will later be replaced
    # with actual data.
    print("word_stats.csv was not found within the directory. A new copy \
will be created.")    
else:
    df_word_stats = pd.read_csv('word_stats.csv')

df_word_stats

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

# %% [markdown]
# ### Creating an RNG seed:
# 
# In order to make the RNG values a bit more random, the following code will derive the RNG seed from the decimal component of the current timestamp. This seed will change 1 million times each second.
# 

# %%
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

# %% [markdown]
# ## Defining Gameplay Functions:
# 
# The script will now define a series of functions that will allow the user to select verses to type; enter responses; and view gameplay statistics.

# %%
# [This fantastic answer](https://stackoverflow.com/a/23294659/13097194) by 
# Kevin at Stack Overflow proved helpful in implementing 
# entry validation code within this program. 

def select_verse():
    '''This function allows the player to select an initial Bible verse 
    to type. The player can choose a random verse; a verse that hasn't
    been typed; or a specific verse.
    The player can also choose to enable an autostart mode, which automatically
    commences new typing tests.
    This function returns the verse to type followed by a boolean value
    that specifies whether autostart is active.''' 

    print("Select a verse to type! Enter 0 to receive a random verse\n\
or enter a verse number (see 'Verse_Order column of\n\
the WEB_Catholic_Version.csv spreadsheet for a list of numbers to enter)\n\
to select a specific verse.\n\
You can also enter -2 to receive a random verse that you haven't yet typed,\n\
-3 to choose the first Bible verse that hasn't yet been typed,\n\
or -4 to enable autostart (which automatically begins a typing test for\n\
the subsequent verse after you finish typing a verse). Autostart can be\n\
canceled by hitting the ` key in version v2 of the typing test or by entering\n\
'exit' as the response in version v1. ")
    
    verses_not_yet_typed = df_Bible.query(
                "Typed == 0").copy().index.to_list()
    while True:
        try:
            response = int(input())
        except:
            print("Please enter an integer corresponding to a particular Bible \
verse or 0 for a randomly selected verse.")
            continue # Allows the user to retry entering a number

        if response == 0: # A random verse will be selected.
            return (rng.integers(1, len(df_Bible) + 1), False) 
            # The number of verses within the Bible .csv file is equal to 
            # len(df_Bible), so we'll pass 1 (the first verse) and 
            # len(df_Bible) + 1 to rng.integers (as this function won't 
            # include the final number within the range.)
        elif response == -2: # A random verse not yet typed will be selected.
            if len(verses_not_yet_typed) == 0:
                print("Congratulations! You have typed all verses from \
the Bible, so there are no new verses to type! Try selecting another option \
instead.")
                continue
            print(f"{len(verses_not_yet_typed)} verses have not yet \
been typed.")
            return (rng.choice(verses_not_yet_typed), False)
            # Chooses one of these untyped verses at random
        elif response == -3: # The first verse not yet typed will be selected.
            if len(verses_not_yet_typed) == 0:
                print("Congratulations! You have typed all verses from \
the Bible, so there are no new verses to type! Try selecting another option \
instead.")
                continue
            print(f"{len(verses_not_yet_typed)} verses have not yet \
been typed.")
            verses_not_yet_typed.sort() # Probably not necessary, as df_Bible
            # was already sorted from the first to the last verse.
            return (verses_not_yet_typed[0], False)
        
        elif response == -4: # This option will enable autostart.
            if len(verses_not_yet_typed) == 0: # If all verses have already
                # been typed, autostart mode will begin with the first verse.
                return (1, True)
            else: # In this case, the first verse not yet typed will
                # be returned. (The player can commence autostart with
                # a different verse later on in a gameplay session.)
                return (verses_not_yet_typed[0], True)
        
        else: # In this case, the player either submitted a valid verse number
            # or an invalid entry.
            if ((response >= 1) 
            & (response <= len(df_Bible))): # Making sure that the response is 
                # an integer between 1 and the length of df_Bible so that it 
                # matches one of the Bible verse numbers present:                    
                return (response, False) # The user entered a valid verse
                # number, so this number will get returned by the function.
            else: # Will be called if a non-integer number was passed
                    # or if the integer didn't correspond to a Bible verse
                    # number. 
                print("Please enter an integer that corresponds to one of the \
verse numbers within the Bible .csv file.") # Since
                # we're still within a While loop, the player will be returned
                # to the initial try/except block.


# %%
def create_word_table(verse):
    '''This function creates a list of words within the verse that can be used
    for word-based analyses.
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
    or end single quotes.
    
    The function begins by identifying the first letter of each word in the
    verse. It then determines the final letter of each word, then returns
    a DataFrame with information about the words in the verse.'''

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
    # print("Words identified by create_word_table():",df_word_index_list['word'].to_list())
    return df_word_index_list

# %%
def run_typing_test(verse_order, results_table, 
    word_stats_table, test_type = 'v2', autostart = False):
    '''This function, which runs a typing test for an individual verse,
    makes up the core of Type Through The Bible's gameplay.
    It calculates how quickly the user types the characters
    passed to the Bible verse represented by verse_order, then saves those 
    results to the DataFrame passed to results_table. Word-level results
    are saved to word_stats_table.
    if autostart is set to True, the function will automatically begin
    the typing test, which saves the player a little bit of time (but
    makes for a more intense gameplay experience).
    '''

    # Retrieving the verse to be typed:
    # df_Bible uses verse order values for its index, so we can access
    # verses within df_Bible by passing verse_order to .at[].
    verse = df_Bible.at[verse_order, 'Verse']
    book = df_Bible.at[verse_order, 'Book_Name']
    chapter = df_Bible.at[verse_order, 'Chapter_Name']
    verse_number_within_chapter = df_Bible.at[verse_order, 'Verse_#']
    
    df_word_index_list = create_word_table(verse)
    # print(df_word_index_list)

    if run_on_notebook == False:
        # The following two lines print ANSI escape codes that provide
        # more space for the introduction, verse, and response.
        print("\033[2J") # This ANSI escape code clears all text
        # above the cursor. The print statement is based on
        # https://en.wikipedia.org/wiki/ANSI_escape_code and
        # https://github.com/tartley/colorama .
        # Using 2J instead of 1J allows for previous lines to remain 
        # accessible; the user simply has to scroll up to access them.
        # 1J would clear out all of these lines (at least on Windows).
        print('\033[0;0H') # This line, another ANSI escape code based on the
        # two links shared above, moves the cursor to 
        # the top left of the screen.

    # I moved these introductory comments out of the following while loop
    # in order to simplify the dialogue presented to users during retest
    # attempts.

    print(f"Welcome to the typing test! Your verse to type is {book} \
{chapter}:{verse_number_within_chapter} (verse {verse_order} \
within the Bible .csv file).\n")
    
    # The following if statement provides terminal resizing instructions
    # so that players can complete longer tests within version v2. (Note that
    # the terminal's size will get stored soon after this print statement
    # appears; therefore, in order to update the size, the player will most
    # likely need to restart the test.)
    if ((len(verse) >= 1000) & (test_type == 'v2')):
        print("You may need to resize your terminal in order to successfully \
complete this test. You can do so by starting the test; exiting out by \
pressing `; maximizing the terminal; and then restarting this test.")


    if run_on_notebook == False: # In this case, the typing test 
        # will begin after any keypress due to the use of getch().
        print("Press any key to begin typing!")
    else:
        print("Press Enter to begin the test!")
    
    complete_flag = 0 # This value will only get set to 1 after the 
    # user has successfully finished a typing test.
    while complete_flag == 0: # This while loop will continue to run
        # until the user has completed a test.
        print(f"Here is the verse:\n\n{verse}") 

        if run_on_notebook == False: # The following line crashed for me
            # when running the program within a notebook (likely because
            # no terminal is present in that case).
            # V2 of the typing test uses terminal width and 
            # height information to determine how to display the player's input. 
            # These values will be determined via os.get_terminal_size() below
            # so that the code can run correctly with different terminal 
            # configurations.
            terminal_width, terminal_height = os.get_terminal_size()
            # print(terminal_width, terminal_height)
            # get_terminal_size() is cross-platform. See
            # https://docs.python.org/3.8/library/os.html?highlight=get_terminal_size#os.get_terminal_size

            # Version V2 of the test also uses the text cursor's
            # current y position to help determine where to begin printing
            # each line. We can retrieve this position using
            # get_location() from Blessed, a Python library. I wasn't
            # able to find a way to do this within colorama, 
            # but thankfully this solution works great. 
            # Visit https://blessed.readthedocs.io/en/latest/location.html 
            # for more details.
            # The documentation page linked above warns that get_location()
            # can take a little while to execute. I've found that it only
            # takes 0.1 to 0.15 seconds on my (pretty fast) computer,
            # but even this short amount could interfere with the typing
            # experience if it gets called after each character.
            # Therefore, we'll call get_location() before the test begins.
            # get_location_start_time = time.perf_counter_ns()
            cursor_y_pos, cursor_x_pos = term.get_location()
            # print(cursor_y_pos, terminal_height)
            if (cursor_y_pos + 1) < terminal_height: # E.g. if the line below
            # the cursor is not the last line in the terminal or one below it
            # I found that cursor_y_pos always seemed to be at least one row 
            # less than terminal_height even
            # if it appeared to be at the bottom of the terminal,
            # which is why I added +1 to that variable.
                cursor_y_pos += 2 # This line moves the starting point
            # of the cursor down by 3, as I found that it would sometimes
            # overwrite the 'Start!' command that appears after
            # the player begins the test.
            else:
                cursor_y_pos += 1 # In this case, the cursor only needs to be
                # moved down one line. (Moving it down further would trigger
                # code later on that repositions the text on the terminal,
                # which can be distracting.)
            # print(cursor_y_pos)
            # get_location_end_time = time.perf_counter_ns()
            # print(cursor_y_pos, cursor_x_pos)
            # print((get_location_end_time - get_location_start_time)/1000000)
            # print("Now printing cursor position:")
            # print(term.get_location())
            # print("Printed cursor position.")
        else:
            column_width = 120 # The default terminal column width on my
            # copy of Windows

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
            if autostart == False: # If autostart is True, the player has
                # chosen to automatically start the test, so the following
                # line can be skipped (thus causing the test to begin
                # right away).
                start_character = getch() # See https://github.com/joeyespo/py-getch

        else: # When running the program within a Jupyter notebook, I wasn't
            # able to enter input after getch() was called, so I added
            # input() below as an alternative start option.
            if autostart == False:
                input()
     
        print("Start!")      
        if test_type == 'v2':
            # This version of the test checks the player's input after
            # each character is typed. If the player's input is correct
            # so far, the text will be highlighted green; otherwise,
            # it will be highlighted red. (This allows the player to be 
            # notified of an error without the need for a line break
            # in the console, which could prove distracting.)
            # This function has been tested on Windows and on Linux, but not yet 
            # on a Mac.
            verse_response = '' # This string will store the player's 
            # response.
            no_mistakes = 1 # This flag will get set to 0 if the player makes
            # a mistake. If it remains at 1 throughout the race, then
            # a mistake-free race will get logged in results_table.
            incorrect_character_count = 0 # Will store how many incorrect
            # keypresses have been entered, thus allowing accuracy 
            # statistics to be calculated.
            backspace_count = 0 # Keeps track of how many backspaces the user
            # has entered. This is a less precise measure of accuracy
            # than incorrect_character_count, since a single backspace can
            # potentially clear out an entire word.
            word_stats_list = [] # Will store WPM stats at the word level.
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
            # 'resetting' the timing for a given word by returning to its 
            # first letter.
            first_letter_indices_reached = []
            last_letter_indices_reached = []

            first_keypress = 1 # Designates whether or not the player is 
            # currently making his or her first keypress. This flag, which
            # will be set to 0 after the first keypress is made,
            # will help determine whether or not to begin timing the player's
            # first word.
            last_letter_index = -1 # Initializing this variable with a number
            # that will never occur within the game ensures that this value 
            # won't get interpreted as an actual word starting point.

            unix_start_time = time.time()
            local_start_time = pd.Timestamp.now()
            utc_start_time = pd.Timestamp.now(timezone.utc)
            # I used to use ISO8601-compatible timestamps via the following
            # lines, but decided to switch to a value that Pandas would 
            # immediately recognize as a datetime.
            # local_start_time = datetime.now().isoformat()
            # utc_start_time = datetime.now(timezone.utc).isoformat()

            typing_start_time = time.perf_counter_ns()
            # perf_counter_ns()
            # measures time at the nanosecond level, which makes for more
            # accurate timing stats, at least on Windows.
            # See https://stackoverflow.com/questions/31526179/most-precise-timing-function-in-python#comment136785349_31526179
            # and https://docs.python.org/3/library/time.html#time.perf_counter_ns
            # for more details.
            
            while True: # This while loop allows the player to 
                # enter multiple characters.
                # The following if statement determines whether to 
                # begin timing the player's first word right after
                # the test begins. Timing will only
                # begin if the length of the response is 0; the player
                # is making his/her first keypress; and the letter is the 
                # first letter of a word in df_word_index.
                if (len(verse_response) == 0) & (
                    0 in df_word_index_list['first_letter_index'].to_list()
                    ) & (first_keypress == 1):
                    word_start_time = typing_start_time
                    last_letter_index = df_word_index_list.query(
                        'first_letter_index == 0').copy().iloc[0][
                            'last_letter_index'] # This line retrieves
                    # the index of the last letter of the word so that
                    # the function can stop timing this word once
                    # the last character has been typed successfully.
                    word = df_word_index_list.query(
                        'first_letter_index == 0').copy().iloc[0][
                            'word']
                    first_letter_indices_reached.append(0)
                    # print(f" Started typing {word}.")
                    typed_word_without_mistakes = 1 # This flag will be changed
                    # to 0 if the player makes an incorrect keystroke in the
                    # process of typing the word.
                    # print(f" {last_letter_index}")
                # code_execution_end_time = time.perf_counter_ns()
                # if first_keypress == 0: 
                #     code_execution_time_list.append(
                    # (code_execution_end_time - character_press_time) 
                    # / 1000000)
                    # We divide by 1,000,000 to convert from nanoseconds 
                    # (the output
                    # of perf_counter_ns() to milliseconds.
                character = getch() # getch() allows each character to be 
                # checked, making it easier to identify mistyped words.
                # The following lines assume that character is stored as a 
                # bytestring rather than as a string. (I initially developed 
                # this game within Windows, in which getch() returns 
                # a bytestring.) However, I found that getch() returned strings 
                # within Linux. Therefore, the following if statement was added 
                # in to convert these strings to bytestrings.
                if type(character) == str:
                    character = character.encode()
                character_press_time = time.perf_counter_ns() # This value
                # will be helpful for calculating word-level typing durations.
                first_keypress = 0 # This flag will remain at 0 for the rest
                # of the test.

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
                    # is pressing the backspace key repeatedly.
                    verse_response = ' '.join(verse_response.rstrip(
                        ).split(' ')[:-1])
                    # The above line first removes all spaces from the right 
                    # of the last word typed so that they won't interfere 
                    # with the split() call. It then splits the response into 
                    # individual words; deselects the last word; and joins 
                    # the response back together.
                    if len(verse_response) != 0: # As long as we're not at 
                        # the start of the console, it will be useful 
                        # to add the space after the last word back in so that 
                        # the player doesn't need to retype it.
                        verse_response += ' '
                    backspace_count += 1 # I was considering increasing 
                    # backspace_count here by the number of characters removed 
                    # through Ctrl + Backspace, but since the player only 
                    # has to press Backspace once in this operation, I decided 
                    # to still increment it by one. This means that 
                    # backspace_count may diverge significantly
                    # from incorrect_character_count and thus 
                    # be a poorer measure of accuracy.
                    typed_word_without_mistakes = 0
                elif character == b'`':
                    print('\033[0m') # This ANSI escape code resets
                    # the color of the text. \033 begins the escape code,
                    # and [0m specifies what action should be performed.
                    # The Colorama documentation, available at
                    # https://pypi.org/project/colorama/ ,
                    # and Wikipedia's ANSI escape code page
                    # (https://en.wikipedia.org/wiki/ANSI_escape_code)
                    # helped me add escape codes into this game.
                    # Colorama's STYLE.RESET_ALL variable could be used here
                    # instead, but I decided to use actual ANSI escape codes
                    # where possible.
                    verse_response += character.decode('ascii') # Adding
                    # this character to verse_response will allow the program
                    # to use its presence within that string to exit the player
                    # out of this test later on.
                    break
                else: 
                    # The following try/except block attempts to add
                    # the latest character typed to verse_response.
                    try:
                        verse_response += character.decode('ascii')  
                        # See https://stackoverflow.com/questions/17615414/how-to-convert-binary-string-to-normal-string-in-python3
                    except: # Keys that fall out of the ascii subset, such as 
                        # arrow keys, could cause the above line to crash. 
                        # Therefore, when the above line fails to work, the 
                        # following 'continue' statement will allow the program 
                        # to ignore the key and move back to the beginning 
                        # of the loop.
                        incorrect_character_count += 1 # It's assumed that
                        # a character that could not be successfully decoded
                        # reflected an incorrect keypress.
                        continue

                # Determining which color to use for the text:
                if verse[0:len(verse_response)] == verse_response: # If this 
                    # returns True, the player's response is correct so far.
                    text_color = '\033[32m' # This ANSI escape code will make
                    # all of the text that follows it green, indicating that
                    # that the player has typed the text correctly so far.
                    # For the use of Colorama to produce red and green text, see
                    # https://pypi.org/project/colorama/
                    # and https://stackoverflow.com/a/3332860/13097194 .
                    # Colorama's Fore.GREEN could be used here instead.

                    # Performing word-level analyses:
                    verse_response_minus_one = len(verse_response) -1 # The 
                    # character index values in df_word_index_list start at 0, 
                    # so this variable will help us convert between verse 
                    # lengths and index positions.        
                    
                    if ((character != character_backspace) & 
                        (character != word_backspace)): # in this case,
                        # the last character was neither a backspace nor
                        # a Ctrl + Backspace combo.

                        # Checking whether a word has begun or ended:
                        # We're placing these checks within the correct 
                        # response and no backspace clauses so that a typo or 
                        # backspace won't count as having correctly begun or 
                        # ended a word. (I'm not sure it would actually be 
                        # possible to trigger the word start or 
                        # end checks with Ctrl + Backspace, but I'll include 
                        # it here just in case a clever player figures out how.)
                        # Note that last_letter_indices_reached and 
                        # first_letter_indices_reached will be checked for the
                        # presence of verse_response_minus_one. If it's already
                        # there, then no action will be taken, as timing
                        # for that word has already ended or started.

                        # Checking whether the player has finished 
                        # typing a word:
                        if (verse_response_minus_one == last_letter_index) & (
                            last_letter_index not in 
                            last_letter_indices_reached): # The user has 
                            # finished correctly typing the current word for the 
                            # first time
                            word_end_time = character_press_time
                            # print(f"Finished typing {word} in \
            # {(word_end_time - word_start_time) / 1000000} ms. typed_word_without_mistakes \
            # is set to {typed_word_without_mistakes}.")
                            # Adding word-level statistics to word_stats_list:
                            # (Note that word_end_time - word_start_time is 
                            # divided by one million to convert it from
                            # nanoseconds to milliseconds.
                            word_stats_list.append({"word":word, 
                            "word_duration (ms)": (word_end_time - 
                            word_start_time) / 1000000, 
                            "typed_word_without_mistakes":
                            typed_word_without_mistakes})
                            last_letter_indices_reached.append(
                                last_letter_index)
                            # Other analyses can be added to our 
                            # word stats table later on, so we don't
                            # need to compute them now.

                        # Checking whether the player has reached the starting
                            # point of a new word:
                        if (verse_response_minus_one in df_word_index_list[
                            'previous_character_index'].to_list()) & (
                            verse_response_minus_one not in 
                            first_letter_indices_reached):
                            # If this returns true, we know we're
                            # at the starting point of a new word.
                            # print(verse_response_minus_one, 
                            # df_word_index_list['previous_character_index'])
                            # print("Start of new word detected (Point A).")
                            typed_word_without_mistakes = 1
                            verse_response_minus_one = len(verse_response) -1
                            word_start_time = character_press_time # The start 
                            # time of this new word is defined as the time 
                            # that the character preceding the word was pressed.
                            # Updating last_letter_index with the location
                            # of the final letter within this word:
                            last_letter_index = df_word_index_list.query(
                            "previous_character_index == @verse_response_minus_one").iloc[
                            0]['last_letter_index']
                            # Updating 'word' with the word that begins
                            # after previous_character_index:
                            word = df_word_index_list.query(
                            "previous_character_index == @verse_response_minus_one").iloc[
                            0]['word']
                            # print(f" Started typing {word}.")
                            first_letter_indices_reached.append(
                            verse_response_minus_one)

                else: # In this case, the most recent keystroke was a typo.
                    no_mistakes = 0 # This flag will remain at 0 for the 
                    # rest of the race.
                    typed_word_without_mistakes = 0 
                    text_color = '\033[31m' # Sets the verse's text to red to 
                    # designate that an error is present.
                    if ((character != character_backspace) & 
                        (character != word_backspace)): 
                        # Backspaces won't be counted as part of the 
                        # incorrect character tally so that
                        # players won't be double-penalized for mistyping
                        # a character.
                        incorrect_character_count += 1
                
                # Printing the player's response so far: 
                
                # This process will involve printing the entirety of 
                # verse_response
                # after each character is pressed rather than 
                # just the most recent character. 
                # This code is more complex than a regular print statement, 
                # but it has
                # several advantages:
                # 1. It allows the player to quickly determine when a typo has 
                # occurred (as the text will show up in red rather than 
                # in green).
                # 2. It supports the use of backspace to correct responses on 
                # previous lines. (I wasn't able to navigate to a previous line 
                # using backspace when printing single characters at a time.)
                # 3. It allows the cursor to appear to the right of the most
                # recent character. If the latest typed line takes up the entire
                # width of the console, the cursor will appear on the left of 
                # the following line.
                # The development of this code involved a decent amount of 
                # trial and error. I've added in documentation in hopes
                # of making it more intuitive. 

                line_count = ((len(verse_response)) // terminal_width)
                # Uses floor division to calculate the number of full lines 
                # that the player's output takes up. This information will help 
                # the code adjust its output when the player reaches the end 
                # of the terminal.

                clear_text_to_right_command = '\033[0K' # This ANSI escape code
                # code clears out all text
                # to the right of the cursor, which will come in handy
                # when the user hits Backspace or Ctrl + Backspace.
                # Based on
                # https://en.wikipedia.org/wiki/ANSI_escape_code
                # and on https://pypi.org/project/colorama/

                clear_text_to_left_command = '\033[1K' # Based on
                # https://en.wikipedia.org/wiki/ANSI_escape_code
                # If the player returns to a previous line, this command
                # will help ensure that the text on the lower line
                # gets cleared out.

                # In order to make the cursor appear on a new line when the 
                # player has reached the end of a line, a space will get added 
                # to the verse after it is printed (see below for more details). 
                # To compensate for this space, the ANSI escape code '\033[D' 
                # will usually get printed, thus moving the cursor one column 
                # back. However, if the verse is one column away from the end 
                # of the line, this step won't be necessary, so an empty string 
                # can get passed to left_cursor_shift instead.
                if terminal_width - (len(verse_response) % terminal_width) == 1:
                    left_cursor_shift = ''
                else:
                    left_cursor_shift = '\033[D'

                # In order to get verses of different lengths to print 
                # correctly, it's helpful to begin each print statement 
                # from the same position. This can be accomplished by 
                # generating an ANSI escape code that moves the cursor to the 
                # same place whenever the print process begins.
                # (Note: an earlier version of this code used an alternate 
                # solution that involved shifting the print statement up or down 
                # depending on the number of lines being printed. This solution 
                # was more complex and less intuitive than the cursor 
                # reposition option, so I replaced that code with this setup. 
                # The earlier solution *does* do a much better job of handling 
                # situations in which the response takes up the entire terminal; 
                # however, in that scenario, the player wouldn't be able to see 
                # the original verse anyway, making the game unplayable, so it's 
                # OK that the current code doesn't function well in that case.)
                    
                # The cursor reposition command makes use of the cursor_y_pos 
                # and cursor_x_pos values retrieved earlier via 
                # term.get_location().
                # (I found that that function took around .1 to .15 seconds 
                # to run, so calling it after each character would slow the 
                # program down noticeably. Therefore, it's best to call it 
                # just once before the start of the typing test.)

                # In most cases, the pre-existing cursor_y_pos value 
                # reflects an ideal cursor height; however, printing issues
                # will result if the player's text extends past the final line 
                # of the terminal. Therefore, the following if statement 
                # was added in to check for and address this condition.    
                    
                if (cursor_y_pos + (line_count)) > terminal_height: # If this
                    # returns True, the text response will extend past the final
                    # line of the terminal, which would cause printing issues.
                    print('\n') # First, a newline will be printed in order
                    # to shift the pre-existing text up, thus preventing it from
                    # being overwritten.
                    cursor_y_pos -= 2 # Next, cursor_y_position will be
                    # decreased by 2 so that it has more room to print the text.
                    # I initially thought -= 1 would work, since we're only
                    # printing one newline above, but for some reason the
                    # original text went up 2 lines. (Perhaps the terminal added
                    # in another line to account for our going past 
                    # the final line.)
                    # Thus, I changed the subtraction amount from
                    # from 1 to 2. (Trial and error was definitely one of
                    # the tools I used in writing this code!)

                    # Note that, now that cursor_y_pos has been reduced by 2, 
                    # this if statement won't return True until we add 
                    # two more lines to our response.

                    # print('\a', end = '') # Prints an alert, which is 
                    # useful for debugging (since printing text would affect 
                    # the output).
                    # See https://stackoverflow.com/a/6537650/13097194

                # We're now ready to create our cursor reposition command,
                # which is yet another ANSI escape code.
                cursor_reposition_command = f'\033[{cursor_y_pos};{cursor_x_pos}H'
                # Based on https://github.com/tartley/colorama

                # A print statement will now be called to display the latest 
                # version of verse_response on the screen. It will do so using 
                # the following steps:
                # (Note: Many of the items to be printed are ANSI escape codes 
                # rather than text.)

                # 1. clear_text_to_left_command gets printed so that 
                # text on a lower line will get removed if the player returns 
                # to a previous line via Backspace or Ctrl + Backspace.
                
                # 2. cursor_reposition_command moves the cursor to an ideal
                # starting point for writing the text. (See notes above
                # for more details.)
                
                # 3. text_color gets printed; this will make the verse red if 
                # a mistake is present and green otherwise.

                # 4. The verse itself gets printed, followed by a space 
                # (in order to make a new line appear if the player has reached 
                # the end of the line). Note that no other spaces are present 
                # within the print statement.

                # 5. In order to compensate for this space, left_cursor_shift 
                # is added, which usually moves the cursor back one column. 
                # (See above for more details.)

                # 6. clear_text_to_right_command is printed so that text removed
                # via Backspace or Ctrl + Backspace will no longer appear.

                # This print statement sets end to '' so that the cursor will 
                # not move to a new line after the string is printed. 
                # In addition, flush is set  to True so that the player's 
                # response will appear immediately. 
                    
                print(f"{clear_text_to_left_command}{cursor_reposition_command}\
{text_color}{verse_response} {left_cursor_shift}{clear_text_to_right_command}", 
                end = '', flush = True)
                
                # Version V2 of the typing test will now check to see
                # whether the player finished typing the test correctly; 
                # if he/she has, the test will end automatically. This setup
                # allows for a more accurate (and faster) WPM to be calculated 
                # relative to a manual option for ending the test.

                if verse_response == verse: # The player has typed the test
                    # correctly.
                    typing_end_time = time.perf_counter_ns()
                    typing_time = (
                        typing_end_time - typing_start_time) / 1000000000
                    # Since perf_counter_ns() measures time at the nanosecond 
                    # level, the output of (typing_end_time - typing_start_time) 
                    # must be divided by one billion in order to determine the 
                    # number of seconds used to type the verse.
                    print('\nSuccess!') # '\n' was added before 'Success!'
                    # so that the cursor will be moved past the lines already
                    # printed, thus preventing words from getting overwritten.
                    print('\033[0m') # Resetting the text's color once again

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
                    # print("Backspace count and incorrect character count:",
                    # backspace_count, incorrect_character_count)
                
                    # converting word_stats_list into a DataFrame
                    # so that it can be added to a pre-existing
                    # word stats table:
                    word_stats_for_latest_test = pd.DataFrame(word_stats_list)
                    # print(word_stats_for_latest_test)
                    # print(f"Code execution stats: Median: {np.median(
                    # code_execution_time_list)}, Mean: {np.mean(
                    # code_execution_time_list)}, Max: {max(
                    # code_execution_time_list)}, Min: {min(
                    # code_execution_time_list)}. All execution times: {
                    # code_execution_time_list}")
                    break

        elif test_type == 'v1': 
            # This is a simple typing test setup that receives input from
            # the user when 'Enter' is pressed, then checks that input
            # against the verse. Because it doesn't check the response
            # for accuracy as the player types, the player might not realize
            # a character was mistyped until the very end, which can get
            # frustrating. Version V2 of the test addresses this issue.
            
            # The following three variables can't be calculated using v1
            # of the test (since the player's response is only evaluated
            # after all words have been submitted), so they will instead
            # be initialized as NaN values.
            no_mistakes = np.NaN
            backspaces_as_pct_of_length = np.NaN
            incorrect_characters_as_pct_of_length = np.NaN
            
            # Storing various start time values:
            unix_start_time = time.time()
            local_start_time = pd.Timestamp.now()
            utc_start_time = pd.Timestamp.now(timezone.utc)

            typing_start_time = time.perf_counter_ns() 

            verse_response = input()
            # The following code will execute once the player finishes typing 
            # and hits Enter. (Having the program evaluate the player's entry 
            # only after 'Enter' is pressed isn't the best option, as the time 
            # required to hit Enter will reduce the player's reported WPM. 
            # Version V2 stops the test right when the final correct
            # character is typed, which will make the final WPM slightly faster.
            typing_end_time = time.perf_counter_ns()
            typing_time = (typing_end_time - typing_start_time) / 1000000000

        if verse_response == verse: 
            print(f"Well done! You typed the verse correctly.")
            complete_flag = 1 # Setting this flag to 1 allows the player to exit
            # out of the while statement.
        elif (verse_response.lower() == 'exit') or ('`' in verse_response):
            print("Exiting typing test.")
            autostart = False # Entering this character will also
            # cancel autostart, thus allowing the player to resume
            # starting tests manually (or exit the game).
            return results_table, word_stats_table, autostart 
            # Exits the function without saving the 
            # current test to results_table or df_Bible. This function has
            # been updated to work with both versions of the typing
            # test.
        else: # This will only return True within V1.
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

    if test_type == 'v2': # Word statistics are only
        # logged in version V2 of the test.
        if len(word_stats_table) == 0: # If there are no
            # pre-existing entries in word_stats_table,
            # we can simply overwrite it with
            # word_stats_for_latest_test.
            word_stats_table = word_stats_for_latest_test.copy()
        else:
            word_stats_table = pd.concat(
        [word_stats_table, word_stats_for_latest_test]).reset_index(
        drop = True)
            
    # Calculating typing statistics:

    cps = len(verse) / typing_time # Calculating characters per second
    wpm = cps * 12 # Multiplying by 60 to convert from seconds to minutes, 
    # then dividing by 5 to convert from characters to words (a standard 
    # conversion practice).

    # Creating a single-row DataFrame that stores the player's results:
    # +1 is added to the length of the results table in order to begin
    # test number values at 1 (rather than 0).
    df_latest_result = pd.DataFrame(index = [
        len(results_table)+1], data = {'Unix_Start_Time':unix_start_time, 
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
    'Book': book,
    'Chapter': chapter,
    'Verse #': verse_number_within_chapter,
    'Verse':verse, 
    'Verse_Order':verse_order})
    df_latest_result.index.name = 'Test_Number'
    df_latest_result

    # Adding this new row to results_table:

    if len(results_table) == 0: # If there are no
        # pre-existing entries within results_table
        # (i.e. because this is the player's first test),
        # we can make results_table a copy of df_latest_result.
        # This avoids challenges related to 
        # concatenating an empty DataFrame with a non-empty one.
        results_table = df_latest_result.copy()
    else: # In this case, we'll use pd.concat() to
        # add df_latest_result to the list of
        # pre-existing results.
        results_table = pd.concat([results_table, df_latest_result])
    # Note: I could also have used df.at or df.iloc to add a new row
    # to df_latest_result, but I chose a pd.concat() setup in order to ensure
    # that the latest result would never overwrite an earlier result.
    
    # Rank and percentile data need to be recalculated after each test,
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
    df_Bible.at[verse_order, 'Typed'] = 1 # Denotes that this verse
    # has now ben typed. Note that .loc[] would not work here because
    # we are updating a value, not merely retrieving one.
    df_Bible.at[verse_order, 'Tests'] += 1 # Keeps track of how 
    # many times this verse has been typed
    fastest_wpm = df_Bible.at[verse_order, 'Fastest_WPM']
    if ((pd.isna(fastest_wpm) == True) | (wpm > fastest_wpm)): 
        # In these cases, we should replace the pre-existing Fastest_WPM value
        # with the WPM the player just achieved.
        # I found that 5 > np.NaN returned False, so if I only checked for
        # wpm > fastest_wpm, blank fastest_wpm values would never get 
        # overwritten. Therefore, I chose to also check for NaN values 
        # in the above if statement.
        df_Bible.at[verse_order, 'Fastest_WPM'] = wpm

    # Autosaving results as separate files: (That way, if the script crashes,
    # the player won't lose all of his/her progress.)
    if verse_order % 10 == 0: # The autosave will only take place for ~10%
        # of the user's verses, thus saving processing time (and wear
        # on solid state hard drives, though I'm not sure how much of 
        # a difference this would make for the SSD's longevity).
        try:
            results_table.to_csv('df_results_autosave.csv', index = True)
            df_Bible.to_csv(
            'WEB_Catholic_Version_for_game_updated_autosave.csv', index = True)
            word_stats_table.to_csv('word_stats_autosave.csv', 
            index = False)
            print("Autosave complete.")
        except: # If one of these files is open, the autosave might not have
            # worked correctly.
            print("At least one of the autosave files could not be saved. \
Close out of any open autosave files so that they can be updated later on.")
    return (results_table, word_stats_table, autostart)


# %%
def select_subsequent_verse(previous_verse_order):
    '''This function allows the player to specify which verse to
    type next, or, alternatively, to exit the game.
    This function will either return a positive number (representing a verse)
    or a negative number (representing another command). Command codes
    were made negative so that they wouldn't be mistaken for verse numbers.
    
    This function is quite similar to select_verse, but also incorporates
    but makes use of the verse_order value for the most recent verse
    typed (previous_verse_order).
    '''

    print("Press 0 to retry the verse you just typed; \
1 to type the next verse; 2 to type the next verse that hasn't yet been typed; \
-3 to select the first verse that hasn't been typed; \
3 to select a different verse; \
-1 to save your results and exit; \
-2 to save your results without running the analysis \
portion of the script; and -4 to enable autostart.") 
# The analysis portion can take a decent amount of
# time to run, which is why an option to save without running these analyses
# was added in. These analyses can then get updated during a later session.
    
    verses_not_yet_typed = df_Bible.query(
    "Typed == 0").copy().index.to_list() # verses_not_yet_typed stores
    # verse_order values.
    while True: 
            try:
                response = int(input())
            except: # The user didn't enter a number.
                print("Please enter a number.")      
                continue
            if response == 0:
                return previous_verse_order
            elif response == 1:
                if previous_verse_order == len(df_Bible):
                    print("You just typed the last verse in the Bible, so \
there's no next verse to type! Please enter an option other than 1.\n")
                    continue
                else:
                    return previous_verse_order + 1
            elif response == 2:
                # In this case, we'll retrieve a list of verses that haven't
                # yet been typed; filter that list to include only verses
                # greater than previous_verse_order; and then select
                # the first verse within that list (i.e. the next 
                # untyped verse).
                if len(verses_not_yet_typed) == 0:
                    print("Congratulations! You have typed all verses from \
the Bible, so there are no new verses to type! Try selecting another option \
instead.")
                    continue
                print(f"{len(verses_not_yet_typed)} verses have not yet \
been typed.")
                verses_not_yet_typed.sort() 
                # Filtering verses_not_yet_typed to include only verses
                # whose verse_order values are greater than 
                # previous_verse_order:
                next_untyped_verses = [verse for verse in verses_not_yet_typed 
                if verse > previous_verse_order]
                return next_untyped_verses[0]
            
            elif response == -3:
                if len(verses_not_yet_typed) == 0:
                    print("Congratulations! You have typed all verses from \
the Bible, so there are no new verses to type! Try selecting another option \
instead.")
                    continue
                print(f"{len(verses_not_yet_typed)} verses have not yet \
been typed.")
                verses_not_yet_typed.sort()
                return verses_not_yet_typed[0]

            elif response == 3: # select_verse() returns two items, but
                # select_subsequent_verse() only returns one, so we'll
                # need to determine which single item to return
                # based on the output of select_verse().
                verse_order, autostart = select_verse()
                if autostart == True: # In this case, we'll return
                    # the autostart enable code (-4).
                    return -4
                else: # If autostart is False, we'll just return
                    # the verse order chosen by select_verse().
                    return verse_order
                    
            elif response in [-1, -2, -4]:
                return response
            else: # A number other than one of the above options was passed.
                print("Please enter a whole number from -3 to 3 (inclusive).\n")  

# %%
def calculate_current_day_results(df):
    ''' This function reports the number of characters, total verses, and 
    unique verses that the player has typed so far today.'''
    if len(df) == 0:
        result_string = "You haven't typed any Bible verses yet today."
    else:
        df_current_day_results = df[pd.to_datetime(
        df['Local_Start_Time']).dt.date == datetime.today().date()].copy()
        if len(df_current_day_results) == 0: # In this case, the DataFrame
        # isn't empty, but there still aren't any records available for
        # today.
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

            # Rounding the average and median WPM values
            # makes the output more readable.
            average_wpm_today = round(df_current_day_results['WPM'].mean(), 3)
            median_wpm_today = round(df_current_day_results['WPM'].median(), 3)
            result_string = f"So far today, you have typed \
{characters_typed_today} characters from {total_verses_typed_today} Bible \
{total_verses_string} (including {unique_verses_typed_today} unique \
{unique_verses_string}). Your mean and median WPM today are \
{average_wpm_today} and {median_wpm_today}, respectively."
    return result_string

# %%
def run_game(results_table, word_stats_table):
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
              
    verse_order, autostart = select_verse()
    
    while True: # Allows the game to continue until the user decides to exit.
        # The output of a given typing test will serve as the input for
        # the next typing test; this approach allows the player's results
        # to get updated over time.
        results_table, word_stats_table, autostart = run_typing_test(
            verse_order=verse_order, 
        results_table=results_table, 
        word_stats_table=word_stats_table,
        test_type = typing_test_version,
        autostart=autostart)
        # The game will next share an updated progress report:
        print(calculate_current_day_results(results_table))
        
        if autostart == True:
            if verse_order == len(df_Bible): # In this case, the final verse
                # of the Bible was just typed, so the player will be given
                # the first verse of the Bible to type instead.
                verse_order = 1
            else:
                verse_order += 1 # The next verse in the Bible will
                # automatically be selected.
        if autostart == False: # The player will now be prompted 
            # to select a new verse (or to save and quit).
            previous_verse_order = verse_order # Saving verse_order here 
            # allows it to get retrieved for use in the autostart mode.
            verse_order = select_subsequent_verse(
                previous_verse_order=previous_verse_order)
            if verse_order == -1: # In this case, the game will quit and the 
                # user's new test results will be saved to results_table.
                run_analyses = 1
                return (results_table, word_stats_table, run_analyses)
            if verse_order == -2: # In this case, the game will quit and the 
                # user's new test results will be saved to results_table.
                # However, the analysis portion of the script will be skipped 
                # in order to save time.
                run_analyses = 0
                return (results_table, word_stats_table, run_analyses)
            if verse_order == -4: # Autostart has been turned on
                autostart = True
                if previous_verse_order == len(df_Bible): 
                # In this case, the final verse
                # of the Bible was just typed, so the player will be given
                # the first verse of the Bible to type instead.
                    verse_order = 1
                else:
                    verse_order = previous_verse_order + 1 
                    # The next verse in the Bible will
                    # automatically be selected.



# %% [markdown]
# Now that all of our gameplay functions have been defined, we can call run_game() to allow the user to play Type Through The Bible.

# %%
df_results, df_word_stats, run_analyses = run_game(results_table = df_results, 
word_stats_table = df_word_stats)

# %% [markdown]
# # Post-Gameplay Code:

# %% [markdown]
# At this point in the script, the player has chosen to exit out of the game. Therefore, the script will now save his/her results via 3 .csv files and then begin creating analyses of those results.

# %% [markdown]
# If df_results is blank (e.g. because the player exited out of his/her first typing test during his/her first game), some of the following code will likely crash, because they are expecting results to be present within df_results. Therefore, the program will exit out early instead of continuing on.

# %%
if len(df_results) == 0:
    print("No results have been entered, so there is nothing to save or \
analyze. Exiting program in 5 seconds.")
    time.sleep(5) # Allows the user to view the above message
    raise SystemExit # See https://stackoverflow.com/a/19747562/13097194

# %%
# Several columns within df_Bible will now be updated 
# to reflect the player's progress.

# %%
# The 'Characters_Typed' column will have a value of 0 for verses the player
# has not yet typed; for typed verses, it will show the number of characters
# within that verse.
df_Bible['Characters_Typed'] = df_Bible['Characters'] * df_Bible['Typed'] 

# The Total_Characters_Typed column will increase in value for a given verse
# each time the player types that verse; this is not the case for 
# the 'Characters_Typed' column.
df_Bible['Total_Characters_Typed'] = df_Bible['Characters'] * df_Bible['Tests']
df_Bible

# %% [markdown]
# The following cell calculates the player's overall progress in typing the Bible, then shares that progress via a print statement.

# %%
characters_typed_sum = df_Bible['Characters_Typed'].sum()
proportion_of_Bible_typed = characters_typed_sum / df_Bible['Characters'].sum()

print(f"You have typed {characters_typed_sum} characters so far, \
which represents {round(100*proportion_of_Bible_typed, 4)}% of the Bible.")

# %% [markdown]
# # Adding additional values and statistics to df_results:
# 
# (The following cell was derived from [this script](https://github.com/kburchfiel/typeracer_data_analyzer/blob/master/typeracer_data_analyzer_v2.ipynb) that I wrote.)
# 
# These statistics will get recreated whenever the script is run; this approach allows for the results to be revised as needed (e.g. if certain rows are removed from the dataset).

# %%
# I found that it was necessary to convert the Local_Start_Time field to
# a datetime value at this point when running the script on my Linux system.
# This might have been due to library differences between my Linux
# and Windows systems, however.
df_results['Local_Start_Time'] = pd.to_datetime(df_results['Local_Start_Time'])

# %% [markdown]
# Here with editing (continue adding/updating documentation in subsequent cells)

# %%
df_results['Last 10 Avg'] = df_results['WPM'].rolling(10).mean()
df_results['Last 100 Avg'] = df_results['WPM'].rolling(100).mean()
df_results['Last 1000 Avg'] = df_results['WPM'].rolling(1000).mean()

df_results['Incorrect Character % Last 10 Avg'] = df_results[
'Incorrect Characters as % of Verse Length'].rolling(10).mean()
df_results['Incorrect Character % Last 100 Avg'] = df_results[
'Incorrect Characters as % of Verse Length'].rolling(100).mean()
df_results['Incorrect Character % Last 1000 Avg'] = df_results[
'Incorrect Characters as % of Verse Length'].rolling(1000).mean()


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

# %% [markdown]
# ### Adding session data to df_results:

# %%
# df.at() could be used here, but it could fail if there happen to be any
# test number gaps within df_results. Therefore, df.iloc[] will be used
# instead. 

# Determining column indices that can be passed to .iloc: (It's better to
# calculate these on demand than to hardcode numbers, as any changes to the 
# column structure of df_results could then make those hardcoded numbers
# incorrect.

# Initailizing blank Session and Test_#_Within_Session columns that
# can then get recognized and updated in subsequent code:
df_results['Session'] = 0 # Using 0 instead of np.NaN initializes these
# columns as integers (the desired type for them)
df_results['Test_#_Within_Session'] = 0


session_col = df_results.columns.get_loc('Session')
test_number_within_session_col = df_results.columns.get_loc(
'Test_#_Within_Session')
local_start_time_col = df_results.columns.get_loc('Local_Start_Time')
local_end_time_col = df_results.columns.get_loc('Local_End_Time')
new_session_cutoff = 300 # The loop below will calculate the time between
# each test's end time and the next test's start time. If this duration
# (in seconds) is greater to or equal than new_session_cutoff,
# a new session will be assigned to the second test.


# Initializing the first row as the first test within session 1:
df_results.iloc[0, session_col] = 1 
df_results.iloc[0, test_number_within_session_col] = 1


for i in range(1, len(df_results)): # Starting at 1 because we'll be looking
    # back one row during each iteration of the loop.
    previous_row_session = df_results.iloc[i-1, session_col]
    previous_row_test_within_session = df_results.iloc[
    i-1, test_number_within_session_col]
    if (df_results.iloc[i, local_start_time_col] - 
        df_results.iloc[i-1, local_end_time_col]).seconds >= new_session_cutoff:
        # In this case, a new session will be assigned to this row.
        df_results.iloc[i, session_col] = previous_row_session + 1
        df_results.iloc[i, test_number_within_session_col] = 1
    else: # Otherwise, this row will be interpreted as a continuation
        # of the previous session.
        df_results.iloc[i, session_col] = previous_row_session
        df_results.iloc[i, test_number_within_session_col
        ] = previous_row_test_within_session + 1

df_results

# %% [markdown]
# # Adding additional metrics to df_word_stats:

# %%
df_word_stats['Count'] = 1
df_word_stats['characters'] = df_word_stats['word'].str.len()
df_word_stats['CPS'] = df_word_stats['characters'] / (
df_word_stats['word_duration (ms)'] / 1000)
df_word_stats['WPM'] = df_word_stats['CPS'] * 12
df_word_stats

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
            print("File could not be saved, likely because it is currently \
open. Try closing the file and trying again. Press Enter to retry.")
            input()

# %%
attempt_save(df_Bible, 'WEB_Catholic_Version_for_game_updated.csv', 
index = True)
# The verse_order index will be stored within this .csv file so that it can
# be accessed during the subsequent run.

# %%
attempt_save(df_results, 'results.csv', index = True)

# %%
attempt_save(df_word_stats, 'word_stats.csv', index = False)

# %%
print("Successfully saved updated copies of the Results, Word Stats, \
and Bible .csv files.")

# %% [markdown]
# # Creating analyses:
# 
# The script will now create a number of speed, accuracy, endurance analyses. It will also generate several visualizations of word-level statistics.

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
print("Creating tree map(s).")

# %%
# This code is based on https://plotly.com/python/treemaps/
# It's pretty amazing that such a complex visualization can be created using
# just one line of code. Thanks Plotly!
fig_tree_map_books_chapters_verses = px.treemap(
    df_Bible, path = ['Book_Name', 'Chapter_Name', 'Verse_#'], 
    values = 'Characters', color = 'Typed',
    title='Proportions of Bible Books and Chapters That Have Been Typed')
# fig_verses_typed

fig_tree_map_books_chapters_verses

# %%
fig_tree_map_books_chapters_verses.write_html(
    'Analyses/tree_map_books_chapters_verses.html')

# %%
# Generating a .png version of this figure takes much longer than does 
# generating an .html version, so a .png copy will only be created
# if extra_analyses is set to True.
if (run_on_notebook == True) & (extra_analyses == True) \
& (save_image_copies_of_charts == True):
    fig_tree_map_books_chapters_verses.write_image(
    'Analyses/tree_map_chapters_verses.png', width = 1920, height = 1080, 
    engine = 'kaleido', scale = 2)

# %%
# # A similar chart that doesn't use the Typed column for color coding:
# (This chart, unlike fig_tree_map_books_chapters_verses_typed above, 
# won't change unless edits are made to the code itself, so it can be 
# commented out after being run once.)
# fig_Bible_verses.write_html('Bible_tree_map.html')
# fig_Bible_verses = px.treemap(df_Bible, path = ['Book_Name', 
# 'Chapter_Name', 'Verse_#'], values = 'Characters')
# fig_Bible_verses

# %%
df_Bible

# %%
# This variant of the tree map shows chapters and verses rather than books,
# chapters, and verses.
if (run_on_notebook == True) & (extra_analyses == True):
    fig_tree_map_chapters_verses = px.treemap(df_Bible, path = [
        'Book_and_Chapter', 'Verse_#'], values = 'Characters', color = 'Typed',
        title = 'Proportions of Bible Chapters and Verses That Have Been Typed')
    fig_tree_map_chapters_verses.write_html(
        'Analyses/tree_map_chapters_verses.html')
    if save_image_copies_of_charts == True:
        fig_tree_map_chapters_verses.write_image(
        'Analyses/tree_map_chapters_verses.png', 
        width = 7680, height = 4320)

# %%
# This variant of the tree map shows each verse as its own box, which results in 
# a very busy graph that takes a while to load within a web browser
# (if it even loads at all).

if (run_on_notebook == True) & (extra_analyses == True):
    fig_tree_map_verses = px.treemap(df_Bible, path = [df_Bible.index], 
    values = 'Characters', color = 'Typed',
    title = 'Proportions of Bible Verses That Have Been Typed')
    fig_tree_map_verses.write_html('Analyses/tree_map_verses.html')
    if save_image_copies_of_charts == True:
        fig_tree_map_verses.write_image('Analyses/tree_map_verses_16K.png', 
                                    width = 15360, height = 8640) 
# fig_tree_map_verses.write_image('Analyses/tree_map_verses.png', width = 30720, 
# height = 17280) # Didn't end up rendering successfully, probably 
# because the dimensions were extremely large!

# %% [markdown]
# ### Creating a bar chart that shows the proportion of each book that has been typed so far:

# %%
print("Creating progress analyses.")

# %%
df_characters_typed_by_book = df_Bible.pivot_table(index = ['Book_Order', 
'Book_Name'], values = ['Characters', 'Characters_Typed'], 
aggfunc = 'sum').reset_index()
df_characters_typed_by_book.rename(
columns={'Characters_Typed':'Characters Typed'}, inplace = True)
# Adding 'Book_Order' as the first index value allows for the pivot tables
# and bars to be ordered by that value.
df_characters_typed_by_book['Proportion Typed'] = df_characters_typed_by_book[
    'Characters Typed'] / df_characters_typed_by_book['Characters']
df_characters_typed_by_book.to_csv(
    'Analyses/characters_typed_by_book.csv')
df_characters_typed_by_book

# %%
fig_percentage_of_each_book_typed = px.bar(df_characters_typed_by_book, 
x = 'Book_Name', y = 'Proportion Typed', title = 'Books by Percentage Typed')
fig_percentage_of_each_book_typed.update_yaxes(range = [0, 1]) # Setting
# the maximum y value as 1 better demonstrates how much of the Bible
# has been typed so far
fig_percentage_of_each_book_typed.update_layout(xaxis_title = 'Book', 
yaxis_title = '% Typed', yaxis_tickformat = ',.2%')

fig_percentage_of_each_book_typed.write_html(
    'Analyses/percentage_of_each_book_typed.html')
if save_image_copies_of_charts == True:
    fig_percentage_of_each_book_typed.write_image(
        'Analyses/percentage_of_each_book_typed.png', 
        width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_percentage_of_each_book_typed

# %% [markdown]
# ### Creating a chart that compares the number of characters in each book with the number that have been typed:
# 
# This provides a clearer view of the player's progress in typing the Bible, as each bar's height is based on the number of characters. (In contrast, bars for fully typed small books will be just as high in fig_percentage_of_each_book_typed as those for fully typed large books.)

# %%
fig_characters_typed_in_each_book = px.bar(df_characters_typed_by_book, 
x = 'Book_Name', y = ['Characters', 'Characters Typed'], barmode = 'overlay',
title = 'Books by Characters Typed')
fig_characters_typed_in_each_book.update_layout(xaxis_title='Book',
yaxis_title = 'Characters', legend_title = 'Variable')

fig_characters_typed_in_each_book.write_html(
    'Analyses/characters_typed_by_book.html')
if save_image_copies_of_charts == True:
    fig_characters_typed_in_each_book.write_image(
        'Analyses/characters_typed_by_book.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_characters_typed_in_each_book

# %% [markdown]
# ## Creating charts that show both book- and chapter-level data:

# %%
df_characters_typed_by_book_and_chapter = df_Bible.pivot_table(index = [
'Book_Order', 'Book_Name',  'Chapter_Name', 'Book_and_Chapter'], values = [
    'Characters', 'Characters_Typed'], aggfunc = 'sum').reset_index()
df_characters_typed_by_book_and_chapter[
'Proportion Typed'] = df_characters_typed_by_book_and_chapter[
'Characters_Typed'] / df_characters_typed_by_book_and_chapter['Characters']
df_characters_typed_by_book_and_chapter.to_csv(
    'Analyses/characters_typed_by_book_and_chapter.csv')
df_characters_typed_by_book_and_chapter

# %% [markdown]
# The following chart shows both books (as bars) and chapters (as sections of these bars). These sections are also color coded by the proportion of each chapter that has been typed.

# %%
fig_characters_typed_in_each_book_and_chapter = px.bar(
df_characters_typed_by_book_and_chapter, x = 'Book_Name', y = [
    'Characters'], color = 'Proportion Typed', 
hover_data = ['Book_Name', 'Chapter_Name'],
title = 'Books and Chapters by Characters Typed')
fig_characters_typed_in_each_book_and_chapter.update_layout(
xaxis_title = 'Book', yaxis_title = 'Characters')

fig_characters_typed_in_each_book_and_chapter.write_html(
    'Analyses/characters_typed_by_book_and_chapter.html')
if save_image_copies_of_charts == True:
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

# %%
print("Analyzing typing activity by period.")

# %% [markdown]
# ## Calculating the dates with the most characters and verses typed:
# 
# Note: In order to create more accurate analyses, I will filter the results to only include values with the same start and end periods. (For instance, if a given test began at 9:59 p.m. on 2023-11-17 but ended after 10 p.m., that test would get filtered out of a 'top hours by characters typed' report, since including it would extend the time frame analyzed beyond a 60-minute window.)

# %%
df_top_dates_by_characters = df_results.pivot_table(
index = ['Local_Start_Date', 'Local_End_Date'], values = 'Characters', 
aggfunc = 'sum').reset_index().sort_values('Characters', ascending = False)
# By using both the start and end dates as pivot index values, we've already 
# separated results with different start and end dates from ones whose 
# start and end dates are the same. (This will prevent the tests included
# in a given date's calculation from extending beyond just that date.)
# We'll also filter the DataFrame to exclude any results whose start
# and end dates differ:
df_top_dates_by_characters = df_top_dates_by_characters.query(
"Local_Start_Date == Local_End_Date").head(50).copy()
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
x = 'Rank and Date', y = 'Characters', text = 'Characters', title = 
'Highest Daily Character Counts')
fig_top_dates_by_characters.update_xaxes(tickangle = 90)

fig_top_dates_by_characters.write_html('Analyses/top_dates_by_characters.html')
if save_image_copies_of_charts == True:
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
x = 'Rank and Date', y = 'Verses', text = 'Verses',
title = 'Highest Daily Verse Counts')
fig_top_dates_by_verses.update_xaxes(tickangle = 90)

fig_top_dates_by_verses.write_html('Analyses/top_dates_by_verses.html')
if save_image_copies_of_charts == True:
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
df_top_months_by_characters.to_csv('Analyses/top_months_by_characters.csv', 
index = False)
df_top_months_by_characters

# %%
fig_top_months_by_characters = px.bar(df_top_months_by_characters, 
x = 'Rank and Month', y = 'Characters', text = 'Characters',
title = 'Highest Monthly Character Counts')
fig_top_months_by_characters.update_xaxes(tickangle = 90)

fig_top_months_by_characters.write_html(
    'Analyses/top_months_by_characters.html')
if save_image_copies_of_charts == True:
    fig_top_months_by_characters.write_image(
        'Analyses/top_months_by_characters.png', 
        width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_months_by_characters

# %%


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
df_top_months_by_verses.to_csv('Analyses/top_months_by_verses.csv', 
index = False)
df_top_months_by_verses

# %%
fig_top_months_by_verses = px.bar(df_top_months_by_verses, 
x = 'Rank and Month', y = 'Verses', text = 'Verses',
title = 'Highest Monthly Verse Counts')
fig_top_months_by_verses.update_xaxes(tickangle = 90)

fig_top_months_by_verses.write_html('Analyses/top_months_by_verses.html')
if save_image_copies_of_charts == True:
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
df_top_hours_by_characters.to_csv('Analyses/top_hours_by_characters.csv', 
index = False)
df_top_hours_by_characters

# %%
fig_top_hours_by_characters = px.bar(df_top_hours_by_characters, 
x = 'Hour', y = 'Characters', text = 'Characters',
title = 'Highest Hourly Character Counts')
fig_top_hours_by_characters.update_xaxes(type = 'category')

fig_top_hours_by_characters.write_html('Analyses/top_hours_by_characters.html')
if save_image_copies_of_charts == True:
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
df_top_30m_by_characters.to_csv('Analyses/top_30m_by_characters.csv', 
index = False)
df_top_30m_by_characters

# %%
fig_top_30m_by_characters = px.bar(df_top_30m_by_characters, 
x = '30-Minute Block', y = 'Characters', text = 'Characters', 
title = 'Highest 30-Minute Character Counts')
fig_top_30m_by_characters.update_xaxes(type = 'category')

fig_top_30m_by_characters.write_html(
'Analyses/top_30m_blocks_by_characters.html')
if save_image_copies_of_charts == True:
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
df_top_15m_by_characters.to_csv('Analyses/top_15m_by_characters.csv', 
index = False)
df_top_15m_by_characters

# %%
fig_top_15m_by_characters = px.bar(df_top_15m_by_characters, 
x = '15-Minute Block', y = 'Characters', text = 'Characters',
title = 'Highest 15-Minute Character Counts')
fig_top_15m_by_characters.update_xaxes(type = 'category')

fig_top_15m_by_characters.write_html(
'Analyses/top_15m_blocks_by_characters.html')
if save_image_copies_of_charts == True:
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
df_top_10m_by_characters.to_csv('Analyses/top_10m_by_characters.csv', 
index = False)
df_top_10m_by_characters

# %%
fig_top_10m_by_characters = px.bar(df_top_10m_by_characters, 
x = '10-Minute Block', y = 'Characters', text = 'Characters',
title = 'Highest 10-Minute Character Counts')
fig_top_10m_by_characters.update_xaxes(type = 'category')

fig_top_10m_by_characters.write_html(
'Analyses/top_10m_blocks_by_characters.html')
if save_image_copies_of_charts == True:
    fig_top_10m_by_characters.write_image(
        'Analyses/top_10m_blocks_by_characters.png', 
        width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_10m_by_characters

# %% [markdown]
# # Analyzing WPM and accuracy data:
# 
# (Some of this section's code derives from my work in [this script](https://github.com/kburchfiel/typeracer_data_analyzer/blob/master/typeracer_data_analyzer_v2.ipynb).)
# 

# %%
print("Creating WPM and accuracy analyses.")

# %% [markdown]
# Highest test WPM results:

# %%
df_top_100_wpm = df_results.sort_values('WPM', ascending = False).head(
    100).copy()
df_top_100_wpm['Test #'] = df_top_100_wpm.index # Creating a column that stores
# index data will make it easier to add that data into chart tooltips. (There
# may be a more elegant way to add index data into tooltips.)
# of charts
df_top_100_wpm.insert(0, 'Rank', df_top_100_wpm['WPM'].rank(
    ascending = False, method = 'min').astype('int'))
# method = 'min' assigns the lowest rank to any rows that happen to have
# the same WPM. See 
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rank.html
df_top_100_wpm.to_csv('Analyses/top_100_wpm.csv')
df_top_100_wpm

# %%
fig_top_100_wpm = px.bar(df_top_100_wpm, x = 'Rank', y = 'WPM', 
text_auto = '.6s', hover_data = ['Test #', 'Local_Start_Time', 'Book', 
'Chapter', 'Verse #', 'Verse_Order'],
title = 'Highest WPM Results for Individual Tests')

fig_top_100_wpm.write_html('Analyses/top_100_wpm.html')
if save_image_copies_of_charts == True:
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
    
    # If the user has completed fewer than 30 races, there will still be some
    # NaN 'Last 10 Avg' values within this dataset, so we'll want to 
    # remove those in order to avoid an IntCastingNaN error later in this
    # cell. The following dropna() call removes those NaN values.
    df_top_last_10_avg_results.dropna(subset = ['Last 10 Avg'], inplace = True)
    df_top_last_10_avg_results.insert(0, 'Rank', 
    df_top_last_10_avg_results['Last 10 Avg'].rank(ascending = False, 
    method = 'min').astype('int'))
    df_top_last_10_avg_results['Test #'] = df_top_last_10_avg_results.index
    df_top_last_10_avg_results.to_csv('Analyses/top_last_10_avg_results.csv', 
    index = False)
    df_top_last_10_avg_results

# %%
if len(df_results) >= 10:
    fig_top_last_10_average_wpm = px.bar(df_top_last_10_avg_results, 
    x = 'Rank', y = 'Last 10 Avg', 
    text_auto = '.6s', hover_data=['Test #', 'Local_Start_Time'],
    title = 'Highest 10-Test WPM Averages')
    fig_top_last_10_average_wpm.update_layout(
    yaxis_title = 'Average WPM over Last 10 Tests')

    fig_top_last_10_average_wpm.write_html(
        'Analyses/top_last_10_average_wpm.html')
    if save_image_copies_of_charts == True:
        fig_top_last_10_average_wpm.write_image(
            'Analyses/top_last_10_average_wpm.png', 
        width = 1920, height = 1080, engine = 'kaleido', scale = 2)
    fig_top_last_10_average_wpm

# %% [markdown]
# ### Showing WPM results and moving averages by test number:

# %%
df_results

# %%
fig_df_results_by_test_number = px.line(df_results.rename(
columns = {'cumulative_avg':'Cumulative Avg'}), x = df_results.index, 
y = ['WPM', 'Last 10 Avg', 'Last 100 Avg', 'Last 1000 Avg', 'Cumulative Avg'],
title = 'WPM by Test Number')
# If data are not yet available for some of these Y values 
# (e.g. 'Last 100 Avg'), they won't appear on the graph, but that missing data 
# won't produce an error.
fig_df_results_by_test_number.update_layout(yaxis_title = 'WPM')

fig_df_results_by_test_number.write_html('Analyses/results_by_test_number.html')
if save_image_copies_of_charts == True:
    fig_df_results_by_test_number.write_image(
    'Analyses/results_by_test_number.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)

fig_df_results_by_test_number

# %% [markdown]
# ### Creating WPM histograms for (1) all tests and (2) the last 1000 tests:
# 
# (Until you've taken more than 1,000 tests, these histograms will have the same appearance.)

# %%
fig_wpm_histogram = px.histogram(x = df_results['WPM'], nbins = 50, 
text_auto = True, title = 'WPM Histogram')
fig_wpm_histogram.update_layout(bargroupgap = 0.1, xaxis_title = 'WPM', 
yaxis_title = 'Number of Tests') 
# bargroupgap = 0.1 adds a bit of space
# in between histogram bars. See https://stackoverflow.com/a/62925197/13097194

fig_wpm_histogram.write_html('Analyses/wpm_histogram.html')
if save_image_copies_of_charts == True:
    fig_wpm_histogram.write_image('Analyses/wpm_histogram.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_wpm_histogram


# %%
fig_wpm_histogram_last_1000 = px.histogram(x = df_results.tail(1000)['WPM'], 
nbins = 50, text_auto = True, title = 'WPM Histogram for Last 1000 Tests')
fig_wpm_histogram_last_1000.update_layout(bargroupgap = 0.1, 
xaxis_title = 'WPM', 
yaxis_title = 'Number of Tests') 
fig_wpm_histogram_last_1000.write_html('Analyses/wpm_histogram_last_1000.html')
if save_image_copies_of_charts == True:
    fig_wpm_histogram_last_1000.write_image(
    'Analyses/wpm_histogram_last_1000.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_wpm_histogram_last_1000


# %% [markdown]
# ### Evaluating average results by month:

# %%
df_results_by_month = df_results.pivot_table(
    index = ['Local_Start_Year', 'Local_Start_Month'], values = [
'Count', 'WPM'], aggfunc = {'Count':'sum', 'WPM':'mean'}).reset_index()
df_results_by_month['Year/Month'] = df_results_by_month[
    'Local_Start_Year'].astype('str') + '-' + df_results_by_month[
    'Local_Start_Month'].astype('str')
df_results_by_month.rename(columns = {'Count':'Number of Tests'}, 
inplace = True)
df_results_by_month.to_csv('Analyses/results_by_month.csv', index = False)
df_results_by_month

# %%
fig_results_by_month = px.bar(df_results_by_month, x = 'Year/Month', 
y = 'WPM', color = 'Number of Tests', text_auto = '.6s', 
title = 'Average WPM by Month')
fig_results_by_month.update_xaxes(type = 'category') # This line, based on
# Pracheta's response at https://stackoverflow.com/a/64424308/13097194,
# updates the axes to show the date-month pairs as strings rather than 
# as Plotly-formatted date values. This will also prevent missing
# months from appearing in the graph.
fig_results_by_month.update_layout(legend_title_text = 'Test Count')

fig_results_by_month.write_html('Analyses/results_by_month.html')
if save_image_copies_of_charts == True:
    fig_results_by_month.write_image('Analyses/results_by_month.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_results_by_month

# %% [markdown]
# ### Evaluating average results by hour of day:

# %%
df_results_by_hour = df_results.pivot_table(index = ['Local_Start_Hour'], 
values = ['Count', 'WPM'], 
aggfunc = {'Count':'sum', 'WPM':'mean'}).reset_index()
df_results_by_hour.rename(columns = {'Count':'Number of Tests'}, inplace = True)
df_results_by_hour.to_csv('Analyses/results_by_hour.csv')
df_results_by_hour

# %%
fig_results_by_hour = px.bar(df_results_by_hour, x = 'Local_Start_Hour', 
y = 'WPM', color = 'Number of Tests', text_auto = '.6s',
title = 'Average WPM by Hour')
fig_results_by_hour.update_layout(xaxis_title = 'Hour')
fig_results_by_hour.write_html('Analyses/results_by_hour.html')
if save_image_copies_of_charts == True:
    fig_results_by_hour.write_image('Analyses/results_by_hour.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_results_by_hour

# %% [markdown]
# ### Comparing mean WPMs of Bible books:

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
x = 'Book', y = 'WPM', color = 'Tests', text_auto = '.6s', 
title = 'Average WPM by Book')
fig_mean_wpm_by_book.add_shape(type = 'line', x0 = -0.5, 
x1 = len(df_wpm_by_book) -1.5, y0 = total_mean_wpm, 
y1 = total_mean_wpm, label = {'textposition':'end',
'text':f'Average overall WPM: {total_mean_wpm.round(3)}'})
# See https://plotly.com/python/shapes/ for the add_shape() code.
# The use of -0.5 and len() - 1.5 is based on gleasocd's answer at 
# https://stackoverflow.com/a/40408960/13097194 . len(df) - 0.5 would normally
# work, except that I reduced the size of the DataFrame by 1 when excluding
# the 'Total' book.
fig_mean_wpm_by_book.write_html('Analyses/mean_wpm_by_book.html')
if save_image_copies_of_charts == True:
    fig_mean_wpm_by_book.write_image('Analyses/mean_wpm_by_book.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_mean_wpm_by_book


# %% [markdown]
# ### Comparing mean WPM for error-free and non-error free tests:

# %%
# We'll only create the graph if there is at least one mistake-free
# result and one result with errors. (Otherwise, we won't be able to
# compare these two outcomes.)
if (len(df_results.query("Mistake_Free_Test == 0")) >= 1) & (
    len(df_results.query("Mistake_Free_Test == 1")) >= 1):
    df_wpm_by_mistake_free_status = df_results.pivot_table(
    index = 'Mistake_Free_Test', values = ['WPM', 'Count'], 
    aggfunc = {'WPM':'mean', 'Count':'sum'}).reset_index()
    df_wpm_by_mistake_free_status.rename(columns = {'Count':'Tests'}, 
    inplace = True)
    df_wpm_by_mistake_free_status['Mistake_Free_Test'].replace(
    {0:'No', 1:'Yes'}, inplace = True)
    df_wpm_by_mistake_free_status.to_csv(
    'Analyses/wpm_by_mistake_free_status.csv', index = False)
    df_wpm_by_mistake_free_status

# %%
# We'll only create the graph if there is at least one mistake-free
# result and one result with errors. (Otherwise, we won't be able
# to compare these two outcomes.)
if (len(df_results.query("Mistake_Free_Test == 0")) >= 1) & (
    len(df_results.query("Mistake_Free_Test == 1")) >= 1):
    fig_wpm_by_mistake_free_status = px.bar(df_wpm_by_mistake_free_status, 
    x = 'Mistake_Free_Test', y = 'WPM', text_auto = '.6s', 
    color = 'Tests', title = 'Average WPM by Mistake-Free Status')
    fig_wpm_by_mistake_free_status.update_layout(
    xaxis_title = 'Mistake-Free Test')
    fig_wpm_by_mistake_free_status.write_html(
'Analyses/mean_wpm_by_mistake_free_status.html')
    if save_image_copies_of_charts == True:
        fig_wpm_by_mistake_free_status.write_image(
        'Analyses/mean_wpm_by_mistake_free_status.png', width = 1920, 
        height = 1080, engine = 'kaleido', scale = 2)
    fig_wpm_by_mistake_free_status

# %% [markdown]
# ### Evaluating the relationship between incorrect keypresses as a % of verse length and WPM:

# %%
# Note: the following code created a runtime error within the 
# pyinstaller-created
# .exe version of the program, so I'm excluding the "trendline = 'ols'" 
# component for now. Hopefully I can find a way to get that code to work
# in the future.
# fig_incorrect_characters_wpm_scatter = px.scatter(df_results, 
# x = 'Incorrect Characters as % of Verse Length', y = 'WPM', trendline = 'ols')
# # Note that you can hover over the best fit line to see the 
# regression results.

fig_incorrect_characters_wpm_scatter = px.scatter(df_results, 
x = 'Incorrect Characters as % of Verse Length', y = 'WPM', 
title = 'Comparison Between Incorrect Character % and WPM')


fig_incorrect_characters_wpm_scatter.write_html(
'Analyses/incorrect_characters_wpm_scatter.html')
if save_image_copies_of_charts == True:
    fig_incorrect_characters_wpm_scatter.write_image(
    'Analyses/incorrect_characters_wpm_scatter.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_incorrect_characters_wpm_scatter

# %%
fig_accuracy_wpm_histogram = px.histogram(df_results, 
x = 'Incorrect Characters as % of Verse Length', y = 'WPM', 
histfunc = 'avg', nbins = 20, text_auto = '.6s',
title = 'Average WPM for Different Character Percentage Bins')
fig_accuracy_wpm_histogram.update_layout(bargroupgap = 0.1, 
yaxis_title = 'Average WPM')
fig_accuracy_wpm_histogram.write_html(
'Analyses/incorrect_characters_wpm_histogram.html')
if save_image_copies_of_charts == True:
    fig_accuracy_wpm_histogram.write_image(
    'Analyses/incorrect_characters_wpm_histogram.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_accuracy_wpm_histogram


# %%
fig_accuracy_count_histogram = px.histogram(df_results, 
x = 'Incorrect Characters as % of Verse Length', nbins = 20, text_auto = True,
title = 'Incorrect Character Percentage Histogram')
fig_accuracy_count_histogram.update_layout(
bargroupgap = 0.1, yaxis_title = '# of Tests')
fig_accuracy_count_histogram.write_html(
'Analyses/incorrect_character_pct_histogram.html')
if save_image_copies_of_charts == True:
    fig_accuracy_count_histogram.write_image(
    'Analyses/incorrect_character_pct_histogram.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_accuracy_count_histogram

# %% [markdown]
# ### Visualizing trends in accuracy over time:

# %%
fig_incorrect_characters_by_test_number = px.line(
df_results, x = df_results.index, 
y = ['Incorrect Characters as % of Verse Length',
'Incorrect Character % Last 10 Avg',
'Incorrect Character % Last 100 Avg',
'Incorrect Character % Last 1000 Avg'],
title = 'Incorrect Characters as % of Verse Length by Test Number')
fig_incorrect_characters_by_test_number.update_layout(yaxis_title='Percentage')
fig_incorrect_characters_by_test_number.write_html(
'Analyses/incorrect_character_pct_over_time.html')
if save_image_copies_of_charts == True:
     fig_incorrect_characters_by_test_number.write_image(
     'Analyses/incorrect_character_pct_over_time.png', 
     width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_incorrect_characters_by_test_number

# %% [markdown]
# ### Average WPM by day:

# %%
df_avg_wpm_by_day = df_results.pivot_table(index = 'Local_Start_Date', 
values = ['WPM', 'Characters'], aggfunc = {
'WPM':'mean', 'Characters':'sum'}).reset_index()
character_threshold = 5000
# The following code limits the results to dates with at least 
# character_threshold characters typed; this 
# step will help prevent the chart from getting skewed by dates with
# very low character counts (which may have unusually high/low average WPMs).
df_avg_wpm_by_day.query("Characters >= @character_threshold", inplace = True)
df_avg_wpm_by_day.to_csv('Analyses/average_wpm_by_day.csv', index = False)
df_avg_wpm_by_day.reset_index(drop=True,inplace=True)
df_avg_wpm_by_day

# %%
# Note the use of <br>, <sub>, and <i> to add a smaller, italicized
# subtitle below the chart's main title. See
# https://plotly.com/chart-studio-help/adding-HTML-and-links-to-charts/
# for other HTML formatting tags that Plotly supports.
fig_avg_wpm_by_day = px.line(df_avg_wpm_by_day, x = 'Local_Start_Date', 
y = 'WPM', title = f'Average WPM by Day<br><sub><i>Note: This chart only \
includes dates on which at least {character_threshold} characters \
were typed.</i></sub>')
fig_avg_wpm_by_day.update_xaxes(type='category')
fig_avg_wpm_by_day.update_layout(xaxis_title = 'Start Date (Local)')
fig_avg_wpm_by_day.write_html('Analyses/avg_wpm_by_day.html')
if save_image_copies_of_charts == True:
    fig_avg_wpm_by_day.write_image('Analyses/avg_wpm_by_day.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_avg_wpm_by_day

# %% [markdown]
# ### Creating a bar chart that features the days with the highest average WPM results:

# %%
fig_top_daily_wpm_averages = px.bar(df_avg_wpm_by_day.sort_values(
'WPM', ascending = False).head(50).copy(), x = 'Local_Start_Date', 
y = 'WPM', text_auto = '.6s', color = 'Characters', 
title = f'Highest Daily WPM Averages\
<br><sub><i>Note: This chart only \
includes dates on which at least {character_threshold} characters \
were typed.</i></sub>')
fig_top_daily_wpm_averages.update_xaxes(type='category')
fig_top_daily_wpm_averages.update_layout(xaxis_title = 'Start Date (Local)')
fig_top_daily_wpm_averages.write_html('Analyses/top_daily_wpm_averages.html')
if save_image_copies_of_charts == True:
    fig_top_daily_wpm_averages.write_image(
    'Analyses/top_daily_wpm_averages.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)

fig_top_daily_wpm_averages

# %% [markdown]
# ### Calculating WPM percentile data:

# %%
df_wpm_by_percentile = df_results['WPM'].quantile(
q = np.arange(0, 1.05, 0.05)).transpose().reset_index()
df_wpm_by_percentile.columns = ['Percentile', 'WPM']
df_wpm_by_percentile['Percentile'] = (
df_wpm_by_percentile['Percentile']*100).astype('int')
# Some of the WPM values had additional decimal values (e.g. 15.000000000000002,
# might currently have additional decimal values, so rounding them as integers
# helps simplify them.
df_wpm_by_percentile.to_csv('Analyses/wpm_by_percentile.csv', index = False)
df_wpm_by_percentile

# %%
fig_wpm_by_percentile = px.bar(df_wpm_by_percentile, x = 'Percentile', 
y = 'WPM', text_auto = '.6s', title = 'WPM Percentiles')
fig_wpm_by_percentile.update_xaxes(type = 'category')
fig_wpm_by_percentile.write_html('Analyses/wpm_by_percentile.html')
if save_image_copies_of_charts == True:
    fig_wpm_by_percentile.write_image(
    'Analyses/wpm_by_percentile.png', width = 1920, 
    height = 1080, engine = 'kaleido', scale = 2)
fig_wpm_by_percentile

# %% [markdown]
# ### Calculating WPM data for within-session test numbers:
# 
# These data can help players determine how long it takes for their fingers to warm up when beginning a session (e.g. a set of consecutive tests) and, conversely, when fatigue begins to set in.

# %%
# Calculating average WPMs for within-session test numbers:

df_results_by_within_session_test_number = df_results.pivot_table(
index = 'Test_#_Within_Session', values = ['WPM', 'Count'], 
aggfunc = {'WPM':'mean', 'Count':'sum'}).reset_index()
df_results_by_within_session_test_number.query("Count >= 10", inplace = True)
# The above line prevents rows with low counts from skewing the results.
df_results_by_within_session_test_number.to_csv(
'Analyses/results_by_within_session_test_number.csv', index = False)
df_results_by_within_session_test_number

# %%
if len(df_results_by_within_session_test_number) > 0: # The player might not
    # yet have completed more than 10 sessions, in which case the following
    # code should be skipped (as there wouldn't be anything to graph).
    fig_wpm_by_within_session_test_number = px.line(
    df_results_by_within_session_test_number, 
    x = 'Test_#_Within_Session', y = 'WPM',
    title = 'Average WPM by Within-Session Test Number<br><sub><i>Note: Only \
sessions with at least 10 tests are included in this chart.')
    fig_wpm_by_within_session_test_number.update_layout(
    xaxis_title = 'Within-Session Test Number')
    fig_wpm_by_within_session_test_number.write_html(
    'Analyses/wpm_by_within_session_test_number.html')
    if save_image_copies_of_charts == True:
        fig_wpm_by_within_session_test_number.write_image(
        'Analyses/wpm_by_within_session_test_number.png', width = 1920, 
        height = 1080, engine = 'kaleido', scale = 2)
    fig_wpm_by_within_session_test_number

# %%
latest_session = df_results['Session'].max()

# The following chart plots the player's most recent sessions 
# on the same graph. This graph will
# be quite 'busy,' but players can double-click a session number in order 
# to show results for only that session (which may be more useful).
fig_session_results = px.line(
df_results.query("Session >= @latest_session - 9"), 
x = 'Test_#_Within_Session', y = 'WPM', color = 'Session',
title = 'WPM by Within-Session Test Number for Last 10 Sessions')
fig_session_results.update_layout(
    xaxis_title = 'Within-Session Test Number')
fig_session_results.write_html('Analyses/latest_session_results.html')
if save_image_copies_of_charts == True:
    fig_session_results.write_image(
    'Analyses/latest_session_results.png', width = 1920, 
    height = 1080, engine = 'kaleido', scale = 2)
fig_session_results

# %% [markdown]
# # Creating word-level analyses:
# 
# Note: This section used to include code that would calculate the fastest single-word entry times. However, I found that these results could be distorted by computer lag. Specifically, if the player enters keys while the computer is frozen, some of those keypress durations will be reported as shorter than they actually were. (This makes sense, in that while the computer is frozen, the actual keypress time might not get logged; instead, a later post-freeze time will get logged. This post-freeze time will then be closer to the next keypress time, causing a shorter-than-actual keypress time to get reported.) (I simulated computer lag in my tests by entering a time.sleep() command, but I believe actual lag would produce similar errors). These skewed keypress durations can in turn skew the reported time needed to enter each word.
# 
# Therefore, while the code still shows median word entry times (which are less susceptible to this issue), it will no longer calculate the fastest times that a particular word was entered. These can still be located within the word stats file, but the results should be interpreted with great caution.

# %%
# We'll skip the word-level analyses section if we have no data to analyze.

if len(df_word_stats) == 0:
    run_word_analyses = 0
else:
    run_word_analyses = 1
    print("Creating word-level analyses.")

run_word_analyses

# %%
if run_word_analyses == 1:
    df_word_stats_pivot = df_word_stats.pivot_table(index = 'word', 
    values = {'Count', 'typed_word_without_mistakes', 'WPM'}, 
    aggfunc = {'Count':'sum', 'typed_word_without_mistakes':'mean', 
    'WPM':'median'}).reset_index().sort_values(
    'WPM', ascending = False).reset_index(drop=True)
    df_word_stats_pivot.rename(columns = {'WPM':'Median WPM', 'word':'Word',
    'typed_word_without_mistakes':'Mistake-Free Entry Proportion'}, 
    inplace = True)
    common_word_cutoff = 5 # This cutoff will be used to create variants
    # of charts and tables that are limited to commonly typed words.
    df_common_word_stats_pivot = df_word_stats_pivot.query(
    "Count >= @common_word_cutoff").copy()
    df_word_stats_pivot.to_csv('Analyses/word_stats_pivot.csv', index = False)
    df_common_word_stats_pivot.to_csv('Analyses/word_stats_pivot_common.csv', 
    index = False)
    df_word_stats_pivot


# %%
df_common_word_stats_pivot

# %%
if run_word_analyses == 1:
    fig_words_with_highest_median_wpms = px.bar(df_word_stats_pivot.head(100), 
    x = 'Word', y = 'Median WPM', color = 'Count', text_auto = '.6s',
    title = 'Words With Highest Median WPMs')
    fig_words_with_highest_median_wpms.write_html(
    'Analyses/words_with_highest_median_wpms.html')
    if save_image_copies_of_charts == True:
        fig_words_with_highest_median_wpms.write_image(
        'Analyses/words_with_highest_median_wpms.png', width = 1920, 
        height = 1080, engine = 'kaleido', scale = 2)
    fig_words_with_highest_median_wpms

# %%
if (run_word_analyses == 1) & (len(df_common_word_stats_pivot) >= 1):
    fig_words_with_highest_median_wpms_common = px.bar(
    df_common_word_stats_pivot.head(100), 
    x = 'Word', y = 'Median WPM', color = 'Count', text_auto = '.6s',
    title = f'Words With Highest Median WPMs\
<br><sub><i>Note: this chart only includes words that have been typed at least \
{common_word_cutoff} times.</i></sub>')
    fig_words_with_highest_median_wpms_common.write_html(
    'Analyses/words_with_highest_median_wpms_common.html')
    if save_image_copies_of_charts == True:
        fig_words_with_highest_median_wpms_common.write_image(
        'Analyses/words_with_highest_median_wpms_common.png', width = 1920, 
        height = 1080, engine = 'kaleido', scale = 2)
    fig_words_with_highest_median_wpms_common

# %%
if run_word_analyses == 1:
    fig_words_with_lowest_median_wpms = px.bar(
    df_word_stats_pivot.sort_values(
    'Median WPM').head(100), x = 'Word', y = 'Median WPM', color = 'Count', 
    text_auto = '.6s', title = 'Words With Lowest Median WPMs')
    fig_words_with_lowest_median_wpms.write_html(
    'Analyses/words_with_lowest_median_wpms.html')
    if save_image_copies_of_charts == True:
        fig_words_with_lowest_median_wpms.write_image(
        'Analyses/words_with_lowest_median_wpms.png', width = 1920, 
        height = 1080, engine = 'kaleido', scale = 2)
    fig_words_with_lowest_median_wpms

# %%
if (run_word_analyses == 1) & (len(df_common_word_stats_pivot) >= 1):
    fig_words_with_lowest_median_wpms_common = px.bar(
    df_common_word_stats_pivot.sort_values('Median WPM').head(100), 
    x = 'Word', y = 'Median WPM', color = 'Count', text_auto = '.6s',
    title = f'Words With Lowest Median WPMs\
<br><sub><i>Note: this chart only includes words that have been typed at least \
{common_word_cutoff} times.</i></sub>')
    fig_words_with_lowest_median_wpms_common.write_html(
    'Analyses/words_with_lowest_median_wpms_common.html')
    if save_image_copies_of_charts == True:
        fig_words_with_lowest_median_wpms_common.write_image(
        'Analyses/words_with_lowest_median_wpms_common.png', width = 1920, 
        height = 1080, engine = 'kaleido', scale = 2)
    fig_words_with_lowest_median_wpms_common

# %%
df_common_word_stats_pivot

# %% [markdown]
# ### Creating charts that show which commonly-typed words have the highest and lowest accuracy rates:

# %%
if (run_word_analyses == 1) & (len(df_common_word_stats_pivot) >= 1):
    fig_words_with_highest_accuracy_rates_common = px.bar(
    df_common_word_stats_pivot.sort_values(
    ['Mistake-Free Entry Proportion', 'Count'], ascending = False).head(100),
    x = 'Word', y = 'Mistake-Free Entry Proportion', color = 'Count', 
    text_auto = '.2%',
    title = f'Words With Highest Accuracy Rates\
<br><sub><i>Note: this chart only includes words that have been typed at least \
{common_word_cutoff} times.</i></sub>')
    fig_words_with_highest_accuracy_rates_common.update_layout(
    yaxis_tickformat = '.0%', yaxis_title = '% of Mistake-Free Entries')
    fig_words_with_highest_accuracy_rates_common.write_html(
    'Analyses/words_with_highest_accuracy_rates_common.html')
    if save_image_copies_of_charts == True:
        fig_words_with_highest_accuracy_rates_common.write_image(
        'Analyses/words_with_highest_accuracy_rates_common.png', width = 1920, 
        height = 1080, engine = 'kaleido', scale = 2)
    fig_words_with_highest_accuracy_rates_common

# %%
if (run_word_analyses == 1) & (len(df_common_word_stats_pivot) >= 1):
    fig_words_with_lowest_accuracy_rates_common = px.bar(
    df_common_word_stats_pivot.sort_values(
    ['Mistake-Free Entry Proportion', 'Count'], 
    ascending = [True, False]).head(100),
    x = 'Word', y = 'Mistake-Free Entry Proportion', color = 'Count', 
    text_auto = '.2%',
    title = f'Words With Lowest Accuracy Rates\
<br><sub><i>Note: this chart only includes words that have been typed at least \
{common_word_cutoff} times.</i></sub>')
    fig_words_with_lowest_accuracy_rates_common.update_layout(
    yaxis_tickformat = '.0%', yaxis_title = '% of Mistake-Free Entries')
    fig_words_with_lowest_accuracy_rates_common.write_html(
    'Analyses/words_with_lowest_accuracy_rates_common.html')
    if save_image_copies_of_charts == True:
        fig_words_with_lowest_accuracy_rates_common.write_image(
        'Analyses/words_with_lowest_accuracy_rates_common.png', width = 1920, 
        height = 1080, engine = 'kaleido', scale = 2)
    fig_words_with_lowest_accuracy_rates_common

# %% [markdown]
# This script used to show the highest-ever WPMs for individual words, but this code has been removed due to accuracy issues caused by computer lag.

# %%
analysis_end_time = time.time()
analysis_time = analysis_end_time - analysis_start_time
print(f"Finished updating analyses in {round(analysis_time, 3)} seconds. \
Press Enter to Exit.") # Allows the console to stay open when the
# .py version of the program is run

input()


