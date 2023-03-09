def test_get_meta_info(get_test_client_app, base_url):
    response = get_test_client_app.get(base_url + '/users/get_meta')
    assert response.status_code == 200
    data = response.json()
    assert data['company_email']
    assert data["company_phone"]
    assert data["company_represent_phone"]
    assert data["google_play_link"]
    assert data["app_store_link"]
    assert data["vk_link"]
    assert data["youtube_link"]
