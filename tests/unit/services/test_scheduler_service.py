import uuid

from mock import patch

from src.constants.settings_state import Settings
from src.constants.thread_state import AutoHvacState
from src.services.scheduler_service import schedule_hvac_tasks


@patch('src.services.scheduler_service.TaskState')
@patch('src.services.scheduler_service.get_hvac_tasks_by_user')
class TestLightService:
    DAYS = 'MonTue'
    USER_ID = 'def098'
    MODE = 'HEAT'
    TYPE = 'hvac'
    START = '05:30:00'
    STOP = '16:50:00'
    START_TEMP = 20
    STOP_TEMP = 16
    TASK_ID = str(uuid.uuid4())

    def setup_method(self):
        self.SETTINGS = Settings.get_instance()
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'UserId': self.USER_ID}

    def test_schedule_hvac_tasks__should_make_call_to_get_hvac_tasks_by_user(self, mock_tasks, mock_state):
        schedule_hvac_tasks()

        mock_tasks.assert_called_with(self.USER_ID)

    def test_schedule_hvac_tasks__should_not_call_add_replace_alarm_when_alarm_time_none(self, mock_tasks, mock_state):
        mock_tasks.return_value = [{'alarm_days': self.DAYS, 'task_type': self.TYPE, 'hvac_mode': self.MODE, 'hvac_start': self.START, 'hvac_stop': self.STOP, 'task_id': self.TASK_ID}]
        schedule_hvac_tasks()

        mock_state.get_instance.return_value.add_hvac_task.assert_not_called()

    def test_schedule_hvac_tasks__should_not_call_add_replace_alarm_when_disabled(self, mock_tasks, mock_state):
        mock_tasks.return_value = [{'alarm_days': self.DAYS, 'task_type': self.TYPE, 'hvac_mode': self.MODE, 'hvac_start': self.START, 'hvac_stop': self.STOP, 'task_id': self.TASK_ID, 'enabled': False}]
        schedule_hvac_tasks()

        mock_state.get_instance.return_value.add_hvac_task.assert_not_called()

    def test_schedule_hvac_tasks__should_not_call_add_replace_alarm_when_alarm_days_none(self, mock_tasks, mock_state):
        mock_tasks.return_value = [{'alarm_days': self.DAYS, 'task_type': self.TYPE, 'hvac_mode': self.MODE, 'hvac_start': self.START, 'hvac_stop': self.STOP, 'task_id': self.TASK_ID}]
        schedule_hvac_tasks()

        mock_state.get_instance.return_value.add_hvac_task.assert_not_called()

    def test_schedule_hvac_tasks__should_not_call_add_light_alarm_when_light_tasks_are_none(self, mock_tasks, mock_state):
        mock_tasks.return_value = None
        schedule_hvac_tasks()

        mock_state.get_instance.return_value.add_hvac_task.assert_not_called()

    def test_schedule_hvac_tasks__should_not_call_add_replace_alarm_when_alarm_group_id_none(self, mock_tasks, mock_state):
        mock_tasks.return_value = [{'alarm_days': self.DAYS, 'task_type': self.TYPE, 'hvac_mode': self.MODE, 'hvac_start': self.START, 'hvac_stop': self.STOP, 'task_id': self.TASK_ID}]
        schedule_hvac_tasks()

        mock_state.get_instance.return_value.add_hvac_task.assert_not_called()

    def test_schedule_hvac_tasks__should_call_add_alarm(self, mock_tasks, mock_state):
        task = {'alarm_days': self.DAYS, 'task_type': self.TYPE, 'hvac_mode': self.MODE, 'hvac_start': self.START, 'hvac_stop': self.STOP, 'task_id': self.TASK_ID, 'enabled': True}
        mock_tasks.return_value = [task]
        schedule_hvac_tasks()

        mock_state.get_instance.return_value.add_hvac_task.assert_called_with(task)

    def test_schedule_hvac_tasks__should_call_remove_light_on_items_missing_from_api_response(self, mock_tasks, mock_state):
        other_task = str(uuid.uuid4())
        missing_task = str(uuid.uuid4())
        pref_one = {'alarm_days': self.DAYS, 'task_type': self.TYPE, 'hvac_mode': self.MODE, 'hvac_start': self.START, 'hvac_stop': self.STOP, 'task_id': self.TASK_ID, 'enabled': True}
        pref_two = {'alarm_days': self.DAYS, 'task_type': self.TYPE, 'hvac_mode': self.MODE, 'hvac_start': self.START, 'hvac_stop': self.STOP, 'task_id': other_task, 'enabled': True}
        alarm_one = AutoHvacState(self.TASK_ID, self.DAYS, self.START, self.STOP, self.START_TEMP, self.STOP_TEMP)
        alarm_two = AutoHvacState(other_task, self.DAYS, self.START, self.STOP, self.START_TEMP, self.STOP_TEMP)
        alarm_three = AutoHvacState(missing_task, self.DAYS, self.START, self.STOP, self.START_TEMP, self.STOP_TEMP)
        mock_state.get_instance.return_value.SCHEDULED_TASKS = [alarm_one, alarm_two, alarm_three]
        mock_tasks.return_value = [pref_one, pref_two]
        schedule_hvac_tasks()

        mock_state.get_instance.return_value.remove_task.assert_called_with(missing_task)

    def test_schedule_hvac_tasks__should_not_fail_when_api_call_returns_empty_list(self, mock_tasks, mock_state):
        mock_tasks.return_value = []
        mock_state.get_instance.return_value.SCHEDULED_TASKS = []
        schedule_hvac_tasks()

        mock_state.get_instance.return_value.add_hvac_task.assert_not_called()
        mock_state.get_instance.return_value.remove_task.assert_not_called()

    @patch('src.services.scheduler_service.logging')
    def test_schedule_hvac_tasks__should_log_when_exception(self, mock_log, mock_tasks, mock_state):
        error = TimeoutError()
        mock_tasks.side_effect = error
        schedule_hvac_tasks()

        mock_log.error.assert_called_with(error)
