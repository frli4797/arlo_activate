#!/usr/bin/python3

import sys
import os
import getopt
import configparser
import logging

import sectoralarm
import json


def __printMessage():
    print('Usage: annex_activate [-f]')
    print('-f force arming of annex')
    print('-n sends notification e-mail if the annex was armed.')
    print('-h this message')
            
def emailNotify(subject, message):
    if sys.platform.startswith('linux'):
        from email.mime.text import MIMEText
        from subprocess import Popen, PIPE
        msg = MIMEText(message)
        msg["From"] = "monitor@jagare-lilja.se"
        msg["To"] = "fredrik@jagare-lilja.se"
        msg["Subject"] = subject
        p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        p.communicate(msg.as_string().encode())


class AnnexActivator:
    
    def __init__(self):

        config = configparser.ConfigParser()
        config.read('config.cfg')
        numeric_level = getattr(logging, config.get('Logging', 'level').upper(), None)
        log_location = config.get('Logging', 'log_location')
        logfile = os.path.join(log_location, 'annex_activate.log')
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=logfile, level=numeric_level)
        logging.debug('Starting')
        self.alarm_email = config.get('Alarm', 'email')
        self.alarm_password = config.get('Alarm', 'password')
        self.alarm_siteId = config.get('Alarm', 'siteId')
        self.alarm_panel_code = config.get('Alarm', 'panel_code')
        
        self.alarm = sectoralarm.connect(self.alarm_email, self.alarm_password, self.alarm_siteId, self.alarm_panel_code)

    def get_status(self):
        current_status = self.alarm.status()
        
        logging.debug(json.dumps(current_status))
       
        if current_status['AlarmStatus'] not in {'armed', 'disarmed'} or \
            current_status['StatusAnnex'] not in {'armed', 'disarmed'}:
            logging.error("Alarm status is " + current_status['AlarmStatus'])
            logging.error("Annex status is " + current_status['StatusAnnex'])
            raise ValueError('Returned status from alarm is not valid.' )
        
        return current_status
    
    
    def get_last_event(self):
        last_event = ''
        try:
            event_log = self.alarm.event_log()
            last_event = event_log[0]['EventType'] 
            logging.debug('Retrieved last event [' + last_event )
        except:
            logging.error('Could not get last event.', exc_info=True)

        return last_event
    
    def arm_annex(self, notify = False):
        try:
            self.alarm.arm_annex()
            if notify:
                emailNotify("Annex armed","The annex was armed.")
        except:
            logging.error('Could not arm annex.', exc_info=True)
    
    def optionalArm(self, status, notify):
        if (status['AlarmStatus'] == 'armed') and (status['StatusAnnex'] == 'disarmed'):
            if activator.get_last_event() == 'armed':
                logging.info('Arming annex')
                self.arm_annex(notify)   

if __name__ == '__main__':
    activator = AnnexActivator()

    status = None
    
    try:
        status = activator.get_status()
    except:
        logging.error('Could not get status from Alarm.', exc_info=True)
        sys.exit(1)
    
    logging.debug("Alarm status is " + status['AlarmStatus'])
    logging.debug("Annex status is " + status['StatusAnnex'])
    arguments= sys.argv[1:]
    
    notify = False
    optional = True
    
    try:
        opts, args= getopt.getopt(sys.argv[1:], 'hnf', '')
    except getopt.GetoptError:
        __printMessage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            __printMessage()
        elif opt == '-f':
            optional = False
        elif opt =='-n':
            notify = True
        else:
            optional = True
    try:
        if optional:
            activator.optionalArm(status, notify)
        else:
            activator.arm_annex(notify)
    except:
        logging.error('Something went wrong.', exc_info=True)
        sys.exit(1)