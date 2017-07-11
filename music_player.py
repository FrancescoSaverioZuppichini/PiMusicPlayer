from time import sleep
from subprocess import call
import RPi.GPIO as GPIO
import os


def say(what):
    os.popen("echo \"{0}\"|espeak".format(what)).read()


USE_USB = False
# music directory
MUSIC_DIR = "Music/music/"
# first thing the player will say
WELCOME_MSG = "Hello!"
# set up the pin of the pi
GPIO.setmode(GPIO.BCM)
if USE_USB:
    try:
        # mout the usb drive
        call("sudo -p devgru18 mount /dev/sda2 Music/".split(" "))
    except Exception as e:
        # no worries here
        print(e)

say(WELCOME_MSG)
# star music server
call(["mocp", "-x"])
sleep(3)
call(["mocp", "-S"])
sleep(1)
# add music folder and play it
# used to prevent to switch state while clicking
state_btn_state = 1
# used to know the current state of the player
is_play = True
# used to know if we are in the playlist mode
is_in_playlist = False

playlists = [o for o in os.listdir(MUSIC_DIR) if os.path.isdir(os.path.join(MUSIC_DIR, o))]


if (len(playlists) <= 0):
    print("No playlist")
    call(["mocp", "-m", MUSIC_DIR, "-a", "-q", "-p"])
else:
    say("Starting playlist {0}".format(playlists[0]))
    call(["mocp", "-c", "-m", MUSIC_DIR + '/' + playlists[0], "-a", "-q", "-p"])

playlists_index = 0
# buttons
prev_btn = 4
next_btn = 5
state_btn = 6
# not used by now
volume_up_btn = 12
volume_down_btn = 13
# array with all the buttons
buttons = [prev_btn, next_btn, state_btn, volume_up_btn, volume_down_btn]
# set all buttons as input
# for button in buttons:
GPIO.setup(buttons, GPIO.IN, GPIO.PUD_UP)
# volume at 100% -> car's trimmer will be used
call(["mocp", "-v +100"])


# main method, check which button was pressed and trigger the correct action

def toogle_state():
    global is_in_playlist
    global is_play

    if is_in_playlist:
        is_in_playlist = False

        call(["mocp", "-c", "-m", MUSIC_DIR + '/' + playlists[playlists_index], "-a", "-p"])

    if is_play:
        call(["mocp", "-P"])
        print("pause")
        sleep(2)
        if (GPIO.input(state_btn) == 0):
            print('playlist mode')
            is_in_playlist = True
            say("Playlist")
    else:
        call(["mocp", "-U"])
        print("play")
    is_play = not is_play


def next():
    global is_in_playlist
    global playlists_index

    if is_in_playlist:

        playlists_index += 1
        playlists_index = playlists_index % len(playlists)

        say(playlists[playlists_index])
        print(playlists_index)
    else:
        call(["mocp", "--next"])
        print("next")


def prev():
    global is_in_playlist
    global playlists_index

    if is_in_playlist:
        playlists_index -= 1
        if (playlists_index < 0):
            playlists_index = 0
        say(playlists[playlists_index])
        print(playlists_index)
    else:
        call(["mocp", "--previous"])
        print("previus")


try:
    while True:
        if GPIO.input(state_btn) != state_btn_state:
            # pressed
            if (GPIO.input(state_btn) == 0):
                toogle_state()
            state_btn_state = GPIO.input(state_btn)
        # for the other two buttons there is not need to check if the state as changed
        # since they are used only for one action
        elif GPIO.input(prev_btn) == 0:
            prev()
        elif GPIO.input(next_btn) == 0:
           next()

        sleep(0.2)

except KeyboardInterrupt:
    call(["mocp", "-x"])
    GPIO.cleanup()
    print('bye! ;)')
