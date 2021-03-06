#!/usr/bin/python

#
#   WORK IN PROGRESS
#
# Classes already created;
# -app pannels
#    pi_link_pnl        - top-left connection box with ip, username, pass
#    view_pnl           - allows you to select which options to view
#
# -main pannels
#    system_info_pnl    - for setting up the raspberry pi system and pigrow install
#    system_ctrl_pnl        - buttons for system_info_pnl
#
#    config_info_pnl    -shows info on current pigorow config
#    config_ctrl_pnl    -  buttons for above
#
#    cron_list_pnl      - shows the 3 cron type lists on the right of the window
#    cron_info_pnl          - buttons for cron_list_pnl
#    cron_job_dialog        - dialogue box for edit cron job
#
#    localfiles_info_pnl  - shows local files for spesific pigrow
#    localfiles_ctrl_pnl  - buttons for above
#       + uoload & download dialog box
#
#
# - useful functions
# run_on_pi(self, command)    -   Runs a command on the pigrow and returns output and error
####    out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/")
#
#
#

print("")
print(" Pigrow Remote Control Utility")
print("     Set-up and manage your Pigrow remotely ")
print("             --work in progress--  ")
print("     Works best on Linux, especially Ubuntu")
print("     ")
print("  More information at www.reddit.com/r/Pigrow")
print("")
print("  Work in progress, please report any errors or problems ")
print("  Code shared under a GNU General Public License v3.0")
print("")

import os
import sys
import platform
import time
import datetime
from stat import S_ISDIR
try:
    import wx
    import wx.lib.scrolledpanel
except:
    print(" You don't have WX Python installed, this makes the gui")
    print(" google 'installing wx python' for your operating system")
    print("on ubuntu try the command;")
    print("   sudo apt install python-wxgtk3.0 ")
    sys.exit(1)
try:
    import paramiko
except:
    print("  You don't have paramiko installed, this is what connects to the pi")
    print(" google 'installing paramiko python' for your operating system")
    print(" on ubuntu;")
    print(" use the command ' pip install paramiko ' to install.")
    sys.exit(1)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#
