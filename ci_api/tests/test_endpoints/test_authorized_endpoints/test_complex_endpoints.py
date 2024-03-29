from tests.test_endpoints.test_authorized_endpoints.base_test_class import BaseTest


class TestComplex(BaseTest):

    def test_get_complex_by_id(self):
        response = self.session.get(self.base_url + "/complex/1", headers=self.headers)
        assert response.status_code == 200
        data: dict = response.json()
        assert data.get('videos') is not None
        assert data.get('name') is not None

    def test_get_complexes_state(self):
        response = self.session.get(self.base_url + "/complex/state", headers=self.headers)
        assert response.status_code == 200
        data: dict = response.json()
        user: dict = data.get('user')
        assert user.get('id') == self.user_id
        assert data.get('not_viewed_complexes') is not None

    def test_set_viewed_complex(self):
        payload = {"id": 1}
        response = self.session.post(
            self.base_url + "/complex/set_viewed", headers=self.headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get('level_up') is not None
