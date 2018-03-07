#!/usr/bin/python
import os, sys
from subprocess import check_output
try:
    from crontab import CronTab   #  pip install python-crontab
    cron = CronTab(user=True)  #can be user+True, 'yourusername' or 'root' all work.
except:
    print(" crontab not installed, run guided set up")

## Main Program if called from console
if __name__ == '__main__':
    for argu in sys.argv:
        thearg = str(argu).split('=')[0]
        if  thearg == 'locs':
            loc_locs = str(argu).split('=')[1]
        elif  thearg == '-pragmo':
            loc_locs = "/home/pragmo/pigitgrow/Pigrow/config/dirlocs.txt"




class Pigrow:

    global homedir
    valid_gpio=[]
    used_gpio_num=[]
    used_gpio=[]

    # Locations
    global config_path, loc_locs, autorun_path, cron_path, switch_path, loc_settings, loc_switchlog, loc_dht_log
    global err_log, caps_path, graph_path, log_path
    global my_client_id, my_client_secret, my_username, my_password, subreddit, wiki_title, live_wiki_title, watcher_name

    #used in set_locs_and_passes():
    global watcher_name, loc_settings, loc_switchlog, loc_dht_log, loc_dht_log, err_log, caps_path, graph_path
    global log_path, my_client_id, my_client_secret, my_username, my_password, subreddit, wiki_title, live_wiki_title

    # used in write_loclocs
    loc_dic = {}

    # used in open, save_setiings, show settings
    pi_set = {}

    def __init__(self):
        self.set_loc_defaults()




    ################ init functions
    def set_loc_defaults(self):

        self.homedir = os.getenv("HOME")
        self.valid_gpio = [2,3,4,17,27,22,10,9,11,0,5,6,13,19,26,14,15,18,23,24,25,8,7,1,12,16,20,21]
        self.used_gpio_num = []

        self.config_path = self.homedir + "/Pigrow/config/"
        self.loc_locs    = self.homedir + "/Pigrow/config/dirlocs.txt"

        #folders that get looked in for the scripts to add to cron  - will deduce thes from main path to take usernames into account when i get round to it
        self.autorun_path = self.homedir + "/Pigrow/scripts/autorun/"    #reboot scripts'
        self.cron_path    = self.homedir + "/Pigrow/scripts/cron/"       #repeting scripts
        self.switch_path  = self.homedir + "/Pigrow/scripts/switches/"   #timed scripts

        # log defaults
        self.loc_settings    = self.homedir + "/Pigrow/config/pigrow_config.txt"
        self.loc_switchlog   = self.homedir + "/Pigrow/logs/switch_log.txt"
        self.loc_dht_log     = self.homedir + "/Pigrow/logs/dht22_log.txt"
        self.err_log         = self.homedir + "/Pigrow/logs/err_log.txt"
        self.caps_path    = self.homedir + "/Pigrow/caps/"
        self.graph_path   = self.homedir + "/Pigrow/graphs/"
        self.log_path     = self.homedir + "/Pigrow/logs/"

        # reddit defaults
        self.my_client_id      = " "
        self.my_client_secret  = " "
        self.my_username       = " "
        self.my_password       = " "
        self.subreddit       = "Pigrow"
        self.wiki_title      = "livegrow_test_settings"
        self.live_wiki_title = "livegrow_test"
        self.watcher_name    = ' '

    def load_locs(self):
        print("Loading location details")
        with open(self.loc_locs, "r") as f:
            for line in f:
                s_item = line.split("=")
                self.loc_dic[s_item[0]]=s_item[1].rstrip('\n')

    def write_loclocs(self):
        with open(self.loc_locs, "w") as f:
            for a,b in self.loc_dic.iteritems():
                try:
                    s_line = str(a) +"="+ str(b) +"\n"
                    f.write(s_line)
                    #print s_line
                except:
                    print("ERROR SETTINGS FILE ERROR SETTING NOT SAVED _ SERIOUS FAULT!")

    def set_locs_and_passes(self):

        try:
            self.load_locs()
        except:
            print(" Couldn't Load the logs")
        try:
            #print loc_settings
            self.loc_settings    = self.loc_dic['loc_settings']
            #print loc_settings
        except:
            print("IMPORTANT - Location of Settings File not included in file, adding default - " + self.loc_settings)
            self.loc_dic['loc_settings']=self.loc_settings
        try:
            self.loc_switchlog    = self.loc_dic['loc_switchlog']
        except:
            print("IMPORTANT - Location of switch log not included in file, adding default - " + self.loc_switchlog)
            self.loc_dic['loc_switchlog']=self.loc_switchlog
        try:
            self.loc_dht_log    = self.loc_dic['loc_dht_log']
        except:
            print("IMPORTANT - Location of DHT log not included in file, adding default - " + self.loc_dht_log)
            self.loc_dic['loc_dht_log']=self.loc_dht_log
        try:
            self.err_log    = self.loc_dic['err_log']
        except:
            print("IMPORTANT - Location of Error log not included in file, adding default - " + self.err_log)
            self.loc_dic['err_log']=self.err_log
        try:
            self.caps_path    = self.loc_dic['caps_path']
        except:
            print("IMPORTANT - Location of caps path not included in file, adding default - " + self.caps_path)
            self.loc_dic['caps_path']=self.caps_path
        try:
            self.graph_path    = self.loc_dic['graph_path']
        except:
            print("IMPORTANT - Location of Graph path not included in file, adding default - " + self.graph_path)
            self.loc_dic['graph_path']=self.graph_path
        try:
            self.log_path    = self.loc_dic['log_path']
        except:
            print("IMPORTANT - Location of log path not included in file, adding default - " + self.log_path)
            self.loc_dic['log_path']=self.log_path

        try:
            self.my_client_id     = self.loc_dic['my_client_id']
            self.my_client_secret = self.loc_dic['my_client_secret']
            self.my_username      = self.loc_dic['my_username']
            self.my_password      = self.loc_dic['my_password']
        except:
            print(" Reddit Login details NOT SET set them if you want to use them...")
            self.my_client_id     = ' '
            self.my_client_secret = ' '
            self.my_username      = ' '
            self.my_password      = ' '
        try:
            self.subreddit        = self.loc_dic['subreddit']
            self.wiki_title       = self.loc_dic['wiki_title']
            self.live_wiki_title  = self.loc_dic['live_wiki_title']
        except:
            print("Subreddit details not set, leaving blank")
            self.subreddit        = ' '
            self.wiki_title       = ' '
            self.live_wiki_title  = ' '
        try:
            self.watcher_name     = self.loc_dic['watcher_name']
        except:
            print("No Reddit user set to recieve mail and issue commands")
            self.watcher_name     = ' '

        if not os.path.exists(self.loc_locs):
            print("Locations and passes file not found, creating default one...")
            self.write_loclocs()
            print(" - Settings saved to file - " + str(self.loc_locs))


    def save_settings(self):
        print("Saving Settings...")
        try:
            with open(self.loc_settings, "w") as f:
                for a,b in self.pi_set.iteritems():
                    s_line = str(a) +"="+ str(b) +"\n"
                    f.write(s_line)
        except:
            print("Settings not saved!")
            raise

    def show_settings(self):
        for a,b in self.pi_set.iteritems():
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

    def guided_setup(self):
        print("\n\n Pigrow dependencies Install ")
        print("")
        print("checking directories")
        make_dirs()
        os.system(homedir + "/Pigrow/scripts/config/install.py")
        print("")
        sys.exit() #needs to be roloaded now the settings are in place
        raw_input("Press return to continue;")

