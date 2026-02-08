def test_search_success():
    url = "http://13.57.30.18:8080/"
    params = {
        "keyword": "music",
        "location": "NewYork"
    }

    r = requests.get(url, params=params)

    assert r.status_code == 200
    data = r.json()
    assert "events" in data
    assert isinstance(data["events"], list)
    print(data["events"])

