#!/usr/bin/python3

import json
import requests
import logging
import tempfile
import os
import configparser
import sys

import sectoralarm
from requests import HTTPError


class AlarmState:
    """
    Alarm state class.
    Consists of a dirty bit and the actual state.
    """

    dirty = False
    state = ""

    def __init__(self, dirty, state):
        self.dirty = dirty
        self.state = state


class StringifyActivator:
    """
    Container class for Arlo Activator.
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('stringify_activator.cfg')
        numeric_level = getattr(logging, config.get('Logging', 'level').upper(), None)
        log_location = config.get('Logging', 'log_location')
        logfile = os.path.join(log_location, 'stringify_activator.log')
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                            filename=logfile, level=numeric_level)
        self.alarm_email = config.get('Alarm', 'email')
        self.alarm_password = config.get('Alarm', 'password')
        self.alarm_siteId = config.get('Alarm', 'siteId')
        self.alarm_panel_code = config.get('Alarm', 'panel_code')

        self.activation_url = config.get('Stringify', 'activate_url')
        self.deactivation_url = config.get('Stringify', 'deactivate_url')

        self.alarm = sectoralarm.Connect(self.alarm_email, self.alarm_password, self.alarm_siteId, self.alarm_panel_code)

    def get_alarm_status(self):
        """
        Returns alarm state as an alarm_state.
        """

        status_file = os.path.join(tempfile.gettempdir(), 'alarm_state')
        logging.debug('Tempfile ' + status_file)
        current_status = self.alarm.status()
        logging.debug(json.dumps(current_status))

        if current_status['AlarmStatus'] not in {'armed', 'disarmed'} or \
                current_status['StatusAnnex'] not in {'armed', 'disarmed'}:
            logging.error("Alarm status is " + current_status['AlarmStatus'])
            logging.error("Annex status is " + current_status['StatusAnnex'])
            raise ValueError('Returned status from alarm is not valid.')

        saved_status = {'AlarmStatus': 'notset'}

        if os.path.isfile(status_file):
            with open(status_file, 'r+') as result_file:
                saved_status = json.load(result_file)
                result_file.seek(0)
                result_file.truncate()
                json.dump(current_status, result_file)
                result_file.close()
                logging.debug('New stored status: ' + saved_status['AlarmStatus'])
        else:
            with open(status_file, 'w') as result_file:
                json.dump(current_status, result_file)
                result_file.close()

        logging.debug('Stored status: ' + saved_status['AlarmStatus'])
        logging.debug('Current status: ' + current_status['AlarmStatus'])

        if current_status['AlarmStatus'] == saved_status['AlarmStatus']:
            logging.debug('Setting to not dirty.')
            return AlarmState(False, current_status)
        else:
            logging.debug('Setting to dirty.')
            return AlarmState(True, current_status)

    def send_stringify(self, activation):
        """
        Sends event to Stringify
        """

        try:
            if activation:
                url = self.activation_url
            else:
                url = self.deactivation_url

            logging.info("Sending request to stringify " + url)
            result = requests.post(url)
            logging.debug("Result " + str(result.status_code) + " " + result.text)
            result.raise_for_status()

        except HTTPError:
            logging.error('Got type error. Doing nothing. ', exc_info=True)


if __name__ == '__main__':
    event_sender = StringifyActivator()
    alarm_status = 'none'

    try:
        alarm_status = event_sender.get_alarm_status()
        logging.debug("Alarm status is " + alarm_status.state['AlarmStatus'])
    except:
        logging.error("Could not read status.", exc_info=True)
        sys.exit(1)

    if not alarm_status.dirty:
        logging.debug('Not dirty. Doing nothing.')
    else:
        if alarm_status.state['AlarmStatus'] == 'armed':
            event_sender.send_stringify(True)
        else:
            event_sender.send_stringify(False)
