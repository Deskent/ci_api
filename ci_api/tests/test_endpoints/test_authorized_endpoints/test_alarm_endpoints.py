from tests.test_endpoints.test_authorized_endpoints.base_test_class import BaseTest


class TestAlarms(BaseTest):

    def test_get_alarm(self):
        response = self.session.get(
            self.base_url + f"/alarms/{self.alarm_id}", headers=self.headers)
        assert response.status_code == 200

    def test_get_alarm_without_headers(self):
        response = self.session.get(self.base_url + f"/alarms/{self.alarm_id}")
        assert response.status_code == 403

    def test_get_alarms_list(self):
        response = self.session.get(self.base_url + "/users/alarms/list", headers=self.headers)
        assert response.status_code == 200
        data: list = response.json()
        assert data is not None
        assert isinstance(data, list)

    def test_get_update_alarm(self):
        response = self.session.get(self.base_url + "/users/alarms/list", headers=self.headers)
        assert response.status_code == 200

        data: list = response.json()
        alarm: dict = data[0]
        alarm_id = alarm.get('id')
        assert alarm_id

        response = self.session.get(self.base_url + f"/alarms/{alarm_id}", headers=self.headers)
        assert response.status_code == 200

        new_vibration = not alarm['vibration']
        new_data = {
            "volume": 10,
            "vibration": new_vibration,
        }
        response = self.session.put(
            self.base_url + f"/alarms/{alarm_id}", headers=self.headers, json=new_data
        )
        assert response.status_code == 200
        alarm_data: dict = response.json()
        assert alarm_data['volume'] == new_data['volume']
        assert alarm_data['vibration'] == new_vibration
