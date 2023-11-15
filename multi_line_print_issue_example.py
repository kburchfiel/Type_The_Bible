from getch import getch

response = ''
while True: 
    character = getch() # getch() allows each character to be 
    # checked, making it easier to identify mistyped words.
    response += character.decode('ascii') 

    # The addition of 'end = "\r", which comes from Sencer H at
    #  https://stackoverflow.com/a/69030559/13097194,
    #  allows characters to get 
    # displayed immediately
    # after one another rather than on separate lines. It also
    # prevents a new line from appearing whenever the user 
    # types an entry.
    print(response, end = "\r", flush = True)