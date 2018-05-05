#!/usr/bin/python3

import logging
import configparser

import sectoralarm

class AnnexActivator:
    
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.cfg')
        numeric_level = getattr(logging, config.get('Logging', 'level').upper(), None)
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='annex_activate.log', level=numeric_level)
        self.alarm_email = config.get('Alarm', 'email')
        self.alarm_password = config.get('Alarm', 'password')
        self.alarm_siteId = config.get('Alarm', 'siteId')
        self.alarm_panel_code = config.get('Alarm', 'panel_code')
        
        self.alarm = sectoralarm.connect(self.alarm_email, self.alarm_password, self.alarm_siteId, self.alarm_panel_code)
  

    def get_status(self):
        current_status = self.alarm.status()
        
        return current_status
    
    
    def get_last_event(self):
        event_log = self.alarm.event_log()

        last_event = event_log[0]['EventType'] 
        logging.debug('Retrieved last event [' + last_event )
    
        return last_event
    
    def arm_annex(self):
        self.alarm.arm_annex()

if __name__ == '__main__':
    activator = AnnexActivator()
    status = activator.get_status()
    logging.debug("Alarm status is " + status['AlarmStatus'])
    logging.debug("Annex status is " + status['StatusAnnex'])

    if (status['AlarmStatus'] == 'armed') and (status['StatusAnnex'] == 'disarmed'):
        if activator.get_last_event()== 'armed':
            logging.info('Arming annex')
            activator.arm_annex()
            
