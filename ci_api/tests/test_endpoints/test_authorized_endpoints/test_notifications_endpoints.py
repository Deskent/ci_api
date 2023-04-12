import datetime

from tests.test_endpoints.test_authorized_endpoints.base_test_class import BaseTest


class TestNotifications(BaseTest):

    def test_create_notification(self):
        payload = {
            "created_at": f"{datetime.datetime.now()}",
            "text": "Test notif"
        }
        response = self.session.post(
            self.base_url + "/notifications/", headers=self.headers, json=payload)
        assert response.status_code == 200
        data: dict = response.json()
        assert data is not None
        assert data.get('id') is not None

    def test_get_notifications(self):
        response = self.session.get(
            self.base_url + "/users/notifications/", headers=self.headers)
        assert response.status_code == 200
        notifications: list[dict] = response.json()
        notification_id = notifications[0].get("id")
        assert notification_id is not None

        response = self.session.get(
            self.base_url + f"/notifications/{notification_id}/", headers=self.headers)
        assert response.status_code == 200
