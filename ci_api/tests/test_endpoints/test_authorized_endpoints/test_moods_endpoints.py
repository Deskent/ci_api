import random

from tests.test_endpoints.test_authorized_endpoints.base_test_class import BaseTest


class TestMoods(BaseTest):

    def test_get_all_moods(self):
        response = self.session.get(
            self.base_url + "/moods/", headers=self.headers)
        assert response.status_code == 200

    def test_set_mood(self):
        payload = {"mood_id": 1}
        response = self.session.put(
            self.base_url + "/moods/set_user_mood", json=payload, headers=self.headers)
        assert response.status_code == 204

    def test_get_mood(self):
        response = self.session.get(
            self.base_url + "/moods/", headers=self.headers)
        assert response.status_code == 200
        all_moods: list[dict] = response.json()
        random_mood: dict = random.choice(all_moods)
        mood_id: int = random_mood['id']
        payload: dict = {"mood_id": mood_id}
        response = self.session.put(
            self.base_url + "/moods/set_user_mood", json=payload, headers=self.headers)
        assert response.status_code == 204
        response = self.session.get(
            self.base_url + "/moods/get_user_mood", headers=self.headers)
        assert response.status_code == 200
        assert response.json().get('id') == mood_id