#
## System Pannel
#
#
class system_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        height_of_pannels_above = 230
        space_left = win_height - height_of_pannels_above
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, height_of_pannels_above), size = wx.Size(285, space_left), style = wx.TAB_TRAVERSAL )
        # Start drawing the UI elements
        wx.StaticText(self,  label='System Config Menu', pos=(25, 10))
        self.read_system_btn = wx.Button(self, label='Read System Info', pos=(10, 70), size=(175, 30))
        self.read_system_btn.Bind(wx.EVT_BUTTON, self.read_system_click)
        self.install_pigrow_btn = wx.Button(self, label='pigrow install', pos=(10, 100), size=(175, 30))
        self.install_pigrow_btn.Bind(wx.EVT_BUTTON, self.install_click)
        self.update_pigrow_btn = wx.Button(self, label='update pigrow', pos=(10, 130), size=(175, 30))
        self.update_pigrow_btn.Bind(wx.EVT_BUTTON, self.update_pigrow_click)
        self.reboot_pigrow_btn = wx.Button(self, label='reboot pigrow', pos=(10, 160), size=(175, 30))
        self.reboot_pigrow_btn.Bind(wx.EVT_BUTTON, self.reboot_pigrow_click)

    def reboot_pigrow_click(self, e):
        dbox = wx.MessageDialog(self, "Are you sure you want to reboot the pigrow?", "reboot pigrow?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo reboot now")
            MainApp.pi_link_pnl.link_with_pi_btn_click("e")
            print out, error

    def read_system_click(self, e):
        #check for hdd space
        try:
            stdin, stdout, stderr = ssh.exec_command("df -l /")
            responce = stdout.read().strip()
            error = stderr.read()
            #print responce, error
        except Exception as e:
            print("oh! " + str(e))
        if len(responce) > 1:
            responce_list = []
            for item in responce.split(" "):
                if len(item) > 0:
                    responce_list.append(item)
            hdd_total = responce_list[-5]
            hdd_percent = responce_list[-2]
            hdd_available = responce_list[-3]
            hdd_used = responce_list[-4]
        system_info_pnl.sys_hdd_total.SetLabel(str(hdd_total) + " KB")
        system_info_pnl.sys_hdd_remain.SetLabel(str(hdd_available) + " KB")
        system_info_pnl.sys_hdd_used.SetLabel(str(hdd_used) + " KB (" + str(hdd_percent) + ")")
        #check installed OS
        try:
            stdin, stdout, stderr = ssh.exec_command("cat /etc/os-release")
            responce = stdout.read().strip()
            error = stderr.read()
            #print responce, error
        except Exception as e:
            print("ahhh! " + str(e))
        for line in responce.split("\n"):
            if "PRETTY_NAME=" in line:
                os_name = line.split('"')[1]
        system_info_pnl.sys_os_name.SetLabel(os_name)
        #check if pigrow folder exits and read size
        try:
            stdin, stdout, stderr = ssh.exec_command("du -s ~/Pigrow/")
            responce = stdout.read().strip()
            error = stderr.read()
            #print responce, error
        except Exception as e:
            print("ahhh! " + str(e))
        if not "No such file or directory" in error:
            self.update_pigrow_btn.SetLabel("update pigrow")
            pigrow_size = responce.split("\t")[0]
            self.pigrow_folder_size = pigrow_size
            #print pigrow_size
            not_pigrow = (int(hdd_used) - int(pigrow_size))
            #print not_pigrow
            folder_pcent = float(pigrow_size) / float(hdd_used) * 100
            folder_pcent = format(folder_pcent, '.2f')
            system_info_pnl.sys_pigrow_folder.SetLabel(str(pigrow_size) + " KB (" +str(folder_pcent) + "% of used)")
        else:
            system_info_pnl.sys_pigrow_folder.SetLabel("No Pigrow folder detected")
            self.update_pigrow_btn.SetLabel("install pigrow")

        #check if git upate needed
        update_needed = False
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git -C ~/Pigrow/ remote -v update")
        if len(error) > 1:
            git_text = error.split("\n")
            count = 0
            for line in git_text:
                if "origin/master" in line:
                    master_branch = line
                    count = count + 1
            if count > 1:
                print("ERROR ERROR TWO MASTER BRANCHES WTF?")
            elif count == 0:
                #print("No Pigrow install detected")
                install_needed = True
            elif count == 1:
                if "[up to date]" in master_branch:
                    #print("master branch is upto date")
                    update_needed = False
                else:
                    #print("Master branch requires updating")
                    update_needed = True
        #print master_branch
        #Read git status
        try:
            stdin, stdout, stderr = ssh.exec_command("git -C ~/Pigrow/ status --untracked-files no")
            responce = stdout.read().strip()
            error = stderr.read()
            #print responce
            #print 'error:' + str(error)
        except Exception as e:
            print("ooops! " + str(e))
        if "Your branch and 'origin/master' have diverged" in responce:
            update_needed = 'diverged'
        elif "Your branch is" in responce:
            git_line = responce.split("\n")[1]
            git_update = git_line.split(" ")[3]
            if git_update == 'behind':
                update_needed = True
                git_num = git_line.split(" ")[6]
            elif git_update == 'ahead':
                update_needed = 'ahead'
            #elif git_update == 'up-to-date':
            #    print("says its up to date")
        else:
            update_needed = 'error'

        if update_needed == True:
            system_info_pnl.sys_pigrow_update.SetLabel("update required, " + str(git_num) + " updates behind")
            self.update_type = "clean"
        elif update_needed == False:
            system_info_pnl.sys_pigrow_update.SetLabel("master branch is upto date")
        elif update_needed == 'ahead':
            system_info_pnl.sys_pigrow_update.SetLabel("you've modified the core pigrow code, caution required!")
            self.update_type = "merge"
        elif update_needed == 'diverged':
            system_info_pnl.sys_pigrow_update.SetLabel("you've modified the core pigrow code, caution required!")
            self.update_type = "merge"
        elif update_needed == 'error':
            if install_needed == True:
                system_info_pnl.sys_pigrow_update.SetLabel("Pigrow folder not found.")
            else:
                system_info_pnl.sys_pigrow_update.SetLabel("some confusion with git, sorry.")
        #
        # pi board revision
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /proc/device-tree/model")
        out = out.strip()
        system_info_pnl.sys_pi_revision.SetLabel(out)
        #check for low power WARNING
        # not entirely sure if this works on all version of the pi, it looks to see if the power light is on
        # it's normally turned off as a LOW POWER warning
        if not "pi 3" in system_info_pnl.sys_pi_revision.GetLabel().lower():
            print system_info_pnl.sys_pi_revision.GetLabel().lower()
            try:
                stdin, stdout, stderr = ssh.exec_command("cat /sys/class/leds/led1/brightness")
                responce = stdout.read().strip()
                error = stderr.read()
                if responce == "255":
                    system_info_pnl.sys_power_status.SetLabel("no warning")
                else:
                    system_info_pnl.sys_power_status.SetLabel("reads " + str(responce) + " low power warning!")
            except Exception as e:
                print("lookit! a problem - " + str(e))
                system_info_pnl.sys_power_status.SetLabel("unable to read")
        else:
            system_info_pnl.sys_power_status.SetLabel("feature disabled on pi 3")
        # WIFI
        # Read the currently connected network name
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("/sbin/iwgetid")
        try:
            network_name = out.split('"')[1]
            system_info_pnl.sys_network_name.SetLabel(network_name)
        except Exception as e:
            print("fiddle and fidgets! - " + str(e))
            system_info_pnl.sys_network_name.SetLabel("unable to read")
        # read /etc/wpa_supplicant/wpa_supplicant.conf for listed wifi networks
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo cat /etc/wpa_supplicant/wpa_supplicant.conf")
        out = out.splitlines()
        in_a_list = False
        network_items = []
        network_list = []
        for line in out:
            if "}" in line:
                in_a_list = False
                # list finished sort into fields
                ssid = ""
                psk = ""
                key_mgmt = ""
                other = ""
                for x in network_items:
                    if "ssid=" in x:
                        ssid = x[5:]
                    elif "psk=" in x:
                        psk = x[4:]
                        psk = "(password hidden)"
                    elif "key_mgmt=" in x:
                        key_mgmt = x[9:]
                    else:
                        other = other + ", "
                network_list.append([ssid, key_mgmt, psk, other])
                network_items = []
            if in_a_list == True:
                network_items.append(line.strip())
            if "network" in line:
                in_a_list = True
        network_text = ""
        for item in network_list:
            for thing in item:
                network_text += thing + " "
            network_text += "\n"
        system_info_pnl.wifi_list.SetLabel(network_text)
        # camera info
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /dev/video*")
        if "No such file or directory" in error:
            cam_text = "No camera detected"
        else:
            camera_list = out.strip().split(" ")
            if len(camera_list) == 1:
                out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("udevadm info --query=all /dev/video0 |grep ID_MODEL=")
                cam_name = out.split("=")[1].strip()
                cam_text = cam_name
            elif len(camera_list) > 1:
                for cam in camera_list:
                    out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("udevadm info --query=all " + cam + " |grep ID_MODEL=")
                    cam_name = out.split("=")[1].strip()
                    cam_text = cam_name + "\n       on " + cam + "\n"
        system_info_pnl.sys_camera_info.SetLabel(cam_text)
        # datetimes and difference
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("date")
        local_time = datetime.datetime.now()
        local_time_text = local_time.strftime("%a %d %b %X") + " " + str(time.tzname[0]) + " " + local_time.strftime("%Y")


        out = out.strip()
        system_info_pnl.sys_pi_date.SetLabel(out)
        system_info_pnl.sys_pc_date.SetLabel(str(local_time_text))

    def install_click(self, e):
        install_dbox = install_dialog(None, title='Install Pigrow to Raspberry Pi')
        install_dbox.ShowModal()

    def update_pigrow_click(self, e):
        #reads button lable for check if update or install is required
        if self.update_pigrow_btn.GetLabel() == "update pigrow":
            do_upgrade = True
        #checks to determine best git merge stratergy
            if self.update_type == "clean":
                git_command = "git -C ~/Pigrow/ pull"
            elif self.update_type == "merge":
                print("WARNING WARNING _ THIS CODE IS VERY MUCH IN THE TESTING PHASE")
                print("if you're doing odd things it's very likely to mess up!")
                #this can cause odd confusions which requires use of 'git rebase'
                #reokace command line question with dialog box
                question = raw_input("merge using default, ours or theirs?")
                if question == "ours":
                    git_command = "git -C ~/Pigrow/ pull --strategy=ours" #if we've changed a file it ignores the remote updated one
                elif question == "theirs":
                    #often needs to commit or stash changes before working
                    git_command = "git -C ~/Pigrow/ pull -s recursive -X theirs" #removes any changes made locally and replaces file with remote updated one
                elif question == "default":
                    git_command = "git -C ~/Pigrow/ pull"
                else:
                    print("not an option, calling the whole thing off...")
                    do_upgrade = False
            #runs the git pull command using the selected stratergy
            if do_upgrade == True:
                dbox = wx.MessageDialog(self, "Are you sure you want to upgrade this pigrow?", "update pigrow?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                answer = dbox.ShowModal()
                dbox.Destroy()
                #if user said ok then upload file to pi
                if (answer == wx.ID_OK):
                    try:
                        stdin, stdout, stderr = ssh.exec_command(git_command)
                        responce = stdout.read().strip()
                        error = stderr.read()
                        print responce
                        if len(error) > 0:
                            print 'error:' + str(error)
                        system_info_pnl.sys_pigrow_update.SetLabel("--UPDATED--")
                    except Exception as e:
                        print("ooops! " + str(e))
                        system_info_pnl.sys_pigrow_update.SetLabel("--UPDATE ERROR--")
        elif self.update_pigrow_btn.GetLabel() == "old install pigrow":
            print("Downloading Pigrow code onto Pi")
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git clone https://github.com/Pragmatismo/Pigrow ~/Pigrow/")
            print out, error
            system_info_pnl.sys_pigrow_update.SetLabel("--NEW INSTALL--")
            print(" -- Installing software on pigrow ")
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("~/Pigrow/scripts/config/install.py")
            print out, error

class system_info_pnl(wx.Panel):
    #
    #  This displays the system info
    # controlled by the system_ctrl_pnl
    #
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        win_width = parent.GetSize()[0]
        w_space_left = win_width - 285
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size(w_space_left , 800), style = wx.TAB_TRAVERSAL )
        ## Draw UI elements
        png = wx.Image('./sysconf.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, png, (0, 0), (png.GetWidth(), png.GetHeight()))
        #SDcard details
        system_info_pnl.sys_hdd_total = wx.StaticText(self,  label='total;', pos=(250, 180), size=(200,30))
        system_info_pnl.sys_hdd_remain = wx.StaticText(self,  label='free;', pos=(250, 250), size=(200,30))
        system_info_pnl.sys_hdd_used = wx.StaticText(self,  label='Used;', pos=(250, 215), size=(200,30))
        system_info_pnl.sys_pigrow_folder = wx.StaticText(self,  label='Pigrow folder;', pos=(250, 285), size=(200,30))
        #Software details
        system_info_pnl.sys_os_name = wx.StaticText(self,  label='os installed;', pos=(250, 365), size=(200,30))
        #system_info_pnl.sys_pigrow_version = wx.StaticText(self,  label='pigrow version;', pos=(250, 405), size=(200,30))
        system_info_pnl.sys_pigrow_update = wx.StaticText(self,  label='Pigrow update status', pos=(250, 450), size=(200,30))
        #wifi deatils
        system_info_pnl.sys_network_name = wx.StaticText(self,  label='network name', pos=(250, 535), size=(200,30))
        system_info_pnl.wifi_list = wx.StaticText(self,  label='wifi list', pos=(140, 620), size=(200,30))

        #camera details
        system_info_pnl.sys_camera_info = wx.StaticText(self,  label='camera info', pos=(585, 170), size=(200,30))
        #power level warning details
        system_info_pnl.sys_power_status = wx.StaticText(self,  label='power status', pos=(625, 390), size=(200,30))
        # Raspberry Pi revision
        system_info_pnl.sys_pi_revision = wx.StaticText(self,  label='raspberry pi version', pos=(625, 450), size=(200,30))
        # Pi datetime vs local pc datetime
        system_info_pnl.sys_pi_date = wx.StaticText(self,  label='datetime on pi', pos=(625, 495), size=(500,30))
        system_info_pnl.sys_pc_date = wx.StaticText(self,  label='datetime on local pc', pos=(625, 525), size=(200,30))
        #system_info_pnl.sys_time_diff = wx.StaticText(self,  label='difference', pos=(700, 555), size=(200,30))

class install_dialog(wx.Dialog):
    #Dialog box for installing pigrow software on a raspberry pi remotely
    def __init__(self, *args, **kw):
        super(install_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 500))
        self.SetTitle("Install Pigrow")
    def InitUI(self):
        # draw the pannel and text
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Install Pigrow', pos=(20, 10))
        wx.StaticText(self,  label='Tool for installing pigrow code and dependencies', pos=(10, 40))
        # Installed components
        pigrow_base_check = wx.StaticText(self,  label='Pigrow base', pos=(25, 90))
        #python modules
        wx.StaticText(self,  label='Python modules;', pos=(10, 120))
        self.matplotlib_check = wx.StaticText(self,  label='Matplotlib', pos=(25, 150))
        self.adaDHT_check = wx.StaticText(self,  label='Adafruit_DHT', pos=(25, 180))
        self.cron_check = wx.StaticText(self,  label='crontab', pos=(25, 210))
        self.praw_check = wx.StaticText(self,  label='praw', pos=(300, 150))
        self.pexpect_check = wx.StaticText(self,  label='pexpect', pos=(300, 180))
        #programs
        wx.StaticText(self,  label='Programs;', pos=(10, 240))
        self.uvccapture_check = wx.StaticText(self,  label='uvccapture', pos=(25, 270))
        self.mpv_check = wx.StaticText(self,  label='mpv', pos=(25, 300))
        self.sshpass_check = wx.StaticText(self,  label='sshpass', pos=(300, 270))
        #status text
        self.currently_doing = wx.StaticText(self,  label="Currently:", pos=(15, 340))
        self.currently_doing = wx.StaticText(self,  label='...', pos=(100, 340))
        self.progress = wx.StaticText(self,  label='...', pos=(15, 370))

        #ok and cancel buttons
        self.start_btn = wx.Button(self, label='Start', pos=(15, 400), size=(175, 30))
        self.start_btn.Bind(wx.EVT_BUTTON, self.start_click)
        self.cancel_btn = wx.Button(self, label='Cancel', pos=(315, 400), size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)
        #run initial checks
        wx.Yield() #update screen to show changes
        self.check_python_dependencies()
        wx.Yield() #update screen to show changes
        self.check_program_dependencies()

    def install_pigrow(self):
        self.currently_doing.SetLabel("using git to clone (download) pigrow code")
        self.progress.SetLabel("####~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git clone https://github.com/Pragmatismo/Pigrow ~/Pigrow/")
        self.currently_doing.SetLabel("creating folders")
        self.progress.SetLabel("#####~~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir ~/Pigrow/caps/")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir ~/Pigrow/graphs/")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir ~/Pigrow/logs/")
        self.currently_doing.SetLabel("-")
        self.progress.SetLabel("######~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()

    def install_all_pip(self):
        #updating pip
        self.currently_doing.SetLabel("Updating PIP the python install manager")
        self.progress.SetLabel("#########~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip install -U pip")
        print out
        #installing dependencies with pip
        self.currently_doing.SetLabel("Using pip to install praw and pexpect")
        self.progress.SetLabel("###########~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip install praw pexpect")
        print out
        self.currently_doing.SetLabel(".")
        self.progress.SetLabel("#############~~~~~~~~~~~~~~~~")
        wx.Yield()
        return out

    def install_all_apt(self):
        #updating apt package list
        self.currently_doing.SetLabel("updating apt the system package manager on the raspberry pi")
        self.progress.SetLabel("################~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt update --yes")
        print out
        #installing dependencies with apt
        self.currently_doing.SetLabel("using apt to install matplot lib, sshpass, python-crontab")
        self.progress.SetLabel("##################~~~~~~~~~~~~~")
        wx.Yield()
        python_dep, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt --yes install python-matplotlib sshpass python-crontab")
        print python_dep
        self.currently_doing.SetLabel("Using apt to install uvccaptre and mpv")
        self.progress.SetLabel("####################~~~~~~~~~~~")
        wx.Yield()
        image_dep, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt --yes install uvccapture mpv")
        print image_dep
        self.currently_doing.SetLabel("..")
        self.progress.SetLabel("######################~~~~~~~~~")
        wx.Yield()

    def install_adafruit_DHT(self):
        print("starting adafruit install")
        print("installing dependencies using apt")
        self.currently_doing.SetLabel("Using apt to install adafruit_dht dependencies")
        self.progress.SetLabel("##########################~~~~~~")
        wx.Yield()
        adafruit_dep, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt --yes install build-essential python-dev python-openssl")
        print adafruit_dep
        print("- Downloading Adafruit_Python_DHT from Github")
        ada_dir = "/home/" + pi_link_pnl.target_user + "/Pigrow/resources/Adafruit_Python_DHT/"
        self.currently_doing.SetLabel("Using git to clone (download) the adafruit code")
        self.progress.SetLabel("###########################~~~~")
        wx.Yield()
        adafruit_clone, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git clone https://github.com/adafruit/Adafruit_Python_DHT.git " + ada_dir)
        print adafruit_clone, error
        print("- Dependencies installed, running adafruit_dht : sudo python setup.py install")
        self.currently_doing.SetLabel("Using the adafruit_DHT setup.py to install the module")
        self.progress.SetLabel("#############################~~")
        wx.Yield()
        adafruit_install, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo python "+ ada_dir +"setup.py install")
        self.currently_doing.SetLabel("...")
        self.progress.SetLabel("##############################~")
        wx.Yield()
        print adafruit_install

    def check_program_dependencies(self):
        program_dependencies = ["sshpass", "uvccapture", "mpv"]
        working_programs = []
        nonworking_programs = []
        for program in program_dependencies:
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("apt-cache policy "+program+" |grep Installed")
            if "Installed" in out:
                if not "(none)" in out:
                    working_programs.append(program)
                else:
                    nonworking_programs.append(program)
            else:
                nonworking_programs.append(program)
        #colour ui
        if "uvccapture" in working_programs:
            self.uvccapture_check.SetForegroundColour((75,200,75))
        else:
            self.uvccapture_check.SetForegroundColour((255,75,75))
        if "mpv" in working_programs:
            self.mpv_check.SetForegroundColour((75,200,75))
        else:
            self.mpv_check.SetForegroundColour((255,75,75))
        if "sshpass" in working_programs:
            self.sshpass_check.SetForegroundColour((75,200,75))
        else:
            self.sshpass_check.SetForegroundColour((255,75,75))


    def check_python_dependencies(self):
        python_dependencies = ["matplotlib", "Adafruit_DHT", "praw", "pexpect", "crontab"]
        working_modules = []
        nonworking_modules = []
        for module in python_dependencies:
            #print module
#this mess is the code that gets run on the pi
            module_question = """\
"try:
    import """ + module + """
    print('True')
except:
    print('False')" """
#that gets run with bash on the pi in this next line
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("python -c " + module_question)
        # this is the old way that doesn't always work
            #out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("python -m " + str(module))
            #if len(out) > 0:
            #    working_modules.append(module)
            #    print("WARNING I THINK THAT MODULE " + module + " may have just run... it's probably fine though." )
            #elif len(error) > 0:
            #    if not "is a package and cannot be directly executed" in error and not "No code object available for" in error:
            #        nonworking_modules.append(module)
            #    else:
            #        working_modules.append(module)
        # that was the old way
            if "True" in out:
                working_modules.append(module)
            else:
                nonworking_modules.append(module)
        # colour UI
        if "matplotlib" in working_modules:
            self.matplotlib_check.SetForegroundColour((75,200,75))
        else:
            self.matplotlib_check.SetForegroundColour((255,75,75))
        wx.Yield()
        if "Adafruit_DHT" in working_modules:
            self.adaDHT_check.SetForegroundColour((75,200,75))
        else:
            self.adaDHT_check.SetForegroundColour((255,75,75))
        if "crontab" in working_modules:
            self.cron_check.SetForegroundColour((75,200,75))
        else:
            self.cron_check.SetForegroundColour((255,75,75))
        if "praw" in working_modules:
            self.praw_check.SetForegroundColour((75,200,75))
        else:
            self.praw_check.SetForegroundColour((255,75,75))
        if "pexpect" in working_modules:
            self.pexpect_check.SetForegroundColour((75,200,75))
        else:
            self.pexpect_check.SetForegroundColour((255,75,75))

    def start_click(self, e):
        print("Install process started;")
        self.progress.SetLabel("##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        self.install_pigrow()
        self.progress.SetLabel("#######~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        pip_text = self.install_all_pip()
        self.progress.SetLabel("##############~~~~~~~~~~~~~~~~~")
        wx.Yield()
        self.install_all_apt()
        self.progress.SetLabel("#######################~~~~~~~~")
        wx.Yield()
        self.install_adafruit_DHT()
        self.progress.SetLabel("####### INSTALL COMPLETE ######")
        wx.Yield()
        self.start_btn.Disable()
        self.cancel_btn.SetLabel("OK")


    def cancel_click(self, e):
        self.Destroy()

#
#
#
### pigrow Config pannel
#
#
class config_ctrl_pnl(wx.Panel):
    #this controlls the data displayed on config_info_pnl
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        height_of_pannels_above = 230
        space_left = win_height - height_of_pannels_above
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, height_of_pannels_above), size = wx.Size(285, space_left), style = wx.TAB_TRAVERSAL )
        # Start drawing the UI elements
        wx.StaticText(self,  label='Pigrow Config', pos=(25, 10))
        self.name_box_btn = wx.Button(self, label='change box name', pos=(15, 95), size=(190, 30))
        self.name_box_btn.Bind(wx.EVT_BUTTON, self.name_box_click)
        self.config_lamp_btn = wx.Button(self, label='config lamp', pos=(15, 130), size=(190, 30))
        self.config_lamp_btn.Bind(wx.EVT_BUTTON, self.config_lamp_click)
        self.config_dht_btn = wx.Button(self, label='config dht', pos=(15, 165), size=(190, 30))
        self.config_dht_btn.Bind(wx.EVT_BUTTON, self.config_dht_click)
        self.new_gpio_btn = wx.Button(self, label='Add new relay device', pos=(15, 200), size=(190, 30))
        self.new_gpio_btn.Bind(wx.EVT_BUTTON, self.add_new_device_relay)
        self.update_config_btn = wx.Button(self, label='read config from pigrow', pos=(15, 460), size=(175, 30))
        self.update_config_btn.Bind(wx.EVT_BUTTON, self.update_config_click)
        self.update_settings_btn = wx.Button(self, label='update pigrow settings', pos=(15, 500), size=(175, 30))
        self.update_settings_btn.Bind(wx.EVT_BUTTON, self.update_setting_click)

    def name_box_click(self, e):
        box_name = config_info_pnl.boxname_text.GetValue()
        if not box_name == MainApp.config_ctrl_pannel.config_dict["box_name"]:
            MainApp.config_ctrl_pannel.config_dict["box_name"] = box_name
            pi_link_pnl.boxname = box_name  #to maintain persistance if needed elsewhere later
            MainApp.pi_link_pnl.link_status_text.SetLabel("linked with - " + box_name)
            self.update_setting_click("e")
        else:
            print("no change")

    def update_config_click(self, e):
        print("reading pigrow and updating local config info")
        # clear dictionaries and tables
        self.dirlocs_dict = {}
        self.config_dict = {}
        self.gpio_dict = {}
        self.gpio_on_dict = {}
        MainApp.config_info_pannel.gpio_table.DeleteAllItems()
        # define file locations
        pigrow_config_folder = "/home/" + pi_link_pnl.target_user + "/Pigrow/config/"
        pigrow_dirlocs = pigrow_config_folder + "dirlocs.txt"
        #read pigrow locations file
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat " + pigrow_dirlocs)
        dirlocs = out.splitlines()
        if len(dirlocs) > 1:
            for item in dirlocs:
                try:
                    item = item.split("=")
                    #self.dirlocs_dict = {item[0]:item[1]}
                    self.dirlocs_dict[item[0]] = item[1]
                except:
                    print("!!error reading value from dirlocs; " + str(item))
        else:
            print("Error; dirlocs contains no information")
        #We've now created self.dirlocs_dict with key:value for every setting:value in dirlocs
        #now we grab some of the important ones from the dictionary
         #folder location info (having this in a file on the pi makes it easier if doing things odd ways)
        location_msg = ""
        location_problems = []
        try:
            pigrow_path = self.dirlocs_dict['path']
        #    location_msg += pigrow_path + "\n"
        except:
            location_msg += ("No path locaion info in pigrow dirlocs\n")
            pigrow_path = ""
            location_problems.append("path")
        try:
            pigrow_logs_path = self.dirlocs_dict['log_path']
        #    location_msg += pigrow_logs_path + "\n"
        except:
            location_msg += ("No logs locaion info in pigrow dirlocs\n")
            pigrow_logs_path = ""
            location_problems.append("log_path")
        try:
            pigrow_graph_path = self.dirlocs_dict['graph_path']
        #    location_msg += pigrow_graph_path + "\n"
        except:
            location_msg += ("No graph locaion info in pigrow dirlocs\n")
            pigrow_graph_path = ""
            location_problems.append("graph_path")
        try:
            pigrow_caps_path = self.dirlocs_dict['caps_path']
        #    location_msg += pigrow_caps_path + "\n"
        except:
            location_msg += ("No caps locaion info in pigrow dirlocs\n")
            pigrow_caps_path = ""
            location_problems.append("caps_path")

         #settings file locations
        try:
            pigrow_settings_path = self.dirlocs_dict['loc_settings']
        except:
            location_msg += ("No pigrow config file locaion info in pigrow dirlocs\n")
            pigrow_settings_path = ""
            location_problems.append("loc_settings")
        try:
            pigrow_cam_settings_path = self.dirlocs_dict['camera_settings']
        except:
            location_msg +=("no camera settings file locaion info in pigrow dirlocs (optional)\n")
            pigrow_cam_settings_path = ""

         # log file locations
        try:
            pigrow_err_log_path = self.dirlocs_dict['err_log']
        except:
            location_msg += ("No err log locaion info in pigrow dirlocs\n")
            pigrow_err_log_path = ""
            location_problems.append("err_log")
        try:
            pigrow_self_log_path = self.dirlocs_dict['self_log']
        except:
            location_msg += ("No self_log locaion info in pigrow dirlocs (optional)\n")
            pigrow_self_log_path = ""
        try:
            pigrow_switchlog_path = self.dirlocs_dict['loc_switchlog']
        except:
            location_msg += "No switchlog locaion info in pigrow dirlocs (optional)\n"
            pigrow_switchlog_path = ""
        #check to see if there were problems and tell the user.
        if len(location_problems) == 0:
            location_msg += ("All vital locations present")
        else:
            location_msg += "Important location information missing! " + str(location_problems) + " not found"
        #display on screen
        config_info_pnl.location_text.SetLabel(location_msg)
        #
        #read pigrow config file
        #
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat " + pigrow_settings_path)
        pigrow_settings = out.splitlines()
        #go through the setting file and put them in the correct dictionary
        if len(pigrow_settings) > 1:
            for item in pigrow_settings:
                try:
                    item = item.split("=")
                    line_split = item[0].split("_")
                    if line_split[0] == 'gpio' and not item[1] == "":
                        if len(line_split) == 2:
                            self.gpio_dict[line_split[1]] = item[1]
                        elif len(line_split) == 3:
                            self.gpio_on_dict[str(line_split[1])] = item[1]
                    else:
                        self.config_dict[item[0]] = item[1]
                except:
                    print("!!error reading value from config file; " + str(item))
        # we've now created self.config_dict with a list of all the items in the config file
        #   and self.gpio_dict and self.gpio_on_dict with gpio numbers and low/high pin direction info


        #unpack non-gpio information from config file
        config_problems = []
        config_msg = ''
        lamp_msg = ''
        dht_msg = ''
        #lamp timeing
        if "lamp" in self.gpio_dict:
            if "time_lamp_on" in self.config_dict:
                lamp_on_hour = int(self.config_dict["time_lamp_on"].split(":")[0])
                lamp_on_min = int(self.config_dict["time_lamp_on"].split(":")[1])

            else:
                lamp_msg += "lamp on time not set "
                config_problems.append('lamp')
            if "time_lamp_off" in self.config_dict:
                lamp_off_hour = int(self.config_dict["time_lamp_off"].split(":")[0])
                lamp_off_min = int(self.config_dict["time_lamp_off"].split(":")[1])
            else:
                lamp_msg += "lamp off time not set\n"
                config_problems.append('lamp')
            #convert to datetime objects and add a day to the off time so that it's
            #   working out the time on gap correctly (i.e. avoid reporting negative time)
            if not 'lamp' in config_problems:
                on_time = datetime.time(int(lamp_on_hour),int(lamp_on_min))
                off_time = datetime.time(int(lamp_off_hour), int(lamp_off_min))
                aday = datetime.timedelta(days=1)
                if on_time > off_time:
                    dateoff = ((datetime.datetime.combine(datetime.date.today(), off_time) + aday))
                else:
                    dateoff = ((datetime.datetime.combine(datetime.date.today(), off_time)))
                length_lamp_on = (dateoff - datetime.datetime.combine(datetime.date.today(), on_time))
                lamp_msg += "Lamp turning on at " + str(on_time)[:-3] + " and off at " + str(off_time)[:-3]
                lamp_msg += " (" + str(length_lamp_on)[:-3] + " on, "  +str(aday - length_lamp_on)[:-3] + " off)\n"

            # checking lamp timings in cron
            on_cron = self.get_cron_time("lamp_on.py")
            off_cron = self.get_cron_time("lamp_off.py")
            if on_cron != "not found" and off_cron != "not found":
                if on_cron != "runs more than once" and off_cron != "runs more than once":
                    on_cron = datetime.time(int(on_cron.split(" ")[1]), int(on_cron.split(" ")[0]))
                    off_cron = datetime.time(int(off_cron.split(" ")[1]), int(off_cron.split(" ")[0]))
                    if on_cron == on_time and off_cron == off_time:
                        lamp_msg += "Lamp synced with cron"
                    else:
                        lamp_msg += "Warning - lamp not synced with cron."
                else:
                    lamp_msg += "Warning - lamp switching more than once a day"
            else:
                lamp_msg += "Warning - cron switching not configured"


                #on_cron_converted = []

        else:
            lamp_msg += "no lamp linked to gpio, ignoring lamp timing settings"
     #heater on and off temps
        if "heater" in self.gpio_dict:
            dht_msg += "heater enabled, "
        else:
            dht_msg += "no heater gpio, "
        # low
        if "heater_templow" in self.config_dict:
            self.heater_templow =  self.config_dict["heater_templow"]
            dht_msg += "Temp low; " + str(self.heater_templow) + " "
        else:
            dht_msg += "\nheater low temp not set\n"
            config_problems.append('heater_templow')
            self.heater_templow = None
        # high
        if "heater_temphigh" in self.config_dict:
            self.heater_temphigh = self.config_dict["heater_temphigh"]
            dht_msg += "temp high: " + str(self.heater_temphigh) + " (Centigrade)\n"
        else:
            dht_msg += "\nheater high temp not set\n"
            config_problems.append('heater_temphigh')
            self.heater_temphigh = None
        #
        # read humid info
        if "humid" in self.gpio_dict or "dehumid" in self.gpio_dict:
            dht_msg += "de/humid linked, "
        else:
            dht_msg += "de/humid NOT linked, "
        # low
        if "humid_low" in self.config_dict:
            self.humid_low = self.config_dict["humid_low"]
            dht_msg += "humidity low; " + str(self.humid_low)
        else:
            dht_msg += "\nHumid low not set\n"
            config_problems.append('humid_low')
            self.humid_low = None
        # high
        if "humid_high" in self.config_dict:
            self.humid_high = self.config_dict["humid_high"]
            dht_msg += " humidity high: " + str(self.humid_high) + "\n"
        else:
            dht_msg += "humid high not set\n"
            config_problems.append('humid_high')
            self.humid_high = None
        #
        #add gpio message to the message text
        config_msg += "We have " + str(len(self.gpio_dict)) + " devices linked to the GPIO\n"
        if "dht22sensor" in self.gpio_dict:
            dht_msg += "DHT Sensor on pin " + str(self.gpio_dict['dht22sensor'] + "\n")
            if "log_frequency" in self.config_dict:
                self.log_frequency = self.config_dict["log_frequency"]
                dht_msg += "Logging dht every " + str(self.log_frequency) + " seconds. \n"
            else:
                self.log_frequency = ""
                dht_msg += "DHT Logging frequency not set\n"
                config_problems.append('dht_log_frequency')
            #check to see if log location is set in dirlocs.txt
            try:
                dht_msg += "logging to; " + self.dirlocs_dict['loc_dht_log'] + "\n"
            except:
                dht_msg += "No DHT log locaion in pigrow dirlocs\n"
                config_problems.append('dht_log_location')
        else:
            dht_msg += "DHT Sensor not linked\n"

        #read cron info to see if dht script is running
        last_index = cron_list_pnl.startup_cron.GetItemCount()
        self.check_dht_running = "not found"
        extra_args = ""
        if not last_index == 0:
            for index in range(0, last_index):
                 name = cron_list_pnl.startup_cron.GetItem(index, 3).GetText()
                 if "checkDHT.py" in name:
                     self.check_dht_running = cron_list_pnl.startup_cron.GetItem(index, 1).GetText()
                     extra_args = cron_list_pnl.startup_cron.GetItem(index, 4).GetText().lower()
                     self.checkdht_cronindex = index
        # write more to dht script messages
        if self.check_dht_running == "True":
            dht_msg += "script check_DHT.py is currently running\n"
        elif self.check_dht_running == "not found":
            dht_msg += "script check_DHT not set to run on startup, add to cron and restart pigrow\n"
        elif self.check_dht_running == "False":
            dht_msg += "script check_DHT.py should be running but isn't - check error logs\n"
        else:
            dht_msg += "error reading cron info\n"
        #extra args used to select options modes, if to ignore heater, etc.
        dht_msg += "extra args = " + extra_args + "\n"
        dht_msg += ""
         #heater
        if "use_heat=true" in extra_args:
            dht_msg += "heater enabled, "
            self.use_heat = True
        elif "use_heat=false" in extra_args:
            dht_msg += "heater disabled, "
            self.use_heat = False
        else:
            dht_msg += "heater enabled, "
            self.use_heat = True
         #humid
        if "use_humid=true" in extra_args:
            dht_msg += "humidifier enabled, "
            self.use_humid = True
        elif "use_humid=false" in extra_args:
            dht_msg += "humidifier disabled, "
            self.use_humid = False
        else:
            dht_msg += "humidifier enabled, "
            self.use_humid = True
         #dehumid
        if "use_dehumid=true" in extra_args:
            dht_msg += "dehumidifier enabled, "
            self.use_dehumid = True
        elif "use_dehumid=false" in extra_args:
            dht_msg += "dehumidifier disabled, "
            self.use_dehumid = False
        else:
            dht_msg += "dehumidifier enabled, "
            self.use_dehumid = True
         #who controls fans
        if "use_fan=heat" in extra_args:
            dht_msg += "fan switched by heater "
            self.fans_owner = "heater"
        elif "use_fan=hum" in extra_args:
            dht_msg += "fan switched by humidifer "
            self.fans_owner = "humid"
        elif "use_fan=dehum" in extra_args:
            dht_msg += "fan switched by dehumidifer "
            self.fans_owner = "dehumid"
        elif "use_fan=hum" in extra_args:
            dht_msg += "dht control of fan disabled "
            self.fans_owner = "manual"
        else:
            dht_msg += "fan swtiched by heater"
            self.fans_owner = "heater"

        #checks to see if gpio devices with on directions are also linked to a gpio pin and counts them
        relay_list_text = "Device - Pin - Switch direction for power on - current device state"
        for key in self.gpio_on_dict:
            if key in self.gpio_dict:
                info = ''
                self.add_to_GPIO_list(str(key), self.gpio_dict[key], self.gpio_on_dict[key], info=info)
        #listing config problems at end of config messsage
        if len(config_problems) > 0:
            config_msg += "found " + str(len(config_problems)) + " config problems; "
        for item in config_problems:
            config_msg += item + ", "

        #putting the info on the screen
        config_info_pnl.boxname_text.SetValue(pi_link_pnl.boxname)
        config_info_pnl.config_text.SetLabel(config_msg)
        config_info_pnl.lamp_text.SetLabel(lamp_msg)
        config_info_pnl.dht_text.SetLabel(dht_msg)

    def get_cron_time(self, script):
        last_index = cron_list_pnl.timed_cron.GetItemCount()
        script_timestring = "not found"
        count = 0
        if not last_index == 0:
            for index in range(0, last_index):
                 name = cron_list_pnl.timed_cron.GetItem(index, 3).GetText()
                 if script in name:
                     script_timestring = cron_list_pnl.timed_cron.GetItem(index, 2).GetText()
                     count = count + 1
            if count > 1:
                return "runs more than once"
        return script_timestring

    def config_lamp_click(self, e):
        lamp_dbox = config_lamp_dialog(None, title='Config Lamp')
        lamp_dbox.ShowModal()

    def config_dht_click(self, e):
        dht_dbox = edit_dht_dialog(None, title='Config DHT')
        dht_dbox.ShowModal()
        self.update_setting_click("e")

    def add_new_device_relay(self, e):
        #define as blank
        config_ctrl_pnl.device_toedit = ""
        config_ctrl_pnl.gpio_toedit = ""
        config_ctrl_pnl.wiring_toedit = ""
        #create dialogue box
        gpio_dbox = edit_gpio_dialog(None, title='Device GPIO link')
        gpio_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        device = config_ctrl_pnl.device_new
        gpio = config_ctrl_pnl.gpio_new
        wiring = config_ctrl_pnl.wiring_new
        if not device == "":
            #update config file
            print device, gpio, wiring
            config_ctrl_pnl.add_to_GPIO_list(MainApp.config_ctrl_pannel, device, gpio, wiring, currently='UNLINKED')
        else:
            print "cancelled"

    def check_device_status(self, gpio_pin, on_power_state):
        #Checks if a device is on or off by reading the pin and compairing to the relay wiring direction
        try:
            ssh.exec_command("echo "+ str(gpio_pin) +" > /sys/class/gpio/export")
            stdin, stdout, stderr = ssh.exec_command("cat /sys/class/gpio/gpio" + str(gpio_pin) + "/value") # returns 0 or 1
            gpio_status = stdout.read().strip()
            gpio_err = stderr.read().strip()
            if gpio_status == "1":
                if on_power_state == 'low':
                    device_status = "OFF"
                elif on_power_state == 'high':
                    device_status = 'ON'
                else:
                    device_status = "settings error"
            elif gpio_status == '0':
                if on_power_state == 'low':
                    device_status = "ON"
                elif on_power_state == 'high':
                    device_status = 'OFF'
                else:
                    device_status = "setting error"
            else:
                device_status = "read error -" + gpio_status + "-"
        except Exception as e:
            print("Error asking pi about gpio status; " + str(e))
            return "error " + str(e)
        return device_status

    def add_to_GPIO_list(self, device, gpio, wiring, currently='', info=''):
        #config_ctrl_pnl.add_to_GPIO_list(self, device, gpio, wiring, currently='', info='')
        if currently == '':
            currently = self.check_device_status(gpio, wiring)
        config_info_pnl.gpio_table.InsertStringItem(0, str(device))
        config_info_pnl.gpio_table.SetStringItem(0, 1, str(gpio))
        config_info_pnl.gpio_table.SetStringItem(0, 2, str(wiring))
        config_info_pnl.gpio_table.SetStringItem(0, 3, str(currently))
        config_info_pnl.gpio_table.SetStringItem(0, 4, str(info))

    def update_setting_click(self, e):
        #create updated settings file
        #
        #creating GPIO config block
        item_count = config_info_pnl.gpio_table.GetItemCount()
        # add dht22 sesnsor if present;
        if "dht22sensor" in self.gpio_dict:
            gpio_config_block = "\ngpio_dht22sensor=" + self.gpio_dict["dht22sensor"]
        else:
            gpio_config_block = ""
        # list all devices with gpio and wiring directions
        for count in range(0, item_count):
            device = config_info_pnl.gpio_table.GetItem(count, 0).GetText()
            gpio = config_info_pnl.gpio_table.GetItem(count, 1).GetText()
            wiring = config_info_pnl.gpio_table.GetItem(count, 2).GetText()
            gpio_config_block += "\ngpio_" + device + "=" + gpio
            gpio_config_block += "\ngpio_" + device + "_on=" + wiring
        # list all non-gpio settings
        other_settings = ""
        for key, value in self.config_dict.items():
            other_settings += "\n" + key + "=" + value
        config_text = other_settings[1:]
        config_text += gpio_config_block
        # show user and ask user if they relly want to update
        dbox = wx.MessageDialog(self, config_text, "upload to pigrow?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        #if user said ok then upload file to pi
        if (answer == wx.ID_OK):
            #
            # REPLACE THE FOLLOWING WITH A FUNCTION THAT ANYONE CAN CALL TO UPLOAD A FILE
            #
            sftp = ssh.open_sftp()
            folder = "/home/" + str(pi_link_pnl.target_user) +  "/Pigrow/config/"
            f = sftp.open(folder + '/pigrow_config.txt', 'w')
            f.write(config_text)
            f.close()
            self.update_config_click("e")

class config_info_pnl(wx.Panel):
    #  This displays the config info
    # controlled by the config_ctrl_pnl
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        win_width = parent.GetSize()[0]
        w_space_left = win_width - 285
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size(w_space_left , 800), style = wx.TAB_TRAVERSAL )
        ## Draw UI elements
        #display background
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        #SDcard details
        config_info_pnl.boxname_text = wx.TextCtrl(self,  pos=(25, 150), size=(265,65))
        config_info_pnl.location_text = wx.StaticText(self,  label='locations', pos=(520, 120), size=(200,30))
        config_info_pnl.config_text = wx.StaticText(self,  label='config', pos=(520, 185), size=(200,30))
        config_info_pnl.lamp_text = wx.StaticText(self,  label='lamp', pos=(10, 330), size=(200,30))
        config_info_pnl.dht_text = wx.StaticText(self,  label='dht', pos=(10, 415), size=(200,30))
        config_info_pnl.gpio_table = self.GPIO_list(self, 1)
        config_info_pnl.gpio_table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_GPIO)

    def OnEraseBackground(self, evt):
        # yanked from ColourDB.py #then from https://www.blog.pythonlibrary.org/2010/03/18/wxpython-putting-a-background-image-on-a-panel/
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap("./config_info.png")
        dc.DrawBitmap(bmp, 0, 0)

    class GPIO_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,635), size=(570,160)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Device')
            self.InsertColumn(1, 'GPIO')
            self.InsertColumn(2, 'wiring')
            self.InsertColumn(3, 'Currently')
            self.InsertColumn(4, 'info')
            self.SetColumnWidth(0, 150)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 100)
            self.SetColumnWidth(3, 100)
            self.SetColumnWidth(4, -1)

    def onDoubleClick_GPIO(self, e):
        index =  e.GetIndex()
        config_info_pnl.index = index
        #get info for dialogue box
        device = config_info_pnl.gpio_table.GetItem(index, 0).GetText()
        gpio = config_info_pnl.gpio_table.GetItem(index, 1).GetText()
        wiring = config_info_pnl.gpio_table.GetItem(index, 2).GetText()
        currently = config_info_pnl.gpio_table.GetItem(index, 3).GetText()
        #set data for dialogue box to read
        config_ctrl_pnl.device_toedit = device
        config_ctrl_pnl.gpio_toedit = gpio
        config_ctrl_pnl.wiring_toedit = wiring
        config_ctrl_pnl.currently_toedit = currently
        #create dialogue box
        gpio_dbox = doubleclick_gpio_dialog(None, title='Device GPIO link')
        gpio_dbox.ShowModal()
        # read data from dbox
        new_device = config_ctrl_pnl.device_new
        new_gpio = config_ctrl_pnl.gpio_new
        new_wiring = config_ctrl_pnl.wiring_new
        new_currently = config_ctrl_pnl.currently_new
        # if changes happened mark the ui
        #
        if not new_currently == "":
            config_info_pnl.gpio_table.SetStringItem(index, 0, str(new_device))
            config_info_pnl.gpio_table.SetStringItem(index, 1, str(new_gpio))
            config_info_pnl.gpio_table.SetStringItem(index, 2, str(new_wiring))
            config_info_pnl.gpio_table.SetStringItem(index, 3, str(new_currently))

