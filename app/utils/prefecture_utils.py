from app.db.mongodb import get_collection

PREFECTURES = {}

async def init():
    global PREFECTURES
    
    # Get prefectures collection from MongoDB
    prefectures_collection = get_collection("prefecture")  # Adjust collection name as needed
    
    # Fetch all prefectures from database
    cursor = prefectures_collection.find({})
    
    # Load prefectures into dictionary with _id as key for O(1) lookup
    async for prefecture in cursor:
        PREFECTURES[prefecture["_id"]] = prefecture.get("name")
    
    print(f"Loaded {len(PREFECTURES)} prefectures into memory for O(1) lookup by _id")


def get_prefecture_by_id(prefecture_id: int) -> dict:
    """
    Get prefecture information by ID with O(1) complexity
    
    Args:
        prefecture_id (int): The prefecture ID
        
    Returns:
        dict: Prefecture information or None if not found
    """
    return PREFECTURES.get(prefecture_id)
