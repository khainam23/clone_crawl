from app.core.config import settings

'''
// Tìm kiểu tên chứa
db.room_mitsui_test.find({
  
	building_name_en: { $regex: "nam", $options: "i" }
})

// Tìm gần đúng, phải tạo trước index
db.users.createIndex({ name: "text" })
db.users.find({ $text: { $search: "nam" } })


// Nâng cao hơn dùng thư viện MongoDB Aggregation

'''

import pymongo
client = pymongo.MongoClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]
collection = db['room_mitsui']

keyword = 'vil'

# python -m app.tests.search.index

# cach 1 dung regrex
# collection.insert_one({'name': 'Nguyen Van A'})
# print(collection.find().count())
print(collection.count_documents({"building_name_en": {"$regex": keyword, "$options": "i"}}))


# cach 2 dung search
# collection.create_index([
#     ('building_name_en', 'text'),
# ])


# print("Tổng kết quả:", collection.count_documents({"$text": {"$search": 'Vil'}}))

