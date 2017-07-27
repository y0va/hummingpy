# hummingpy
Python sound fft 2 txt transformer on RPI3 for bee hives 

## Setup a hummingpy image

### Platform
We decided to use [Raspberry 3 SBC](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) with [Wolfson Audio Card](https://www.element14.com/community/community/raspberry-pi/raspberry-pi-accessories/wolfson_pi).
Use the Raspian Jessie Lite image from: https://www.raspberrypi.org/downloads/raspbian/
Don't forget to enable ssh: https://www.raspberrypi.org/documentation/remote-access/ssh/
All configuration is done via ssh. Raspian standard UN/PW: pi/raspberry

### Sound Drivers
#### Wolfson Audio Card
I did some kernel patching to get the Wolfson Card running on a raspbian, but today the drivers seem to be included within the Kernel: http://www.horus.com/~hias/cirrus-driver.html

Run the right usecase script, to activate the hardware suitable for your case. Normally `./Record_from_Linein.sh` .

Disable the built-in sound card: http://www.instructables.com/id/Disable-the-Built-in-Sound-Card-of-Raspberry-Pi/ .

Now we can talk to the Wolfson Card as 'default'.

#### Normal USB Sound Chips
Normal USB Sound Cards also work aout of the box, but have less quality.

### Clone project to RPI
Install git and pip and then clone repo to home dir.
As user pi in $HOME:
```
sudo apt install git
git clone https://github.com/y0va/hummingpy.git
```

### Setup 
#### Hive Name
Hive name equals to hostname, which is set in `/etc/hostname`.
#### Network
If you want to use wlan edit install/interfaces accordingly to your local settings. *TODO: Stabelize WLAN especially over GSM*
#### Config File
Main config file is `install/config.py`
It will be reloaded from the WEBDAV structure defined in it during every start.
Define WEBDAV-URL in config.py. See there for details.
##### WEBDAV Structure
In the root of the WEBDAV Structure there has to be config.py and humming.py out of the install directory.
In this directory each Hive has to have it's own directory named 'Hive Name'. See above. Each hive directory has to have directories called `logs` and `recordings`
*TODO: Create directory structure automagically on new system*
##### Other settings
Recorded data is temporarily stored in /var/recordings
Log file is in /var/log/hummingpy.log
See config.py

#### Installation
run install script: 
```
cd hummingpy
sudo bash install.sh
```
see install.sh for details.

#### Run
Type:
`sudo service humming restart`

or similar to control service ' humming'.


