## Type Through The Bible: A Typing Game of Biblical Proportions

Type Through The Bible is an open-source computer game that lets you build up your typing skills by writing Bible verses. The game also produces detailed analyses of your results, allowing you to see both your progress in typing the entire Bible and your growth as a typist. These analyses include word-level statistics so that you can identify words that require extra practice.

**A video overview of Type Through The Bible with gameplay footage can be found [at this link](https://youtu.be/z4cRMBTL4DM).**

## Downloading the Game

There are two ways to download and play Type Through The Bible:

### 1. Downloading the game via Itch.io

The easiest way to download and start playing the game, at least for Windows and Linux users, is to visit [its Itch.io page](https://kburchfiel.itch.io/type-through-the-bible). This page provides zipped folders that contain prebuilt executable versions of Type Through The Bible for Windows, Mac, and Linux. The other files contained within the folder are also necessary for the game to run.

Windows: Download and unzip the folder, then double-click the .exe file to launch the game. The other files contained within the folder are also necessary for the game to run.

Linux: Download and unzip the folder. Next, navigate to the unzipped folder in your terminal and enter ./ + the application's name (e.g. "./Type_The_Bible_v13"). (If you're having trouble with this second step, make sure that Type_The_Bible_v13 is allowed to be executed as a program.)  The other files contained within the folder are also necessary for the game to run.

Mac: **This program is unsigned. Therefore, in order to successfully run the executable, you would need to disable and then re-enable Gatekeeper AT YOUR OWN RISK. I strongly recommend that, instead of taking these steps, you run the program on Windows or Linux instead. Alternatively, you can run the game's Python file by downloading the source code from GitHub (see steps below).**

### 2. Downloading the game's source code from GitHub

If you are already familiar with Python, you may prefer to download the game [from GitHub](https://github.com/kburchfiel/Type_The_Bible). If you choose the latter option, make sure to reference Type_The_Bible_vx*.ipynb to review several steps you'll need to take in order to begin playing. You can then begin playing the game by navigating to the directory and running Type_The_Bible_vx*.py. 

*vx refers to the most recent version, e.g. v13. In the project's folder directory, higher numbers indicate more recent versions.

## How to Play

### Starting the Game

When you open up Type Through the Bible, you'll first get to choose which version of the typing test to use. (I recommend using V2 since it allows for more detailed statistics and also checks your responses for accuracy in real time; however, if you have trouble getting it to work, you can try V1 instead. This overview assumes that you are using V2.) Next, you'll need to select which verse to type. This can be a random verse; the first verse you haven't yet typed; or a specific verse. 

*Note: You can find the numbers corresponding to specific verses within WEB_Catholic_Version_for_game_updated.csv. For instance, if you want to type John 1:1, you can scroll down to this verse within the .csv file, identify its verse number (30326), then enter this number into the console.*

<img src = https://raw.githubusercontent.com/kburchfiel/Type_The_Bible/main/Screenshots/Starting_Game.png width="600">

### Typing a Verse

Once you've made your choice, you'll be presented with a verse to type. You can press any key to begin the test; I suggest using the space bar so that your hands can stay in the home row position. The test will end once you've successfully typed the entire verse (although you can also exit out of a test beforehand by pressing the ` key). 

The Python code underlying the game will check your response as you write it; green text means that your response is correct so far, whereas red text means that you've made a typo. (Once you've corrected the typo by pressing Backspace and/or Ctrl + Backspace, the red text will become green again.)

**​Note regarding the Mac version**: To delete a whole word when typing, use Fn + Delete. However, this will only work if there is not a space between the word and the cursor. Therefore, you'll need to press Delete until you get to the word and then hit Fn + Delete to actually delete it. (For the Windows and Linux versions, you can use Ctrl + Backspace to delete both the most recent word and any space before the word.)

<img src = https://raw.githubusercontent.com/kburchfiel/Type_The_Bible/main/Screenshots/Finished%20Typing%20Verse.png width="600">

### Choosing a New Verse

Once you've entered the last character of the verse successfully, the test will automatically end, and you'll be presented with your results. You'll then get to choose whether to retype the verse; move on to the following verse; type the first verse that you haven't finished yet; or exit the game.

### Autostart

The game also includes an autostart feature. When autostart is enabled, you'll be prompted to start typing a new verse immediately after you've finished typing the preceding verse. This makes for a more intense experience and *may* reduce your individual WPM results (since you won't have any time to review a verse before you start to write it); however, it should help you achieve a new personal best for the most characters typed in a given period. (See the Analyses section for more details about endurance-level statistics.)

### Ending the Game

When you're ready to quit, the game will save your progress in the form of three .csv files: results.csv, WEB_Catholic_Version_for_game_updated.csv, and word_stats.csv. (The Results section describes these files in more detail.) It will then create a number of analyses. Once the game informs you that it has finished updating these analyses, you'll be able to exit the console. 

Because it can take around 30 seconds (on my computer, at least) to update these analyses, you also have the option to skip them. In this case, the game will still save your progress to the aforementioned .csv files. You'll be able to update your analyses as usual the next time you play.

<img src = https://raw.githubusercontent.com/kburchfiel/Type_The_Bible/main/Screenshots/Quitting%20Game.png width="600">

## Results

Your typing stats and progress will get saved to three .csv files. **results.csv** lists all of the typing tests you have completed. It shows, for each test, the starting date and time; the verse that you typed, along with its book and chapter numbers; your CPS (characters per second) and WPM (words per minute) results; and accuracy data.

**WEB_Catholic_Version_for_game_updated.csv** lists all verses in the Catholic edition of the [World English Bible (WEB)](https://ebible.org/web/webfaq.htm), the translation used by the game. This file also shows your highest WPM for each verse along with how many times you've typed it.

**word_stats.csv** shows each word that you have typed along with corresponding CPS and WPM statistics. (I recommend interpreting these stats with caution, as computer lag can lead to incorrectly high or low WPM results.)

## Analyses

Type Through the Bible produces many different visualizations and analyses of your typing test results. These include:

**Verse WPM analyses**, including your average WPM over time; WPM results by day and month; WPM results by Bible book; and WPM histograms. 

<img src = https://raw.githubusercontent.com/kburchfiel/Type_The_Bible/main/Screenshots/Selected%20Analyses/results_by_test_number.png width="600">

<img src = https://raw.githubusercontent.com/kburchfiel/Type_The_Bible/main/Screenshots/Selected%20Analyses/wpm_by_percentile.png width="600">


**Progress analyses**, such as the number of characters you have typed in each book (along with the total number of characters in those books) and the % of each book that has been typed.

<img src = https://raw.githubusercontent.com/kburchfiel/Type_The_Bible/main/Screenshots/Selected%20Analyses/tree_map_chapters_verses.png width="600">

<img src = https://raw.githubusercontent.com/kburchfiel/Type_The_Bible/main/Screenshots/Selected%20Analyses/characters_typed_by_book.png width="600">

**Endurance analyses**. These analyses show the highest number of keypresses you have typed in a given hour, 30-minute block, 15-minute block, and 10-minute block. *(Note: these blocks of time start at specific points within the day, so if you want to beat your endurance records, you'll want to start right when these blocks begin. For instance, if you type from 5:30 to 6:30 PM, your first 30 minutes of results will get counted within the 5-to-6-PM hourly block, and your last 30 minutes will get counted within the 6-to-7-PM block. 10-, 15-, and 30-minute blocks begin at minutes that produce a whole number for a quotient when divided by 10, 15, and 30, respectively.)

<img src = https://raw.githubusercontent.com/kburchfiel/Type_The_Bible/main/Screenshots/Selected%20Analyses/top_hours_by_characters.png width="600">


**Incorrect keypress analyses**, including as your average incorrect keypress percentages over time; your average WPM by incorrect keypress tier; and an incorrect keypress/WPM scatter plot. 

<img src = https://raw.githubusercontent.com/kburchfiel/Type_The_Bible/main/Screenshots/Selected%20Analyses/incorrect_characters_wpm_scatter.png width="600">

**Word-level analyses.** These analyses reveal which words have the highest (and lowest) accuracy rates and median WPMs. (Medians are used instead of means so that computer lag will have a smaller effect on word-level statistics.)

<img src = https://raw.githubusercontent.com/kburchfiel/Type_The_Bible/main/Screenshots/Selected%20Analyses/words_with_highest_median_wpms.png width="600">

<img src = https://raw.githubusercontent.com/kburchfiel/Type_The_Bible/main/Screenshots/Selected%20Analyses/words_with_lowest_median_wpms.png width="600">

Visualizations of this data are saved to the Analyses folder in both HTML and PNG format. The HTML files are interactive, whereas the PNG files are easier to share. You can also find .csv versions of certain analyses in this folder as well.

To see all analyses available, visit [the sample Analyses folder](https://github.com/kburchfiel/Type_The_Bible/tree/main/Analyses) on the Type Through the Bible GitHub page.

## Open-Source Information

The verses presented in Type Through The Bible come from the Catholic version of the [World English Bible (WEB)](https://ebible.org/web/webfaq.htm). This translation was chosen because it is in the public domain, thus allowing it to be freely distributed. To make it easier to type verses, I replaced the em dashes in the original file with double hyphens and replaced curly single and double quotes with straight ones.

Type Through The Bible's code has been released under the MIT license, allowing you to use it for your own personal and commercial projects. See the project's [License page](https://github.com/kburchfiel/Type_The_Bible/blob/main/LICENSE) for more details. I have added documentation to the game's code to make it easier to interpret. Although the Python file (e.g. Type_The_Bible_v13.py or a later version) should be used to run the game, I recommend referencing the Jupyter notebook (e.g. Type_The_Bible_v13.ipynb) on which that file is based.

## Dedication

This project is dedicated to my wife, Allie, who has been very patient with me during the development process. Allie happens to be a very fast typist, so I'm hoping she will enjoy trying out this game herself. :)
