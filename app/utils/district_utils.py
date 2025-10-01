"""
District utilities for geospatial queries
"""
from typing import List, Optional
from app.db.mongodb import mongodb_sync
from pymongo.errors import OperationFailure

def get_district(lat: float, lng: float) -> List[Optional[str]]:
    try:
        # Get districts collection (sync version)
        districts_collection = mongodb_sync.get_collection('district')

        # Ensure 2dsphere index exists on 'location'
        try:
            indexes = districts_collection.index_information()
            if 'location_2dsphere' not in indexes:
                districts_collection.create_index([("location", "2dsphere")], name='location_2dsphere')
                print("✅ Created 2dsphere index on 'location'")
        except OperationFailure as e:
            print(f"❌ Failed to create/check index: {e}")
            return [None, None, None]

        # MongoDB uses [longitude, latitude] order for GeoJSON
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [float(lng), float(lat)]
                    }
                }
            }
        }

        # Find the nearest district
        district = districts_collection.find_one(query)
        
        if district:
            return [
                district.get('name'),
                district.get('prefecture'), 
                district.get('city')
            ]
        else:
            print(f"⚠️ No district found for coordinates: lat={lat}, lng={lng}")
            return [None, None, None]

    except (ValueError, TypeError) as e:
        print(f"❌ Invalid coordinates: lat={lat}, lng={lng}, error={e}")
        return [None, None, None]
    except Exception as e:
        print(f"❌ Error getting district: {e}")
        return [None, None, None]
