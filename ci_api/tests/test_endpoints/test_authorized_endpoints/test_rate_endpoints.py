from tests.test_endpoints.test_authorized_endpoints.base_test_class import BaseTest


class TestRates(BaseTest):

    def test_get_rates(self):
        response = self.session.get(self.base_url + "/rates", headers=self.headers)
        assert response.status_code == 200
        data: list[dict] = response.json()
        assert data is not None
        assert isinstance(data, list)

    def test_get_rate_by_id_api(self):
        rate_id = 2
        response = self.session.get(
            self.base_url + f"/rates/{rate_id}", headers=self.headers)
        assert response.status_code == 200
        assert response.json().get('link') is not None

    def test_unsubscribe(self):
        response = self.session.delete(self.base_url + "/rates/", headers=self.headers)
        assert response.status_code == 202
