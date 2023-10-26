# %% [markdown]
# # Type The Bible
# 
# By Kenneth Burchfiel
# 
# Code is released under the MIT license; Bible verses are from the Web English Bible (Catholic Edition)* and are in the public domain.
# 
# * Genesis was not found within the original WEB Catholic Edition folder, so I copied in files from another Web English Bible translation instead. I imagine, but am not certain, that these files are the same as the actual Catholic Edition Genesis files.

# %% [markdown]
# ## More documentation to come!

# %% [markdown]
# Next steps:
# 
# 1. Prevent the script from crashing if someone has typed all of the Bible verses (which would make verses_not_yet_typed a blank list)
# 2. Add in additional visualizations to show players' progress in (1) typing the Bible and (2) increasing their typing speed

# %%
import pandas as pd
import time
from getch import getch # Installed this library using pip install py-getch, not
# pip install getch. See https://github.com/joeyespo/py-getch
import numpy as np
from datetime import datetime, date, timezone # Based on 
# https://docs.python.org/3/library/datetime.html

# %%
df_Bible = pd.read_csv('WEB_Catholic_Version_for_game_updated.csv')
df_Bible

# %%
df_results = pd.read_csv('results.csv', index_col='Test_Number')
df_results

# %%
# # If you ever need to drop a particular result (e.g. due to a glitch), you can do so as follows:
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
# [This fantastic answer](https://stackoverflow.com/a/23294659/13097194) by 'Kevin' at Stack Overflow proved helpful in implementing user validation code within this program. 

# %%
def select_verse():
    print("Select a verse to type! Enter 0 to receive a random verse\n\
or enter a verse number (see 'Verse_Order_Within_Bible column of\n\
the WEB_Catholic_Version.csv spreadsheet for a list of numbers to enter\n\
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
            verses_not_yet_typed = list(df_Bible.query("Typed == 0")['Verse_Order_Within_Bible'].copy())
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
            verses_not_yet_typed = list(df_Bible.query("Typed == 0")['Verse_Order_Within_Bible'].copy())
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
len(list(df_Bible.query("Typed == 7")['Verse_Order_Within_Bible'].copy()))

# %%
def run_typing_test(verse_number, results_table):
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
        verse_number-1]['Verse_Order_Within_Bible']
    
    complete_flag = 0
    while complete_flag == 0:
        print(f"Your verse to type is {book} \
{chapter}:{verse_number_within_chapter} (verse {verse_number_within_Bible} \
within the Bible .csv file).\n")
        print(f"Here is the verse:\n{verse}\n") 
        print("You can also exit this test by entering 'exit'.\nPress any key \
to begin typing!'")
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
        print("Start!")
        local_start_time = datetime.now().isoformat()
        utc_start_time = datetime.now(timezone.utc).isoformat()
        typing_start_time = time.time()
        verse_response = input() 
        # The following code will execute once the player finishes typing and
        # hits Enter. (Having the program evaluate the player's entry only after
        # 'Enter' is pressed isn't the best option, as the time required to
        # hit Enter will reduce the player's reported WPM. In the future,
        # I might revise this code so that the text can get evaluated
        # immediately when the player has typed all characters of the text.
        # (Counting the characters as the player types would be one way
        # to implement this revision.)

        typing_end_time = time.time()
        typing_time = typing_end_time - typing_start_time
        if verse_response == verse:
            print(f"Well done! You typed the verse correctly.")
            complete_flag = 1 # Setting this flag to 1 allows the player to exit
            # out of the while statement.
        elif verse_response.lower() == 'exit':
            print("Exiting typing test.")
            return results_table # Exits the function without saving the 
            # current test to results_table or df_Bible
        else:
            print("Sorry, that wasn't the correct input. Try again!")   


    # Calculating typing statistics and storing them within a single-row
    # DataFrame:

    cps = len(verse) / typing_time # Calculating characters per second
    wpm = cps * 12 # Multiplying by 60 to convert from characters to minutes, 
    # then dividing by 5 to convert from characters to words.
    wpm

    print(f"Your CPS and WPM were {round(cps, 3)} and {round(wpm, 3)}, respectively.")

    # Creating a single-row DataFrame that stores the player's results:
    df_latest_result = pd.DataFrame(index = [len(results_table)+1], data = {'Unix_Start_Time':typing_start_time, 
    'Local_Start_Time':local_start_time,
    'UTC_Start_Time':utc_start_time,
    'Characters':len(verse),
    'Seconds':typing_time, 
    'CPS': cps,
    'WPM':wpm,
    'Book': book,
    'Chapter': chapter,
    'Verse #': verse_number_within_chapter,
    'Verse':verse, 
    'Verse_Order':verse_number_within_Bible})
    df_latest_result.index.name = 'Test_Number'
    df_latest_result

    # Adding this new row to results_table:
    results_table = pd.concat([results_table, df_latest_result])\
    
    # Note: I could also have used df.at or df.iloc to add a new row
    # to df_latest_result, but I chose a pd.concat() setup in order to ensure
    # that the latest result would never overwrite an earlier result.
    

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

    return results_table


# %%
# run_typing_test(1, results_table=df_results)

# %%
def select_subsequent_verse(previous_verse_number):
    '''This function allows the player to specify which verse to
    type next, or, alternatively, to exit the game.'''
    print("Press 0 to retry the verse you just typed; \
1 to type the next verse; 2 to type the next verse that hasn't yet been typed; \
3 to select a different verse; \
or -1 to save your results and exit.")
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
                    "Typed == 0")['Verse_Order_Within_Bible'].copy())
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
            elif response == -1:
                return response
            else: # A number other than -1, 0, 1, 2, or 3 was passed.
                print("Please enter either -1, 0, 1, 2, or 3.\n")  

# %%
def run_game(results_table):
    '''This function runs Type the Bible by calling various other functions.
    It allows users to select
    verses to type, then runs typing tests and stores the results in
    the DataFrame passed to results_table.'''
    
    print("Welcome to Type the Bible!")
    verse_number = select_verse()
    
    while True: # Allows the game to continue until the user exits
        results_table = run_typing_test(verse_number=verse_number, 
        results_table=results_table)
        
        # The player will now be prompted to select a new verse number 
        # (or to save and quit). This verse_number, provided it is not -1,
        # will then be passed back to run_typing_test().
        verse_number = select_subsequent_verse(
            previous_verse_number=verse_number)
        if verse_number == -1: # In this case, the game will quit and the 
            # user's new test results will be saved to results_table.
            return results_table 

# %%
df_results = run_game(results_table = df_results)

# %%
# Updating certain df_Bible columns to reflect new results:

# %%
df_Bible['Characters_Typed'] = df_Bible['Characters'] * df_Bible['Typed']
df_Bible['Total_Characters_Typed'] = df_Bible['Characters'] * df_Bible['Tests']
df_Bible

# %%
characters_typed_sum = df_Bible['Characters_Typed'].sum()
proportion_of_Bible_typed = characters_typed_sum / df_Bible['Characters'].sum()

print(f"You have typed {characters_typed_sum} characters so far, which represents \
{round(100*proportion_of_Bible_typed, 5)}% of the Bible.")



# %%
df_results

# %%
df_results.to_csv('results.csv')

# %%
df_Bible.to_csv('WEB_Catholic_Version_for_game_updated.csv', index = False)

# %%
print("Enter any key to exit.") # Allows the console to stay open when the
# .py version of the program is run
input()


