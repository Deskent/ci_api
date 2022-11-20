import pytest


# @pytest.mark.skip
class TestUsers:

    @pytest.mark.asyncio
    def create_user(self):
        response = self.session.post(self.base_url + "/auth/register", json=self.user_create)
        assert response.status_code == 200

        response = self.session.post(self.base_url + "/auth/login", json=self.user_payload)
        assert response.status_code == 200
        token = response.json().get('token')

        return {'Authorization': f"Bearer {token}"}

    @pytest.mark.asyncio
    def create_alarm(self, new_alarm):
        response = self.session.post(
            self.base_url + "/alarms", headers=self.headers, json=new_alarm,
            allow_redirects=True
        )
        assert response.status_code == 200
        alarm_id = response.json().get("id")
        assert alarm_id
        return alarm_id

    @pytest.mark.asyncio
    def create_notification(self, new_notification):
        response = self.session.post(
            self.base_url + "/notifications", headers=self.headers, json=new_notification,
            allow_redirects=True
        )
        assert response.status_code == 200
        notification_id = response.json().get("id")
        assert notification_id
        return notification_id

    @pytest.mark.asyncio
    def delete_notification(self):
        response = self.session.delete(self.base_url + f"/notifications/{self.notification_id}",
            headers=self.headers, allow_redirects=True)
        assert response.status_code == 204

    @pytest.mark.asyncio
    def delete_alarm(self):
        response = self.session.delete(self.base_url + f"/alarms/{self.alarm_id}",
            headers=self.headers, allow_redirects=True)
        assert response.status_code == 204

    @pytest.mark.asyncio
    def delete_user(self):
        response = self.session.delete(self.base_url + "/users",
            headers=self.headers, allow_redirects=True)
        assert response.status_code == 204

    @pytest.fixture
    def setUp(self, get_test_app, base_url, user_create, user_payload, new_alarm, new_notification):
        self.session = get_test_app
        self.base_url = base_url
        self.user_create = user_create
        self.user_payload = user_payload
        self.headers = self.create_user()
        self.alarm_id = self.create_alarm(new_alarm)
        self.notification_id = self.create_notification(new_notification=new_notification)
        yield self.headers
        self.delete_user()

    @pytest.mark.asyncio
    def test_get_me(self, setUp):
        response = self.session.get(self.base_url + "/users/me", headers=self.headers)
        assert response.status_code == 200
        assert response.json().get("id") is not None

    @pytest.mark.asyncio
    def test_verify_email(self, setUp, token):
        url = self.base_url + "/auth/verify_email" + f"?token={token}"
        response = self.session.get(url)
        assert response.status_code == 202

    @pytest.mark.asyncio
    async def test_login_endpoint(self, setUp):
        response = self.session.post(self.base_url + "/auth/login", json=self.user_payload)
        assert response.status_code == 200
        token = response.json().get("token")
        assert token is not None

    @pytest.mark.asyncio
    async def test_get_user_alarms(self, setUp):
        response = self.session.get(self.base_url + "/users/alarms", headers=self.headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_user_notifications(self, setUp):
        response = self.session.get(self.base_url + "/users/notifications", headers=self.headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_change_password(self, setUp):
        payload = {
            "old_password": self.user_payload["password"],
            "password": self.user_payload["password"],
            "password2": self.user_payload["password"]
        }
        response = self.session.put(self.base_url + "/auth/change_password", json=payload, headers=self.headers)
        assert response.status_code == 202

    @pytest.mark.asyncio
    async def test_get_video_by_id(self, setUp):
        response = self.session.get(self.base_url + "/videos/1", headers=self.headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_notification_by_id(self, setUp):
        response = self.session.get(
            self.base_url + f"/notifications/{self.notification_id}", headers=self.headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_alarm(self, setUp, new_alarm):
        response = self.session.get(self.base_url + f"/alarms/{self.alarm_id}", headers=self.headers)
        assert response.status_code == 200
