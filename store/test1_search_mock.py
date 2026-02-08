import pytest
from unittest.mock import patch

@pytest.mark.parametrize(  # 先用一个字符串写明 key，再用一个列表写 value，用元组装
    "keyword, distance, location",
    [
        ("music", "10", "Los Angeles"),
        ("", "10", "Los Angeles"),
        ("%%%%", "10", "Los Angeles"),
        ("music", "0", "Los Angeles"),
        ("music", "999", "Los Angeles"),
    ]
)
def test_search_param_with_mock(client, keyword, distance, location):
    mock_events = [  # 直接写明要返回的结果
        {
            "Event": "Mock Event",
            "Date": "2026-01-01",
            "Genre": "Music",
            "Id": "mock-id"
        }
    ]

    with patch("main.find_events", return_value=mock_events):  # 写明要测试哪个函数，并恒返回之前那个结果
        response = client.get(
            "/search",
            query_string={
                "keyword": keyword,
                "distance": distance,
                "category": "Default",
                "location": location
            }
        )

        assert response.status_code == 200  # 断言，全过了这个测试文件就过了
        data = response.get_json()
        assert data[0]["Id"] == "mock-id"
