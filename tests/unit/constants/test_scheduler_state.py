import datetime
import uuid
from threading import Event

import mock

from src.constants.home_automation import Automation
from src.constants.scheduler_state import TaskState
from src.constants.thread_state import HvacState
from src.utilities.event_utils import MyThread


@mock.patch('src.constants.scheduler_state.create_thread')
class TestLightState:
    DAYS = 'MonTueWed'
    TASK_ID = str(uuid.uuid4())
    STOP_TIME = datetime.time.fromisoformat('22:00:00')
    START_TIME = datetime.time.fromisoformat('08:00:00')

    def setup_method(self):
        self.STATE = TaskState.get_instance()
        self.STATE.SCHEDULED_TASKS = []

    @mock.patch('src.constants.scheduler_state.HvacState')
    def test_add_hvac_task__should_create_the_event_thread(self, mock_state, mock_thread):
        self.STATE.add_hvac_task(self.TASK_ID, self.DAYS, self.START_TIME, self.STOP_TIME)

        mock_thread.assert_called_with(mock.ANY, Automation.TIME.ONE_MINUTE)
        mock_state.assert_called()

    def test_add_hvac_task__should_store_the_thread_on_the_alarm_list(self, mock_thread):
        self.STATE.add_hvac_task(self.TASK_ID, self.DAYS, self.START_TIME, self.STOP_TIME)

        assert len(self.STATE.SCHEDULED_TASKS) == 1

    def test_add_hvac_task__should_start_the_newly_created_thread(self, mock_thread):
        mock_alarm = mock.create_autospec(MyThread)
        mock_thread.return_value = mock_alarm
        self.STATE.add_hvac_task(self.TASK_ID, self.DAYS, self.START_TIME, self.STOP_TIME)

        mock_alarm.start.assert_called()

    def test_add_hvac_task__should_not_create_thread_when_it_already_exists(self, mock_thread):
        alarm = HvacState(self.TASK_ID, self.DAYS, self.START_TIME, self.STOP_TIME)
        self.STATE.SCHEDULED_TASKS.append(alarm)
        self.STATE.add_hvac_task(self.TASK_ID, self.DAYS, self.START_TIME, self.STOP_TIME)

        mock_thread.assert_not_called()

    def test_add_hvac_task__should_create_thread_when_other_non_matching_threads(self, mock_thread):
        alarm = HvacState(str(uuid.uuid4()), self.DAYS, self.START_TIME, self.STOP_TIME)
        self.STATE.SCHEDULED_TASKS.append(alarm)
        self.STATE.add_hvac_task(self.TASK_ID, self.DAYS, self.START_TIME, self.STOP_TIME)

        mock_thread.assert_called()

    def test_remove_light_alarm__should_remove_item_from_list_with_matching_task_id(self, mock_thread):
        event = mock.create_autospec(Event)
        my_alarm = mock.create_autospec(MyThread)
        my_alarm.stopped = event
        alarm = HvacState(self.TASK_ID, self.DAYS, self.START_TIME, self.STOP_TIME)
        alarm.ACTIVE_THREAD = my_alarm
        self.STATE.SCHEDULED_TASKS.append(alarm)
        self.STATE.remove_task(self.TASK_ID)

        assert self.STATE.SCHEDULED_TASKS == []

    def test_remove_light_alarm__should_not_remove_item_from_list_with_different_task_id(self, mock_thread):
        alarm = HvacState(str(uuid.uuid4()), self.DAYS, self.START_TIME, self.STOP_TIME)
        self.STATE.SCHEDULED_TASKS.append(alarm)
        self.STATE.remove_task(self.TASK_ID)

        assert self.STATE.SCHEDULED_TASKS == [alarm]

    def test_remove_light_alarm__should_stop_matching_alarms(self, mock_thread):
        event = mock.create_autospec(Event)
        my_alarm = mock.create_autospec(MyThread)
        my_alarm.stopped = event
        alarm = HvacState(self.TASK_ID, self.DAYS, self.START_TIME, self.STOP_TIME)
        alarm.ACTIVE_THREAD = my_alarm
        self.STATE.SCHEDULED_TASKS.append(alarm)
        self.STATE.remove_task(self.TASK_ID)

        event.set.assert_called()