class config_lamp_dialog(wx.Dialog):
    #Dialog box for creating for adding or editing the lamp timing settings
    def __init__(self, *args, **kw):
        super(config_lamp_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 500))
        self.SetTitle("Config Lamp")
    def InitUI(self):
        #
        on_hour = int(MainApp.config_ctrl_pannel.config_dict["time_lamp_on"].split(":")[0])
        on_min = int(MainApp.config_ctrl_pannel.config_dict["time_lamp_on"].split(":")[1])
        off_hour = int(MainApp.config_ctrl_pannel.config_dict["time_lamp_off"].split(":")[0])
        off_min = int(MainApp.config_ctrl_pannel.config_dict["time_lamp_off"].split(":")[1])

        # draw the pannel and text
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Lamp Config;', pos=(20, 10))
        # hour on - first line
        wx.StaticText(self,  label='on time', pos=(10, 50))
        self.on_hour_spin = wx.SpinCtrl(self, min=0, max=23, value=str(on_hour), pos=(80, 35), size=(60, 50))
        self.on_hour_spin.Bind(wx.EVT_SPINCTRL, self.on_spun)
        wx.StaticText(self,  label=':', pos=(145, 50))
        self.on_min_spin = wx.SpinCtrl(self, min=0, max=59, value=str(on_min), pos=(155, 35), size=(60, 50))
        self.on_min_spin.Bind(wx.EVT_SPINCTRL, self.on_spun)
        # length on on period - second line
        wx.StaticText(self,  label='Lamp on for ', pos=(25, 100))
        self.on_period_h_spin = wx.SpinCtrl(self, min=0, max=23, value="", pos=(130, 85), size=(60, 50))
        self.on_period_h_spin.Bind(wx.EVT_SPINCTRL, self.on_spun)
        wx.StaticText(self,  label='hours and ', pos=(195, 100))
        self.on_period_m_spin = wx.SpinCtrl(self, min=0, max=59, value="", pos=(280, 85), size=(60, 50))
        self.on_period_m_spin.Bind(wx.EVT_SPINCTRL, self.on_spun)
        wx.StaticText(self,  label='min', pos=(345, 100))
        # off time - third line (worked out by above or manual input)
        wx.StaticText(self,  label='off time', pos=(10, 150))
        self.off_hour_spin = wx.SpinCtrl(self, min=0, max=23, value=str(off_hour), pos=(80, 135), size=(60, 50))
        self.off_hour_spin.Bind(wx.EVT_SPINCTRL, self.off_spun)
        wx.StaticText(self,  label=':', pos=(145, 150))
        self.off_min_spin = wx.SpinCtrl(self, min=0, max=59, value=str(off_min), pos=(155, 135), size=(60, 50))
        self.off_min_spin.Bind(wx.EVT_SPINCTRL, self.off_spun)
        # cron timing of switches
        wx.StaticText(self,  label='Cron Timing of Switches;', pos=(10, 250))
        wx.StaticText(self,  label='Current                          New', pos=(50, 280))
        lamp_on_string = MainApp.config_ctrl_pannel.get_cron_time("lamp_on.py").strip()
        lamp_off_string = MainApp.config_ctrl_pannel.get_cron_time("lamp_off.py").strip()
        wx.StaticText(self,  label=" on;", pos=(20, 310))
        wx.StaticText(self,  label="off;", pos=(20, 340))
        self.cron_lamp_on = wx.StaticText(self,  label=lamp_on_string, pos=(60, 310))
        self.cron_lamp_off = wx.StaticText(self,  label=lamp_off_string, pos=(60, 340))


        new_on_string = (str(on_min) + " " + str(on_hour) + " * * *")
        new_off_string = (str(off_min) + " " + str(off_hour) + " * * *")
        self.new_on_string_text = wx.StaticText(self,  label=new_on_string, pos=(220, 310))
        self.new_off_string_text = wx.StaticText(self,  label=new_off_string, pos=(220, 340))
        # set lamp period values
        on_period_hour, on_period_min = self.calc_light_period(on_hour, on_min, off_hour, off_min)
        self.on_period_h_spin.SetValue(on_period_hour)
        self.on_period_m_spin.SetValue(on_period_min)
        #ok and cancel buttons
        self.ok_btn = wx.Button(self, label='Ok', pos=(15, 450), size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        self.cancel_btn = wx.Button(self, label='Cancel', pos=(315, 450), size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)

    def on_spun(self, e):
        # make light hour and min into time delta
        light_period_h = self.on_period_h_spin.GetValue()
        light_period_m = self.on_period_m_spin.GetValue()
        time_period = datetime.timedelta(hours=light_period_h, minutes=light_period_m)
        # make on hour and min into datetime
        on_hour = self.on_hour_spin.GetValue()
        on_min = self.on_min_spin.GetValue()
        on_time = datetime.time(int(on_hour),int(on_min))
        date_on = datetime.datetime.combine(datetime.date.today(), on_time)
        # new off time
        new_off_time = date_on + time_period
        self.off_hour_spin.SetValue(new_off_time.hour)
        self.off_min_spin.SetValue(new_off_time.minute)
        self.new_on_string_text.SetLabel(str(on_min) + " " + str(on_hour) + " * * *")
        self.new_off_string_text.SetLabel(str(new_off_time.minute) + " " + str(new_off_time.hour) + " * * *")

    def off_spun(self, e):
        # make on hour and min into datetime
        on_hour = self.on_hour_spin.GetValue()
        on_min = self.on_min_spin.GetValue()
        off_hour = self.off_hour_spin.GetValue()
        off_min = self.off_min_spin.GetValue()
        hours, mins = self.calc_light_period(on_hour, on_min, off_hour, off_min)
        self.on_period_h_spin.SetValue(hours)
        self.on_period_m_spin.SetValue(mins)
        self.new_on_string_text.SetLabel(str(on_min) + " " + str(on_hour) + " * * *")
        self.new_off_string_text.SetLabel(str(off_min) + " " + str(off_hour) + " * * *")

    def calc_light_period(self, on_hour, on_min, off_hour, off_min):
        # make datetime objects
        on_time = datetime.time(int(on_hour),int(on_min))
        date_on = datetime.datetime.combine(datetime.date.today(), on_time)
        off_time = datetime.time(int(off_hour),int(off_min))
        # determine on/off cycle order and account for daily on/off cycle being inverted
        #                        i.e. lamp turning on at 7am and off at 6am gives 23 hours of light
        if on_time > off_time:
            dateoff = ((datetime.datetime.combine(datetime.date.today(), off_time) + datetime.timedelta(days=1)))
        else:
            dateoff = ((datetime.datetime.combine(datetime.date.today(), off_time)))
        # determine lamp period
        length_lamp_on = (dateoff - datetime.datetime.combine(datetime.date.today(), on_time))
        length_on_in_min = length_lamp_on.seconds / 60
        hours = length_on_in_min / 60 #because it's an int it ignores the remainder thus giving only whole hours (hacky?)
        mins = length_on_in_min - (hours * 60)
        return hours, mins


    def ok_click(self, e):
        # check for changes to cron
        if self.cron_lamp_on.GetLabel() == "not found" or self.cron_lamp_off.GetLabel() == "not found":
            mbox = wx.MessageDialog(None, "Add new job to cron?", "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
            sure = mbox.ShowModal()
            if sure == wx.ID_YES:
                if self.cron_lamp_on.GetLabel() == "not found":
                    cron_task = "/home/pi/Pigrow/scripts/switches/" + "lamp_on.py"
                    MainApp.cron_info_pannel.add_to_onetime_list("new", "True", self.new_on_string_text.GetLabel(), cron_task)
                if self.cron_lamp_off.GetLabel() == "not found":
                    cron_task = "/home/pi/Pigrow/scripts/switches/" + "lamp_off.py"
                    MainApp.cron_info_pannel.add_to_onetime_list("new", "True", self.new_off_string_text.GetLabel(), cron_task)
                    MainApp.cron_info_pannel.update_cron_click("e")
        elif not self.new_on_string_text.GetLabel() == self.cron_lamp_on.GetLabel() or not self.new_off_string_text.GetLabel() == self.cron_lamp_off.GetLabel():
            print(":" + self.new_on_string_text.GetLabel() + ":")
            print(":" + self.cron_lamp_on.GetLabel() + ":")
            mbox = wx.MessageDialog(None, "Update cron timing?", "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
            sure = mbox.ShowModal()
            result_on = 'done'  # these are for cases when only one is changed
            result_off = 'done' # if it attempts to update cron and fails it'll change to an error message
            if sure == wx.ID_YES:
                if not self.new_on_string_text.GetLabel() == self.cron_lamp_on.GetLabel():
                    result_on = self.change_cron_trigger("lamp_on.py", self.new_on_string_text.GetLabel())
                if not self.new_off_string_text.GetLabel() == self.cron_lamp_off.GetLabel():
                    result_off = self.change_cron_trigger("lamp_off.py", self.new_off_string_text.GetLabel())
                if result_on != "done" or result_off != "done":
                    wx.MessageBox('Cron update error, edit lamp switches in the cron pannel', 'Info', wx.OK | wx.ICON_INFORMATION)
                else:
                    MainApp.cron_info_pannel.update_cron_click("e")

        # check for changes to settings file

        time_lamp_on = str(self.on_hour_spin.GetValue()) + ":" + str(self.on_min_spin.GetValue())
        time_lamp_off = str(self.off_hour_spin.GetValue()) + ":" + str(self.off_min_spin.GetValue())
        if not MainApp.config_ctrl_pannel.config_dict["time_lamp_on"] == time_lamp_on or not MainApp.config_ctrl_pannel.config_dict["time_lamp_off"] == time_lamp_off:
            MainApp.config_ctrl_pannel.config_dict["time_lamp_on"] = time_lamp_on
            MainApp.config_ctrl_pannel.config_dict["time_lamp_off"] = time_lamp_off
            MainApp.config_ctrl_pannel.update_setting_click("e")
            MainApp.config_ctrl_pannel.update_config_click("e")
        self.Destroy()

    def change_cron_trigger(self, script, new_time):
        last_index = cron_list_pnl.timed_cron.GetItemCount()
        script_timestring = "not found"
        count = 0
        if not last_index == 0:
            for index in range(0, last_index):
                 name = cron_list_pnl.timed_cron.GetItem(index, 3).GetText()
                 if script in name:
                     script_index = index
                     count = count + 1
            if count > 1:
                return "runs more than once"
        cron_list_pnl.timed_cron.SetStringItem(script_index, 2, new_time)
        return "done"

    def cancel_click(self, e):
        print("does nothing")
        self.Destroy()

class doubleclick_gpio_dialog(wx.Dialog):
    #Dialog box for creating for adding or editing device gpio config data
    def __init__(self, *args, **kw):
        super(doubleclick_gpio_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((400, 200))
        self.SetTitle("GPIO config")
    def InitUI(self):
        # draw the pannel and text
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Edit Device Config', pos=(20, 10))
        self.msgtext = wx.StaticText(self,  label='', pos=(10, 40))
        self.update_box_text()
        # buttons
        okButton = wx.Button(self, label='Ok', pos=(25, 150))
        edit_Button = wx.Button(self, label='Edit', pos=(150, 150))
        switch_Button = wx.Button(self, label='Switch', pos=(275, 150))
        okButton.Bind(wx.EVT_BUTTON, self.OnClose)
        edit_Button.Bind(wx.EVT_BUTTON, self.OnEdit)
        switch_Button.Bind(wx.EVT_BUTTON, self.OnSwitch)

    def update_box_text(self):
        msg = config_ctrl_pnl.device_toedit
        msg += "\n GPIO pin; " + config_ctrl_pnl.gpio_toedit
        msg += "\n Wiring direction; " + config_ctrl_pnl.wiring_toedit
        msg += "\n Currently: " + config_ctrl_pnl.currently_toedit
        self.msgtext.SetLabel(msg)

    def OnClose(self, e):
        self.Destroy()

    def OnEdit(self, e):
        # show edit_gpio_dialog box
        gpio_dbox = edit_gpio_dialog(None, title='Device GPIO link')
        gpio_dbox.ShowModal()
        # catch any changes made if ok was pressed, if cancel all == ''
        if not config_ctrl_pnl.currently_new == "":
            config_ctrl_pnl.device_toedit =  config_ctrl_pnl.device_new
            config_ctrl_pnl.gpio_toedit =  config_ctrl_pnl.gpio_new
            config_ctrl_pnl.wiring_toedit =  config_ctrl_pnl.wiring_new
            config_ctrl_pnl.currently_toedit =  config_ctrl_pnl.currently_new
        self.Destroy()


    def OnSwitch(self, e):
        device = config_ctrl_pnl.device_toedit
        currently = config_ctrl_pnl.currently_toedit
        self.switch_device(device, currently)
        if not currently == config_ctrl_pnl.currently_new:
            # if changes happened mark the ui
            config_info_pnl.gpio_table.SetStringItem(config_info_pnl.index, 3, str(config_ctrl_pnl.currently_new))

    def switch_device(self, device, currently):
        switch_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/switches/"
        if currently == "ON":
            switch_command = switch_path + device + "_off.py"
            future_state = "OFF"
        elif currently == "OFF":
            switch_command = switch_path + device + "_on.py"
            future_state = "ON"
        else:
            switch_command = "ERROR"
        #if error show error message
        if not switch_command == "ERROR":
            #make dialogue box to ask if should switch the device
            d = wx.MessageDialog(
                self, "Are you sure you want to switch " + device + " to the " +
                future_state + " poisition?\n\n\n " +
                "Note: automated control scripts might " +
                "\n      switch this " + currently + " again " +
                "\n      if thier trigger conditions are met. "
                , "Switch " + device + " " + future_state + "?"
                , wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = d.ShowModal()
            d.Destroy()
            #if user said ok then switch device
            if (answer == wx.ID_OK):
                out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(switch_command)
                print out   # shows box with switch info from pigrow
                if not error == "": print error
                config_ctrl_pnl.currently_toedit = future_state #for if toggling within the dialog box
                self.update_box_text()
                config_ctrl_pnl.currently_new = future_state
                config_ctrl_pnl.device_new = device
                config_ctrl_pnl.gpio_new = config_ctrl_pnl.gpio_toedit
                config_ctrl_pnl.wiring_new = config_ctrl_pnl.wiring_toedit
        else:
            d = wx.MessageDialog(self, "Error, current state not determined\n You must upload the settings to the pigrow before switching the device", "Error", wx.OK | wx.ICON_ERROR)
            answer = d.ShowModal()
            d.Destroy()
            return "ERROR"

class edit_gpio_dialog(wx.Dialog):
    #Dialog box for creating for adding or editing device gpio config data
    def __init__(self, *args, **kw):
        super(edit_gpio_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((750, 300))
        self.SetTitle("Device GPIO config")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        # these need to be set by whoever calls the dialog box before it's created
        device = config_ctrl_pnl.device_toedit
        gpio = config_ctrl_pnl.gpio_toedit
        wiring = config_ctrl_pnl.wiring_toedit

        # draw the pannel
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Device GPIO Config', pos=(20, 10))
        #background image
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        # devices combo box
        switch_list = self.list_switch_scripts()
        unlinked_devices = self.list_unused_devices(switch_list)
        wx.StaticText(self,  label='Device;', pos=(20, 50))
        self.devices_combo = wx.ComboBox(self, choices = unlinked_devices, pos=(90,50), size=(175, 25))
        self.devices_combo.SetValue(device)
        # gpio text box
        wx.StaticText(self,  label='GPIO', pos=(10, 100))
        self.gpio_tc = wx.TextCtrl(self, pos=(56, 98), size=(40, 25))
        self.gpio_tc.SetValue(gpio)
        self.gpio_tc.Bind(wx.EVT_CHAR, self.onChar) #limit to valid gpio numbers
        # wiring direction combo box
        wiring_choices = ['low', 'high']
        wx.StaticText(self,  label='Wiring side;', pos=(100, 100))
        self.wiring_combo = wx.ComboBox(self, choices = wiring_choices, pos=(200,98), size=(110, 25))
        self.wiring_combo.SetValue(wiring)
        #Buttom Row of Buttons
        okButton = wx.Button(self, label='Ok', pos=(200, 250))
        closeButton = wx.Button(self, label='Cancel', pos=(300, 250))
        okButton.Bind(wx.EVT_BUTTON, self.set_new_gpio_link)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def OnEraseBackground(self, evt):
        # yanked from ColourDB.py #then from https://www.blog.pythonlibrary.org/2010/03/18/wxpython-putting-a-background-image-on-a-panel/
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap("./relaydialogue.png")
        dc.DrawBitmap(bmp, 0, 0)

    def onChar(self, event):
        #this inhibits any non-numeric keys
        key = event.GetKeyCode()
        try: character = chr(key)
        except ValueError: character = "" # arrow keys will throw this error
        acceptable_characters = "1234567890"
        if character in acceptable_characters or key == 13 or key == 314 or key == 316 or key == 8 or key == 127: # 13 = enter, 314 & 316 = arrows, 8 = backspace, 127 = del
            event.Skip()
            return
        else:
            return False

    def list_switch_scripts(self):
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/scripts/switches/")
        switches = out.split("\n")
        switch_list = []
        for item in switches:
            if item[-6:] == "_on.py":
                switch_list.append(item.split("_")[0])
        return switch_list

    def list_unused_devices(self, switch_list):
        item_count = config_info_pnl.gpio_table.GetItemCount()
        used_devices = []
        for num in range(0, item_count):
            device = config_info_pnl.gpio_table.GetItem(num, 0).GetText()
            used_devices.append(device)
        unused_devices = []
        for item in switch_list:
            if not item in used_devices:
                unused_devices.append(item)
        return unused_devices

    def list_used_gpio(self):
        item_count = config_info_pnl.gpio_table.GetItemCount()
        used_gpio = []
        for num in range(0, item_count):
            gpio = config_info_pnl.gpio_table.GetItem(num, 1).GetText()
            used_gpio.append(gpio)
        return used_gpio

    def list_unused_gpio(self, used_gpio):
        valid_gpio = ['2', '3', '4', '17', '27', '22', '10', '9', '11', '5',
                      '6', '13', '19', '26', '14', '15', '18', '23', '24',
                      '25', '8', '7', '12', '16', '20', '21']
        unused_gpio = []
        for item in valid_gpio:
            if not item in used_gpio:
                unused_gpio.append(item)
        return unused_gpio

    def set_new_gpio_link(self, e):
        #get data from combo boxes.
        unused_gpio = self.list_unused_gpio(self.list_used_gpio())
        config_ctrl_pnl.device_new = self.devices_combo.GetValue()
        config_ctrl_pnl.gpio_new = self.gpio_tc.GetValue()
        config_ctrl_pnl.wiring_new = self.wiring_combo.GetValue()
        #check to see if info is valid and closes if it is
        should_close = True
        # check if device is set
        if config_ctrl_pnl.device_new == "":
            wx.MessageBox('Select a device to link from the list', 'Error', wx.OK | wx.ICON_INFORMATION)
            should_close = False
        #check if gpio number is valid
        if not config_ctrl_pnl.gpio_new == config_ctrl_pnl.gpio_toedit or config_ctrl_pnl.gpio_toedit == "":
            if not config_ctrl_pnl.gpio_new in unused_gpio and should_close == True:
                wx.MessageBox('Select a valid and unused gpio pin', 'Error', wx.OK | wx.ICON_INFORMATION)
                config_ctrl_pnl.gpio_new = self.gpio_tc.SetValue("")
                should_close = False
        # check if wiring direction is set to a valid setting
        if not config_ctrl_pnl.wiring_new == "low" and should_close == True:
            if not config_ctrl_pnl.wiring_new == "high":
                wx.MessageBox("No wiring direction set, \nIf you don't know guess and change it if the device turns on when it should be off", 'Error', wx.OK | wx.ICON_INFORMATION)
                should_close = False
        # if box should be closed then close it
        if should_close == True:
            #checks to see if changes have been made and updates ui if so
            if not config_ctrl_pnl.device_new == config_ctrl_pnl.device_toedit:
                config_ctrl_pnl.currently_new = 'unlinked'
            else:
                if not config_ctrl_pnl.gpio_new == config_ctrl_pnl.gpio_toedit:
                    config_ctrl_pnl.currently_new = 'unlinked'
                else:
                    if not config_ctrl_pnl.wiring_new == config_ctrl_pnl.wiring_toedit:
                        config_ctrl_pnl.currently_new = 'unlinked'
                    else:
                        config_ctrl_pnl.currently_new = config_ctrl_pnl.currently_toedit
            self.Destroy()

    def OnClose(self, e):
        config_ctrl_pnl.device_new = ''
        config_ctrl_pnl.gpio_new = ''
        config_ctrl_pnl.wiring_new = ''
        config_ctrl_pnl.currently_new = ''
        self.Destroy()

class edit_dht_dialog(wx.Dialog):
    #Dialog box for creating for adding or editing device gpio config data
    def __init__(self, *args, **kw):
        super(edit_dht_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 500))
        self.SetTitle("Dht config")
    def InitUI(self):
        # draw the pannel and text
        pnl = wx.Panel(self)
        ## top text
        wx.StaticText(self,  label='Sensor Config;', pos=(20, 10))
        # editable info text
        self.sensor_combo = wx.ComboBox(self, pos=(10,35), choices=['dht22', 'dht11', 'am2302'])
        self.sensor_combo.SetValue("dht22")
        wx.StaticText(self,  label=' on GPIO pin ', pos=(120, 40))
        self.gpio_text = wx.TextCtrl(self, value="", pos=(230, 35))
        # gpio pin
        if "dht22sensor" in MainApp.config_ctrl_pannel.gpio_dict:
            self.sensor_pin = MainApp.config_ctrl_pannel.gpio_dict['dht22sensor']
        else:
            self.sensor_pin = ""
        self.gpio_text.SetValue(self.sensor_pin)
        # read buttons
        self.read_dht_btn = wx.Button(self, label='read sensor', pos=(5, 70), size=(150, 60))
        self.read_dht_btn.Bind(wx.EVT_BUTTON, self.read_dht_click)
        ## temp and humid live reading
        wx.StaticText(self,  label='Temp;', pos=(165, 75))
        wx.StaticText(self,  label='Humid;', pos=(165, 100))
        self.temp_text = wx.StaticText(self,  label='', pos=(230, 75))
        self.humid_text = wx.StaticText(self,  label='', pos=(230, 100))
        ##
        if MainApp.config_ctrl_pannel.check_dht_running == "True":
            check_msg = "Active"
        elif MainApp.config_ctrl_pannel.check_dht_running == "not found":
            check_msg = "not set"
        elif MainApp.config_ctrl_pannel.check_dht_running == "False":
            check_msg = "Error"
       # device control
        wx.StaticText(self,  label='Device Control - checkDHT.py : ' + check_msg, pos=(10, 140))
        wx.StaticText(self,  label='DHT controlled switching of device relays', pos=(5, 155))
        self.heater_checkbox = wx.CheckBox(self, label='Heater', pos = (10,180))
        self.humid_checkbox = wx.CheckBox(self, label='Humid', pos = (110,180))
        self.dehumid_checkbox = wx.CheckBox(self, label='Dehumid', pos = (210,180))
        self.heater_checkbox.SetValue(MainApp.config_ctrl_pannel.use_heat)
        self.humid_checkbox.SetValue(MainApp.config_ctrl_pannel.use_humid)
        self.dehumid_checkbox.SetValue(MainApp.config_ctrl_pannel.use_dehumid)
        wx.StaticText(self,  label='fans controlled by ', pos=(10, 210))
        self.fans_combo = wx.ComboBox(self, pos=(170,205), choices=['manual', 'heater', 'humid', 'dehumid'])
        self.fans_combo.SetValue(MainApp.config_ctrl_pannel.fans_owner)
        #
        # logging info
        wx.StaticText(self,  label='logging every ', pos=(10, 360))
        self.log_rate_text = wx.TextCtrl(self, value="", pos=(130, 355))
        wx.StaticText(self,  label='seconds', pos=(230, 360))
        # logging frequency
        self.log_frequency = MainApp.config_ctrl_pannel.log_frequency
        self.log_rate_text.SetValue(self.log_frequency)
        # log location
        wx.StaticText(self,  label='to; ', pos=(10, 390))
        self.log_loc_text = wx.TextCtrl(self, value="", pos=(30, 385), size=(350, 25))
        if "loc_dht_log" in MainApp.config_ctrl_pannel.dirlocs_dict:
            log_location = MainApp.config_ctrl_pannel.dirlocs_dict['loc_dht_log']
            print log_location
            print ("log location")
        else:
            log_location = "none set"
        self.log_loc_text.SetValue(log_location)
        # if checkdht not set to run then greyout unused commands
        if check_msg == "not set":
            self.heater_checkbox.Enable(False)
            self.humid_checkbox.Enable(False)
            self.dehumid_checkbox.Enable(False)
            self.fans_combo.Enable(False)
            self.log_rate_text.Enable(False)
            self.log_loc_text.Enable(False)


        # temp and humidity brackets
        temp_low = MainApp.config_ctrl_pannel.heater_templow
        temp_high = MainApp.config_ctrl_pannel.heater_temphigh
        humid_low = MainApp.config_ctrl_pannel.humid_low
        humid_high = MainApp.config_ctrl_pannel.humid_high
        wx.StaticText(self,  label='Temp', pos=(55, 235))
        wx.StaticText(self,  label='Humid', pos=(250, 235))
        wx.StaticText(self,  label='high -', pos=(5, 260))
        wx.StaticText(self,  label='high -', pos=(200, 260))
        wx.StaticText(self,  label='low -', pos=(5, 295))
        wx.StaticText(self,  label='low -', pos=(200, 295))
        self.high_temp_text = wx.TextCtrl(self, value=temp_high, pos=(50, 255))
        self.low_temp_text = wx.TextCtrl(self, value=temp_low, pos=(50, 290))
        self.high_humid_text = wx.TextCtrl(self, value=humid_high, pos=(250, 255))
        self.low_humid_text = wx.TextCtrl(self, value=humid_low, pos=(250, 290))
        #buttons
        # need to add - check if software installed if not change read dht to install dht and if config changes made change to confirm changes or something
        self.ok_btn = wx.Button(self, label='Ok', pos=(15, 450), size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        self.cancel_btn = wx.Button(self, label='Cancel', pos=(315, 450), size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)


    def read_dht_click(self, e):
        self.sensor_pin = self.gpio_text.GetValue()
        self.sensor = self.sensor_combo.GetValue()
        args = "gpio=" + self.sensor_pin + " sensor=" + self.sensor
        print args
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/build_test/test_dht.py " + args)
        out = out.strip()
        if "temp" in out:
            out = out.split(" ")
            temp = out[0].split("=")[1]
            humid = out[1].split("=")[1]
            self.temp_text.SetLabel(temp)
            self.humid_text.SetLabel(humid)
        elif "failed" in out:
            self.temp_text.SetLabel("failed")
            self.humid_text.SetLabel("failed")
        else:
            self.temp_text.SetLabel("error")
            self.humid_text.SetLabel("error")

    def ok_click(self, e):
        #check for changes
        changes_made = ""
        # loking for changes to config options for settings file
        if not self.gpio_text.GetValue() == MainApp.config_ctrl_pannel.gpio_dict['dht22sensor']:
            changes_made += "Dht gpio; " + self.gpio_text.GetValue() + " "
        if not self.log_rate_text.GetValue() == MainApp.config_ctrl_pannel.config_dict['log_frequency']:
            changes_made += "log rate; " + self.log_rate_text.GetValue() + " "
        if not self.high_temp_text.GetValue() == MainApp.config_ctrl_pannel.config_dict['heater_temphigh']:
            changes_made += "temp high; " + self.high_temp_text.GetValue() + " "
        if not self.low_temp_text.GetValue() == MainApp.config_ctrl_pannel.config_dict['heater_templow']:
            changes_made += "temp low; " + self.low_temp_text.GetValue() + " "
        if not self.high_humid_text.GetValue() == MainApp.config_ctrl_pannel.config_dict["humid_high"]:
            changes_made += "humid high; " + self.high_humid_text.GetValue() + " "
        if not self.low_humid_text.GetValue() == MainApp.config_ctrl_pannel.config_dict['humid_low']:
            changes_made += "humid low; " + self.low_humid_text.GetValue() + " "
        # looking for changes to cron options for checkDHT.py
        extra_args = ""
        if not changes_made == "":
            changes_made += "\n"
        if not self.heater_checkbox.GetValue() == MainApp.config_ctrl_pannel.use_heat:
            changes_made += " Heater enabled;" + str(self.heater_checkbox.GetValue())
        if self.heater_checkbox.GetValue() == False:
            extra_args += " use_heat=false"
        if not self.humid_checkbox.GetValue() == MainApp.config_ctrl_pannel.use_humid:
            changes_made += " Humid enabled:" + str(self.humid_checkbox.GetValue())
        if self.humid_checkbox.GetValue() == False:
            extra_args += " use_humid=false"
        if not self.dehumid_checkbox.GetValue() == MainApp.config_ctrl_pannel.use_dehumid:
            changes_made += " Dehumid enabled;" + str(self.dehumid_checkbox.GetValue())
        if self.dehumid_checkbox.GetValue() == False:
            extra_args += " use_dehumid=false"
        if not self.fans_combo.GetValue() == MainApp.config_ctrl_pannel.fans_owner:
            changes_made += " Fans set by;" + self.fans_combo.GetValue()
        if self.fans_combo.GetValue() == "manual":
            extra_args += " usefan=none"
        elif self.fans_combo.GetValue() == "humid":
            extra_args += " usefan=hum"
        elif self.fans_combo.GetValue() == "dehumid":
            extra_args += " usefan=dehum"
        if len(extra_args) > 1:
            extra_args = extra_args[1:]
            print "extra args = " + extra_args
            index = MainApp.config_ctrl_pannel.checkdht_cronindex
            cron_list_pnl.startup_cron.SetStringItem(index, 4, str(extra_args))
            changes_made += "\n -- Update Cron to save changes --"

        #
        # changing settings ready for updating config file
        #
        if not changes_made == "":
            #setting dht22 in config dictionary
            if not self.gpio_text.GetValue() == "":
                MainApp.config_ctrl_pannel.gpio_dict["dht22sensor"] = self.gpio_text.GetValue()
            else:
                del MainApp.config_ctrl_pannel.gpio_dict["dht22sensor"]
            print("ignoring self.sensor_combo box because code not written for pigrow base code")
            # logging rate in config dictionary
            if not self.log_rate_text.GetValue() == "":
                MainApp.config_ctrl_pannel.config_dict["log_frequency"] = self.log_rate_text.GetValue()
            else:
                del MainApp.config_ctrl_pannel.config_dict["log_frequency"]
            # temp and humid min max values
            if not self.high_temp_text.GetValue() == "":
                MainApp.config_ctrl_pannel.config_dict["heater_temphigh"] = self.high_temp_text.GetValue()
            else:
                del MainApp.config_ctrl_pannel.config_dict["heater_temphigh"]
            if not self.low_temp_text.GetValue() == "":
                MainApp.config_ctrl_pannel.config_dict["heater_templow"] = self.low_temp_text.GetValue()
            else:
                del MainApp.config_ctrl_pannel.config_dict["heater_templow"]
            if not self.high_humid_text.GetValue() == "":
                MainApp.config_ctrl_pannel.config_dict["humid_high"] = self.high_humid_text.GetValue()
            else:
                del MainApp.config_ctrl_pannel.config_dict["humid_high"]
            if not self.low_humid_text.GetValue() == "":
                MainApp.config_ctrl_pannel.config_dict["humid_low"] = self.low_humid_text.GetValue()
            else:
                del MainApp.config_ctrl_pannel.config_dict["humid_low"]
            #
            # edit dht message text
            MainApp.config_info_pannel.dht_text.SetLabel("changes have been made update pigrow config to use them\n" + changes_made)

        self.Destroy()

    def cancel_click(self, e):
        print("nothing happens")
        self.Destroy()

#
#
##Cron tab
#
#
class cron_info_pnl(wx.Panel):
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        height_of_pannels_above = 230
        space_left = win_height - height_of_pannels_above

        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, height_of_pannels_above), size = wx.Size(285, space_left), style = wx.TAB_TRAVERSAL )
        wx.StaticText(self,  label='Cron Config Menu', pos=(25, 10))
        self.read_cron_btn = wx.Button(self, label='Read Crontab', pos=(10, 40), size=(175, 30))
        self.read_cron_btn.Bind(wx.EVT_BUTTON, self.read_cron_click)
        self.new_cron_btn = wx.Button(self, label='New cron job', pos=(10, 80), size=(175, 30))
        self.new_cron_btn.Bind(wx.EVT_BUTTON, self.new_cron_click)
        self.update_cron_btn = wx.Button(self, label='Update Cron', pos=(10, 120), size=(175, 30))
        self.update_cron_btn.Bind(wx.EVT_BUTTON, self.update_cron_click)
        self.SetBackgroundColour('sea green') #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS

        bSizer = wx.BoxSizer(wx.VERTICAL)
        bSizer.Add(self.read_cron_btn, 0, wx.ALL, 5)
        bSizer.Add(self.new_cron_btn, 0, wx.ALL, 5)
        bSizer.Add(self.update_cron_btn, 0, wx.ALL, 5)
        self.SetSizer(bSizer)

    def update_cron_click(self, e):
        #make a text file of all the cron jobs
        cron_text = ''
        startup_num = cron_list_pnl.startup_cron.GetItemCount()
        for num in range(0, startup_num):
            cron_line = ''
            if cron_list_pnl.startup_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            cron_line += '@reboot ' + cron_list_pnl.startup_cron.GetItemText(num, 3) # cron_task
            cron_line += ' ' + cron_list_pnl.startup_cron.GetItemText(num, 4) # cron_extra_args
            cron_line += ' ' + cron_list_pnl.startup_cron.GetItemText(num, 5) # cron_comment
            cron_text += cron_line + '\n'
        repeat_num = cron_list_pnl.repeat_cron.GetItemCount()
        for num in range(0, repeat_num):
            cron_line = ''
            if cron_list_pnl.repeat_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            cron_line += cron_list_pnl.repeat_cron.GetItemText(num, 2).strip(' ')
            cron_line += ' ' + cron_list_pnl.repeat_cron.GetItemText(num, 3) # cron_task
            cron_line += ' ' + cron_list_pnl.repeat_cron.GetItemText(num, 4) # cron_extra_args
            cron_line += ' ' + cron_list_pnl.repeat_cron.GetItemText(num, 5) # cron_comment
            cron_text += cron_line + '\n'
        onetime_num = cron_list_pnl.timed_cron.GetItemCount()
        for num in range(0, onetime_num):
            cron_line = ''
            if cron_list_pnl.timed_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            cron_line += cron_list_pnl.timed_cron.GetItemText(num, 2).strip(' ')
            cron_line += ' ' + cron_list_pnl.timed_cron.GetItemText(num, 3) # cron_task
            cron_line += ' ' + cron_list_pnl.timed_cron.GetItemText(num, 4) # cron_extra_args
            cron_line += ' ' + cron_list_pnl.timed_cron.GetItemText(num, 5) # cron_comment
            cron_text += cron_line + '\n'
        # ask the user if they're sure
        msg_text = "Update cron to; \n\n" + cron_text
        mbox = wx.MessageDialog(None, msg_text, "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
        sure = mbox.ShowModal()
        if sure == wx.ID_YES:
            print "Updating remote cron"
            # save cron text onto pigrow as text file then import into cron
            sftp = ssh.open_sftp()
            try:
                tempfolder = '/home/pi/Pigrow/temp'
                sftp.mkdir(tempfolder)
            except IOError:
                pass
            f = sftp.open(tempfolder + '/remotecron.txt', 'w')
            f.write(cron_text)
            f.close()
            try:
                stdin, stdout, stderr = ssh.exec_command("crontab " + tempfolder + '/remotecron.txt')
                responce = stdout.read()
                error = stderr.read()
                print responce, error
            except Exception as e:
                print("this ain't right, it just ain't right! " + str(e))
        else:
            print("Updating cron cancelled")
        mbox.Destroy()
        #refresh cron list
        self.read_cron_click("event")

    def read_cron_click(self, event):
        #reads pi's crontab then puts jobs in correct table
        print("Reading cron information from pi")
        try:
            stdin, stdout, stderr = ssh.exec_command("crontab -l")
            cron_text = stdout.read().split('\n')
        except Exception as e:
            print("oh - that didn't work! " + str(e))
        #select instance of list to use
        startup_list_instance = cron_list_pnl.startup_cron
        repeat_list_instance = cron_list_pnl.repeat_cron
        onetime_list_instance = cron_list_pnl.timed_cron
        #clear lists of prior data
        startup_list_instance.DeleteAllItems()
        repeat_list_instance.DeleteAllItems()
        onetime_list_instance.DeleteAllItems()
        #sort cron info into lists
        line_number = 0

        for cron_line in cron_text:
            line_number = line_number + 1
            real_job = True
            if len(cron_line) > 5:
                cron_line.strip()
                #determine if enabled or disabled with hash
                if cron_line[0] == '#':
                    job_enabled = False
                    cron_line = cron_line[1:].strip(' ')
                else:
                    job_enabled = True
                # sort for job type, split into timing string and cmd sting
                if cron_line.find('@reboot') > -1:
                    cron_jobtype = 'reboot'
                    timing_string = '@reboot'
                    cmd_string = cron_line[8:]
                else:
                    split_cron = cron_line.split(' ')
                    timing_string = ''
                    for star in split_cron[0:5]:
                        if not star.find('*') > -1 and not star.isdigit():
                            real_job = False
                        timing_string += star + ' '
                    cmd_string = ''

                    for cmd in split_cron[5:]:
                        cmd_string += cmd + ' '
                    if timing_string.find('/') > -1:
                        cron_jobtype = 'repeating'
                    else:
                        cron_jobtype = 'one time'
                # split cmd_string into cmd_string and comment
                cron_comment_pos = cmd_string.find('#')
                if cron_comment_pos > -1:
                    cron_comment = cmd_string[cron_comment_pos:].strip(' ')
                    cmd_string = cmd_string[:cron_comment_pos].strip(' ')
                else:
                    cron_comment = ''
                # split cmd_string into task and extra args
                cron_task = cmd_string.split(' ')[0]
                cron_extra_args = ''
                for arg in cmd_string.split(' ')[1:]:
                    cron_extra_args += arg + ' '
                if real_job == True and not cmd_string == '':
                    #print job_enabled, timing_string, cron_jobtype, cron_task, cron_extra_args, cron_comment
                    if cron_jobtype == 'reboot':
                        self.add_to_startup_list(line_number, job_enabled, cron_task, cron_extra_args, cron_comment)
                    elif cron_jobtype == 'one time':
                        self.add_to_onetime_list(line_number, job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
                    elif cron_jobtype == 'repeating':
                        self.add_to_repeat_list(line_number, job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
        print("cron information read and updated into tables.")

    def test_if_script_running(self, script):
        #cron_info_pnl.test_if_script_running(MainApp.cron_info_pannel, script)
        stdin, stdout, stderr = ssh.exec_command("pidof -x " + str(script))
        script_text = stdout.read().strip()
        #error_text = stderr.read().strip()
        if script_text == '':
            return False
        else:
            #print 'pid of = ' + str(script_text)
            return True

    def add_to_startup_list(self, line_number, job_enabled, cron_task, cron_extra_args='', cron_comment=''):
        is_running = self.test_if_script_running(cron_task)
        cron_list_pnl.startup_cron.InsertStringItem(0, str(line_number))
        cron_list_pnl.startup_cron.SetStringItem(0, 1, str(job_enabled))
        cron_list_pnl.startup_cron.SetStringItem(0, 2, str(is_running))   #tests if script it currently running on pi
        cron_list_pnl.startup_cron.SetStringItem(0, 3, cron_task)
        cron_list_pnl.startup_cron.SetStringItem(0, 4, cron_extra_args)
        cron_list_pnl.startup_cron.SetStringItem(0, 5, cron_comment)

    def add_to_repeat_list(self, line_number, job_enabled, timing_string, cron_task, cron_extra_args='', cron_comment=''):
        cron_list_pnl.repeat_cron.InsertStringItem(0, str(line_number))
        cron_list_pnl.repeat_cron.SetStringItem(0, 1, str(job_enabled))
        cron_list_pnl.repeat_cron.SetStringItem(0, 2, timing_string)
        cron_list_pnl.repeat_cron.SetStringItem(0, 3, cron_task)
        cron_list_pnl.repeat_cron.SetStringItem(0, 4, cron_extra_args)
        cron_list_pnl.repeat_cron.SetStringItem(0, 5, cron_comment)

    def add_to_onetime_list(self, line_number, job_enabled, timing_string, cron_task, cron_extra_args='', cron_comment=''):
        cron_list_pnl.timed_cron.InsertStringItem(0, str(line_number))
        cron_list_pnl.timed_cron.SetStringItem(0, 1, str(job_enabled))
        cron_list_pnl.timed_cron.SetStringItem(0, 2, timing_string)
        cron_list_pnl.timed_cron.SetStringItem(0, 3, cron_task)
        cron_list_pnl.timed_cron.SetStringItem(0, 4, cron_extra_args)
        cron_list_pnl.timed_cron.SetStringItem(0, 5, cron_comment)

    def make_repeating_cron_timestring(self, repeat, repeat_num):
        #assembles timing sting for cron
        # min (0 - 59) | hour (0 - 23) | day of month (1-31) | month (1 - 12) | day of week (0 - 6) (Sunday=0)
        if repeat == 'min':
            if int(repeat_num) in range(0,59):
                cron_time_string = '*/' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string = '*'
        if repeat == 'hour':
            if int(repeat_num) in range(0,23):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        if repeat == 'day':
            if int(repeat_num) in range(1,31):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        if repeat == 'month':
            if int(repeat_num) in range(1,12):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        if repeat == 'dow':
            if int(repeat_num) in range(1,12):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        return cron_time_string

    def make_onetime_cron_timestring(self, job_min, job_hour, job_day, job_month, job_dow):
        # timing_string = str(job_min) + ' ' + str(job_hour) + ' * * *'
        if job_min.isdigit():
            timing_string = str(job_min)
        else:
            timing_string = '*'
        if job_hour.isdigit():
            timing_string += ' ' + str(job_hour)
        else:
            timing_string += ' *'
        if job_day.isdigit():
            timing_string += ' ' + str(job_day)
        else:
            timing_string += ' *'
        if job_month.isdigit():
            timing_string += ' ' + str(job_month)
        else:
            timing_string += ' *'
        if job_dow.isdigit():
            timing_string += ' ' + str(job_dow)
        else:
            timing_string += ' *'
        return timing_string

    def new_cron_click(self, e):
        #define blank fields and defaults for dialogue box to read
        cron_info_pnl.cron_path_toedit = '/home/pi/Pigrow/scripts/cron/'
        cron_info_pnl.cron_task_toedit = 'input cron task here'
        cron_info_pnl.cron_args_toedit = ''
        cron_info_pnl.cron_comment_toedit = ''
        cron_info_pnl.cron_type_toedit = 'repeating'
        cron_info_pnl.cron_everystr_toedit = 'min'
        cron_info_pnl.cron_everynum_toedit = '5'
        cron_info_pnl.cron_min_toedit = '30'
        cron_info_pnl.cron_hour_toedit = '8'
        cron_info_pnl.cron_day_toedit = ''
        cron_info_pnl.cron_month_toedit = ''
        cron_info_pnl.cron_dow_toedit = ''
        cron_info_pnl.cron_enabled_toedit = True
        #make dialogue box
        cron_dbox = cron_job_dialog(None, title='Cron Job Editor')
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        cron_extra_args = cron_dbox.job_args
        cron_comment = cron_dbox.job_comment
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        job_day = cron_dbox.job_day
        job_month = cron_dbox.job_month
        job_dow = cron_dbox.job_dow
        # make timing_string from min:hour or repeat + repeat_num
        if cron_jobtype == 'repeating':
            timing_string = self.make_repeating_cron_timestring(job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = self.make_onetime_cron_timestring(job_min, job_hour, job_day, job_month, job_dow)
        # sort into the correct table
        if not job_script == None or not job_script == '':
            cron_task = job_path + job_script
            if cron_jobtype == 'startup':
                self.add_to_startup_list('new', job_enabled, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'one time':
                self.add_to_onetime_list('new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'repeating':
                self.add_to_repeat_list('new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

class cron_list_pnl(wx.Panel):
    #
    #  This displays the three different cron type lists on the big-pannel
    #  double click to edit one of the jobs (not yet written)
    #  ohter control buttons found on the cron control pannel
    #

    #none of these resize or anything at the moment
    #consider putting into a sizer or autosizing with math
    #--to screen size tho not to size of cronlist that'd be super messy...
    class startup_cron_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,10), size=(900,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'Active')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.InsertColumn(5, 'comment')
            self.SetColumnWidth(0, 100)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 75)
            self.SetColumnWidth(3, 650)
            self.SetColumnWidth(4, 500)
            self.SetColumnWidth(5, -1)

    class repeating_cron_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,245), size=(900,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'every')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.InsertColumn(5, 'comment')
            self.SetColumnWidth(0, 75)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 100)
            self.SetColumnWidth(3, 500)
            self.SetColumnWidth(4, 500)
            self.SetColumnWidth(5, -1)

    class other_cron_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,530), size=(900,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'Time')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.InsertColumn(5, 'comment')
            self.SetColumnWidth(0, 75)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 100)
            self.SetColumnWidth(3, 500)
            self.SetColumnWidth(4, 500)
            self.SetColumnWidth(5, -1)

    def __init__( self, parent ):
        #find size
        win_height = parent.GetSize()[1]
        win_width = parent.GetSize()[0]
        w_space_left = win_width - 285

        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size(w_space_left , 800), style = wx.TAB_TRAVERSAL )

        wx.StaticText(self,  label='Cron start up;', pos=(5, 10))
        cron_list_pnl.startup_cron = self.startup_cron_list(self, 1, pos=(5, 40), size=(w_space_left-10, 200))
        cron_list_pnl.startup_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_startup)
        wx.StaticText(self,  label='Repeating Jobs;', pos=(5,245))
        cron_list_pnl.repeat_cron = self.repeating_cron_list(self, 1, pos=(5, 280), size=(w_space_left-10, 200))
        cron_list_pnl.repeat_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_repeat)
        wx.StaticText(self,  label='One time triggers;', pos=(5,500))
        cron_list_pnl.timed_cron = self.other_cron_list(self, 1, pos=(5, 530), size=(w_space_left-10, 200))
        cron_list_pnl.timed_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_timed)

    # TESTING CODE WHILE SCRIPT WRITING IS IN PROGRESS
        self.SetBackgroundColour('sea green')  ###THIS IS JUST TO TEST SIZE REMOVE TO STOP THE UGLY

    def onDoubleClick_timed(self, e):
        index =  e.GetIndex()
        #define blank fields and defaults for dialogue box to read
        cmd_path = cron_list_pnl.timed_cron.GetItem(index, 3).GetText()
        cmd = cmd_path.split('/')[-1]
        cmd_path = cmd_path[:-len(cmd)]
        timing_string = cron_list_pnl.timed_cron.GetItem(index, 2).GetText()
        cron_stars = timing_string.split(' ')
        cron_min = cron_stars[0]
        cron_hour = cron_stars[1]
        cron_day = cron_stars[2]
        cron_month = cron_stars[3]
        cron_dow = cron_stars[4]

        cron_info_pnl.cron_path_toedit = str(cmd_path)
        cron_info_pnl.cron_task_toedit = str(cmd)
        cron_info_pnl.cron_args_toedit = str(cron_list_pnl.timed_cron.GetItem(index, 4).GetText())
        cron_info_pnl.cron_comment_toedit = str(cron_list_pnl.timed_cron.GetItem(index, 5).GetText())
        cron_info_pnl.cron_type_toedit = 'one time'
        cron_info_pnl.cron_everystr_toedit = 'min'
        cron_info_pnl.cron_everynum_toedit = '5'
        cron_info_pnl.cron_min_toedit = cron_min
        cron_info_pnl.cron_hour_toedit = cron_hour
        cron_info_pnl.cron_day_toedit = cron_day
        cron_info_pnl.cron_month_toedit = cron_month
        cron_info_pnl.cron_dow_toedit = cron_dow
        if str(cron_list_pnl.timed_cron.GetItem(index, 1).GetText()) == 'True':
            enabled = True
        else:
            enabled = False
        cron_info_pnl.cron_enabled_toedit = enabled
        #make dialogue box
        cron_dbox = cron_job_dialog(None, title='Cron Job Editor')
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        if not job_path == None:
            cron_task = job_path + job_script
        else:
            cron_task = None
        cron_extra_args = cron_dbox.job_args
        cron_comment = cron_dbox.job_comment
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        job_day = cron_dbox.job_day
        job_month = cron_dbox.job_month
        job_dow = cron_dbox.job_dow
        # make timing_string from min:hour or repeat + repeat_num
        if cron_jobtype == 'repeating':
            timing_string = cron_info_pnl.make_repeating_cron_timestring(MainApp.cron_info_pannel, job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = cron_info_pnl.make_onetime_cron_timestring(MainApp.cron_info_pannel, job_min, job_hour, job_day, job_month, job_dow)
        # sort into the correct table
        if not job_script == None:
            # remove entry
            cron_list_pnl.timed_cron.DeleteItem(index)
            #add new entry to correct table
            if cron_jobtype == 'startup':
                cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'new', job_enabled, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'one time':
                cron_info_pnl.add_to_onetime_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'repeating':
                cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

    def onDoubleClick_repeat(self, e):
        index =  e.GetIndex()
        #define blank fields and defaults for dialogue box to read
        cmd_path = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
        cmd = cmd_path.split('/')[-1]
        cmd_path = cmd_path[:-len(cmd)]
        timing_string = cron_list_pnl.repeat_cron.GetItem(index, 2).GetText()
        cron_stars = timing_string.split(' ')
        if not timing_string == 'fail':
            if '/' in cron_stars[0]:
                cron_rep = 'min'
                cron_num = cron_stars[0].split('/')[-1]
            elif '/' in cron_stars[1]:
                cron_rep = 'hour'
                cron_num = cron_stars[1].split('/')[-1]
            elif '/' in cron_stars[2]:
                cron_rep = 'day'
                cron_num = cron_stars[2].split('/')[-1]
            elif '/' in cron_stars[3]:
                cron_rep = 'month'
                cron_num = cron_stars[3].split('/')[-1]
            elif '/' in cron_stars[4]:
                cron_rep = 'dow'
                cron_num = cron_stars[4].split('/')[-1]
        else:
            cron_rep = 'min'
            cron_num = '5'


        cron_info_pnl.cron_path_toedit = str(cmd_path)
        cron_info_pnl.cron_task_toedit = str(cmd)
        cron_info_pnl.cron_args_toedit = str(cron_list_pnl.repeat_cron.GetItem(index, 4).GetText())
        cron_info_pnl.cron_comment_toedit = str(cron_list_pnl.repeat_cron.GetItem(index, 5).GetText())
        cron_info_pnl.cron_type_toedit = 'repeating'
        cron_info_pnl.cron_everystr_toedit = cron_rep
        cron_info_pnl.cron_everynum_toedit = cron_num
        cron_info_pnl.cron_min_toedit = '0'
        cron_info_pnl.cron_hour_toedit = '8'
        cron_info_pnl.cron_day_toedit = '*'
        cron_info_pnl.cron_month_toedit = '*'
        cron_info_pnl.cron_dow_toedit = '*'
        if str(cron_list_pnl.repeat_cron.GetItem(index, 1).GetText()) == 'True':
            enabled = True
        else:
            enabled = False
        cron_info_pnl.cron_enabled_toedit = enabled
        #make dialogue box
        cron_dbox = cron_job_dialog(None, title='Cron Job Editor')
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        if not job_path == None:
            cron_task = job_path + job_script
        else:
            cron_task = None
        cron_extra_args = cron_dbox.job_args
        cron_comment = cron_dbox.job_comment
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        # make timing_string from min:hour or repeat + repeat_num
        if cron_jobtype == 'repeating':
            timing_string = cron_info_pnl.make_repeating_cron_timestring(MainApp.cron_info_pannel, job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = str(job_min) + ' ' + str(job_hour) + ' * * *'
        # sort into the correct table
        if not job_script == None:
            # remove entry
            cron_list_pnl.repeat_cron.DeleteItem(index)
            #add new entry to correct table
            if cron_jobtype == 'startup':
                cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'new', job_enabled, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'one time':
                cron_info_pnl.add_to_onetime_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'repeating':
                cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

    def onDoubleClick_startup(self, e):
        index =  e.GetIndex()
        #define blank fields and defaults for dialogue box to read
        cmd_path = cron_list_pnl.startup_cron.GetItem(index, 3).GetText()
        cmd = cmd_path.split('/')[-1]
        cmd_path = cmd_path[:-len(cmd)]
        cron_info_pnl.cron_path_toedit = str(cmd_path)
        cron_info_pnl.cron_task_toedit = str(cmd)
        cron_info_pnl.cron_args_toedit = str(cron_list_pnl.startup_cron.GetItem(index, 4).GetText())
        cron_info_pnl.cron_comment_toedit = str(cron_list_pnl.startup_cron.GetItem(index, 5).GetText())
        cron_info_pnl.cron_type_toedit = 'startup'
        cron_info_pnl.cron_everystr_toedit = 'min'
        cron_info_pnl.cron_everynum_toedit = '5'
        cron_info_pnl.cron_min_toedit = '0'
        cron_info_pnl.cron_hour_toedit = '8'
        cron_info_pnl.cron_day_toedit = '*'
        cron_info_pnl.cron_month_toedit = '*'
        cron_info_pnl.cron_dow_toedit = '*'
        if str(cron_list_pnl.startup_cron.GetItem(index, 1).GetText()) == 'True':
            enabled = True
        else:
            enabled = False
        cron_info_pnl.cron_enabled_toedit = enabled
        #make dialogue box
        cron_dbox = cron_job_dialog(None, title='Cron Job Editor')
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        if not job_path == None:
            cron_task = job_path + job_script
        else:
            cron_task = None
        cron_extra_args = cron_dbox.job_args
        cron_comment = cron_dbox.job_comment
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        # make timing_string from min:hour or repeat + repeat_num
        if cron_jobtype == 'repeating':
            timing_string = self.make_repeating_cron_timestring(job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = str(job_min) + ' ' + str(job_hour) + ' * * *'
        # sort into the correct table
        if not job_script == None:
            # remove entry
            cron_list_pnl.startup_cron.DeleteItem(index)
            #add new entry to correct table
            if cron_jobtype == 'startup':
                cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'new', job_enabled, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'one time':
                cron_info_pnl.add_to_onetime_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'repeating':
                cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

class cron_job_dialog(wx.Dialog):
    #Dialog box for creating or editing cron scripts
    #   takes ten variables from cron_info_pnl
    #   which need to be set before it's called
    #   then it creates ten outgonig variables to
    #   be grabbed after it closes to be stored in
    #   whatever table they belong in
    #    - cat_script displays text of currently selected script
    #            this is useful for sh scripts with no -h option.
    #    - get_cronable_scripts(script_path) takes path and
    #            returns a list of py or sh scripts in that folder.
    #    - get_help_text(script_to_ask) which takes script location and
    #            returns the helpfile text from the -h output of the script.
    def __init__(self, *args, **kw):
        super(cron_job_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((750, 300))
        self.SetTitle("Cron Job Editor")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        #these need to be set before the dialog is created
        cron_path = cron_info_pnl.cron_path_toedit
        cron_task = cron_info_pnl.cron_task_toedit
        cron_args = cron_info_pnl.cron_args_toedit
        cron_comment = cron_info_pnl.cron_comment_toedit
        cron_type = cron_info_pnl.cron_type_toedit
        cron_everystr = cron_info_pnl.cron_everystr_toedit
        cron_everynum = cron_info_pnl.cron_everynum_toedit
        cron_enabled = cron_info_pnl.cron_enabled_toedit
        cron_min = cron_info_pnl.cron_min_toedit
        cron_hour = cron_info_pnl.cron_hour_toedit
        cron_day = cron_info_pnl.cron_day_toedit
        cron_month = cron_info_pnl.cron_month_toedit
        cron_dow = cron_info_pnl.cron_dow_toedit
        #draw the pannel
         ## universal controls
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Cron job editor', pos=(20, 10))
        cron_type_opts = ['startup', 'repeating', 'one time']
        wx.StaticText(self,  label='cron type;', pos=(165, 10))
        self.cron_type_combo = wx.ComboBox(self, choices = cron_type_opts, pos=(260,10), size=(125, 25))
        self.cron_type_combo.Bind(wx.EVT_COMBOBOX, self.cron_type_combo_go)
        wx.StaticText(self,  label='path;', pos=(10, 50))
        cron_path_opts = ['/home/pi/Pigrow/scripts/cron/', '/home/pi/Pigrow/scripts/autorun/', '/home/pi/Pigrow/scripts/switches/']
        self.cron_path_combo = wx.ComboBox(self, style=wx.TE_PROCESS_ENTER, choices = cron_path_opts, pos=(100,45), size=(525, 30))
        self.cron_path_combo.Bind(wx.EVT_TEXT_ENTER, self.cron_path_combo_go)
        self.cron_path_combo.Bind(wx.EVT_COMBOBOX, self.cron_path_combo_go)
        show_cat_butt = wx.Button(self, label='view script', pos=(625, 75))
        show_cat_butt.Bind(wx.EVT_BUTTON, self.cat_script)
        wx.StaticText(self,  label='Extra args;', pos=(10, 110))
        self.cron_args_tc = wx.TextCtrl(self, pos=(100, 110), size=(525, 25))
        show_help_butt = wx.Button(self, label='show help', pos=(625, 110))
        show_help_butt.Bind(wx.EVT_BUTTON, self.show_help)
        wx.StaticText(self,  label='comment;', pos=(10, 140))
        self.cron_comment_tc = wx.TextCtrl(self, pos=(100, 140), size=(525, 25))
        self.cron_enabled_cb = wx.CheckBox(self,  label='Enabled', pos=(400, 190))
        ### set universal controls data...
        self.cron_type_combo.SetValue(cron_type)
        self.cron_path_combo.SetValue(cron_path)
        self.cron_args_tc.SetValue(cron_args)
        self.cron_comment_tc.SetValue(cron_comment)
        cron_script_opts = self.get_cronable_scripts(cron_path) #send the path of the folder get script list
        self.cron_script_cb = wx.ComboBox(self, choices = cron_script_opts, pos=(25,80), size=(600, 25))
        self.cron_script_cb.SetValue(cron_task)
        self.cron_enabled_cb.SetValue(cron_enabled)
        # draw and hide optional option controlls
        ## for repeating cron jobs
        self.cron_rep_every = wx.StaticText(self,  label='Every ', pos=(60, 190))
        self.cron_every_num_tc = wx.TextCtrl(self, pos=(115, 190), size=(40, 25))  #box for number, name num only range set by repeat_opt
        self.cron_every_num_tc.Bind(wx.EVT_CHAR, self.onChar)
        cron_repeat_opts = ['min', 'hour', 'day', 'month', 'dow']
        self.cron_repeat_opts_cb = wx.ComboBox(self, choices = cron_repeat_opts, pos=(170,190), size=(100, 30))
        self.cron_rep_every.Hide()
        self.cron_every_num_tc.Hide()
        self.cron_repeat_opts_cb.Hide()
        self.cron_repeat_opts_cb.SetValue(cron_everystr)
        self.cron_every_num_tc.SetValue(cron_everynum)
        ## for one time cron jobs
        self.cron_switch = wx.StaticText(self,  label='Time; ', pos=(60, 190))
        self.cron_switch2 = wx.StaticText(self,  label='[min : hour : day : month : day of the week]', pos=(110, 220))
        self.cron_timed_min_tc = wx.TextCtrl(self, pos=(115, 190), size=(40, 25)) #limit to 0-23
        self.cron_timed_min_tc.SetValue(cron_min)
        self.cron_timed_min_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_hour_tc = wx.TextCtrl(self, pos=(160, 190), size=(40, 25)) #limit to 0-59
        self.cron_timed_hour_tc.SetValue(cron_hour)
        self.cron_timed_hour_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_day_tc = wx.TextCtrl(self, pos=(205, 190), size=(40, 25)) #limit to 0-59
        self.cron_timed_day_tc.SetValue(cron_day)
        self.cron_timed_day_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_month_tc = wx.TextCtrl(self, pos=(250, 190), size=(40, 25)) #limit to 0-59
        self.cron_timed_month_tc.SetValue(cron_month)
        self.cron_timed_month_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_dow_tc = wx.TextCtrl(self, pos=(295, 190), size=(40, 25)) #limit to 0-59
        self.cron_timed_dow_tc.SetValue(cron_dow)
        self.cron_timed_dow_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_switch.Hide()
        self.cron_switch2.Hide()
        self.cron_timed_min_tc.Hide()
        self.cron_timed_hour_tc.Hide()
        self.cron_timed_day_tc.Hide()
        self.cron_timed_month_tc.Hide()
        self.cron_timed_dow_tc.Hide()
        self.set_control_visi() #set's the visibility of optional controls
        #Buttom Row of Buttons
        okButton = wx.Button(self, label='Ok', pos=(200, 250))
        closeButton = wx.Button(self, label='Cancel', pos=(300, 250))
        okButton.Bind(wx.EVT_BUTTON, self.do_upload)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def onChar(self, event):
        #this inhibits any non-numeric keys
        key = event.GetKeyCode()
        try: character = chr(key)
        except ValueError: character = "" # arrow keys will throw this error
        acceptable_characters = "1234567890"
        if character in acceptable_characters or key == 13 or key == 314 or key == 316 or key == 8 or key == 127: # 13 = enter, 314 & 316 = arrows, 8 = backspace, 127 = del
            event.Skip()
            return
        else:
            return False

    def cat_script(self, e):
        #opens an ssh pipe and runs a cat command to get the text of the script
        target_ip = pi_link_pnl.target_ip
        target_user = pi_link_pnl.target_user
        target_pass = pi_link_pnl.target_pass
        script_path = self.cron_path_combo.GetValue()
        script_name = self.cron_script_cb.GetValue()
        script_to_ask = script_path + script_name
        try:
        #    ssh.connect(target_ip, username=target_user, password=target_pass, timeout=3)
            print "Connected to " + target_ip
            print("running; cat " + str(script_to_ask))
            stdin, stdout, stderr = ssh.exec_command("cat " + str(script_to_ask))
            script_text = stdout.read().strip()
            error_text = stderr.read().strip()
            if not error_text == '':
                msg_text =  'Error reading script \n\n'
                msg_text += str(error_text)
            else:
                msg_text = script_to_ask + '\n\n'
                msg_text += str(script_text)
            wx.MessageBox(msg_text, 'Info', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            print("oh bother, this seems wrong... " + str(e))

    def get_cronable_scripts(self, script_path):
        #this opens an ssh channel and reads the files in the path provided
        #then creates a list of all .py and .sh scripts in that folder
        cron_opts = []
        try:
            print("reading " + str(script_path))
            stdin, stdout, stderr = ssh.exec_command("ls " + str(script_path))
            cron_dir_list = stdout.read().split('\n')
            for filename in cron_dir_list:
                if filename.endswith("py") or filename.endswith('sh'):
                    cron_opts.append(filename)
        except Exception as e:
            print("aggghhhhh cap'ain something ain't right! " + str(e))
        return cron_opts
    def cron_path_combo_go(self, e):
        cron_path = self.cron_path_combo.GetValue()
        cron_script_opts = self.get_cronable_scripts(cron_path) #send the path of the folder get script list
        self.cron_script_cb.Clear()
        for x in cron_script_opts:
            self.cron_script_cb.Append(x)
    def cron_type_combo_go(self, e):
        self.set_control_visi()
    def set_control_visi(self):
        #checks which type of cron job is set in combobox and shows or hides
        #which ever UI elemetns are required - doesn't lose or change the data.
        cron_type = self.cron_type_combo.GetValue()
        if cron_type == 'one time':
            self.cron_rep_every.Hide()
            self.cron_every_num_tc.Hide()
            self.cron_repeat_opts_cb.Hide()
            self.cron_switch.Show()
            self.cron_switch2.Show()
            self.cron_timed_min_tc.Show()
            self.cron_timed_hour_tc.Show()
            self.cron_timed_day_tc.Show()
            self.cron_timed_month_tc.Show()
            self.cron_timed_dow_tc.Show()
        elif cron_type == 'repeating':
            self.cron_rep_every.Show()
            self.cron_every_num_tc.Show()
            self.cron_repeat_opts_cb.Show()
            self.cron_switch.Hide()
            self.cron_switch2.Hide()
            self.cron_timed_min_tc.Hide()
            self.cron_timed_hour_tc.Hide()
            self.cron_timed_day_tc.Hide()
            self.cron_timed_month_tc.Hide()
            self.cron_timed_dow_tc.Hide()
        elif cron_type == 'startup':
            self.cron_rep_every.Hide()
            self.cron_every_num_tc.Hide()
            self.cron_repeat_opts_cb.Hide()
            self.cron_switch.Hide()
            self.cron_switch2.Hide()
            self.cron_timed_min_tc.Hide()
            self.cron_timed_hour_tc.Hide()
            self.cron_timed_day_tc.Hide()
            self.cron_timed_month_tc.Hide()
            self.cron_timed_dow_tc.Hide()
    def get_help_text(self, script_to_ask):
        #open an ssh pipe and runs the script with a -h argument
        #
        #WARNING
        #       If the script doesn't support -h args then it'll just run it
        #       this can cause switches to throw, photos to be taken or etc
        if script_to_ask.endswith('sh'):
            return ("Sorry, .sh files don't support help arguments, try viewing it instead.")
        try:
            print("reading " + str(script_to_ask))
            stdin, stdout, stderr = ssh.exec_command(str(script_to_ask) + " -h")
            helpfile = stdout.read().strip()
        except Exception as e:
            print("sheee-it something ain't right! " + str(e))
        return helpfile
    def show_help(self, e):
        script_path = self.cron_path_combo.GetValue()
        script_name = self.cron_script_cb.GetValue()
        helpfile = self.get_help_text(str(script_path + script_name))
        msg_text =  script_name + ' \n \n'
        msg_text += str(helpfile)
        wx.MessageBox(msg_text, 'Info', wx.OK | wx.ICON_INFORMATION)
    def do_upload(self, e):
        #get data from boxes
        #   these are the exit variables, they're only set when ok is pushed
        #   this is to stop any dirty old data mixing in with the correct stuff
        self.job_type = self.cron_type_combo.GetValue()
        self.job_path = self.cron_path_combo.GetValue()
        self.job_script = self.cron_script_cb.GetValue()
        self.job_args = self.cron_args_tc.GetValue()
        self.job_comment = self.cron_comment_tc.GetValue()
        self.job_enabled = self.cron_enabled_cb.GetValue()
        self.job_repeat = self.cron_repeat_opts_cb.GetValue()
        self.job_repnum = self.cron_every_num_tc.GetValue()
        self.job_min = self.cron_timed_min_tc.GetValue()
        self.job_hour = self.cron_timed_hour_tc.GetValue()
        self.job_day = self.cron_timed_day_tc.GetValue()
        self.job_month = self.cron_timed_month_tc.GetValue()
        self.job_dow = self.cron_timed_dow_tc.GetValue()
        self.Destroy()
    def OnClose(self, e):
        #set all post-creation flags to zero
        #   this is so that it doesn't ever somehow confuse old dirty data
        #   with new correct data, stuff comes in one side and leaves the other.
        self.job_type = None
        self.job_path = None
        self.job_script = None
        self.job_args = None
        self.job_comment = None
        self.job_enabled = None
        self.job_repeat = None
        self.job_repnum = None
        self.job_min = None
        self.job_hour = None
        self.job_day = None
        self.job_month = None
        self.job_dow = None
        self.Destroy()

#
#
#
## Local Files tab
#
#
#
class localfiles_info_pnl(wx.Panel):
    #
    #  This displays the system info
    # controlled by the system_ctrl_pnl
    #
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        win_width = parent.GetSize()[0]
        w_space_left = win_width - 285
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size(w_space_left , 800), style = wx.TAB_TRAVERSAL )
        #set blank variables
        localfiles_info_pnl.local_path = ""
        ## Draw UI elements
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        # placing the information boxes
        localfiles_info_pnl.local_path_txt = wx.StaticText(self,  label='local path', pos=(220, 80), size=(200,30))
        #local photo storage info
        localfiles_info_pnl.caps_folder = 'caps'
        localfiles_info_pnl.folder_text = wx.StaticText(self,  label=' ' + localfiles_info_pnl.caps_folder, pos=(720, 130), size=(200,30))
        localfiles_info_pnl.photo_text = wx.StaticText(self,  label='photo text', pos=(575, 166), size=(170,30))
        localfiles_info_pnl.first_photo_title = wx.StaticText(self,  label='first image', pos=(575, 290), size=(170,30))
        localfiles_info_pnl.last_photo_title = wx.StaticText(self,  label='last image', pos=(575, 540), size=(170,30))
        #file list boxes
        localfiles_info_pnl.config_files = self.config_file_list(self, 1, pos=(5, 160), size=(550, 200))
        localfiles_info_pnl.config_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_config)
        localfiles_info_pnl.logs_files = self.logs_file_list(self, 1, pos=(5, 390), size=(550, 200))
        localfiles_info_pnl.logs_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_logs)
        #localfiles_info_pnl.config_files = self.config_file_list(self, 1, pos=(5, 160), size=(550, 200))
    #    localfiles_info_pnl.config_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_config)
        #cron info text
        localfiles_info_pnl.cron_info = wx.StaticText(self,  label='cron info', pos=(290, 635), size=(200,30))

    def OnEraseBackground(self, evt):
        # yanked from ColourDB.py #then from https://www.blog.pythonlibrary.org/2010/03/18/wxpython-putting-a-background-image-on-a-panel/
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap("./localfiles.png")
        dc.DrawBitmap(bmp, 0, 0)

    class config_file_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(25, 250), size=(550,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Filename')
            self.InsertColumn(1, 'date modified')
            self.InsertColumn(2, 'age')
            self.InsertColumn(3, 'updated?')
            self.SetColumnWidth(0, 190)
            self.SetColumnWidth(1, 150)
            self.SetColumnWidth(2, 110)
            self.SetColumnWidth(3, 100)

    class logs_file_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(25, 500), size=(550,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Filename')
            self.InsertColumn(1, 'date modified')
            self.InsertColumn(2, 'age')
            self.InsertColumn(3, 'updated?')
            self.SetColumnWidth(0, 190)
            self.SetColumnWidth(1, 150)
            self.SetColumnWidth(2, 110)
            self.SetColumnWidth(3, 100)

    def draw_photo_folder_images(self, first_pic, last_pic):
        # load and display first image
        first = wx.Image(first_pic, wx.BITMAP_TYPE_ANY)
        first = first.Scale(225, 225, wx.IMAGE_QUALITY_HIGH)
        first = first.ConvertToBitmap()
        localfiles_info_pnl.photo_folder_first_pic = wx.StaticBitmap(self, -1, first, (620, 310), (first.GetWidth(), first.GetHeight()))
        # load and display last image
        last = wx.Image(last_pic, wx.BITMAP_TYPE_ANY)
        last = last.Scale(225, 225, wx.IMAGE_QUALITY_HIGH)
        last = last.ConvertToBitmap()
        localfiles_info_pnl.photo_folder_last_pic = wx.StaticBitmap(self, -1, last, (620, 565), (last.GetWidth(), last.GetHeight()))

    def add_to_config_list(self, name, mod_date, age, update_status):
        localfiles_info_pnl.config_files.InsertStringItem(0, str(name))
        localfiles_info_pnl.config_files.SetStringItem(0, 1, str(mod_date))
        localfiles_info_pnl.config_files.SetStringItem(0, 2, str(age))
        localfiles_info_pnl.config_files.SetStringItem(0, 3, str(update_status))

    def add_to_logs_list(self, name, mod_date, age, update_status):
        localfiles_info_pnl.logs_files.InsertStringItem(0, str(name))
        localfiles_info_pnl.logs_files.SetStringItem(0, 1, str(mod_date))
        localfiles_info_pnl.logs_files.SetStringItem(0, 2, str(age))
        localfiles_info_pnl.logs_files.SetStringItem(0, 3, str(update_status))

    def onDoubleClick_config(self, e):
        print("and nothing happens")

    def onDoubleClick_logs(self, e):
        print("and nothing happens")

class localfiles_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        height_of_pannels_above = 230
        space_left = win_height - height_of_pannels_above
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, height_of_pannels_above), size = wx.Size(285, space_left), style = wx.TAB_TRAVERSAL )
        # Start drawing the UI elements
        wx.StaticText(self,  label='Local file and backup options', pos=(25, 10))
        self.update_local_filelist_btn = wx.Button(self, label='Refresh Filelist Info', pos=(15, 60), size=(175, 30))
        self.update_local_filelist_btn.Bind(wx.EVT_BUTTON, self.update_local_filelist_click)
        self.download_btn = wx.Button(self, label='Download files', pos=(15, 95), size=(175, 30))
        self.download_btn.Bind(wx.EVT_BUTTON, self.download_click)
        self.upload_btn = wx.Button(self, label='Restore to pi', pos=(15, 130), size=(175, 30))
        self.upload_btn.Bind(wx.EVT_BUTTON, self.upload_click)

    def run_on_pi(self, command):
        #Runs a command on the pigrow and returns output and error
        #  out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/")
        try:
            stdin, stdout, stderr = ssh.exec_command(command)
            out = stdout.read()
            error = stderr.read()
        except Exception as e:
            error = "failed running command;" + str(command) + " with error - " + str(e)
            print(error)
            return "", error
        return out, error

    def update_local_filelist_click(self, e):
        print("looking for local files.")
        # clear lists
        localfiles_info_pnl.config_files.DeleteAllItems()
        localfiles_info_pnl.logs_files.DeleteAllItems()
        # create local folder path
        if not MainApp.OS == "Windows":
            localfiles_info_pnl.local_path = MainApp.localfiles_path + str(pi_link_pnl.boxname) + "/"
        else:
            localfiles_info_pnl.local_path = MainApp.localfiles_path + str(pi_link_pnl.boxname) + "\\"
        localfiles_info_pnl.local_path_txt.SetLabel("\n" + localfiles_info_pnl.local_path)
        # check for data and sort into on screen lists
        if not os.path.isdir(localfiles_info_pnl.local_path):
            localfiles_info_pnl.local_path_txt.SetLabel("no local data, press download to create folder \n " + localfiles_info_pnl.local_path)
        else:
            local_files = os.listdir(localfiles_info_pnl.local_path)
            #set caps folder
            localfiles_info_pnl.folder_text.SetLabel(localfiles_info_pnl.caps_folder)
            #define empty lists
            folder_list = []
            #read all the folders in the pigrows local folder
            for item in local_files:
                if os.path.isdir(localfiles_info_pnl.local_path + item) == True:
                    folder_files = os.listdir(localfiles_info_pnl.local_path + item)
                    counter = 0
                    for thing in folder_files:
                        counter = counter + 1
                    folder_list.append([item, counter])
                    #add local config files to list and generate info
                    if item == "config":
                        config_list = []
                        config_files = os.listdir(localfiles_info_pnl.local_path + item)
                        for thing in config_files:
                            if thing.endswith("txt"):
                                modified = os.path.getmtime(localfiles_info_pnl.local_path + item + "/" + thing)
                                #config_list.append([thing, modified])
                                modified = datetime.datetime.fromtimestamp(modified)
                                file_age = datetime.datetime.now() - modified
                                modified = modified.strftime("%Y-%m-%d %H:%M")
                                file_age = str(file_age).split(".")[0]
                                update_status = "unchecked"
                                localfiles_info_pnl.add_to_config_list(MainApp.localfiles_info_pannel, thing, modified, file_age, update_status)
                    if item == "logs":
                        logs_list = []
                        logs_files = os.listdir(localfiles_info_pnl.local_path + item)
                        for thing in logs_files:
                            if thing.endswith("txt"):
                                modified = os.path.getmtime(localfiles_info_pnl.local_path + item + "/" + thing)
                                modified = datetime.datetime.fromtimestamp(modified)
                                file_age = datetime.datetime.now() - modified
                                modified = modified.strftime("%Y-%m-%d %H:%M")
                                file_age = str(file_age).split(".")[0]
                                update_status = "unchecked"
                                localfiles_info_pnl.add_to_logs_list(MainApp.localfiles_info_pannel, thing, modified, file_age, update_status)
                    #read caps info and make report
                    if item == localfiles_info_pnl.caps_folder:
                        caps_files = os.listdir(localfiles_info_pnl.local_path + item)
                        caps_files.sort()
                        caps_message = str(len(caps_files)) + " files locally \n"
                        #read pi's caps folder
                        try:
                            stdin, stdout, stderr = ssh.exec_command("ls /home/" + pi_link_pnl.target_user + "/Pigrow/" + localfiles_info_pnl.caps_folder)
                            remote_caps = stdout.read().splitlines()
                        except Exception as e:
                            print("reading remote caps folder failed; " + str(e))
                            remote_caps = []
                        if len(caps_files) > 1:
                            #lable first and last image with name
                            localfiles_info_pnl.first_photo_title.SetLabel(caps_files[0])
                            localfiles_info_pnl.last_photo_title .SetLabel(caps_files[-1])
                            #determine date range of images
                            first_date, first_dt = self.filename_to_date(caps_files[0])
                            last_date, last_dt = self.filename_to_date(caps_files[-1])
                            caps_message += "  " + str(first_date) + " - " + str(last_date)
                            length_of_local = last_dt - first_dt
                            caps_message += '\n     ' + str(length_of_local)
                            #draw first and last imagess to the screen
                            localfiles_info_pnl.draw_photo_folder_images(MainApp.localfiles_info_pannel, localfiles_info_pnl.local_path + item + "/" + caps_files[0], localfiles_info_pnl.local_path + item + "/" + caps_files[-1])
                        caps_message += "\n" + str(len(remote_caps)) + " files on Pigrow \n"
                        if len(remote_caps) > 1:
                            first_remote, first_r_dt = self.filename_to_date(remote_caps[0])
                            last_remote, last_r_dt = self.filename_to_date(remote_caps[-1])
                            caps_message += "  " + str(first_remote) + " - " + str(last_remote)
                            length_of_remote = last_r_dt - first_r_dt
                            caps_message += '\n     ' + str(length_of_remote)
                        else:
                            caps_message += " "

                        #update the caps info pannel with caps message
                        localfiles_info_pnl.photo_text.SetLabel(caps_message)


                    # check to see if crontab is saved locally
                    localfiles_ctrl_pnl.cron_backup_file = localfiles_info_pnl.local_path + "crontab_backup.txt"
                    if os.path.isfile(localfiles_ctrl_pnl.cron_backup_file) == True:
                        #checks time of local crontab_backup and determines age
                        modified = os.path.getmtime(localfiles_ctrl_pnl.cron_backup_file)
                        modified = datetime.datetime.fromtimestamp(modified)
                        file_age = datetime.datetime.now() - modified
                        modified = modified.strftime("%Y-%m-%d %H:%M")
                        file_age = str(file_age).split(".")[0]
                        #checks to see if local and remote files are the same
                        remote_cron_text, error = MainApp.localfiles_ctrl_pannel.run_on_pi("crontab -l")
                        #read local file
                        with open(localfiles_ctrl_pnl.cron_backup_file, "r") as local_cron:
                            local_cron_text = local_cron.read()
                        #compare the two files
                        if remote_cron_text == local_cron_text:
                            updated = True
                        else:
                            updated = False
                        cron_msg = "local cron file last updated\n    " + modified + "\n    " + file_age + " ago,\n  \n\n identical to pi version: " + str(updated)
                        localfiles_info_pnl.cron_info.SetLabel(cron_msg)
                    else:
                        localfiles_info_pnl.cron_info.SetLabel("no local cron file")
                    ## output
        print("local file info discovered..")

    def filename_to_date(self, filename):
        date = float(filename.split(".")[0].split("_")[-1])
        file_datetime = datetime.datetime.fromtimestamp(date)
        date = time.strftime('%Y-%m-%d %H:%M', time.localtime(date))
        return date, file_datetime

    def download_click(self, e):
        #show download dialog boxes
        file_dbox = file_download_dialog(None, title='Download dialog box')
        file_dbox.ShowModal()
        self.update_local_filelist_click("e")

    def upload_click(self, e):
        upload_dbox = upload_dialog(None, title='Upload dialog box')
        upload_dbox.ShowModal()
        self.update_local_filelist_click("e")

class file_download_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, *args, **kw):
        super(file_download_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 300))
        self.SetTitle("Download files from Pigrow")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        #draw the pannel
        wx.StaticText(self,  label='Select elements to download to local storage', pos=(30, 5))
        self.cb_conf = wx.CheckBox(self, label='Config',pos = (80,30))
        self.cb_logs = wx.CheckBox(self, label='Logs',pos = (80,55))
        self.cb_cron = wx.CheckBox(self, label='Crontab',pos = (80,80))
        self.cb_pics = wx.CheckBox(self, label='Photos',pos = (80,105))
        self.cb_graph = wx.CheckBox(self, label='Graphs',pos = (80,130))
        #right side
        self.cb_all = wx.CheckBox(self, label='Back up\nWhole Pigrow Folder',pos = (270,75))
        #progress bar
        wx.StaticText(self,  label='saving to; '+ localfiles_info_pnl.local_path, pos=(15, 155))
        self.current_file_txt = wx.StaticText(self,  label='--', pos=(30, 190))
        self.current_dest_txt = wx.StaticText(self,  label='--', pos=(30, 215))
        #buttons
        self.start_download_btn = wx.Button(self, label='Download files', pos=(40, 240), size=(175, 50))
        self.start_download_btn.Bind(wx.EVT_BUTTON, self.start_download_click)
        self.close_btn = wx.Button(self, label='Close', pos=(415, 240), size=(175, 50))
        self.close_btn.Bind(wx.EVT_BUTTON, self.OnClose)
         ## universal controls
        pnl = wx.Panel(self)

    def start_download_click(self, e):
        #make folder if it doesn't exist
        if not os.path.isdir(localfiles_info_pnl.local_path):
            os.makedirs(localfiles_info_pnl.local_path)
        #make empty lists
        files_to_download = []
        # downloading cron file and saving it as a local backup
        if self.cb_cron.GetValue() == True:
            print("including crontab file")
            try:
                stdin, stdout, stderr = ssh.exec_command("crontab -l")
                cron_text = stdout.read()
            except Exception as e:
                print("failed to read cron due to;" + str(e))
            with open(localfiles_ctrl_pnl.cron_backup_file, "w") as file_to_save:
                file_to_save.write(cron_text)
        ## Downloading files from the pi
        # connecting the sftp pipe
        port = 22
        ssh_tran = paramiko.Transport((pi_link_pnl.target_ip, port))
        print("  - connecting transport pipe... " + pi_link_pnl.target_ip + " port:" + str(port))
        ssh_tran.connect(username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass)
        self.sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        # creating a list of files to be download from the pigrow
        if self.cb_all.GetValue() == False:
        # make list using selected components to be downloaded, list contains two elemnts [remote file, local destination]
            if self.cb_conf.GetValue() == True:
                local_config = localfiles_info_pnl.local_path + "config/"
                if not os.path.isdir(local_config):
                    os.makedirs(local_config)
                target_config_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/config/"
                remote_config = self.sftp.listdir(target_config_files)
                for item in remote_config:
                    files_to_download.append([target_config_files + item, local_config + item])
            if self.cb_logs.GetValue() == True:
                local_logs = localfiles_info_pnl.local_path + "logs/"
                if not os.path.isdir(local_logs):
                    os.makedirs(local_logs)
                target_logs_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/logs/"
                remote_logs = self.sftp.listdir(target_logs_files)
                for item in remote_logs:
                    files_to_download.append([target_logs_files + item, local_logs + item])
            if self.cb_pics.GetValue() == True:
                caps_folder = localfiles_info_pnl.caps_folder
                local_pics = localfiles_info_pnl.local_path + caps_folder + "/"
                if not os.path.isdir(local_pics):
                    os.makedirs(local_pics)
                #get list of pics we already have
                listofcaps_local = os.listdir(local_pics)
                #get list of remote images
                target_caps_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/" + caps_folder + "/"
                try:
                    remote_caps = self.sftp.listdir(target_caps_files)
                except IOError as e:
                    if "No such file" in str(e):
                        remote_caps = []
                    else:
                        print("Error downloadig files - " + str(e))
                for item in remote_caps:
                    if item not in listofcaps_local:
                        files_to_download.append([target_caps_files + item, local_pics + item])
            if self.cb_graph.GetValue() == True:
                target_graph_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/graphs/"
                local_graphs = localfiles_info_pnl.local_path + "graphs/"
                if not os.path.isdir(local_graphs):
                    os.makedirs(local_graphs)
                try:
                    remote_graphs = self.sftp.listdir(target_graph_files)
                except IOError as e:
                    if "No such file" in str(e):
                        remote_graphs = []
                    else:
                        print("Error downloadig files - " + str(e))
                for item in remote_graphs:
                    files_to_download.append([target_graph_files + item, local_graphs + item])
        else:
            # this is when the backup checkbox is ticked
            folder_name = "/Pigrow" #start with / but don't end with one.
            target_folder = "/home/" + str(pi_link_pnl.target_user) + folder_name
            local_folder = localfiles_info_pnl.local_path + "backup"
            if not os.path.isdir(local_folder):
                os.makedirs(local_folder)
            folders, files = self.sort_folder_for_folders(target_folder)
            while len(folders) > 0:
                if not ".git" in folders[0]:
                    new_folders, new_files = self.sort_folder_for_folders(folders[0])
                    files = files + new_files
                    folders = folders + new_folders
                    new_folder = local_folder + "/" + folders[0].split(folder_name + "/")[1]
                    print new_folder
                    if not os.path.isdir(new_folder):
                        os.makedirs(new_folder)
                folders = folders[1:]

            for item in files:
                filename = item[len(target_folder):]
                files_to_download.append([item, local_folder + filename])
            #
            print("downloading entire pigrow folder")
        # Work though the list of files to download
        print("downloading; " + str(len(files_to_download)))
        for remote_file in files_to_download:
            #grabs all files in the list and overwrites them if they already exist locally.
            self.current_file_txt.SetLabel("from; " + remote_file[0])
            self.current_dest_txt.SetLabel("to; " + remote_file[1])
            wx.Yield() #update screen to show changes
            self.sftp.get(remote_file[0], remote_file[1])
        self.current_file_txt.SetLabel("Done")
        self.current_dest_txt.SetLabel("Downloaded " + str(len(files_to_download)) + " files")
        #disconnect the sftp pipe
        self.sftp.close()
        ssh_tran.close()

    def sort_folder_for_folders(self, target_folder):
        folders = []
        files = []
        for f in self.sftp.listdir_attr(target_folder):
            if S_ISDIR(f.st_mode):
                folders.append(str(target_folder + '/' + f.filename))
            else:
                files.append(str(target_folder + '/' + f.filename))
        return folders, files

    def OnClose(self, e):
        #closes the dialogue box
        self.Destroy()

class upload_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, *args, **kw):
        super(upload_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 355))
        self.SetTitle("upload files to Pigrow")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        #draw the pannel
        wx.StaticText(self,  label='Select elements to upload from local storage to pi\n\n   ** Warning this will overwrite current pigrow files \n                          which may result in loss of data **', pos=(30, 5))
        self.cb_conf = wx.CheckBox(self, label='Config',pos = (80,90))
        self.cb_logs = wx.CheckBox(self, label='Logs',pos = (80,115))
        self.cb_cron = wx.CheckBox(self, label='Crontab',pos = (80,140))
        self.cb_pics = wx.CheckBox(self, label='Photos',pos = (80,165))
        self.cb_graph = wx.CheckBox(self, label='Graphs',pos = (80,190))
        #right side
        self.cb_all = wx.CheckBox(self, label='Restore Back up\nof whole Pigrow Folder',pos = (270,130))
        #progress bar
        wx.StaticText(self,  label='uploading from; '+ localfiles_info_pnl.local_path, pos=(15, 215))
        self.current_file_txt = wx.StaticText(self,  label='--', pos=(30, 245))
        self.current_dest_txt = wx.StaticText(self,  label='--', pos=(30, 270))
        #buttons
        self.start_upload_btn = wx.Button(self, label='Upload files', pos=(40, 300), size=(175, 50))
        self.start_upload_btn.Bind(wx.EVT_BUTTON, self.start_upload_click)
        self.close_btn = wx.Button(self, label='Close', pos=(415, 300), size=(175, 50))
        self.close_btn.Bind(wx.EVT_BUTTON, self.OnClose)
         ## universal controls
        pnl = wx.Panel(self)

    def start_upload_click(self, e):
        files_to_upload  = []
        ## connecting the sftp pipe
        port = 22
        ssh_tran = paramiko.Transport((pi_link_pnl.target_ip, port))
        print("  - connecting transport pipe... " + pi_link_pnl.target_ip + " port:" + str(port))
        ssh_tran.connect(username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass)
        sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        ## Downloading files from the pi
        # creating a list of files to be download from the pigrow
        if self.cb_all.GetValue() == False:
            # uploading and installing cron file
            temp_folder = "/home/" + pi_link_pnl.target_user + "/Pigrow/temp/"
            cron_temp = temp_folder + "cron.txt"
            if self.cb_cron.GetValue() == True:
                print("including crontab file")
                #upload cronfile to temp folder
                try:
                    sftp.put(localfiles_ctrl_pnl.cron_backup_file, cron_temp)
                except IOError:
                    sftp.mkdir(temp_folder)
                    sftp.put(localfiles_ctrl_pnl.cron_backup_file, cron_temp)
                self.current_file_txt.SetLabel("from; " + localfiles_ctrl_pnl.cron_backup_file)
                self.current_dest_txt.SetLabel("to; " + cron_temp)
                wx.Yield()
                try:
                    stdin, stdout, stderr = ssh.exec_command("crontab " + cron_temp)
                except Exception as e:
                    print("failed to read cron due to;" + str(e))
        # make list using selected components to be uploaded, list contains two elemnts [local file, remote destination]
            if self.cb_conf.GetValue() == True:
                local_config = localfiles_info_pnl.local_path + "config/"
                target_config = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/config/"
                local_config_files = os.listdir(local_config)
                for item in local_config_files:
                    files_to_upload.append([local_config + item, target_config + item])
            #do the same for the logs folder
            if self.cb_logs.GetValue() == True:
                local_logs = localfiles_info_pnl.local_path + "logs/"
                target_logs = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/logs/"
                target_logs_files = os.listdir(local_logs)
                for item in target_logs_files:
                    files_to_upload.append([local_logs + item, target_logs + item])
            #and the graphs folder
            if self.cb_graph.GetValue() == True:
                local_graphs = localfiles_info_pnl.local_path + "graphs/"
                target_graphs = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/graphs/"
                local_graph_files = os.listdir(local_graphs)
                for item in local_graph_files:
                    files_to_upload.append([local_graphs + item, target_graphs + item])
            ## for photos only upload photos that don't already exost on pi
            if self.cb_pics.GetValue() == True:
                caps_folder = localfiles_info_pnl.caps_folder
                local_pics = localfiles_info_pnl.local_path + caps_folder + "/"
                #get list of pics we already have
                listofcaps_local = os.listdir(local_pics)
                #get list of remote images
                target_caps_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/" + caps_folder + "/"
                remote_caps = sftp.listdir(target_caps_files)
                for item in listofcaps_local:
                    if item not in remote_caps:
                        files_to_upload.append([local_pics + item, target_caps_files + item])
        else:
            # make list of all ~/Pigrow/ files using os.walk
            #    - this is for complete backups ignoring the file system.
            print("restoring entire pigrow folder (not yet implimented)")
        print files_to_upload
        print(len(files_to_upload))
        for upload_file in files_to_upload:
            #grabs all files in the list and overwrites them if they already exist locally.
            self.current_file_txt.SetLabel("from; " + upload_file[0])
            self.current_dest_txt.SetLabel("to; " + upload_file[1])
            wx.Yield()
            sftp.put(upload_file[0], upload_file[1])
        self.current_file_txt.SetLabel("Done")
        self.current_dest_txt.SetLabel("--")
        #disconnect the sftp pipe
        sftp.close()
        ssh_tran.close()


    def OnClose(self, e):
        #closes the dialogue box
        self.Destroy()

