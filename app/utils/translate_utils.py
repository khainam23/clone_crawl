import requests
    
def translate_ja_to_en(lan_src: str = 'ja', lan_dl: str = 'en', text: str = ''):
    if not text:
        return None
    
    call_api = requests.get(f'https://ftapi.pythonanywhere.com/translate?sl={lan_src}&dl={lan_dl}&text={text}')
    
    if call_api:
        return call_api.json().get('destination-text')

    return None