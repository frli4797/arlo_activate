#!/usr/bin/python3

import json
import logging
import tempfile
import os
import configparser
import sys

import sectoralarm
import annex_activate


class alarm_state:
    """
    Alarm state class.
    Consists of a dirty bit and the actual state.
    """

    dirty = False
    state = ""

    def __init__(self, dirty, state):
        self.dirty = dirty
        self.state = state


class arlo_activator:
    """
    Container class for Arlo Activator.
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.cfg')
        numeric_level = getattr(logging, config.get('Logging', 'level').upper(), None)
        log_location = config.get('Logging', 'log_location')
        logfile = os.path.join(log_location, 'arlo_activate.log')
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                            filename=logfile, level=numeric_level)
        self.alarm_email = config.get('Alarm', 'email')
        self.alarm_password = config.get('Alarm', 'password')
        self.alarm_siteId = config.get('Alarm', 'siteId')
        self.alarm_panel_code = config.get('Alarm', 'panel_code')

        self.arlo_email = config.get('Arlo', 'email')
        self.arlo_password = config.get('Arlo', 'password')

        self.alarm = sectoralarm.Connect(self.alarm_email, self.alarm_password, self.alarm_siteId)
        self.arlo = None

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
            return alarm_state(False, current_status)
        else:
            logging.debug('Setting to dirty.')
            return alarm_state(True, current_status)

    def __getArlo(self):
        """
        Lazy loads Arlo.
        """
        if self.arlo is None:
            from pyarlo import PyArlo
            self.arlo = PyArlo(self.arlo_email, self.arlo_password)
            logging.debug('Lazy loading Arlo')
        return self.arlo

    def get_arlo_mode(self):
        """
        Returns the Arlo mode.
        """
        from pyarlo import PyArlo
        arlo = PyArlo(self.arlo_email, self.arlo_password)

        if arlo is None or arlo.base_stations is None:
            logging.error('Could not read arlo base station.')
            raise TypeError('Could not read arlo base station.')

        base = arlo.base_stations[0]

        arlo_mode = base.mode

        if arlo_mode is None:
            logging.error('Could not read arlo mode.')
            raise TypeError('Could not read arlo mode.')

        logging.info("Is mode " + arlo_mode)
        return arlo_mode

    def set_arlo_mode(self, mode_name):
        """
        Sets Arlo mode to mode_name
        """

        try:
            from pyarlo import PyArlo
            arlo = PyArlo(self.arlo_email, self.arlo_password)

            base = arlo.base_stations[0]

            logging.info("Setting Arlo mode to " + mode_name)
            base.mode = mode_name
            annex_activate.email_notify('Arlo change',
                                        'Alarm change state. Changing state of Arlo to [' + mode_name + '].')
        except TypeError:
            logging.error('Got type error. Doing nothing. ', exc_info=True)


if __name__ == '__main__':
    activator = arlo_activator()

    alarm_status = 'none'

    try:
        alarm_status = activator.get_alarm_status()
        logging.debug("Alarm status is " + alarm_status.state['AlarmStatus'])
    except:
        logging.error("Could not read status.", exc_info=True)
        sys.exit(1)

    if not alarm_status.dirty:
        logging.debug('Not dirty. Doing nothing.')
    else:
        if alarm_status.state['AlarmStatus'] == 'armed':
            activator.set_arlo_mode('armed')
        else:
            activator.set_arlo_mode('schedule')