#
#
#
## Graphing Tab
#
#
#

class graphing_info_pnl(wx.Panel):
    #
    #  This displays the graphing info
    # controlled by the graphing_ctrl_pnl
    #
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        win_width = parent.GetSize()[0]
        w_space_left = win_width - 285
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size(w_space_left , 800), style = wx.TAB_TRAVERSAL )
        ## Draw UI elements
        # placing the information boxes
        localfiles_info_pnl.local_path_txt = wx.StaticText(self,  label='graphs graphs graphs!', pos=(220, 80), size=(200,30))


class graphing_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        height_of_pannels_above = 230
        space_left = win_height - height_of_pannels_above
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, pos=(0, height_of_pannels_above), size=wx.Size(285, space_left), style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour('sea green') #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        # Start drawing the UI elements
        #graphing engine selection
        wx.StaticText(self,  label='Make graphs on;', pos=(15, 10))
        graph_opts = ['Pigrow', 'local']
        self.graph_cb = wx.ComboBox(self, choices = graph_opts, pos=(10,30), size=(265, 30))
        self.graph_cb.Bind(wx.EVT_COMBOBOX, self.graph_engine_combo_go)
        # shared buttons
        self.make_graph_btn = wx.Button(self, label='Make Graph', pos=(15, 520), size=(175, 30))
        self.make_graph_btn.Bind(wx.EVT_BUTTON, self.make_graph_click)
        #
        ### for pi based graphing only
        self.pigraph_text = wx.StaticText(self,  label='Graphing directly on the pigrow\n saves having to download logs', pos=(15, 70))
        # select graphing script
        self.script_text = wx.StaticText(self,  label='Graphing Script;', pos=(15, 130))
        select_script_opts = ['BLANK']
        self.select_script_cb = wx.ComboBox(self, choices = select_script_opts, pos=(10,150), size=(265, 30))
        self.select_script_cb.Bind(wx.EVT_COMBOBOX, self.select_script_combo_go)
        script_opts_opts = ['BLANK']
        self.opts_cb = wx.ComboBox(self, choices = script_opts_opts, pos=(10,230), size=(195, 30))
        self.opts_cb.Bind(wx.EVT_COMBOBOX, self.opt_combo_go)
        # list box for of graphing options
        self.get_opts_tb = wx.CheckBox(self, label='Get Options', pos = (10,180))
        self.get_opts_tb.Bind(wx.EVT_CHECKBOX, self.get_opts_click)
        # various ui elements for differing options value sets - text, list
        self.opts_text = wx.TextCtrl(self,  pos=(2, 265), size=(265,30))
        command_line_opts_value_list = ['BLANK']
        self.command_line_opts_value_list_cb = wx.ComboBox(self, choices = command_line_opts_value_list, pos=(2,265), size=(265, 30))
        # button to add arg to string
        self.add_arg_btn = wx.Button(self, label='Add to command line', pos=(20, 310), size=(175, 30))
        self.add_arg_btn.Bind(wx.EVT_BUTTON, self.add_arg_click)

        # extra arguments string
        self.extra_args = wx.TextCtrl(self,  pos=(2, 450), size=(265,30))
        # hideing all pigrow graphing UI elements until graph on pigrow is selected
        self.pigraph_text.Hide()
        self.script_text.Hide()
        self.select_script_cb.Hide()
        self.get_opts_tb.Hide()
        self.opts_cb.Hide()
        self.opts_text.Hide()
        self.command_line_opts_value_list_cb.Hide()
        self.add_arg_btn.Hide()

    def get_opts_click(self, e):
        #turns on UI elements for automatically found script options
        #then asks get_script_options to ask the script on the pi to list flags
        if self.get_opts_tb.IsChecked():
            print("fetching scripts options, warning script must know how to respond to -flags argument")
            self.opts_cb.Show()
            self.add_arg_btn.Show()
            wx.Yield()
            if not self.select_script_cb.GetValue() == "":
                self.get_script_options()
        else:
            self.blank_options_ui_elements()

    def get_script_options(self):
        #runs the script on the raspberry pi and adds all detected flags to
        #the command line options combo box (self.opts_cb)
        #also a dictionary of all the commands and their defaults or options (self.options_dict)
        scriptpath = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/visualisation/" + self.select_script_cb.GetValue()
        print("Fetching options for; " + scriptpath)
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(scriptpath + " -flags")
        flags = out.splitlines()
        self.opts_cb.Clear()
        self.options_dict={}
        try:
            for opt in flags:
                if "=" in opt:
                    optpair = opt.split("=")
                    optkey = optpair[0]
                    optval = optpair[1]
                    self.opts_cb.Append(optkey)
                    self.options_dict[optkey]=optval

        except:
            self.blank_options_ui_elements()
        if self.opts_cb.GetCount() < 1:
            self.blank_options_ui_elements()

    def blank_options_ui_elements(self):
        #hides UI elements for auto-discovered command line arguments.
        self.opts_cb.Hide()
        self.opts_cb.SetValue("")
        self.opts_text.Hide()
        self.opts_text.SetValue("")
        self.command_line_opts_value_list_cb.Hide()
        self.command_line_opts_value_list_cb.SetValue("")
        self.add_arg_btn.Hide()

    def opt_combo_go(self, e):
        #selects which UI elements to show for command line option values and defaults
        #attempts to parse command line string into list or text
        self.opts_text.Hide()
        option = self.opts_cb.GetValue()
        value_text = str(self.options_dict[option])
        if "[" in value_text and "]" in value_text:
            value_text = value_text.split("[")[1]
            value_text = value_text.split("]")[0]
            value_text = value_text.split(",")
            self.opts_text.Hide()
            self.opts_text.SetValue("")
            self.command_line_opts_value_list_cb.Clear()
            self.command_line_opts_value_list_cb.SetValue("")
            self.command_line_opts_value_list_cb.Show()
            for item in value_text:
                self.command_line_opts_value_list_cb.Append(item)
        else:
            self.command_line_opts_value_list_cb.Hide()
            self.command_line_opts_value_list_cb.SetValue("")
            self.command_line_opts_value_list_cb.Clear()
            self.opts_text.Show()
            self.opts_text.SetValue(value_text)

    def add_arg_click(self, e):
        #reads the user selected option from the two text boxes then
        #adds it to the end of the existing command line arguments text
        argkey = self.opts_cb.GetValue()
        if not self.command_line_opts_value_list_cb.GetCount() > 0:
            argval = self.opts_text.GetValue()
        else:
            argval = self.command_line_opts_value_list_cb.GetValue()
        argval = argval.replace(" ", "_")
        argstring = argkey + "=" + argval
        existing_args = self.extra_args.GetValue()
        self.extra_args.SetValue(existing_args + " " + argstring)

    def get_graphing_scripts(self):
        # checks the pigrows visualisation folder for graphing scripts and adds to list
        print("getting graphing scripts")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/scripts/visualisation")
        vis_list = out.split("\n")
        graph_opts = []
        for filename in vis_list:
            if filename.endswith("py") or filename.endswith('sh'):
                graph_opts.append(filename)
        return graph_opts

    def make_graph_click(self, e):
        # currently asks the pi to make the graph using the options supplied
        # will be upgraded to run graphing modules locally at some point if that options selected instead
        script_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/visualisation/" + self.select_script_cb.GetValue()
        script_command = script_path + " " + self.extra_args.GetValue()
        print("Running; " + script_command)
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(script_command)
        msg = str(out) + " " + str(error)
        dmsg = "Script Output;\n"# + msg.replace("...", ",")
        for line in msg.splitlines():  #this is a hacky way of removing nonsence
            pos = line.find("...")     #from the output which breaks the dialog box
            if pos > 0:                    #stops line at an ... which avoids displaying
                line = line[:pos]      #bad log info as this is often gibberish
            dmsg += line + "\n"        #which would otherwise disrupt the messagebox
        wx.MessageBox(dmsg, 'Script Output', wx.OK | wx.ICON_INFORMATION)
        print dmsg

    def graph_engine_combo_go(self, e):
        # combo box selects if you want to make graphs on pi or locally
        # then shows the relevent UI elements for that option.
        graph_mode = self.graph_cb.GetValue()
        if graph_mode == 'Pigrow':
            select_script_opts = self.get_graphing_scripts()
            self.pigraph_text.Show()
            self.script_text.Show()
            self.select_script_cb.Show()
            self.select_script_cb.Clear()
            for x in select_script_opts:
                self.select_script_cb.Append(x)
            self.get_opts_tb.Show()
        if graph_mode == 'local':
            self.pigraph_text.Hide()
            self.script_text.Hide()
            self.select_script_cb.Hide()
            self.get_opts_tb.Hide()
            print("Yah, that's not really an option yet...")

    def select_script_combo_go(self, e):
        #this is the same as pressing the button to enable asking the script
        #to send a list of -flags.
        self.opts_cb.SetValue("")
        self.opts_text.SetValue("")
        self.command_line_opts_value_list_cb.SetValue("")
        self.get_opts_click("fake event")
        #graphing_script = self.select_script_cb.GetValue()
        #print graphing_script


