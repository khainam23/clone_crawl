from app.db.mongodb import get_collection

CITIES = {}

async def init():
    global CITIES
    
    # Get cities collection from MongoDB
    cities_collection = get_collection("city")  # Adjust collection name as needed
    
    # Fetch all cities from database
    cursor = cities_collection.find({})
    
    # Load cities into dictionary with name as key for O(1) lookup
    async for city in cursor:
        CITIES[city["_id"]] = city.get("name")
    
def get_city_by_id(id_city: int) -> dict:
    """
    Get city information by name with O(1) complexity
    
    Args:
        city_name (str): The city name
        
    Returns:
        dict: City information or None if not found
    """
    return CITIES.get(id_city)