#!/usr/bin/python

import datetime
import alsaaudio
import signal
import sys
import requests
import os
import logging

import numpy as np
import matplotlib


from shutil import make_archive
from glob import glob
from time import sleep
from threading import Thread

from scipy.signal import welch

import config as c

# create logger 

logger = logging.getLogger('humming')
if c.DEBUG : logger.setLevel(logging.DEBUG)
else : logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler(c.LOGFILE)
formatter = logging.Formatter('%(asctime)s %(message)s')
if c.DEBUG : 
    logger.setLevel(logging.DEBUG)
    fh.setLevel(logging.DEBUG)
else : 
    logger.setLevel(logging.INFO)
    fh.setLevel(logging.INFO)

fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)


if c.DISPLAY : 
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  plt.style.use('grayscale')

def stop_all(a,b) :
  
  logger.info ( "ciao, perhaps we have to wait for the fft to terminate...")

  quit()
  
  
signal.signal(signal.SIGINT, stop_all)



# this returns the seconds and microseconds till the next full x minutes
def time_to_wait():
  now = datetime.datetime.now()
  next_minute=now + datetime.timedelta( minutes = c.LENGTH_PCM- (now.minute % c.LENGTH_PCM) )
  
  future = next_minute.replace (second=0, microsecond=0)
  
  return future



  
def record(minutes = 0.1):
    
  inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, c.DEVICE_NAME)
  
  #set attributes: Mono
  inp.setchannels(1)
  inp.setrate(c.SAMPLERATE)
  inp.setformat(alsaaudio.PCM_FORMAT_U8)
  inp.setperiodsize(c.PERIOD_SIZE)

  frames = (minutes * 60 *8000)
  
  logger.debug ("Planning to record " + str(minutes) +" minutes and " + str(frames) + " samples audio")
  
  chunk = ""
  if c.GAUGE : stopping_time= datetime.datetime.now() + datetime.timedelta(minutes=c.LENGTH_PCM)
  else : stopping_time=time_to_wait()
  
  while datetime.datetime.now() < stopping_time:
    
    # Read data from device
    l, data = inp.read()
    chunk += data
  
  return chunk

def start_network() :
    if c.KILL_WIFI : 
        os.system('rfkill unblock wifi')
        os.system('ifdown ' + c.IFACE +' && ifup ' + c.IFACE)
        os.system('ping -c 1 google.de')

    
    

def stop_network() :
    if c.KILL_WIFI : 
        os.system('rfkill block wifi')

def upload(filename="", files="") :
        
    logger.debug("created zipfile: " + filename)
    
    furl = c.URL +c.HIVE+ '/recordings/' + filename.rsplit('/',1)[-1]
    
    start_network()


    
    try:
        r=requests.head(furl,auth=c.AUTH, verify=False, timeout=c.REQUESTSTIMEOUT)
    except requests.exceptions.RequestException as e:
        logger.debug("while trying to get head of " + furl + " : " + str(e))
        stop_network()
        os.remove(filename)
        return False 
    
    
    if not r.status_code == requests.codes.ok :   ## FILE DOES NOT EXIST
        map (os.remove,files)
        try: 
            r = requests.put(furl, data= open (filename), auth=c.AUTH, verify=False, timeout=c.REQUESTSTIMEOUT)
        except requests.exceptions.RequestException as e:
            logger.debug("while trying to upload file: " + furl + " : " + str(e))
            stop_network()
            os.remove(filename)
            return False 
	  
        stop_network()
        logger.debug( "file " + filename + " uploaded")
        
        if (r.status_code == 201) and c.REMOVE_FILES: 
            os.remove(filename)
            
            logger.debug( "and deleted locally")
            
            return True
        else : 
	    logger.debug("while uploading something went wrong, requests status code: " + str(r.status_code))
	    return False
    else : 
        stop_network()
        logger.debug("file "+filename+ " already uploaded")
        if c.REMOVE_FILES :
            os.remove(filename)
            logger.debug("now deleted")
        return True
        
            
   

#   defines filename and thereby the update interval
def get_file_name(time_string="") :
    switcher = {
        'm' : time_string,
        'h' : time_string[:-2],
        'd' : time_string[:-4]
    }
    return switcher.get(c.U_INTERVAL,"wrong_u_interval")


        
def save_temp(filename) :
    with open(c.TFILE,'r') as f:
        temp=f.readline()
    with open(filename + '_temperature.txt','a') as f:
        f.write(datetime.datetime.now().strftime("%Y%m%d%H%M") + ': ' + str(int(temp)/1000.) + '\n')
        
    
def display(hums, filename) :
    fig = plt.figure()
    axes = fig.add_subplot(1,1,1)
    
    axes.plot(hums)
    fig.set_size_inches(8, 6)
    fig.savefig(filename[:-3]+'png', dpi=100, bbox_inches='tight')
    
    