#
#
## gui control pannels - network link, tab select bar, splash screen
#
#
class pi_link_pnl(wx.Panel):
    #
    # Creates the pannel with the raspberry pi data in it
    # and connects ssh to the pi when button is pressed
    # or allows seeking
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0,0), size = wx.Size( 285,190 ), style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,230,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        pi_link_pnl.target_ip = ''
        pi_link_pnl.target_user = ''
        pi_link_pnl.target_pass = ''
        pi_link_pnl.config_location_on_pi = '/home/pi/Pigrow/config/pigrow_config.txt'
     ## the three boxes for pi's connection details, IP, Username and Password
        self.l_ip = wx.StaticText(self,  label='address', pos=(10, 20))
        self.tb_ip = wx.TextCtrl(self, pos=(125, 25), size=(150, 25))
        self.tb_ip.SetValue("192.168.1.")
        self.l_user = wx.StaticText(self,  label='Username', pos=(10, 60))
        self.tb_user = wx.TextCtrl(self, pos=(125, 60), size=(150, 25))
        self.tb_user.SetValue("pi")
        self.l_pass = wx.StaticText(self,  label='Password', pos=(10, 95))
        self.tb_pass = wx.TextCtrl(self, pos=(125, 95), size=(150, 25))
        self.tb_pass.SetValue("raspberry")
     ## link with pi button
        self.link_with_pi_btn = wx.Button(self, label='Link to Pi', pos=(10, 125), size=(175, 30))
        self.link_with_pi_btn.Bind(wx.EVT_BUTTON, self.link_with_pi_btn_click)
        self.link_status_text = wx.StaticText(self,  label='-- no link --', pos=(25, 160))
     ## seek next pi button
        self.seek_for_pigrows_btn = wx.Button(self, label='Seek next', pos=(190,125))
        self.seek_for_pigrows_btn.Bind(wx.EVT_BUTTON, self.seek_for_pigrows_click)
    def __del__(self):
        print("psssst it did that thing, the _del_ one you like so much...")
        pass

    def seek_for_pigrows_click(self, e):
        print("seeking for pigrows...")
        number_of_tries_per_host = 1
        pi_link_pnl.target_ip = self.tb_ip.GetValue()
        pi_link_pnl.target_user = self.tb_user.GetValue()
        pi_link_pnl.target_pass = self.tb_pass.GetValue()
        if pi_link_pnl.target_ip.split(".")[3] == '':
            pi_link_pnl.target_ip = pi_link_pnl.target_ip + '0'
        start_from = pi_link_pnl.target_ip.split(".")[3]
        lastdigits = len(str(start_from))
        hostrange = pi_link_pnl.target_ip[:-lastdigits]
        #Iterate through the ip_to_test and stop when  pigrow is found
        for ip_to_test in range(int(start_from)+1,255):
            host = hostrange + str(ip_to_test)
            pi_link_pnl.target_ip = self.tb_ip.SetValue(host)
            seek_attempt = 1
            log_on_test = False
            while True:
                print("Trying to connect to " + host)
                try:
                    ssh.connect(host, username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass, timeout=3)
                    print("Connected to " + host)
                    log_on_test = True
                    box_name = self.get_box_name()
                    print("Pigrow Found; " + str(box_name))
                    self.set_link_pi_text(log_on_test, box_name)
                    return box_name #this just exits the loop
                except paramiko.AuthenticationException:
                    print("Authentication failed when connecting to " + str(host))
                except Exception as e:
                    print("Could not SSH to " + host + " because:" + str(e))
                    seek_attempt += 1
                # check if final attempt and if so stop trying
                if seek_attempt == number_of_tries_per_host + 1:
                    print("Could not connect to " + host + " Giving up")
                    break #end while loop and look at next host

    def link_with_pi_btn_click(self, e):
        log_on_test = False
        if self.link_with_pi_btn.GetLabel() == 'Disconnect':
            print("breaking ssh connection")
            ssh.close()
            self.link_with_pi_btn.SetLabel('Link to Pi')
            self.tb_ip.Enable()
            self.tb_user.Enable()
            self.tb_pass.Enable()
            self.link_status_text.SetLabel("-- Disconnected --")
            self.seek_for_pigrows_btn.Enable()
            self.blank_settings()
            MainApp.welcome_pannel.Show()
        else:
            #clear_temp_folder()
            pi_link_pnl.target_ip = self.tb_ip.GetValue()
            pi_link_pnl.target_user = self.tb_user.GetValue()
            pi_link_pnl.target_pass = self.tb_pass.GetValue()
            try:
                ssh.connect(pi_link_pnl.target_ip, username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass, timeout=3)
                print("Connected to " + pi_link_pnl.target_ip)
                log_on_test = True
            except Exception as e:
                print("Failed to log on due to; " + str(e))
            if log_on_test == True:
                box_name = self.get_box_name()
            else:
                box_name = None
            self.set_link_pi_text(log_on_test, box_name)


    def blank_settings(self):
        print("clearing settings")
        # clear system pannel text
        system_info_pnl.sys_hdd_total.SetLabel("")
        system_info_pnl.sys_hdd_remain.SetLabel("")
        system_info_pnl.sys_hdd_used.SetLabel("")
        system_info_pnl.sys_pigrow_folder.SetLabel("")
        system_info_pnl.sys_os_name.SetLabel("")
        #system_info_pnl.sys_pigrow_version.SetLabel("")
        system_info_pnl.sys_pigrow_update.SetLabel("")
        system_info_pnl.sys_network_name.SetLabel("")
        system_info_pnl.wifi_list.SetLabel("")
        system_info_pnl.sys_power_status.SetLabel("")
        system_info_pnl.sys_camera_info.SetLabel("")
        system_info_pnl.sys_pi_revision.SetLabel("")
        system_info_pnl.sys_pi_date.SetLabel("")
        system_info_pnl.sys_pc_date.SetLabel("")
        #system_info_pnl.sys_time_diff.SetLabel("")
        # clear config ctrl text and tables
        try:
            MainApp.config_ctrl_pannel.dirlocs_dict.clear()
            MainApp.config_ctrl_pannel.config_dict.clear()
            MainApp.config_ctrl_pannel.gpio_dict.clear()
            MainApp.config_ctrl_pannel.gpio_on_dict.clear()
        except:
            pass
        MainApp.config_info_pannel.gpio_table.DeleteAllItems()
        config_info_pnl.boxname_text.SetValue("")
        config_info_pnl.location_text.SetLabel("")
        config_info_pnl.config_text.SetLabel("")
        config_info_pnl.lamp_text.SetLabel("")
        config_info_pnl.dht_text.SetLabel("")
        # clear cron tables
        cron_list_pnl.startup_cron.DeleteAllItems()
        cron_list_pnl.repeat_cron.DeleteAllItems()
        cron_list_pnl.timed_cron.DeleteAllItems()
        # clear local files text and images
        localfiles_info_pnl.cron_info.SetLabel("")
        localfiles_info_pnl.local_path_txt.SetLabel("")
        localfiles_info_pnl.folder_text.SetLabel("") ## check this updates on reconnect
        localfiles_info_pnl.photo_text.SetLabel("")
        localfiles_info_pnl.first_photo_title.SetLabel("")
        localfiles_info_pnl.last_photo_title.SetLabel("")

        blank = wx.EmptyBitmap(220, 220)
        try:
            localfiles_info_pnl.photo_folder_first_pic.SetBitmap(blank)
            localfiles_info_pnl.photo_folder_last_pic.SetBitmap(blank)
        except:
            pass
        # clear local file info
        localfiles_info_pnl.local_path = ""
        localfiles_info_pnl.config_files.DeleteAllItems()
        localfiles_info_pnl.logs_files.DeleteAllItems()

    def set_link_pi_text(self, log_on_test, box_name):
        pi_link_pnl.boxname = box_name  #to maintain persistance if needed elsewhere later
        if not box_name == None:
            self.link_status_text.SetLabel("linked with - " + str(pi_link_pnl.boxname))
            MainApp.welcome_pannel.Hide()
            MainApp.config_ctrl_pannel.Show()
            MainApp.config_info_pannel.Show()
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.tb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()
            cron_info_pnl.read_cron_click(MainApp.cron_info_pannel, "event")
            system_ctrl_pnl.read_system_click(MainApp.system_ctrl_pannel, "event")
            config_ctrl_pnl.update_config_click(MainApp.config_ctrl_pannel, "event")
            localfiles_ctrl_pnl.update_local_filelist_click(MainApp.localfiles_ctrl_pannel, "event")

        elif log_on_test == False:
            self.link_status_text.SetLabel("unable to connect")
            ssh.close()
        if log_on_test == True and box_name == None:
            self.link_status_text.SetLabel("No Pigrow config file")
            MainApp.welcome_pannel.Hide()
            MainApp.system_ctrl_pannel.Show()
            MainApp.system_info_pannel.Show()
            system_ctrl_pnl.read_system_click(MainApp.system_ctrl_pannel, "event")
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.tb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()

    def get_box_name(self):
        boxname = None
        try:
            stdin, stdout, stderr = ssh.exec_command("cat /home/pi/Pigrow/config/pigrow_config.txt | grep box_name")
            boxname = stdout.read().strip().split("=")[1]
            print "Pigrow Found; " + boxname
        except Exception as e:
            print("Can't read Pigrow's name " + str(e))
        if boxname == '':
            boxname = None
        return boxname

