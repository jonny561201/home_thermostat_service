import json

from mock import MagicMock, patch

from svc.controllers.hvac_queue_controller import update_hvac_worker


@patch('svc.controllers.hvac_queue_controller.file_utils')
class TestUpdateHvacWorker:
    TASKS = [{'taskId': 'task-1', 'alarmDays': 'MonTue', 'hvacStart': '06:00:00', 'hvacStop': '22:00:00',
              'hvacStartTemp': 21.0, 'hvacStopTemp': 18.0, 'hvacMode': 'heating'}]

    def _delivery(self):
        method = MagicMock()
        method.delivery_tag = 'tag'
        channel = MagicMock()
        return channel, method

    def _body(self, payload):
        return json.dumps(payload).encode('UTF-8')

    def test_set__should_save_desired_state(self, mock_file):
        channel, method = self._delivery()
        body = self._body({'action': 'set', 'desiredTemp': 21.5, 'mode': 'heating'})

        update_hvac_worker(channel, method, None, body)

        mock_file.save_desired_state.assert_called_once_with(21.5, 'heating')
        channel.basic_ack.assert_called_once_with(delivery_tag='tag')

    def test_set__should_nack_when_mode_missing(self, mock_file):
        channel, method = self._delivery()
        body = self._body({'action': 'set', 'desiredTemp': 21.5})

        update_hvac_worker(channel, method, None, body)

        mock_file.save_desired_state.assert_not_called()
        channel.basic_nack.assert_called_once_with(delivery_tag='tag', requeue=False)

    def test_schedule__should_save_tasks(self, mock_file):
        channel, method = self._delivery()
        body = self._body({'action': 'schedule', 'tasks': self.TASKS})

        update_hvac_worker(channel, method, None, body)

        mock_file.save_schedule.assert_called_once_with(self.TASKS)
        channel.basic_ack.assert_called_once_with(delivery_tag='tag')

    def test_schedule__should_nack_when_tasks_missing(self, mock_file):
        channel, method = self._delivery()
        body = self._body({'action': 'schedule'})

        update_hvac_worker(channel, method, None, body)

        mock_file.save_schedule.assert_not_called()
        channel.basic_nack.assert_called_once_with(delivery_tag='tag', requeue=False)

    def test_update_hvac_worker__should_nack_when_body_is_not_json(self, mock_file):
        channel, method = self._delivery()

        update_hvac_worker(channel, method, None, b'not-json')

        channel.basic_nack.assert_called_once_with(delivery_tag='tag', requeue=False)
