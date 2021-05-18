## radio
#radio2py
import os
import random
import wave
import contextlib
import time
import subprocess
import random

dir = "/home/pi/Desktop/temp/"
dir2 = "/media/pi/5427-67DD"
playing = True
def startup(d1,d2):
    dir=d1
    dir2=d2

def play(path2, title, artist,freq=93.7, fast=False, power=1, info="93.7 the radio station"):
    namestring = "\""+title + " by " + artist + "\""
    os.system('sudo killall -9 pifm') # cleanup helps manage memory leak. its not perfect and eventually explodes
    time.sleep(1)
    p=subprocess.Popen("sudo /home/pi/PiFM/src/pifm --ps \"93.7 the bean\" --rt "+namestring+" --freq "+freq+" --audio \"" + path2 + "\" --preemph us --pty 9 --power "+str(power), shell=True)
    print('Now playing: ' + title + ' by ' + artist)
    with contextlib.closing(wave.open(path2,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = 2*round(frames / float(rate)) + 1 # the + 1 makes sure it doesn't cut off early, but it includes a short stutter at the end
    if fast: ##this deals with the initial song being played at 2x speed in some cases. it plays a silent .WAV and kills it in 15 seconds when enabled
        time.sleep(15)
        os.system('sudo killall -9 pifm')
        time.sleep(5)
        return 0
    for i in range(duration):
        time.sleep(1)
        print("Time remaining: " + str(duration-i) + "      ", end='\r') #waits for the song to end before killing it, and prints duration to console
    time.sleep(1)
    os.system('sudo killall -9 pifm')

def preprocess(): #converts a handful of filetypes to the required WAV files with a really wierd encoding
    print('preprocessing\n\n')
    nef = 0
    try:
        leng=len(os.listdir(dir2))
    except:
        nef = 1
        print("no drive, defaulting to last setup")
        return None
        leng=0
    if nef == 0:
        print('clearing temp')
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
    prog=0
    opens = open("processed.txt","a")
    opens.close()
    for g in range(2):
        for f in os.listdir(dir2):
            if f != "System Volume Information":
                print(str(prog)+ "/" + str(leng), end="\r")
                extension=f.split(".")[1]
                #print("ffmpeg -i \"" + os.path.join(dir2,str(f)) + "\" \"" + os.path.join(dir2,str(f)).split(".")[0] + ".wav\"") #<-- debug crap
                if extension != "wav":
                    os.system("ffmpeg -y -i \"" + os.path.join(dir2,str(f)) + "\" \"" + os.path.join(dir2,str(f)).split(".")[0] + ".wav\"")
                else:
                    os.system('sudo sox "'+dir2+f+'" "'+dir+f.split(".")[0] + '.wav" speed 2' )
                prog+=1

def info(filename): ##this returns a formatted list of song info from its filename thats formatted properly; "Backstreet Boys-I want it that way.wav" would return [Backstreet Boys, I want it that way]
    try:
        raw = filename.split(" - ")
        artist = raw[0]
        title = raw[1].split(".")[0]
    except:
        artist = "unknown"
        title = "unknown"
    return [title,artist]

def shuffle_play(overspeed=False):
    playing=True
    try:
        if os.path.exists(os.path.join(dir2,"processed.txt")): #this checks for a text file in the main directoyr called "processed.txt". if it exists, it will skip processing, because it takes ages
            pass
        else:
            preprocess()
    except:
        print('no drive')

    print('starting')

    if overspeed:
        play('/home/pi/Desktop/silent.wav','unknown','unknown',True)

    while playing:
        try:
            files = os.listdir("/home/pi/Desktop/temp/")
            random.shuffle(files)
            for f in files:
                if f.endswith(".wav"):
                    data=info(f)
                    play(str(os.path.join(dir,f)), data[0], data[1])
        except:
            print('fatal, restarting')

def stop():
    playing=False
    os.system('sudo killall -9 pifm')
    time.sleep(1)