def spec_print (samples="",time_string="") :
    a=np.fromstring(samples,np.dtype('<i1'))
 
    #normalize sample data around [-1,1), so data looks like a signal
    logger.debug("Analysing "+str(len(a))+ " samples of timeblock " + time_string)
      
    b=[(ele/2**8.)*2-1 for ele in a]
    if c.SAMPLERATE/c.DOWNSAMPLERATE < 256 : nperseg = c.SAMPLERATE/c.DOWNSAMPLERATE
    else : nperseg = 256
    
    #estimate power spectrum density
    f, fft = welch(b, nperseg = nperseg, nfft=c.SAMPLERATE/c.DOWNSAMPLERATE, axis=0)
  
    # write it to a file
    
    
    
    if c.GAUGE : 
        c.OUTPUT_ROWS = False
        filename = c.HOME + 'humming.gauge'
    else : 
        filename = c.OUTPUT_FOLDER + c.HIVE + get_file_name(time_string)
        if c.OUTPUT_ROWS : filename += '.csv'
        else : filename += '.hum'
    
    if c.FILTER and not c.GAUGE:
        with open(c.HOME + 'humming.gauge', 'r') as filterfile :
            filterhums = filterfile.readlines()
            
        
    
    if os.path.exists(filename) :
        if c.GAUGE : 
            hupdate = False
        else : 
            if not c.OUTPUT_ROWS : 
                with open (filename, 'a+') as humfile :
                    hums = humfile.readlines()
            hupdate = True
    else :
        # we start from the beginning or from new U_INTERVAL
        hupdate = False
    
        files_to_upload = glob(c.OUTPUT_FOLDER+'/*')
    
        if not len(files_to_upload) == 0 : 
            #  for compatibility with windoze use zip
            zip_file=make_archive('/tmp/' + c.HIVE + get_file_name(time_string), 'zip',c.OUTPUT_FOLDER)
            
            # Start upload in an own thread, so that no data is lost, if something goes wrong
            
            th = Thread(target=upload, args = (zip_file,files_to_upload))
            th.daemon = False
            th.start()
            
        else : logger.debug("no files to upload")
    
    if c.DISPLAY: display(fft, filename)
    
    outstring=""
  
    if not c.OUTPUT_ROWS : 
        if hupdate : outstring += hums[0][:-1] + '\t'
        outstring += time_string + '\n'
    else :
        outstring += time_string + ';'
    
    
    
    loudest=1
    for frequency in range(1,c.VALUES+1) :
        
        if c.FILTER and not c.GAUGE :
            if len(filterhums) != c.VALUES + 1 :
                logger.error("need to gauge when filtering!")
                exit()
            fft[frequency]-= float(filterhums[frequency])
            if fft[frequency] < 0 : fft[frequency] = 0
                
        if c.DEBUG :  
            if abs(fft[loudest]) < abs(fft[frequency]) : loudest=frequency
        if not c.OUTPUT_ROWS : 
            if hupdate : outstring += hums[frequency][:-1] + '\t'
            outstring += "%12.10f" % abs(fft[frequency]) + '\n'
        else :
            outstring += "%12.10f" % abs(fft[frequency]) + ';'
  
    if c.OUTPUT_ROWS : 
        outstring += '\n'
        with open (filename, 'a+') as humfile :
            humfile.write(outstring)
    else :
        with open (filename, 'w+') as humfile :
            humfile.write(outstring)
    
    if c.TEMP : save_temp(filename[:-4])
    
    logger.debug ("primitive analysis, in timeblock " + time_string + " the most powerful frequency is in Block: " + str(loudest*c.DOWNSAMPLERATE - c.DOWNSAMPLERATE) + '-' + str(loudest*c.DOWNSAMPLERATE))
    
  



# this starts the recording thread
def start_recording(time_to_record=0.1):
  global t
  
  starting_time = datetime.datetime.now()
  time_string = starting_time.strftime("%Y%m%d%H%M")
  logger.debug("Start recording @ " + time_string)
  data = record (minutes = time_to_record)
  
  #all calculation go into an seperate thread
  logger.debug ("start calculating chunk " + time_string)
  t = Thread(target=spec_print, args = (data,time_string))
  t.daemon = False
  t.start()
  


# sets the timer for controlling record in an own thread

def main():  
#  global t
#  t = Thread
  if c.GAUGE :
   data = record (c.LENGTH_PCM)
   spec_print(data, 'gauge')
   exit()
   
  timetowait =  time_to_wait()
  ssleep=timetowait - datetime.datetime.now()
  
  if c.DEBUG : 
    logger.debug("We have to wait " + str (ssleep) + " for the next complete " + str(c.LENGTH_PCM) +" minutes, be patient..." )
    
    
  sleep(ssleep.seconds + ssleep.microseconds/1000000.)
  
  
  #here we go (and go and go and...)
  while True: 
      start_recording(c.LENGTH_PCM)
      
    
if __name__ == "__main__":
    main()



