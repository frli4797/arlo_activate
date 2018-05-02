
import json
import logging
import tempfile
import os

import sectoralarm

class AlarmState:
    dirty = False
    state = ""
    
    def __init__(self, dirty, state):
        self.dirty = dirty
        self.state = state

def __get_status():
    email = 'fredrik@jagare-lilja.se'
    password = 'Sieko54Ger'
    siteId = '02581279'
    
    status_file = os.path.join(tempfile.gettempdir(), 'alarm_state')
    
    alarm = sectoralarm.connect(email, password, siteId)
    current_status = alarm.status()
    saved_status = {}
    
    
    
    if os.path.isfile(status_file):    
        with open(status_file, 'r+') as result_file:
                saved_status = json.load(result_file)
                result_file.truncate()
                result_file.close# result_file.truncate()
                logging.debug('Stored status: ' + saved_status['AlarmStatus'])  
    else:
        with open(status_file, 'w') as result_file:
                json.dump(current_status, result_file)
                result_file.close
    
    logging.debug('Stored status: ' + saved_status['AlarmStatus'])  
    logging.debug('Current status: ' + current_status['AlarmStatus'])  
     
    if(current_status['AlarmStatus'] == saved_status['AlarmStatus']):
        logging.debug('Setting to not dirty.') 
        return AlarmState(False, current_status)
    else:
        logging.debug('Setting to dirty.')       
        return AlarmState(True, current_status)
    
       
    

def __set_mode(mode_name):

    from pyarlo import PyArlo
    arlo  = PyArlo('fredrik@jagare-lilja.se', '3rNQFmBLNBrK')

    base = arlo.base_stations[0]
    logging.info("Is mode " + base.mode)

    if base.mode != mode_name:
        print("Setting mode " + mode_name)
        base.mode = mode_name
        base.update()
    else:
        logging.debug("Mode not set")

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='arlo_activate.log',level=logging.DEBUG)

    status = __get_status()
    logging.debug("Alarm status is " + status.state['AlarmStatus'])
    
    if status.dirty == False:
        logging.debug('Not dirty. Doing nothing.')
    else:
        logging.info('Dirty. Changing state.')
        if status.state['AlarmStatus'] == 'armed':
            __set_mode('armed')
        else:
            __set_mode('schedule')
        
  


# import json
# import logging
# 
# import sectoralarm
# import config
# 
# 
# 
# def __get_status():
#     SECTORSTATUS = sectoralarm.SectorStatus(config)
# 
#     result = SECTORSTATUS.status()
# 
#     print json.dumps(result)
#     return result['ArmedStatus']
# 
# def __set_mode(mode_name):
# 
#     from pyarlo import PyArlo
#     arlo  = PyArlo('fredrik@jagare-lilja.se', '3rNQFmBLNBrK')
# 
#     base = arlo.base_stations[0]
#     print "Is mode " + base.mode
# 
#     logging.info('I told you so')
#     if base.mode != mode_name:
#         print "Setting mode " + mode_name
#         base.mode = mode_name
#         base.update()
#     else:
#         print "Mode not set"
# 
# if __name__ == '__main__':
#     logging.basicConfig(filename='example.log',level=logging.INFO)
# 
#     status = __get_status()
#     print "Alarm status is " + status
#     if status == 'armed':
#         __set_mode('armed')
#     else:
#         __set_mode('schedule')
