#!/usr/bin/python
import time
import socket
import os

homedir = os.getenv("HOME")
path = homedir + "/Pigrow/temp/"

def is_connected():
    site = "www.reddit.com"
    try:
        host = socket.gethostbyname(site)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

def initial_setup():
    while is_connected() == False:
        time.sleep(10)

    print("Found reddit, internet is up")

    filename = "./../config/dirlocs.txt"

    print("Updating program files directories")

    f1 = open('./../config/templates/dirlocs_temp.txt', 'r')
    f2 = open('./../config/dirlocs.txt', 'w')
    for line in f1:
        f2.write(line.replace('**', homedir))
    f1.close()
    f2.close()


    try:
        if not os.path.exists(homedir + '/Pigrow/temp/'):
            os.makedirs(homedir + '/Pigrow/caps/')
        if not os.path.exists(homedir + '/Pigrow/caps/'):
            os.makedirs(homedir + '/Pigrow/caps/')
        if not os.path.exists(homedir + '/Pigrow/graphs/'):
            os.makedirs(homedir + '/Pigrow/graphs/')
        if not os.path.exists(homedir + '/Pigrow/logs/'):
            os.makedirs(homedir + '/Pigrow/logs/')
        if not os.path.exists(path):
            os.makedirs(path)
    except:
        print("Couldn't make dirs, possibly not a pi...")

    print("Checking Dependencies...")
    print("  - DHT Sensor;")
    print(" This is for reading the Temp and Humid sensor, it's supplied by")
    print("    https://en.wikipedia.org/wiki/Adafruit_Industries")
    print("")
    print( "   https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated")
    print("")
    try:
        import Adafruit_DHT
        print("- Adafruit DHT driver is installed and working")
        print("- ")
    except:
        try:
            print("- Doesn't look like the ADafruit DHT driver is installed,")
            print("- Installing...")
            os.chdir(path)
            print("- Downloading Adafruit_Python_DHT from Github")
            os.system("git clone https://github.com/adafruit/Adafruit_Python_DHT.git")
            ada_path = path + "Adafruit_Python_DHT/"
            os.chdir( ada_path)
            print("- Updating your apt list and installing dependencies,")
            os.system("sudo apt-get update --yes")
            os.system("sudo apt-get install --yes build-essential python-dev python-openssl")
            print("- Dependencies installed, running --: sudo python setup.py install :--")
            os.system("sudo python "+ ada_path +"setup.py install")
            print("- Done! ")
            try:
                import Adafruit_DHT
                print("Adafruit_DHT Installed and working.")
            except:
                print("...but it doens't seem to have worked...")
                print(" Try running this script again, if not then")
                print(" follow the manual install instructions above")
                print(" and then try this script again...")
                print("")
        except:
            print("Install failed, use the install instructions linked above to do it manually.")
