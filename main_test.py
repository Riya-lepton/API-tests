from fastapi.testclient import TestClient
from main import api

client = TestClient(api)


def test_catchments():
    # make query without latitude and longitude, should fail with 422 status code
    response = client.get("/geojson/catchment")
    assert response.status_code == 422

    # make query from Delhi, should return 1km catchment
    response = client.get("/geojson/catchment?latitude=28.7041&longitude=77.1025")
    assert response.status_code == 200


def test_get_places():
    # create a function which generates a query with region and catrgory and name
    def generate_query(region, category, name):
        return f"/geojson/places?region={region}&category={category}&name={name}&fields=address"

    # Test a successful request with valid data
    response = client.get(
        "/geojson/places?name=places&fields=address&category=shopping&region=181328,159333"
    )
    assert response.status_code == 200

    response = client.get(
        "/geojson/places?region=159333&category=shopping&name=places&fields=address"
    )
    assert response.status_code == 200

    # Test a request that returns no places
    response = client.get(
        "/geojson/places?name=places&fields=address&category=shopping&region=181"
    )
    assert response.status_code == 404

    # test a request that returns a json response
    # select ST_Area ( boundary_geom  ),id  from region order by 1 limit 10 // to select smallest area
    response = client.get(
        "/geojson/places?region=167330&category=shopping&name=Tailor&fields=address,subcategory"
    )
    assert response.status_code == 200
    expected_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "geometry": {"type": "Point", "coordinates": [86.43404, 23.796692]},
                "properties": {
                    "id": 17576066,
                    "name": "Pamicy Store",
                    "category": "shopping_places",
                    "address": "",
                    "subcategory": "other_shopping_centres",
                },
            },
            {
                "geometry": {"type": "Point", "coordinates": [86.43404, 23.796692]},
                "properties": {
                    "id": 17576130,
                    "name": "Men Parlour",
                    "category": "shopping_places",
                    "address": "",
                    "subcategory": "shopping_retail_shops",
                },
            },
        ],
    }

    response_data = response.json()
    assert response_data == expected_data

    # Test a request that causes an internal server error
    response = client.get("/geojson/places")
    print(response)
    assert response.status_code == 422


if __name__ == "__main__":
    test_get_places()  # test_catchments()
    print("All tests passed!")
