from app.db.mongodb import mongodb_sync
import time
import requests
import re
from datetime import datetime

def get_room():
    rooms = list(mongodb_sync.get_collection('room_mitsui').find({}))
    return rooms

def handle_except(e: Exception) -> str:
    return f"[{type(e).__name__}] {e}"

def first_check_room(room: dict) -> list:
    try:
        field_required = [
            "address",
            "floors",
            "floor_no",
            "year",
            "room_type",
            "monthly_rent",
            "size",
            "image_url_1",
        ]
        return [f for f in field_required if not room.get(f)]
    except Exception as e:
        print(f"first_check_room -->", handle_except(e))


def last_check_room(room: dict) -> list:
    try:
        field_required = [
            # "chome_banchi",
            # "postcode",
            "available_from",
            "address",
            "floors",
            "floor_no",
            "year",
            "room_type",
            "monthly_rent",
            "size",
            "image_url_1",
        ]

        return [f for f in field_required if not room.get(f)]
    except Exception as e:
        print("last_check_rom -->", handle_except(e))


def check_image_url(url: str) -> bool:
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)

        if response.status_code == 405:
            response = requests.get(url, stream=True, timeout=5)

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            if "image" in content_type.lower():
                return True
        return False
    except requests.RequestException:
        return False


def check_floor_v2(room: dict) -> bool:
    try:

        def extract_first_number(s: str) -> int | None:
            match = re.match(r"(\d+)", s)
            if match:
                return int(match.group(1))
            return None

        def normalize_floor(value) -> int:
            if isinstance(value, int):
                return abs(value)

            if isinstance(value, str):
                num = extract_first_number(value)
                if num is not None:
                    return num

            return 1

        def check_floor_no(floor_no: int, floors: int):
            return floor_no <= floors

        floors = room.get("floors")
        floor = room.get("floor_no")
        basement = room.get("basement_floors")

        if basement and basement != 0:
            basement_no = normalize_floor(basement)
            room["basement_floors"] = basement_no
            no_floor = -abs(basement_no)
            if check_floor_no(no_floor, floors):
                room["floor_num"] = no_floor
            else:
                return False

        if floor and floor != 0 and not basement:
            if isinstance(floor, str):
                num_floor = normalize_floor(floor)
                if isinstance(num_floor, int):
                    if check_floor_no(num_floor, floors):
                        room["floor_num"] = num_floor
                        return True

            if isinstance(floor, int):
                if check_floor_no(floor, floors):
                    room["floor_num"] = floor
                    return True

    except Exception as e:
        print(f"check_floor_v2 --> room_id {room['_id']}", handle_except(e))
        return False


def handle_date_now():
    now = datetime.now()
    return now.strftime("%Y-%m-%d")


def check_availabel_from(date_str: str) -> bool:
    try:
        parts = date_str.split("-")
        if len(parts) != 3:
            return False
        year, month, day = parts
        # Check year
        if not (year.isdigit() and len(year) == 4):
            return False
        # Check month and day
        if not (month.isdigit() and day.isdigit()):
            return False
        # Parser int
        year, month, day = int(year), int(month), int(day)
        if not (1 <= month <= 12):
            return False
        try:
            datetime(year, month, day)
        except ValueError:
            return False
        return True
    except Exception as e:
        print(f"check_availabel_from --> {handle_except(e)}")
        return False


def check_field_is_number(room: dict) -> tuple[bool, list]:
    try:
        fields_check = [
            "monthly_rent",
            "monthly_maintenance",
            "numeric_deposit",
            "numeric_key",
            "numeric_agency",
            "months_renewal",
            "lock_exchange",
            "fire_insurance",
            "other_subscription_fees",
            "numeric_guarantor",
            "numeric_guarantor_max",
            "security_deposit",
            "numeric_renewal",
            "numeric_security_deposit",
            # "numeric_discount",
        ]

        def is_negative(num):
            return num < 0

        invalid_fees = []
        for fie in fields_check:
            value = room.get(fie)
            if not value:
                continue
            if isinstance(value, str):
                invalid_fees.append(fie)
            if isinstance(value, float):
                invalid_fees.append(fie)
            if is_negative(value):
                invalid_fees.append(fie)

        if len(invalid_fees) > 0:
            return False, invalid_fees
        return True, invalid_fees

    except Exception as e:
        print(f"check_fee --> {handle_except(e)}")
        return False, invalid_fees


