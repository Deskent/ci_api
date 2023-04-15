import pytest


class BaseTest:

    @pytest.fixture(autouse=True)
    def setUp(self, setup_class):
        self.session = setup_class.session
        self.test_user = setup_class.test_user
        self.base_url = setup_class.base_url
        self.user_create = setup_class.user_create
        self.user_payload = setup_class.user_payload
        self.headers = setup_class.headers
        self.email_token = setup_class.email_token
        self.alarm_id = setup_class.alarm_id
        self.push_token = setup_class.push_token
        self.user_id = None
        yield
