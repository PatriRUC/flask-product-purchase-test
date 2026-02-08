import requests
from geolib import geohash

GOOGLE_API_KEY = "AIzaSyAoF9K80AmRLSq8BXcJvIJ-IA0EwpuIB_w"  
TICKETMASTER_API_KEY = "LlrRfYQsMaRIIcvk127MTDu0SWurP6DV"

google_url = "https://maps.googleapis.com/maps/api/geocode/json"
ticketmaster_url_event = "https://app.ticketmaster.com/discovery/v2/events"
ticketmaster_url_venue = "https://app.ticketmaster.com/discovery/v2/venues"

segmentld = {"Default": None, 
             "Music": "KZFzniwnSyZfZ7v7nJ", 
             "Sports": "KZFzniwnSyZfZ7v7nE", 
             "Arts & Theatre": "KZFzniwnSyZfZ7v7na",
             "Film": "KZFzniwnSyZfZ7v7nn", 
             "Miscellaneous": "KZFzniwnSyZfZ7v7n1"}
# Parse JSON response
def find_events(keyword, distance, catagory, location):
    return_data = []
    google_params = {
        "address": location,
        "key": GOOGLE_API_KEY
    }
    google_response = requests.get(google_url, params=google_params)  # google把地址转为经纬度，geohash把经纬度转为encode，tm用encode作地址
    if google_response.status_code == 200:
        data = google_response.json()
        lat_and_lnt = data['results'][0]['geometry']['location']
        encode = geohash.encode(lat_and_lnt['lat'], lat_and_lnt['lng'], 7)
        ticketmaster_params = {
            "apikey": TICKETMASTER_API_KEY,
            "geoPoint": encode,
            "radius": distance, 
            "unit": "miles",
            "segmentId": segmentld[catagory], 
            "keyword": keyword, 
        }
        ticketmaster_response = requests.get(ticketmaster_url_event, params=ticketmaster_params)
        if ticketmaster_response.status_code == 200:
            tm_data = ticketmaster_response.json()
            if "_embedded" not in tm_data:
                return []
            want = tm_data["_embedded"]["events"]
            for event in want:
                try:
                    Date = event["dates"]["start"].get("localDate") + " " + event["dates"]["start"].get("localTime", "")
                except:
                    Date = None
                try:
                    Image = event["images"][0]['url']
                except:
                    Image = None
                try:
                    Event = event["name"]
                except:
                    Event = None
                try:
                    Genre = event["classifications"][0]["segment"]['name']
                except:
                    Genre = None
                try:
                    Venue = event["_embedded"]["venues"][0]["name"]
                except:
                    Venue = None
                try:
                    Id = event["id"]
                except:
                    Id = None
                event_data = {"Date": Date, 
                              "Image": Image, 
                              "Event": Event, 
                              "Genre": Genre, 
                              "Venue": Venue, 
                              "Id": Id}
                return_data.append(event_data)
        else:
            print("Error:", ticketmaster_response.status_code, google_response.text)

    else:
        print("Error:", google_response.status_code, google_response.text)
    return return_data


def find_detail(id):
    ticketmaster_params = {
        "apikey": TICKETMASTER_API_KEY
    }
    ticketmaster_response = requests.get(
        ticketmaster_url_event + '/' + id, 
        params=ticketmaster_params
    )
    if ticketmaster_response.status_code == 200:
        event = ticketmaster_response.json()
        try:
            Date = event["dates"]["start"].get("localDate") + " " + event["dates"]["start"].get("localTime", "")
        except:
            Date = None
        try:
            at = event["_embedded"]["attractions"]
            Artist_Team = {}
            for a in at:
                Artist_Team[a["name"]] = a["url"]
        except:
            Artist_Team = {}
        try:
            Venue = event["_embedded"]["venues"][0]["name"]
        except:
            Venue = None
        try:
            Ge = event["classifications"][0]
            Genre = Ge["segment"]['name'] + " | " + Ge["genre"]["name"] + " | " + Ge["subGenre"]["name"]
        except:
            Genre = None
        try:
            pR = event["priceRanges"][0]
            Price_Ranges = str(pR["min"]) + '-' + str(pR["max"]) + ' ' + pR["currency"]
        except:
            Price_Ranges = None
        try:
            Ticket_Status = event["dates"]["status"]["code"]
        except:
            Ticket_Status = None
        try:
            Buy_Ticket = event["url"]
        except:
            Buy_Ticket = None
        try:
            Seat_Map = event["seatmap"]["staticUrl"]
        except:
            Seat_Map = None 
        detail_data = {
            "Date": Date, 
            "Artist_Team": Artist_Team, 
            "Venue": Venue, 
            "Genre": Genre, 
            "Price_Ranges": Price_Ranges, 
            "Ticket_Status": Ticket_Status, 
            "Buy_Ticket": Buy_Ticket, 
            "Seat_Map": Seat_Map
        }
        return detail_data

def find_venue(keyword):
    ticketmaster_params = {
        "apikey": TICKETMASTER_API_KEY,
        "keyword": keyword,
    }
    ticketmaster_response = requests.get(ticketmaster_url_venue, params=ticketmaster_params)
    if ticketmaster_response.status_code == 200:
        tm_data = ticketmaster_response.json()
        if "_embedded" not in tm_data:
            return []
        want = tm_data["_embedded"]["venues"]
        venue = want[0]
        try:
            Name = venue["name"]
        except:
            Name = None
        try:
            Address = venue["address"]["line1"]
        except:
            Address = None
        try:
            City = venue["city"]["name"]
        except:
            City = None
        try:
            State = venue["state"]["stateCode"]
        except:
            State = None
        try:
            Postal_Code = venue["postalCode"] 
        except:
            Postal_Code = None
        try:
            Upcoming_Events = venue["url"]
        except:
            Upcoming_Events = None
        try:
            Image = venue["images"][0]["url"]
        except:
            Image = None
        venue_data = {
            "Name": Name, 
            "Address": Address, 
            "City": City, 
            "Postal_Code": Postal_Code, 
            "Upcoming_Events": Upcoming_Events, 
            "Image": Image, 
            "State": State
        }
        return venue_data



