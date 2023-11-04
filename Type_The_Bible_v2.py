# %% [markdown]
# # Type Through The Bible
# 
# By Kenneth Burchfiel
# 
# Code is released under the MIT license; Bible verses are from the Web English Bible (Catholic Edition)* and are in the public domain.
# 
# \* Genesis was not found within the original WEB Catholic Edition folder, so I copied in files from another Web English Bible translation instead. I imagine, but am not certain, that these files are the same as the actual Catholic Edition Genesis files.

# %% [markdown]
# ## More documentation to come!

# %% [markdown]
# Next steps: (Not necessarily in order of importance)
# 
# * See if there's a way to alert the user (perhaps via a sound?) when a character is typed incorrectly.
# * Improve chart formatting (e.g. add titles, legend names, etc.)
# * Add in more documentation

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
        verse_number-1]['Verse_Order']
    
    # I moved these introductory comments out of the following while loop
    # in order to simplify the dialogue presented to users during retest
    # attempts.
    print("Welcome to the typing test! Note that you can exit a test in \
progress by entering 'exit.'")
    print(f"\nYour verse to type is {book} \
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
            print("Try again!")

    # Calculating typing statistics and storing them within a single-row
    # DataFrame:

    cps = len(verse) / typing_time # Calculating characters per second
    wpm = cps * 12 # Multiplying by 60 to convert from characters to minutes, 
    # then dividing by 5 to convert from characters to words.
    wpm

    print(f"Your CPS and WPM were {round(cps, 3)} and {round(wpm, 3)}, \
respectively.")

    # Creating a single-row DataFrame that stores the player's results:
    df_latest_result = pd.DataFrame(index = [
        len(results_table)+1], data = {'Unix_Start_Time':typing_start_time, 
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
            elif response == -1:
                return response
            else: # A number other than -1, 0, 1, 2, or 3 was passed.
                print("Please enter either -1, 0, 1, 2, or 3.\n")  

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
def run_game(results_table):
    '''This function runs Type Through the Bible by 
    calling various other functions. It allows users to select
    verses to type, then runs typing tests and stores the results in
    the DataFrame passed to results_table.'''
    
    print("Welcome to Type Through the Bible!")
    # The game will now share the player's progress for the current day:
    print(calculate_current_day_results(results_table))
    verse_number = select_verse()
    
    while True: # Allows the game to continue until the user exits
        results_table = run_typing_test(verse_number=verse_number, 
        results_table=results_table)
        # The game will next share an updated progress report:
        print(calculate_current_day_results(results_table))
        
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

df_results['Local_Year'] = pd.to_datetime(df_results['Local_Start_Time']).dt.year
df_results['Local_Month'] = pd.to_datetime(df_results['Local_Start_Time']).dt.month
df_results['Local_Date'] = pd.to_datetime(df_results['Local_Start_Time']).dt.date
df_results['Local_Hour'] = pd.to_datetime(df_results['Local_Start_Time']).dt.hour
df_results['Count'] = 1 # Useful for pivot tables that analyze test counts
# by book, month, etc.

# The following line uses a list comprehension to generate a cumulative average
# of all WPM scores up until the current race. .iloc searches from 0 to i+1 for
# each row so that that row is included in the calculation.
df_results['cumulative_avg'] = [round(np.mean(df_results.iloc[0:i+1]['WPM']),
3) for i in range(len(df_results))]
df_results

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
print("Successfully saved updated copies of the Results and Bible .csv files.")

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
# ## Calculating the dates with the most characters and verses typed:

# %%
df_top_dates_by_characters = df_results.pivot_table(
    index = 'Local_Date', values = 'Characters', aggfunc = 'sum').reset_index(
    ).sort_values('Characters', ascending = False).head(50)
df_top_dates_by_characters['Rank'] = df_top_dates_by_characters[
    'Characters'].rank(ascending = False, method = 'min').astype('int')
# Creating a column that shows both the rank and date: (This also prevents
# Plotly from converting the x axis to a date range, which would interfere
# with the order of the chart items)
df_top_dates_by_characters['Rank and Date'] = '#'+df_top_dates_by_characters[
    'Rank'].astype('str') + ': ' + df_top_dates_by_characters[
        'Local_Date'].astype('str')
df_top_dates_by_characters.reset_index(drop=True,inplace=True)

# %%
fig_top_dates_by_characters = px.bar(df_top_dates_by_characters, 
x = 'Rank and Date', y = 'Characters')
fig_top_dates_by_characters.update_xaxes(tickangle = 90)
fig_top_dates_by_characters.write_html('Analyses/top_dates_by_characters.html')
fig_top_dates_by_characters.write_image(
    'Analyses/top_dates_by_characters.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_dates_by_characters

# %%
df_top_dates_by_verses = df_results.pivot_table(
    index = 'Local_Date', values = 'Count', aggfunc = 'sum').reset_index(
    ).rename(columns = {'Count':'Verses'}).sort_values(
        'Verses', ascending = False).head(50)


df_top_dates_by_verses['Rank'] = df_top_dates_by_verses['Verses'].rank(
    ascending = False, method = 'min').astype('int')
df_top_dates_by_verses['Rank and Date'] = '#'+df_top_dates_by_verses[
    'Rank'].astype('str') + ': ' + df_top_dates_by_verses[
        'Local_Date'].astype('str')
df_top_dates_by_verses.reset_index(drop=True,inplace=True)
df_top_dates_by_verses

# %%
fig_top_dates_by_verses = px.bar(df_top_dates_by_verses, 
x = 'Rank and Date', y = 'Verses')
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
    index = ['Local_Year', 'Local_Month'], 
    values = 'Characters', aggfunc = 'sum').reset_index(
    ).sort_values('Characters', ascending = False).head(50)

df_top_months_by_characters['Rank'] = df_top_months_by_characters[
'Characters'].rank(ascending = False, method = 'min').astype('int')
df_top_months_by_characters['Rank and Month'] = '#'+df_top_months_by_characters[
    'Rank'].astype('str') + ': ' + df_top_months_by_characters[
        'Local_Year'].astype('str') + '-' + df_top_months_by_characters[
            'Local_Month'].astype('str')
df_top_months_by_characters.reset_index(drop=True,inplace=True)

df_top_months_by_characters

# %%
fig_top_months_by_characters = px.bar(df_top_months_by_characters, 
x = 'Rank and Month', y = 'Characters')
fig_top_months_by_characters.update_xaxes(tickangle = 90)
fig_top_months_by_characters.write_html(
    'Analyses/top_months_by_characters.html')
fig_top_months_by_characters.write_image(
    'Analyses/top_months_by_characters.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_months_by_characters

# %%
df_top_months_by_verses = df_results.pivot_table(
    index = ['Local_Year', 'Local_Month'], 
    values = 'Count', aggfunc = 'sum').reset_index(
    ).rename(columns={'Count':'Verses'}).sort_values(
        'Verses', ascending = False).head(50)

df_top_months_by_verses['Rank'] = df_top_months_by_verses['Verses'].rank(
    ascending = False, method = 'min').astype('int')
df_top_months_by_verses['Rank and Month'] = '#'+df_top_months_by_verses[
    'Rank'].astype('str') + ': ' + df_top_months_by_verses[
        'Local_Year'].astype('str') + '-' + df_top_months_by_verses[
            'Local_Month'].astype('str')
df_top_months_by_verses.reset_index(drop=True,inplace=True)

df_top_months_by_verses

# %%
fig_top_months_by_verses = px.bar(df_top_months_by_verses, 
x = 'Rank and Month', y = 'Verses')
fig_top_months_by_verses.update_xaxes(tickangle = 90)
fig_top_months_by_verses.write_html('Analyses/top_months_by_verses.html')
fig_top_months_by_verses.write_image(
    'Analyses/top_months_by_verses.png', 
    width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_months_by_verses

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
fig_top_100_wpm = px.bar(df_top_100_wpm, x = 'Rank', y = 'WPM')
fig_top_100_wpm.write_html('Analyses/top_100_wpm.html')
fig_top_100_wpm.write_image('Analyses/top_100_wpm.png', 
width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_top_100_wpm

# %% [markdown]
# Top 20 'Last 10 Average' values:

# %%
df_top_20_last_10_avg_results = df_results.sort_values(
    'Last 10 Avg', ascending = False).head(20).copy()
df_top_20_last_10_avg_results

# %%
fig_df_results_by_test_number = px.line(df_results, x = df_results.index, 
y = ['WPM', 'Last 10 Avg', 'Last 100 Avg', 'Last 1000 Avg', 'cumulative_avg'])
fig_df_results_by_test_number.write_html('Analyses/results_by_test_number.html')
fig_df_results_by_test_number.write_image('Analyses/results_by_test_number.png', 
width = 1920, height = 1080, engine = 'kaleido', scale = 2)
fig_df_results_by_test_number

# %% [markdown]
# ## Evaluating average results by month:

# %%
df_results_by_month = df_results.pivot_table(
    index = ['Local_Year', 'Local_Month'], values = ['Count', 'WPM'], 
    aggfunc = {'Count':'sum', 'WPM':'mean'}).reset_index()
# Enclosing the year/month in parentheses so that they won't be converted
df_results_by_month['Year/Month'] = df_results_by_month[
    'Local_Year'].astype('str') + '-' + df_results_by_month[
    'Local_Month'].astype('str')
df_results_by_month.to_csv('Analyses/results_by_month.csv')
df_results_by_month

# %%
fig_results_by_month = px.bar(df_results_by_month, x = 'Year/Month', 
y = 'WPM', color = 'Count')
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
df_results_by_hour = df_results.pivot_table(index = ['Local_Hour'], 
values = ['Count', 'WPM'], aggfunc = {'Count':'sum', 'WPM':'mean'}).reset_index()
df_results_by_hour

# %%
fig_results_by_hour = px.bar(df_results_by_hour, x = 'Local_Hour', 
y = 'WPM', color = 'Count')
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
df_wpm_by_book.columns = 'Book', 'Tests', 'Mean WPM'
df_wpm_by_book.sort_values('Mean WPM', ascending = False, inplace = True)
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
total_mean_wpm = df_wpm_by_book.query("Book == 'Total'").iloc[0]['Mean WPM']
total_mean_wpm

fig_mean_wpm_by_book = px.bar(df_wpm_by_book.query("Book != 'Total'"), 
x = 'Book', y = 'Mean WPM', color = 'Tests')
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


# %%
analysis_end_time = time.time()
analysis_time = analysis_end_time - analysis_start_time
print(f"Finished updating analyses in {round(analysis_time, 3)} seconds. \
Enter any key to exit.") # Allows the console to stay open when the
# .py version of the program is run

input()


