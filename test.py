
import json
import logging
import tempfile
import os

import sectoralarm



def __get_status():
    __email = 'fredrik@jagare-lilja.se'
    __password = 'Sieko54Ger'
    __siteid = '02581279'
    
    __status_file = os.path.join(tempfile.gettempdir(), 'alarm_state')
    
    alarm = sectoralarm.connect(__email, __password, __siteid)
    
    if os.path.isfile(__status_file):    
        with open(__status_file, 'w') as result_file:
                current_status = result_file.read()
                result_file.close# result_file.truncate()
                result_file.truncate()
                
    
    print('Current status: ' + current_status)     
    
    result = alarm.status()



    print(result)
    return result['AlarmStatus']

def __set_mode(mode_name):

    from pyarlo import PyArlo
    arlo  = PyArlo('fredrik@jagare-lilja.se', '3rNQFmBLNBrK')

    base = arlo.base_stations[0]
    print("Is mode " + base.mode)

    logging.info('I told you so')
    if base.mode != mode_name:
        print("Setting mode " + mode_name)
        base.mode = mode_name
        base.update()
    else:
        print("Mode not set")

if __name__ == '__main__':
    logging.basicConfig(filename='example.log',level=logging.INFO)

    status = __get_status()
    print("Alarm status is " + status)
    if status == 'armed':
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
