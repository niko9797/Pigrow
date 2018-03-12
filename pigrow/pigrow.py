#!/usr/bin/python
import os, sys, install
from subprocess import check_output
from crontab import CronTab   #  pip install python-crontab
cron = CronTab(user=True)  #can be user+True, 'yourusername' or 'root' all work.

homedir = os.getenv("HOME")
config_path = homedir + "/Pigrow/config/"
loc_locs    = homedir + "/Pigrow/config/dirlocs.txt"

#folders that get looked in for the scripts to add to cron  - will deduce thes from main path to take usernames into account when i get round to it
autorun_path = homedir + "/Pigrow/scripts/autorun/"    #reboot scripts'
cron_path    = homedir + "/Pigrow/scripts/cron/"       #repeting scripts
switch_path  = homedir + "/Pigrow/scripts/switches/"   #timed scripts

#autorun_path = "/home/pragmo/pigitgrow/Pigrow/scripts/autorun/"      #reboot scripts'           #######
#cron_path    = "/home/pragmo/pigitgrow/Pigrow/scripts/cron/"         #repeting scripts      ################   THESE ARE FOR ME ONLY!!!!
#switch_path  = "/home/pragmo/pigitgrow/Pigrow/scripts/switches/"     #timed scripts             ########

valid_gpio=[2,3,4,17,27,22,10,9,11,0,5,6,13,19,26,14,15,18,23,24,25,8,7,1,12,16,20,21]
used_gpio_num=[]
loc_dic = {}
pi_set={}
used_gpio=[]
# Defaults


def set_loc_defaults():
    global watcher_name, loc_settings, loc_switchlog, loc_dht_log, loc_dht_log, err_log, caps_path, graph_path, log_path, my_client_id, my_client_secret, my_username, my_password, subreddit, wiki_title, live_wiki_title
    loc_settings    = homedir + "/Pigrow/config/pigrow_config.txt"
    loc_switchlog   = homedir + "/Pigrow/logs/switch_log.txt"
    loc_dht_log     = homedir + "/Pigrow/logs/dht22_log.txt"
    err_log         = homedir + "/Pigrow/logs/err_log.txt"
    caps_path    = homedir + "/Pigrow/caps/"
    graph_path   = homedir + "/Pigrow/graphs/"
    log_path     = homedir + "/Pigrow/logs/"
    my_client_id      = " "
    my_client_secret  = " "
    my_username       = " "
    my_password       = " "
    subreddit       = "Pigrow"
    wiki_title      = "livegrow_test_settings"
    live_wiki_title = "livegrow_test"
    watcher_name    = ' '


def load_loclocs():
    print("Loading location details")
    with open(loc_locs, "r") as f:
        for line in f:
            s_item = line.split("=")
            loc_dic[s_item[0]]=s_item[1].rstrip('\n') #adds each setting to dictionary

def load_locs():
    with open(loc_settings, "r") as f:
        for line in f:
            s_item = line.split("=")
            pi_set[s_item[0]]=s_item[1].rstrip('\n')


def write_loclocs():
    with open(loc_locs, "w") as f:
        for a,b in loc_dic.iteritems():
            try:
                s_line = str(a) +"="+ str(b) +"\n"
                f.write(s_line)
                #print s_line
            except:
                print("ERROR SETTINGS FILE ERROR SETTING NOT SAVED _ SERIOUS FAULT!")