def check_room_type(room: dict) -> bool:
    try:
        room_type = [
            "1R",
            "1K",
            "1SK",
            "1DK",
            "1SLK",
            "1SDK",
            "1LDK",
            "1SLDK",
            "2K",
            "2SK",
            "2DK",
            "2SLK",
            "2SDK",
            "2LDK",
            "2SLDK",
            "3K",
            "3SK",
            "3DK",
            "3SLK",
            "3SDK",
            "3LDK",
            "3SLDK",
            "4K",
            "4SK",
            "4DK",
            "4SLK",
            "4SDK",
            "4LDK",
            "4SLDK",
            "5K",
            "5SK",
            "5DK",
            "5SLK",
            "5SDK",
            "5LDK",
            "5SLDK",
            "6K",
            "6SK",
            "6DK",
            "6SLK",
            "6SDK",
            "6LDK",
            "6SLDK",
            "7K",
            "7SK",
            "7DK",
            "7SLK",
            "7SDK",
            "7LDK",
            "7SLDK",
            "8K",
            "8SK",
            "8DK",
            "8SLK",
            "8SDK",
            "8LDK",
            "8SLDK",
            "9K",
            "9SK",
            "9DK",
            "9SLK",
            "9SDK",
            "9LDK",
            "9SLDK",
            "10K",
            "10SK",
            "10DK",
            "10SLK",
            "10SDK",
            "10LDK",
            "10SLDK",
            "Office",
            "Shop",
            "Restaurant",
            "Shared",
            "Private",
        ]
        if room.get("room_type") not in room_type:
            return False
        return True
    except Exception as e:
        print(f"check_room_type --> {handle_except(e)}")
        return False


def preprocess_room(room: dict) -> tuple[bool, dict]:
    try:
        # First check
        first_check_missing = first_check_room(room)
        if first_check_missing:
            room["first_check_missing"] = first_check_missing
            return False, room

        # Check image
        image_status = check_image_url(room.get("image_url_1"))
        if not image_status:
            room["log"] = "Invalid image"
            return False, room

        # Check floor
        if not check_floor_v2(room):
            room["log"] = "Invalid floors and floor_no"
            return False, room

        # Check fields is number
        fee_sta, fee_field = check_field_is_number(room)
        if fee_sta == False:
            room["log"] = ", ".join(fee_field)
            return False, room

        if check_room_type(room) == False:
            room["log"] = "invalid room_type"
            return False, room

        # Add postcode if missing but address exists
        address = room.get("address")
        # if not room.get("postcode") and address:
        #     room["postcode"] = get_postcode(address)

        # Add chome_banchi if missing
        if not room.get("chome_banchi") and address:
            room["chome_banchi"] = address

        # Add available_from if missing
        avai_from = room.get("available_from")
        if not avai_from:
            room["available_from"] = handle_date_now()
        else:
            if check_availabel_from(avai_from) == False:
                # logs.append("Invalid available from")
                room["log"] = "Invalid available form"
                return False, room

        # Add default fields if missing
        field_add = {
            "building_type": "other",
            "delivery_box": "Y",
        }
        for key, value in field_add.items():
            if key not in room or room[key] is None:
                room[key] = value

        # Last check
        last_check_missing = last_check_room(room)
        if last_check_missing:
            room["last_check_missing"] = last_check_missing
            return False, room

        return True, room

    except Exception as e:
        print("preprocess_room -->", handle_except(e))
        return False, room


def filter_list(list_room: list) -> list:
    try:
        unique_dict = {}
        for r in list_room:
            if r["_id"] not in unique_dict:
                unique_dict[r["_id"]] = r
        return list(unique_dict.values())
    except Exception as e:
        print(f"filter_list --> {handle_except(e)}")


def filter_unique_room(rooms: list) -> list:
    try:
        seen = set()
        unique_rooms = []
        for room in rooms:
            key = (
                room.get("address") or "UNKNOWN_ADDRESS",
                room.get("room_type") or "UNKNOWN_ADDRESS",
                room.get("monthly_rent") or 0,
            )
            if key not in seen:
                seen.add(key)
                unique_rooms.append(room)
        return unique_rooms
    except Exception as e:
        print(f"filter_unique_room --> {handle_except(e)}")
        return []


def filter_room():
    try:
        sta_time = time.time()
        room_fail_db = mongodb_sync.get_collection("room_fail")
        room_okay_db = mongodb_sync.get_collection("room_okay")
        room_okay_db.drop()
        room_fail_db.drop()
        # rooms = get_room_client()  # From db production
        rooms = get_room()  # From db local
        print(f"Total room {len(rooms)}")
        unique_room = filter_unique_room(rooms)  # filter unique room
        print(f"Total room after filter {len(unique_room)}")
        room_ok = []
        room_fail = []
        for room in unique_room:
            status, res_room = preprocess_room(room)

            if status == True:
                room_ok.append(res_room)
            else:
                room_fail.append(res_room)

        print(f"Total OK ==> {len(room_ok)}")
        print(f"Total failure ==> {len(room_fail)}")
        if len(room_ok) > 0:
            room_insert_ok = filter_list(room_ok)
            room_okay_db.insert_many(room_insert_ok)
        if len(room_fail) > 0:
            room_insert_fail = filter_list(room_fail)
            room_fail_db.insert_many(room_insert_fail)
        print(f"TIME PROCESS {time.time() - sta_time:.2f} seconds")
    except Exception as e:
        print(f"filter_room --> {handle_except(e)}")


if __name__ == "__main__":
    # python -m app.tests.crawl.check
    filter_room()
