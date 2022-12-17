import pytest
from tests.test_endpoints.test_authorized_endpoints.base_test_class import BaseTest

class TestComplex(BaseTest):

    @pytest.mark.server
    def test_get_complexes_list(self):
        response = self.session.get(self.base_url + "/complex/list", headers=self.headers)
        assert response.status_code == 200
        data: dict = response.json()
        assert data.get('user') is not None
        assert data.get('complexes') is not None

    @pytest.mark.server
    def test_get_viewed_complexes_list(self):
        response = self.session.get(self.base_url + "/complex/viewed/list", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get('viewed') is not None
        assert data.get('user') is not None
        assert data.get('complexes') is not None


    @pytest.mark.skip("Not delete relations viewed complexes")
    def test_set_viewed_complex(self):
        response = self.session.get(
            self.base_url + "/complex/complex_viewed/1", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get('level_up') is not None