class view_pnl(wx.Panel):
    #
    # Creates the little pannel with the navigation tabs
    # small and simple, it changes which pannels are visible
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, 190), size = wx.Size( 285,35 ), style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((230,200,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        view_opts = ['System Config', 'Pigrow Setup', 'Camera Config', 'Cron Timing', 'multi-script', 'Local Files', 'Timelapse', 'Graphs', 'Live View', 'pieye watcher']
        #Showing only completed tabs
        view_opts = ['System Config', 'Pigrow Setup', 'Cron Timing', 'Local Files', 'Graphs']
        self.view_cb = wx.ComboBox(self, choices = view_opts, pos=(10,2), size=(265, 30))
        self.view_cb.Bind(wx.EVT_COMBOBOX, self.view_combo_go)
    def view_combo_go(self, e):
        display = self.view_cb.GetValue()
        #hide all the pannels
        MainApp.system_ctrl_pannel.Hide()
        MainApp.system_info_pannel.Hide()
        MainApp.config_ctrl_pannel.Hide()
        MainApp.config_info_pannel.Hide()
        MainApp.cron_list_pannel.Hide()
        MainApp.cron_info_pannel.Hide()
        MainApp.localfiles_ctrl_pannel.Hide()
        MainApp.localfiles_info_pannel.Hide()
        MainApp.welcome_pannel.Hide()
        MainApp.graphing_ctrl_pannel.Hide()
        MainApp.graphing_info_pannel.Hide()
        #show whichever pannels correlate to the option selected
        if display == 'System Config':
            MainApp.system_ctrl_pannel.Show()
            MainApp.system_info_pannel.Show()
        elif display == 'Pigrow Setup':
            MainApp.config_ctrl_pannel.Show()
            MainApp.config_info_pannel.Show()
        elif display == 'Camera Config':
            print("changing window display like i'm Mr Polly on weed")
        elif display == 'Cron Timing':
            MainApp.cron_list_pannel.Show()
            MainApp.cron_info_pannel.Show()
        elif display == 'Multi-script':
            print("changing window display like i'm Mr Polly on coke")
        elif display == 'Local Files':
            MainApp.localfiles_ctrl_pannel.Show()
            MainApp.localfiles_info_pannel.Show()
        elif display == 'Timelapse':
            print("changing window display like i'm Mr Polly on crack")
        elif display == 'Graphs':
            MainApp.graphing_ctrl_pannel.Show()
            MainApp.graphing_info_pannel.Show()
        elif display == 'Live View':
            print("changing window display like i'm Mr Polly on LSD")
        elif display == 'pieye watcher':
            print("changing window display like i'm Mr Polly in a daydream")
        else:
            print("!!! Option not recognised, this is a programming error! sorry")
            print("          message me and tell me about it and i'll be very thankful")

class welcome_pnl(wx.Panel):
    #
    #  This displays the welcome message on start up
    #     this explains how to get started
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size( 910,800 ), style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,210,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    def OnEraseBackground(self, evt):
        # yanked from ColourDB.py #then from https://www.blog.pythonlibrary.org/2010/03/18/wxpython-putting-a-background-image-on-a-panel/
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap("./splash.png")
        dc.DrawBitmap(bmp, 0, 0)


#
#
#  The main bit of the program
#           EXCITING HU?!!!?
#
class MainFrame ( wx.Frame ):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1200,800 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.Layout()
        self.Centre( wx.BOTH )
    def __del__( self ):
        pass

class MainApp(MainFrame):
    def __init__(self, parent):
        MainFrame.__init__(self, parent)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        MainApp.pi_link_pnl = pi_link_pnl(self)
        self.view_pnl = view_pnl(self)
        #
        #Set the local file paths for this computer_username
        self.set_local_options()
        #
        # loads all the pages at the start then hides them,
        #         maybe i should change this later but let's make it work first
        MainApp.welcome_pannel = welcome_pnl(self)
        MainApp.system_ctrl_pannel = system_ctrl_pnl(self)
        MainApp.system_info_pannel = system_info_pnl(self)
        MainApp.config_ctrl_pannel = config_ctrl_pnl(self)
        MainApp.config_info_pannel = config_info_pnl(self)
        MainApp.cron_list_pannel = cron_list_pnl(self)
        MainApp.cron_info_pannel = cron_info_pnl(self)
        MainApp.localfiles_ctrl_pannel = localfiles_ctrl_pnl(self)
        MainApp.localfiles_info_pannel = localfiles_info_pnl(self)
        MainApp.graphing_ctrl_pannel = graphing_ctrl_pnl(self)
        MainApp.graphing_info_pannel = graphing_info_pnl(self)
        #hide all except the welcome pannel
        MainApp.system_ctrl_pannel.Hide()
        MainApp.system_info_pannel.Hide()
        MainApp.config_ctrl_pannel.Hide()
        MainApp.config_info_pannel.Hide()
        MainApp.cron_list_pannel.Hide()
        MainApp.cron_info_pannel.Hide()
        MainApp.localfiles_ctrl_pannel.Hide()
        MainApp.localfiles_info_pannel.Hide()
        MainApp.graphing_ctrl_pannel.Hide()
        MainApp.graphing_info_pannel.Hide()

    def OnClose(self, e):
        #Closes SSH connection even on quit
        # need to add 'ya sure?' question if there's unsaved data
        print("Closing SSH connection")
        ssh.close()
        sys.exit(0)

    def set_local_options(self):
        MainApp.OS =  platform.system()
        if MainApp.OS == "Linux":
            computer_username = os.getlogin()
            MainApp.localfiles_path = "/home/" + computer_username + "/frompigrow/"
        elif MainApp.OS == "Windows":
            localpath = os.getcwd()
            localpath += '\\frompigrow\\'
            MainApp.localfiles_path = localpath
        else:
            localpath = os.getcwd()
            localpath += '/frompigrow/'
            MainApp.localfiles_path = localpath


def main():
    app = wx.App()
    window = MainApp(None)
    window.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
