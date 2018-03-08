#!/usr/bin/python

class Device:
    global name, pin, path, devicetype


class Sensor(Device):
    global sensorType

    def __init__(self, name_, pin_, senstype_, path_):
        self.devicetype = 1
        self.sensorType = senstype_
        self.name = name_
        self.pin = pin_
        self.path = path_

class Switch(Device):
    global switchType, normalState

    def __init__(self, name_, pin_, switchtype_, normalstate_):
        self.devicetype = 2
        self.switchType = switchtype_
        self.name = name_
        self.pin = pin_
        self.normalstate = normalstate_

class Script():
    global name
    global active
    global scriptType
    #path

class StartupScript(Script):
    self.scriptType = 1

class TimedScript(Script):
    self.scriptType = 2

class TriggeredScript(Script):
    sel.scriptType = 3


class RedditManager:
    global bot_username
    global bot_password
    global username
    global password

    global subbreddit
    global wiki_title
    global live_wiki_title
    global watcher_name

    def __init__:


    def send_test_message:
        import praw
        import socket
        print("Attempting to send a message to" + self.watcher_name)

        if (    self.username and self.password
            and self.bot_username and self.bot_password
            and self.watcher_name ):

            try:
                reddit = praw.Reddit(user_agent="pigrow config script test message",
                                     client_id=self.bot_username,
                                     client_secret=self.bot_password,
                                     username=self.username,
                                     password=self.password)
            except:
                print("Couldn't log into Reddit.")
                raise
                try:
                    print(" - Checking conneciton..")
                    host = socket.gethostbyname("www.reddit.com")
                    s = socket.create_connection((host, 80), 2)
                    print(" -- Connected to the internet and reddit is up.")
                    print("check you login details")
                except:
                    print("We don't appear to be able to connect to reddit, check your connection and try again...")
                exit()

                print("Logged into reddit, trying to send message to " + str(watcher_name))

                try:
                    whereto = praw.models.Redditor(reddit, name=watcher_name)
                    whereto.message('Test message from setup.py', "Congratulations, you have a working pigrow!")
                    print("The message has been sent, it should appear in your inbox any second...")
                    print(" If you don't get the message check your login details and reddit settings")
                    print("   -also it might be worth checking you can send messages from the bot account")
                    print("    log into it from reddit and send your main account a hello")
                except Exception as e:
                    print("Sorry it didn't work this time, check your login details and username")
                    print("The exception was; " + str(e))
                    print("")
                    print("A 403 means bad login details or reddit issues, 404 means connection issues or reddit issues")
                    print("If everything seems correct then check you can post on reddit from the bot account normally")
                print("")
                raw_input("Press return to continue...")

        else:
            print("You need to add aditional credentials")





    def start_reddit_ear(self):
        print("Reddit Settings Ear is the program that listens for reddit messages,")
        print(" -use the cron start-up script menu to enable it on boot up")
        print("")
        print("Checking it's not already running..")

        try:
            script = autorun_path+"reddit_settings_ear.py"
            script_test = map(int,check_output(["pidof",script,"-x"]).split())
            print(" Found "+str(len(script_test))+" running versions.")
            killorignore = raw_input("Do you want to kill these and restart the script? Y/n")
            if killorignore == "y" or killorignore == "Y":
                os.system("pkill reddit_set")
                print("Old scripts killed")
                os.system("nohup "+autorun_path+"reddit_settings_ear.py &")
                print("new script started.")
        except:
            print("reddit_settings_ear.py doesn't appear to be running...")
            print autorun_path+"reddit_settings_ear.py"
            os.system("nohup "+autorun_path+"reddit_settings_ear.py &")

        print(" ")
        print(" Press return to continue")
        raw_input("...")


    def print_reddit_details(self):
            print("  Reddit Log in details;")
            print("      ")
            print("Pigrow Bot Account; ")
            print("   Username; " + my_username)
            print("   Password; " + my_password)
            print("  Client id; " + my_client_id)
            print("  Secret id; " + my_client_secret)
            print("")
            print("Wiki Information;")
            print("     Subreddit; " + subreddit)
            print(" Settings Wiki; " + wiki_title)
            print("     Live Wiki; " + live_wiki_title)
            print("")
            print("Person who is in control,")
            print("  Watcher/Commander; " + watcher_name)
            print("")
