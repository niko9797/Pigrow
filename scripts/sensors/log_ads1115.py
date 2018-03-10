#!/usr/bin/python
import os
import sys
import time
import datetime
try:
    import Adafruit_ADS1x15 #Requires adafruit ads1x15 installed
except:
    print("Adafruit ADS1x15 python module not installed, instructions can be found easily via goodle")
    sys.exit()
#default values for setting up the adafruit ads1x15 module
GAIN = 1
samples_per_second = 8
pin_address = "gnd"  #gnd,vdd,sda,sdl - use lower case because argu gets lowercased
i2c_busnum = 1
sensor_type = "ads1115"
convert_volt = True #set false to record results without conversion

homedir = os.environ['HOME']

try:
    sys.path.append(homedir + '/Pigrow/scripts/')
    import pigrow_defs
    script = 'log_ads1115.py'
    loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    log_path = loc_dic['log_path']
    log_path = log_path + "ads1115_log.txt"
except Exception as e:
    print("Using Defaults because - " + str(e))
    log_path = homedir + "/Pigrow/logs/ads1115_log.txt"

for argu in sys.argv[1:]:
    argu = str(argu).lower()
    if argu == 'help' or argu == '-h' or argu == '--help':
        print(" Script for logging ADS1115 Analogue to Digital Converter ")
        print(" ")
        print(" log=" + homedir + "/Pigrow/logs/ads1115_log.txt")
        print(" ")
        print(" gain=1")
        print("      use gain to set input voltage range; ")
        print("      2/3 = +/-6.144V/\n      1 = +/-4.096V\n      2 = +/-2.048V\n      4 = +/-1.024V\n      8 = +/-0.512V\n      16 = +/-0.256V")
        print("      if you're unsure then set to 1 and incraese")
        print("      if all values are towards the bottom of the graaph.")
        print("")
        print(" address=gnd ")
        print("      the address of the ADS1115 on the i2c register as")
        print("      determined by connecting the ADDR pin to one of the following options")
        print("      GND - (0x48)\n      VDD - (0x49)\n      SDA - (0x4A)\n      SCL - (0x4B)")
        print("")
        print(" sensor_type=ads1115")
        print("            select either ads1015 or ads1115 ")
        print("")
        print(" sps=8")
        print("     samples per second")
        print("       ads1015 - 128, 250, 490, 920, 1600, 2400, 3300")
        print("       ads1115 - 8, 16, 32, 64, 128, 250, 475, 860")
        print("     at low values the average voltage is taken over")
        print("     a longer period which can be useful in some")
        print("     situations, for faster readings use a higher value.")
        print("")
        print(" convert_volt=True/False")
        print("             When true it converts the recorded values to volts ")
        print("             referencing the gain value. ")
        sys.exit()
    elif argu == '-flags':
        print("log=[LOG_PATH]")
        print("gain=[2/3,1,2,4,8,16]")
        print("sensor_type=[ads1115, ads1015]")
        print("sps=[8,16,32,64,128,250,475,860,/ads1015,128,250,490,920,1600,2400,3300]")
        print("pin_address=[0,1]")
        print("i2c_busnum=[gnd,vdd,sda,scl]")
        print("convert_volt=[True,False]")
        sys.exit()
    elif "=" in argu:
        thearg = argu.split('=')[0].lower()
        thevalue = argu.split('=')[1].lower()
        if thearg == 'log' or thearg == 'log_path':
            log_path = thevalue
        elif thearg == 'gain':
            GAIN = int(thevalue)
        elif thearg == 'address':
            pin_address = thevalue
        elif thearg == 'bus' or thearg == 'busnum':
            i2c_busnum = int(thevalue)
        elif thearg == 'sensor_type' or thearg == 'sensor':
            sensor_type = thevalue
        elif thearg == 'samples_per_second' or thearg == 'sps':
            samples_per_second = int(thevalue)
        elif thearg == "convert_volt" or thearg == "cv" or thearg == "convert_to_volt":
            if thevalue == "false" or thevalue == 'no':
                convert_volt = False
            elif thevalue == "true" or thevalue == 'yes':
                convert_volt = True
            else:
                print("Didn't understand if you wanted to convert to volts or not, use flag convert_volt=false if not")

