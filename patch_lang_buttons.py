import codecs

with codecs.open('lang.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = '''    "Pilih Bahasa / Language": {"en": "Choose Language / Bahasa", "es": "Elegir Idioma / Language", "ja": "????? / Language", "ar": "???? ????? / Language"},
}'''

replacement = '''    "Pilih Bahasa / Language": {"en": "Choose Language / Bahasa", "es": "Elegir Idioma / Language", "ja": "????? / Language", "ar": "???? ????? / Language"},
    "Trek Sebelumnya": {"en": "Previous Track", "es": "Pista Anterior", "ja": "???", "ar": "?????? ??????"},
    "Mainkan / Jeda": {"en": "Play / Pause", "es": "Reproducir / Pausa", "ja": "?? / ????", "ar": "????? / ????? ????"},
    "Berhenti": {"en": "Stop", "es": "Detener", "ja": "??", "ar": "????"},
    "Trek Berikutnya": {"en": "Next Track", "es": "Siguiente Pista", "ja": "???", "ar": "?????? ??????"},
    "Volume": {"en": "Volume", "es": "Volumen", "ja": "??", "ar": "????? ?????"},
    "Kesalahan": {"en": "Error", "es": "Error", "ja": "???", "ar": "???"},
}'''

c = c.replace(target, replacement)

with codecs.open('lang.py', 'w', encoding='utf-8') as f:
    f.write(c)
