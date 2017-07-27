#!/usr/bin/python
import sys
import os
import datetime
import subprocess
import requests
import hashlib
import logging

sys.path.append('/root/hummingpy/')
import config as c

# create logger 
logger = logging.getLogger('HUMMON')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(c.LOGFILE)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)

requestsstatus=True

def get_new_file(filename="") :
	try:
		r = requests.get(c.URL + filename,auth=c.AUTH, verify=False, timeout=c.REQUESTSTIMEOUT)
	except requests.exceptions.RequestException as e:
        	logger.debug("while trying to download file " + filename +  ": " + str(e))
		return False

	newhash = hashlib.md5(r.text).hexdigest()

	with open (c.HOME + filename,'r') as f:
		oldtext=f.read()
	oldhash = hashlib.md5(oldtext).hexdigest()

	if oldhash != newhash :
		logger.info("there seems to be a new version of " + filename +". Lets download it!")
	with open (c.HOME + filename,'w') as f:
		f.write(r.text)
        
	return True


#if c.KILL_WIFI :
if (os.system('rfkill unblock wifi')!=0) : 
	logger.error("could not unblock wifi")
	
#if (os.system('ifdown ' + c.IFACE +' && ifup ' + c.IFACE)!=0) :
#	logger.error("could not establish connection")
	
#if (os.system('ntpdate  ntps1.gwdg.de')!=0) :
#	logger.error('could not connect to time server')
	
logger.debug('established connection')
right_now=datetime.datetime.now().strftime("%Y%m%d%H%M")

# upload logfile
fh.close()
filename="humming"+ c.HIVE + right_now + ".log"

try:
	r = requests.put(c.URL +c.HIVE +'/log/'+ filename, data = open (c.LOGFILE), auth=c.AUTH, verify=False, timeout=c.REQUESTSTIMEOUT)
except requests.exceptions.RequestException as e:
	logger.error("while trying to upload logfile: " + str(e))
	requestsstatus=False
if requestsstatus and c.REMOVE_FILES: 
#	print ("removed logfile")
	os.remove(c.LOGFILE)


  

# reopen logging file
logger.addHandler(fh)  

# checking for new version of humming.py and config file
get_new_file('humming.py')
get_new_file('config.py')

#switch off wifi again
#if c.KILL_WIFI :
  
#if (os.system('ifdown ' + c.IFACE + ' && rfkill block wifi') != 0) : 
#	logging.error("could not block wifi")
	

logger.info("system starting @ " + right_now)
fh.close()
pid = subprocess.Popen([c.HOME + 'humming.py']).pid

with open(c.HOME + 'humming.pid','w') as f:
	f.write(str(pid))

