# Chạy: python -m app.tests.translate.index
import time

def gg_translate():
    # Nhanh uy tín, có giới hạn 2 million characters per day and 100,000 characters per 100 second
    # time: < 1s
    from deep_translator import GoogleTranslator

    text = "東京都練馬区桜台三丁目２０番３号"
    translation = GoogleTranslator(source='ja', target='en').translate(text)
    
    print(translation)
    
def ftapi():
    import requests
    # Nhiều cái mở rộng như có giọng đọc, từ liên quan, lâu hơn translate
    # time: 1s
    # có thể bị block request - cần test thêm 
    
    lan_src = 'ja'
    lan_dl = 'en'
    text = "ル・シュクレ永福"
    call_api = requests.get(f'https://ftapi.pythonanywhere.com/translate?sl={lan_src}&dl={lan_dl}&text={text}')
    print(call_api.json().get('destination-text'))
    
def model():
    # cài nặng, nhiều
    # không giới hạn dịch hay chặn request, không phụ thuộc
    # lâu: 7s
    from transformers import MarianMTModel, MarianTokenizer

    model_name = 'Helsinki-NLP/opus-mt-ja-en'
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)

    def translate(text):
        tokens = tokenizer(text, return_tensors="pt", padding=True)
        translated = model.generate(**tokens)
        return tokenizer.decode(translated[0], skip_special_tokens=True)

    text = "東京都練馬区桜台三丁目２０番３号"
    print(translate(text))

from app.db.mongodb import connect_to_mongo, close_mongo_connection, get_collection
from app.utils.translate_utils import translate_ja_to_en

# Bộ nhớ cache tạm trong RAM
translated_cache = {}

async def run():
    await connect_to_mongo()
    collection_mitsui = get_collection('room_mitsui')
    
    async for document in collection_mitsui.find({'building_name_en': {'$exists': False}}):
        building_name_ja = document.get('building_name_ja')
        if not building_name_ja:
            continue

        # Kiểm tra cache trước
        if building_name_ja in translated_cache:
            building_name_en = translated_cache[building_name_ja]
        else:
            building_name_en = translate_ja_to_en(text=building_name_ja)
            translated_cache[building_name_ja] = building_name_en  # Lưu vào cache

        print(f"Document id: {document['_id']} - {building_name_ja} -> {building_name_en}")

        if building_name_en:
            await collection_mitsui.update_one(
                {'_id': document['_id']},
                {'$set': {'building_name_en': building_name_en}}
            )
        
    await close_mongo_connection()

import asyncio

if __name__ == '__main__':
    asyncio.run(run())
    # ftapi()