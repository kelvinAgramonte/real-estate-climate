import pandas as pd
from src.transform import transform

def make_dfs():
    listings = pd.DataFrame([
        {"apn":"123-456-789","address":"123 Main St","city":"Miami","state":"FL","zip":"33101","price":"250000","beds":"3","baths":"2","sqft":"1600","status":"for_sale"},
        {"apn":"123456789","address":"123 Main Street","city":"Miami","state":"FL","zip":"33101","price":"260000","beds":"3","baths":"2","sqft":"1600","status":"for_sale"},
        {"apn":"222-333-444","address":"88 Palm Ave","city":"Orlando","state":"FL","zip":"32801","price":"310000","beds":"4","baths":"3","sqft":"2000","status":"pending"},
        {"apn":"666-777-888","address":"12 Bay Blvd","city":"Miami","state":"FL","zip":"33101","price":"1200000","beds":"5","baths":"4","sqft":"3000","status":"withdrawn"},
        {"apn":"555-666-777","address":"99 Lake Rd","city":"Orlando","state":"FL","zip":"32801","price":"400000","beds":"4","baths":"3","sqft":"","status":"for_sale"},
    ])
    climate = pd.DataFrame([
        {"apn":"123456789","flood_zone":"AE","avg_rain_inches":"54.2"},
        {"apn":"222333444","flood_zone":"X","avg_rain_inches":"50.0"},
    ])
    return listings, climate

def test_end_to_end_basic():
    listings, climate = make_dfs()
    out = transform(listings, climate)
    # Correct statuses only
    assert set(out["status"]) == {"for_sale","pending"}
    # Dedup by APN keeps the lower price = 250000
    row = out[out["apn"]=="123456789"].iloc[0]
    assert row["price"] == 250000
    # Joined climate and derived field
    assert row["flood_zone"] == "AE"
    assert int(row["price_per_sqft"]) == round(250000/1600)

def test_sorted_by_price():
    listings, climate = make_dfs()
    out = transform(listings, climate)
    prices = out["price"].tolist()
    assert prices == sorted(prices)
