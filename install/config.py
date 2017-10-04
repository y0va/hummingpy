from platform import node

# CONSTANTS

#name of hive
HIVE=node()

#Length of the PCM to be recorded in minutes
LENGTH_PCM=1

#Downsamplerate in Hertz
DOWNSAMPLERATE=1

#How many values do we want to have? max=SAMPLERATE/(DOWNSAMPLERATE*2)
VALUES=500

#Samplingrate
SAMPLERATE=8000

#upload interval: 'm' each minute, 'h' hourly, 'd' daily
# if U_INTERVAL < LENGTH_PCM -> U_INTERVAL=LENGTH_PCM
U_INTERVAL='m'

# Print output in rows (better for machine) or in columns (better human readable)
OUTPUT_ROWS=False

#Display something somewhere?
DISPLAY=True

#switch off wifi after each upload
KILL_WIFI=False

#which wifi interface to use
IFACE='wlan0'


# URL for DATA, and Skript files, needs subdir 'HIVE' with subdirs "recordings" and "log"
# In 'HIVE' should be config.py and humming.py
URL='https://webdav.uni-kassel.de/webdav/ReloadInsectTab/ITApic/BananaBee/'


# Username and Password for Uploading URL
AUTH=('','')

# Remove files after upload?
REMOVE_FILES=True

# DEBUG?
DEBUG=True

#FILTER out noise?
FILTER=False

#GAUGE needs to be set once before each use. Should be command line option
GAUGE=False

# save temperature?
TEMP=True

# File to look for Temp
#RPI:
TFILE = '/sys/class/thermal/thermal_zone0/temp'

#BPI:
#TFILE = '/sys/devices/platform/a20-tp-hwmon/temp1_input'


#logfile to use
LOGFILE = '/var/log/humming.log'

#output folder, please fully qualified
OUTPUT_FOLDER="/var/recordings/"

#Audio device to use for microphone
#for naming see: http://www.alsa-project.org/main/index.php/DeviceNames
DEVICE_NAME="default"
#DEVICE_NAME="plug:front:1"

#Homedir, where all the base is
#has to be the same as in /usr/sbin/hummon.py
HOME='/root/hummingpy/'

#period size for recording !!doesnt work on bananapi
PERIOD_SIZE=934

# Timeout for internet requests api

REQUESTSTIMEOUT=5