def set_locs_and_passes():
    global watcher_name, loc_settings, loc_switchlog, loc_dht_log, loc_dht_log, err_log, caps_path, graph_path, log_path, my_client_id, my_client_secret, my_username, my_password, subreddit, wiki_title, live_wiki_title
    try:
        load_loclocs()
    except:
        print(" Couldn't Load the logs")
    try:
        #print loc_settings
        loc_settings    = loc_dic['loc_settings']
        #print loc_settings
    except:
        print("IMPORTANT - Location of Settings File not included in file, adding default - " + loc_settings)
        loc_dic['loc_settings']=loc_settings
    try:
        loc_switchlog    = loc_dic['loc_switchlog']
    except:
        print("IMPORTANT - Location of switch log not included in file, adding default - " + loc_switchlog)
        loc_dic['loc_switchlog']=loc_switchlog
    try:
        loc_dht_log    = loc_dic['loc_dht_log']
    except:
        print("IMPORTANT - Location of DHT log not included in file, adding default - " + loc_dht_log)
        loc_dic['loc_dht_log']=loc_dht_log
    try:
        err_log    = loc_dic['err_log']
    except:
        print("IMPORTANT - Location of Error log not included in file, adding default - " + err_log)
        loc_dic['err_log']=err_log
    try:
        caps_path    = loc_dic['caps_path']
    except:
        print("IMPORTANT - Location of caps path not included in file, adding default - " + caps_path)
        loc_dic['caps_path']=caps_path
    try:
        graph_path    = loc_dic['graph_path']
    except:
        print("IMPORTANT - Location of Graph path not included in file, adding default - " + graph_path)
        loc_dic['graph_path']=graph_path
    try:
        log_path    = loc_dic['log_path']
    except:
        print("IMPORTANT - Location of log path not included in file, adding default - " + log_path)
        loc_dic['log_path']=log_path

    try:
        my_client_id     = loc_dic['my_client_id']
        my_client_secret = loc_dic['my_client_secret']
        my_username      = loc_dic['my_username']
        my_password      = loc_dic['my_password']
    except:
        print(" Reddit Login details NOT SET set them if you want to use them...")
        my_client_id     = ' '
        my_client_secret = ' '
        my_username      = ' '
        my_password      = ' '
    try:
        subreddit        = loc_dic['subreddit']
        wiki_title       = loc_dic['wiki_title']
        live_wiki_title  = loc_dic['live_wiki_title']
    except:
        print("Subreddit details not set, leaving blank")
        subreddit        = ' '
        wiki_title       = ' '
        live_wiki_title  = ' '
    try:
        watcher_name     = loc_dic['watcher_name']
    except:
        print("No Reddit user set to recieve mail and issue commands")
        watcher_name     = ' '

    if not os.path.exists(loc_locs):
        print("Locations and passes file not found, creating default one...")
        write_loclocs()
        print(" - Settings saved to file - " + str(loc_locs))


def save_settings():
    print("Saving Settings...")
    try:
        with open(loc_settings, "w") as f:
            for a,b in pi_set.iteritems():
                s_line = str(a) +"="+ str(b) +"\n"
                f.write(s_line)
    except:
        print("Settings not saved!")
        raise

def show_settings():
    for a,b in pi_set.iteritems():
        print str(a) +"  = "+ str(b)

