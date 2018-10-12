import arlo_activate
import unittest
import os
import tempfile
import json
import time
from unittest.mock import MagicMock


class arlo_activator_test(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.activator = arlo_activate.arlo_activator()

    def __write_disarmed(self):
        status_file = os.path.join(tempfile.gettempdir(), 'alarm_state')
        status = '{"StatusAnnex": "disarmed", "AnnexAvailable": null, "AlarmStatus": "disarmed"}'
        with open(status_file, 'w') as result_file:
            result_file.truncate()
            result_file.write(status)
            result_file.close()

    def __write_armed(self):
        status_file = os.path.join(tempfile.gettempdir(), 'alarm_state')
        status = '{"StatusAnnex": "disarmed", "AnnexAvailable": null, "AlarmStatus": "armed"}'
        with open(status_file, 'w') as result_file:
            result_file.truncate()
            result_file.write(status)
            result_file.close()

    def __read_tmp(self):
        status_file = os.path.join(tempfile.gettempdir(), 'alarm_state')
        with open(status_file, 'r') as result_file:
            result_json = json.load(result_file)
            result_file.close()
        return result_json

    def test_status_should_be_schedule(self):
        self.activator.set_arlo_mode('schedule')
        mode = self.activator.get_arlo_mode()

        self.assertTrue(mode in ['schedule'], 'Mode should be schedule.')

    def test_status_should_be_armed(self):
        self.activator.set_arlo_mode('armed')
        mode = self.activator.get_arlo_mode()

        self.assertEqual(mode, 'armed', 'Mode should be armed.')

    def test_disarmed_armed_should_be_dirty(self):
        self.activator.alarm.status = MagicMock(
            return_value={"StatusAnnex": "disarmed", "AnnexAvailable": None, "AlarmStatus": "armed"})
        self.__write_disarmed()
        alarm_status = self.activator.get_alarm_status()

        self.assertEqual(alarm_status.dirty, True, 'Should be dirty')
        self.assertEqual(alarm_status.state['AlarmStatus'], 'armed', 'Should be armed')
        stored = self.__read_tmp()
        self.assertEqual(alarm_status.state['AlarmStatus'], stored['AlarmStatus'],
                         'Stored state is wrong, should be armed.')

    def test_disarmed_armed_should_be_not_dirty(self):
        self.activator.alarm.status = MagicMock(
            return_value={"StatusAnnex": "disarmed", "AnnexAvailable": None, "AlarmStatus": "disarmed"})
        self.__write_disarmed()
        alarm_status = self.activator.get_alarm_status()

        self.assertEqual(alarm_status.dirty, False, 'Should be dirty')
        self.assertEqual(alarm_status.state['AlarmStatus'], 'disarmed', 'Should be disarmed')
        stored = self.__read_tmp()
        self.assertEqual(alarm_status.state['AlarmStatus'], stored['AlarmStatus'],
                         'Stored state is wrong, should be disarmed.')

    def tearDown(self):
        time.sleep(1)


if __name__ == '__main__':
    unittest.main()
