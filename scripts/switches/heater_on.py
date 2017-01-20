#!/usr/bin/python
import datetime, sys
sys.path.append('/home/pi/Pigrow/scripts/')
import pigrow_defs


def heater_on(set_dic, switch_log):
    script = 'heater_on.py'
    msg = ("")
    msg +=("      #############################################")
    msg +=("      ##         Turning the heater - ON         ##")
    if 'gpio_heater' in set_dic and not str(set_dic['gpio_heater']).strip() == '':
        gpio_pin = int(set_dic['gpio_heater'])
        gpio_pin_on = set_dic['gpio_heater_on']
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(gpio_pin, GPIO.OUT)
        if gpio_pin_on == "low":
            GPIO.output(gpio_pin, GPIO.LOW)
        elif gpio_pin_on == "high":
            GPIO.output(gpio_pin, GPIO.HIGH)
        else:
            msg +=("      !!       CAN'T DETERMINE GPIO DIRECTION    !!")
            msg +=("      !!  run config program or edit config.txt  !!")
            msg +=("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            pigrow_defs.write_log(script, 'Failed - no direction set in config', switch_log)
            return msg

    else:
        msg +=("      !!               NO HEATER SET             !!")
        msg +=("      !!  run config program or edit config.txt  !!")
        msg +=("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        pigrow_defs.write_log(script, 'Failed - due to none set in config', switch_log)
        return msg

    msg +=("      ##            by switching GPIO "+str(gpio_pin)+" to "+gpio_pin_on+"  ##")
    msg +=("      #############################################")
    pigrow_defs.write_log(script, 'Heater turned on', switch_log)
    return msg

if __name__ == '__main__':

    ### default settings
    loc_dic = pigrow_defs.load_locs("/home/pi/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'],)
    heater_on(set_dic, loc_dic['loc_switchlog'])
    print msg