def make_dirs():
    if not os.path.exists(caps_path):
        os.makedirs(caps_path)
        print("Created; " + caps_path)
    if not os.path.exists(graph_path):
        os.makedirs(graph_path)
        print("Created; " + graph_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
        print("Created; " + log_path)

def guided_setup():
    print("\n\n Pigrow dependencies Install ")
    print("")
    print("checking directories")
    make_dirs()
    install.initial_setup()
    print("")
    sys.exit() #needs to be roloaded now the settings are in place
    raw_input("Press return to continue;")

def bind_realy(device):
    setting = raw_input("Select GPIO pin to use;")
    if setting in used_gpio_num:
        print("")
        print("That GPIO pin is already in use!")
    else:
        if int(setting) in valid_gpio:
            print("Setting " + device + " to use GPIO " + setting)
            print("")
            print(" Select Normal State;")
            print("    type on  --OR-- off")
            print(" This relates to if current can flow through the relay when it's powered down ")
            print("  -- It's perfectly safe to get this wrong as long as you're using he right GPIO number --")
            print("           --- if you've got it backwards turning on will instead turn it off..  ---")
            direction = raw_input("Input option;")
            if direction.lower() in ["0", "l", "low", "down", "off"]:
                print("Direction set to LOW")
                pi_set[device+"_on"] = "low"
                pi_set[device] = setting
                save_settings()
            elif direction.lower() in ["1", "h", "high", "up", "on" ]:
                print("Direction set to HIGH")
                pi_set[device+"_on"] = 'high'
                pi_set[device] = setting
                save_settings()
                print("Set " + device + " to " + setting + " with it's normal state as " + direction)
            else:
                print("All those options and you still messaed up...")


def refresh_gpio():
    used_gpio_num=[]
    for a,b in pi_set.iteritems():
        asplit = str(a).split("_")
        if asplit[0] == 'gpio':
            if len(asplit) == 2:
                #print("   ####   " + asplit[1])
                used_gpio.append([a,b])
                used_gpio_num.append(b)


def show_gpio():
    refresh_gpio()
    for x in range(0,len(used_gpio)):
        if not str(used_gpio[x][1]) == "":
            print("   #### Currently Used gpio pins; ")
            print("   ####    GPIO     DEVICE")
            print("   ####     " +str(used_gpio[x][1])+"        " + str(used_gpio[x][0].split("_")[1] + "  "))

def show_scripts(path):
    count = 0
    for x in os.listdir(path):
        if x.endswith("py"):
            print("   #### " + str(count) + " - " + x)
        count = count + 1
    print("   ####   ")

def show_gpio_menu():

    print("")
    print("   ##############################################")
    print("   ####          GPIO SETTINGS               ####")
    print("   ####                                      ####")
    show_gpio()
    print("   ####                                      ####")
    print("   ####   1  - Add new device                ####")
    print("   ####                                      ####")
    print("   ####   2  - Remove device                 ####")
    print("   ####                                      ####")
    print("   ####   3  - Test device                   ####")
    print("   ####                        m - main menu ####")
    print("   ####                        q - quit      ####")
    option = raw_input("Type the number and press return;")
    if option == "1":
        print("Select device to add;")
        print("   Sensors;")
        print("  1   - DHT22 Temp and Humidity")
        print("")
        print("   Relay Bindings;")
        print(" 2 - Custom")
        print("")
        option = raw_input("Type the number and press return; ")
        if option == "1":
            setting = raw_input("Select GPIO pin to use; ")
            try:
                setting = int(setting)
            except:
                print("Should use a number")

            print used_gpio_num
            if setting in used_gpio_num:
                print("")
                print("That GPIO pin is already in use!")
            else:
                if setting in valid_gpio:
                    print("")
                    print("Setting DHT22 Sensor on pin " + str(setting))
                    pi_set['gpio_dht22sensor'] = setting
                    save_settings()
                else:
                    print("Sorry that doesn't seem to be a valid pin... ")
        elif option == "2":
            print("select script to add")
            count = 0
            for x in os.listdir(path):
                count += 1
                if x.endswith(".py"):
                    print("   #### " + str(count) + " - " + x)

            option = raw_input("Select script to add")
            try:
                bind_realy("gpio_"os.listdir(path)[int(option)])
            except:
                print("Should use numbers for this,,,")
                show_gpio_menu()
                exit()
        show_gpio_menu()

    elif option == "2":
        print(" ")
        print(" Choose Device to remove;")
        show_gpio()
        option = raw_input("Type the number and press return;")
        try:
            option = int(option)
            setting = used_gpio[int(option)]
            print setting
            pi_set[setting[0]] = ''
            used_gpio = []
            used_gpio_num = []
            save_settings()
            show_gpio_menu()
            #show_gpio_menu()
        except:
            print("Should use numbers for this,,,")
            show_gpio_menu()
            exit()
    elif option == "3":
        print("Select device to test;")
            ##### newwww
        show_scripts(switch_path)
            #####
        choice = raw_input("Select device to test;")
        os.system(switch_path+os.listdir(switch_path)[int(choice)])
        show_gpio_menu()
        exit()
        #show_gpio_menu()
    elif option == "m":
        show_main_menu()
    elif option == "q":
        exit()
    else:
        show_gpio_menu()
        exit()

def show_start_script_menu():
    print("\n\nhahahahahahahahahaahaha NO.")
    print("             ok, coming soon....")


def show_cron(path):
    count = 0
    for x in os.listdir(path):
        print("   #### " + str(count) + " - " + x)
        count = count + 1


def show_active_cron():
    count = 0
    for job in cron:
        print("  "+str(count)+"  - " + str(job))
        count = count + 1




def show_cron_menu():
    print("   ##############################################")
    print("   ####  Cron Scripts                        ####")
    print("   ####     1  -  Add start up script        ####")
    print("   ####                                      ####")
    print("   ####     2  -  Add Timed Switch           ####")
    print("   ####                                      ####")
    print("   ####     3  -  Add Repeating script       ####")
    print("   ####                                      ####")
    print("   ####     4  -  Remove job from Cron       ####")
    print("   ####                        s = show cron ####")
    print("   ####                        m = main menu ####")
    option = raw_input("Select option and press return;")
    if option == "1":
        print("   #### Choose script to run on start up,")
        print("   ####    -NOTE: This should be considered an alternative way")
        print("   ####            it's not as robust as starting a service")
        print("   #### ")
        show_scripts(autorun_path)
        option = raw_input("Select script to add;")
        try:
            job = autorun_path + os.listdir(autorun_path)[int(option)]
        except:
            print("Sorry, that doesn't seem to have been a valid option")
            show_cron_menu()
            exit()
        job = cron.new(command=job, comment='Pigrow')
        job.every_reboot()
        cron.write()

    elif option == "2":
        print("   #### Choose script you want to trigger at a set time")
        show_scripts(switch_path)
        print("   ####   ")
        option = raw_input("Select script to add; ")
        hour = raw_input("Input hour to trigger (0-23); ")
        minpast = raw_input("How man min past the hour? (0-59); ")
        try:
            job = switch_path + os.listdir(switch_path)[int(option)]
            hour = int(hour)
            minpast = int(minpast)
        except:
            print("")
            print(" those needed to both be numbers...")
            show_cron_menu()
            exit()
        job = cron.new(command=job, comment='Pigrow')
        job.hour.on(hour)
        job.minute.on(minpast)
        cron.write()
        show_cron_menu()

    elif option == "3":
        print("")
        print("   #### Choose script you want to trigger periodically")
        show_scripts(cron_path)
        print("   ####   ")
        option = raw_input("Select script to add;")
        job = cron_path + os.listdir(cron_path)[int(option)]
        job = cron.new(command=job, comment='Pigrow')
        print ("")
        print(" Set frequency in,")
        print("  1 - minute")
        print("  2 - hour")
        print("  3 - day")
        print("  4 - week")
        print("  5 - month")
        freqin = raw_input(" ; ")
        freq = raw_input("How frequently do you want it to trigger")
        freq = int(freq)
        if freqin == "1":
            job.minute.every(freq)
        elif freqin == "2":
            job.hour.every(freq)
        elif freqin == "3":
            job.day.every(freq)
        elif freqin == "4":
            job.week.every(freq)
        elif freqin == "5":
            job.month.every(freq)
        cron.write()
        print("   -----------")
        print(" -- Job added --")
        show_cron_menu()

    elif option == "4":
        print(" Choose script to remove;")
        show_active_cron()
        torem = raw_input("Type number and press return;")

        try:
            torem = int(torem)
        except:
            print("\n\n THAT WAS NOT A NUMBER \n\n")
            show_cron_menu()
        print("Removing --" + str(cron[torem]))
        print("")
        cron.remove(cron[torem])
        cron.write()
        show_cron_menu()

    elif option == "s":
        print("   ###########")
        show_active_cron()
        raw_input("hit return to continue...")
        show_cron_menu()
    elif option == "m":
        print("   #################")
        show_main_menu()

def show_reddit_menu():
    global watcher_name, loc_settings, loc_switchlog, loc_dht_log, loc_dht_log, err_log, caps_path, graph_path, log_path, my_client_id, my_client_secret, my_username, my_password, subreddit, wiki_title, live_wiki_title

    print("\n\n")
    print("   ##############################################")
    print("   ####                                      ####")
    print("   ####    Reddit passwords and stuff        ####")
    print("   ####        bot: " + my_username)
    print("   ####        sub: " + subreddit)
    print("   ####       user: " + watcher_name)
    print("   ####  Settings;                           ####")
    print("   ####      1  -  Bot Login Info            ####")
    print("   ####      2  -  Wiki Details              ####")
    print("   ####      3  -  User to recieve messages  ####")
    print("   ####  Test;                               ####")
    print("   ####      4  -  Send test message         ####")
    print("   ####      5  -  Start Reddit settings ear ####")
    print("   ####                                      ####")
    print("   ####              s - Show Reddit Details ####")
    print("   ####                                      ####")

    option = raw_input("Selection option;")
    if option == "1":
        print(" These are the login details of your bot account, not your main reddit account...")
        print("                    -- best not to use the same for both, it'd mess up your messages")
        print("              ")
        print("leave blank to keep seetings or input a single space ' ' to blank them;")
        i_my_username       =raw_input("Input the reddit username of your bot; ")
        i_my_password       =raw_input("Input reddit password; ")
        i_my_client_id      =raw_input("Input Client Id (the Shorter gibberish); ")
        i_my_client_secret  =raw_input("Input Client secret code (the longer gibberish); ")

        if i_my_username == '':
            print("Leaving username set to; " + my_username)
        else:
            loc_dic['my_username']=i_my_username
            my_username = i_my_username

        if i_my_password == '':
            print("Leaving password set to; " + my_password)
        else:
            loc_dic['my_password']=i_my_password
            my_password = i_my_password

        if i_my_client_id == '':
            print("Leaving Client ID set to; " + my_client_id)
        else:
            loc_dic['my_client_id']=i_my_client_id
            my_client_id = i_my_client_id

        if i_my_client_secret == '':
            print("Leaving Client Secret set to; " + my_client_secret  + " yeah, means nothing to me either...")
        else:
            loc_dic['my_client_secret']=i_my_client_secret
            my_client_secret == i_my_client_secret

        write_loclocs()
        print("")
        print(" Login Details Saved;")
        show_reddit_menu()
    elif option == "2":
        print("")
        subreddit         =raw_input("Input name of subreddit; ")
        wiki_title        =raw_input("Input name of wiki page for settings; ")
        live_wiki_title   =raw_input("Input name wiki to use for live updates; ")
        loc_dic['subreddit']=subreddit
        loc_dic['wiki_title']=wiki_title
        loc_dic['live_wiki_title']=live_wiki_title
        write_loclocs()
        print("Subreddit Details Saved,")
        show_reddit_menu()
    elif option == "3":
        print(" Input the name of the account you want to be in control of your Pigrow")
        print("       - this user will be able to alter settings and recieve updates.")
        i_watcher_name  =raw_input("Input just he username, press return to leave it the same or add a space to blank it: ")
        print("")
        if i_watcher_name == '':
            print("No change made")
        else:
            loc_dic['watcher_name']=i_watcher_name
            watcher_name = i_watcher_name
            write_loclocs()
            print("Watcher Username set and saved.")
        show_reddit_menu()

    elif option == "4":
        import praw
        import socket
        print("Attempting to send a message to" + loc_dic['watcher_name'])
        try:
            my_client_id = loc_dic['my_client_id']
            my_client_secret = loc_dic['my_client_secret']
            my_username = loc_dic['my_username']
            my_password = loc_dic['my_password']
            watcher_name = loc_dic['watcher_name']
        except:
            print("You need to set reddit login details and a trusted user to receive mail first")
            exit()
        try:
            reddit = praw.Reddit(user_agent="pigrow config script test message",
                                 client_id=my_client_id,
                                 client_secret=my_client_secret,
                                 username=my_username,
                                 password=my_password)
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

    elif option == "5":
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
        show_reddit_menu()

    elif option == 's' or option == 'S':
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
        raw_input("Press return to continue...")
        show_reddit_menu()

def show_restore_default_menu():
    print("\n\nThis will errase all settings and reset to default values")
    print("                          .")
    if raw_input("Type yes to contnie") == "yes":
        set_loc_defaults()
        save_settings()
        print("Location settings and passes have been set to defaults")
    if raw_input("Do you want to empty [delete] the default directories? type yes") == "yes":
        os.system("sudo rm" + homedir +"/Pigrow/logs/*.*")
        os.system("sudo rm" + homedir +"/Pigrow/graphs/*.*")
        os.system("sudo rm" + homedir +"/Pigrow/caps/*.*")
    print("NOTE: I need to add default settings for other settings file..")

def show_main_menu():
    print("")
    print("   ##############################################")
    print("   ####                                      ####")
    print("   ####     Pigrow Setup                     ####")
    print("   ####                                      ####")
    print("   ####        1 - Install Dependencies      ####")
    print("   ####                                      ####")
    print("   ####        2 - GPIO set up               ####")
    #print("   ####                  -change to view settings                    ####")
    #print("   ####        3 - Start-up services         ####")
    print("   ####                                      ####")
    print("   ####        4 - Cron run scripts          ####")
    print("   ####                                      ####")
    print("   ####        5 - Reddit login              ####")
    print("   ####                                      ####")
    print("   ####        6 - Restore Default           ####")
    print("   ####                    s - show settings ####")
    print("   ####                    q - to quit       ####")
    print("   ##############################################")

    option = raw_input("Type the number and press return;")
    if option == "1":
        guided_setup()
        show_main_menu()
    elif option == "2":
        show_gpio_menu()
        #show_main_menu()
    elif option == "3":
        show_start_script_menu()
        show_main_menu()
    elif option == "4":
        show_cron_menu()
        show_main_menu()
    elif option == "5":
        show_reddit_menu()
        show_main_menu()
    elif option == "6":
        show_restore_default_menu()
        show_main_menu()
    elif option == "q":
        exit()
    elif option == "s":
        show_settings()
        option = raw_input("return to continue;")
        show_main_menu()

if __name__ == '__main__':
    for argu in sys.argv:
        thearg = str(argu).split('=')[0]
        if  thearg == 'locs':
            loc_locs = str(argu).split('=')[1]
        elif  thearg == '-pragmo':
            loc_locs = "/home/pragmo/pigitgrow/Pigrow/config/dirlocs.txt"
    set_loc_defaults()
    set_locs_and_passes()
    load_locs()


    print("##################################")
    print("##   Pigrow Setup Utility       ##")
    print("")
    show_main_menu()