############## GPIO Functions

    def bind_realy(self, device, option):
        if option == 0:
            self.pi_set[device+"_on"] = "low"
            self.pi_set[device] = option
        else:
            self.pi_set[device+"_on"] = 'high'
            self.pi_set[device] = option
        save_setiings()


    def print_used_GPIO(self):
        for a,b in self.pi_set.iteritems():
            asplit = str(a).split("_")
            if asplit[0] == 'gpio':
                if len(asplit) == 2:
                    print("   ####   " + asplit[1])
                    self.used_gpio.append([a,b])
                    self.used_gpio_num.append(b)

    def print_GPIO(self):
        for x in range(0,len(self.used_gpio)):
            if not str(self.used_gpio[x][1]) == "":
                print("   ####     " +str(self.used_gpio[x][1])+"        " + str(self.used_gpio[x][0].split("_")[1] + "  "))

    def add_new_device(self, device_type, pin_num):
        #try:
            #check_gpio_valid_add(pin_num)
        #except:
            #pass
        self.pi_set['gpio_dht22sensor'] = pin_num
        save_settings()

    def print_used_GPIO_all(self):
        for x in range(0,len(self.used_gpio)):
            if not str(self.used_gpio[x][1]) == "":
                print("   ####     " + str(x) + "        " + str(self.used_gpio[x][0].split("_")[1] + "  "))

    def remove_device(self, pin_num):
        check_gpio_valid_remove(pin_num)
        return 0

    def add_startup_cron(self, device, cronscript):
        job = cron_path + os.listdir(cron_path)[int(device)]
        job = cron.new(command=job, comment='Pigrow')
        job.every_reboot()
        cron.write()

    def add_timed_cron(self, device, cronscript, hour, minpast):
        job = cron_path + os.listdir(cron_path)[int(device)]
        job = cron.new(command=job, comment='Pigrow')
        job.hour.on(hour)
        job.minute.on(minpast)
        cron.write()

    def add_triggered_cron(self, device, frequency, frequencyset):
        job = cron_path + os.listdir(cron_path)[int(device)]
        job = cron.new(command=job, comment='Pigrow')
        if frequencyset == "1":
            job.minute.every(freq)
        elif frequencyset == "2":
            job.hour.every(freq)
        elif frequencyset == "3":
            job.day.every(freq)
        elif frequencyset == "4":
            job.week.every(freq)
        elif frequencyset == "5":
            job.month.every(freq)
        cron.write()

    def remove_script_cron(self, device):
        cron.remove(cron[device])
        cron.write()

    def show_cron_config(self):
        for line in cron:
            #if job.command=="Pigrow":
            print("   #### " + str(line)) #s.command)


################ Aditional functions


    def show_active_cron(self):
        count = 0
        for job in cron:
            print("  "+str(count)+"  - " + str(job))
            count = count + 1

    #just trash - does nothing well
    def show_cron_scripts(self):
        count = 0
        for x in os.listdir(switch_path):
            count = count + 1
            print("   #### " + str(count) + " - " + x)
        print("   ####   ")

    def check_gpio_valid_add(gpiopin):
        try:
            gpiopin = int(gpiopin)
        except:
            print("Should use a number")
            return False


        if gpiopin in self.valid_gpio:

            if gpiopin in self.used_gpio:
                print("Already in use")
                return False
            else:
                print("Valid pin")
                return True
        else:
            print("Not a valid GPIO PIN Number")
            return False

    def check_gpio_valid_remove(gpiopin):

        try:
            gpiopin = int(gpiopin)
        except:
            print("Should use a number")
            return False

        if gpiopin in self.used_gpio_num:
            return True
        else:
                return False
                print("Pin not in use")
