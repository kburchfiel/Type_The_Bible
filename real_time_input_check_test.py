from getch import getch
from colorama import just_fix_windows_console, Fore, Back, Style
# From https://github.com/tartley/colorama/blob/master/demos/demo01.py
just_fix_windows_console() # From https://github.com/tartley/colorama/blob/master/demos/demo01.py


string_to_type = 'This is a test.'
# response = ''
response = ''
print(f"Try typing: '{string_to_type}'")
while True:
    character = getch()
    if character == b'\x08': # called print(character) after
        # hitting backspace in order to find this code
        response = response[:-1]
    elif character == b'\r': # Returns True if the user hits Enter.
        break
    else:
        response += character.decode('ascii') 
    # See https://stackoverflow.com/questions/17615414/how-to-convert-binary-string-to-normal-string-in-python3
    if string_to_type[0:len(response)] == response:
        text_color = Fore.GREEN
    else:
        text_color = Fore.RED 
    print(f"{text_color}{response}", end = "\r", flush = True)
    # The 'end' and 'flush' arguments are 
    # Based on https://stackoverflow.com/a/69030559/13097194
    # For the use of Colorama to produce red and green text, see
    # https://pypi.org/project/colorama/
    # and https://stackoverflow.com/a/3332860/13097194
    if response == string_to_type:
        print("\nSuccess!")
        print(Style.RESET_ALL) # Resets the color of the text.
        # See https://pypi.org/project/colorama/
        break