#setting up the adafruit sensor drivers
adc = Adafruit_ADS1x15.ADS1115()
if sensor_type == "ads1115":
    if pin_address == "gnd":
        adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=i2c_busnum)
    elif pin_address == "vdd":
        adc = Adafruit_ADS1x15.ADS1115(address=0x49, busnum=i2c_busnum)
    elif pin_address == "sda":
        adc = Adafruit_ADS1x15.ADS1115(address=0x4A, busnum=i2c_busnum)
    elif pin_address == "scl":
        adc = Adafruit_ADS1x15.ADS1115(address=0x4B, busnum=i2c_busnum)
    else:
        print("invalid pin address, try gnd vdd sda or scl instead")
        sys.exit()
elif sensor_type == "ads1015":
    if pin_address == "gnd":
        adc = Adafruit_ADS1x15.ADS1015(address=0x48, busnum=i2c_busnum)
    elif pin_address == "vdd":
        adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=i2c_busnum)
    elif pin_address == "sda":
        adc = Adafruit_ADS1x15.ADS1015(address=0x4A, busnum=i2c_busnum)
    elif pin_address == "scl":
        adc = Adafruit_ADS1x15.ADS1015(address=0x4B, busnum=i2c_busnum)
    else:
        print("invalid pin address, try gnd vdd sda or scl instead")
        sys.exit()


print("using log path : " + str(log_path))


def read_adc():
    try:
        val1 = adc.read_adc(0, gain=GAIN, data_rate=samples_per_second)
        val2 = adc.read_adc(1, gain=GAIN, data_rate=samples_per_second)
        val3 = adc.read_adc(2, gain=GAIN, data_rate=samples_per_second)
        val4 = adc.read_adc(3, gain=GAIN, data_rate=samples_per_second)
        print val1, val2, val3, val4
        return [val1, val2, val3, val4]
    except Exception as e:
        print("Reading sensor failed - " + str(e))
        return None

def convert_to_volt(vals):
    # 2/3 gain =  0.1875mV (default) ###(not actually default from what i can tell)
    if GAIN == 1:
        vals[0] = vals[0] * 0.125
        vals[1] = vals[1] * 0.125
        vals[2] = vals[2] * 0.125
        vals[3] = vals[3] * 0.125
    if GAIN == 2:
        vals[0] = vals[0] * 0.0625
        vals[1] = vals[1] * 0.0625
        vals[2] = vals[2] * 0.0625
        vals[3] = vals[3] * 0.0625
    if GAIN == 4:
        vals[0] = vals[0] * 0.03125
        vals[1] = vals[1] * 0.03125
        vals[2] = vals[2] * 0.03125
        vals[3] = vals[3] * 0.03125
    if GAIN == 8:
        vals[0] = vals[0] * 0.015625
        vals[1] = vals[1] * 0.015625
        vals[2] = vals[2] * 0.015625
        vals[3] = vals[3] * 0.015625
    if GAIN == 16:
        vals[0] = vals[0] * 0.0078125
        vals[1] = vals[1] * 0.0078125
        vals[2] = vals[2] * 0.0078125
        vals[3] = vals[3] * 0.0078125
    return vals


def log_ads1115(log_path, vals):
    timenow = str(datetime.datetime.now())
    log_entry  = timenow + ">"
    log_entry += str(vals[0]) + ">"
    log_entry += str(vals[1]) + ">"
    log_entry += str(vals[2]) + ">"
    log_entry += str(vals[3]) + "\n"
    with open(log_path, "a") as f:
        f.write(log_entry)
    print("Written; " +  log_entry)


if __name__ == '__main__':
    vals = read_adc()
    if not vals == None:
        if not convert_volt == False:
            convert_to_volt(vals)
        log_ads1115(log_path, vals)
    else:
        print("failed to find results")
