import pytest
from tests.test_endpoints.test_authorized_endpoints.base_test_class import BaseTest


class TestAlarms(BaseTest):
    @pytest.mark.server
    def test_get_alarm(self):
        response = self.session.get(self.base_url + f"/alarms/{self.alarm_id}", headers=self.headers)
        assert response.status_code == 200

    @pytest.mark.server
    def test_get_alarms_list(self):
        response = self.session.get(self.base_url + "/users/alarms/list", headers=self.headers)
        assert response.status_code == 200
        data: list = response.json()
        assert data is not None
        assert isinstance(data, list)
