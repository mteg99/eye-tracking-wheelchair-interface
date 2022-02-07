from  pycreate2 import Create2
import time

# Create a Create2.
port = "/dev/serial"  # Update with serial port
bot = Create2(port)

# Start the Create 2
bot.start()

# Put the Create2 into 'safe' mode so we can drive it
# This will still provide some protection
bot.safe()

print("\n")
print("s-stop f-forward b-backward r-right l-left e-exit")
print("\n")  

while (1):

    x = input()

    if x == 'f':
        print('forward')
        bot.drive_direct(100, 100)
        x = 'z'

    elif x == 'r':
        print('right')
        bot.drive_direct(-200,200)
        x = 'z'

    elif x == 'l':
        print('left')
        bot.drive_direct(200,-200) 
        x = 'z'

    elif x == 'b':
        print('backwards')
        bot.drive_direct(-100, -100)
        x = 'z'

    elif x == 's':
        print('stop')
        bot.drive_stop()
        x = 'z'

    elif x == 'e':
        print('end')
        bot.drive_stop()
        bot.close()
        break

    else:
        print("<<<  wrong data  >>>")
        print("please enter the defined data to continue.....")