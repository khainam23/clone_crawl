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
    text = "東京都練馬区桜台三丁目２０番３号"
    call_api = requests.get(f'https://ftapi.pythonanywhere.com/translate?sl={lan_src}&dl={lan_dl}&text={text}')
    print(call_api.json())
    
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

if __name__ == '__main__':
    old_time = time.time()
    # gg_translate()
    ftapi()
    # model()
    new_time = time.time()
    print(f'need:{new_time-old_time}s')