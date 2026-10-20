import codecs

lang_content = '''TRANSLATIONS = {
    "Menu Pemutaran": {"en": "Playback Menu", "es": "Menu de Reproduccion", "ja": "Saisei Menu", "ar": "Qaimat Al-Tashghil"},
    "Pengatur Waktu Tidur (Ctrl+T)": {"en": "Sleep Timer (Ctrl+T)", "es": "Temporizador de sueno (Ctrl+T)", "ja": "Sleep Timer (Ctrl+T)", "ar": "Sleep Timer (Ctrl+T)"},
    "Mainkan / Jeda (Spasi)": {"en": "Play / Pause (Space)", "es": "Reproducir / Pausa (Espacio)", "ja": "Play / Pause (Space)", "ar": "Play / Pause (Space)"},
    "Lagu Sebelumnya (A)": {"en": "Previous Track (A)", "es": "Pista Anterior (A)", "ja": "Previous Track (A)", "ar": "Previous Track (A)"},
    "Lagu Berikutnya (G)": {"en": "Next Track (G)", "es": "Siguiente Pista (G)", "ja": "Next Track (G)", "ar": "Next Track (G)"},
    "Putar Lambat (S)": {"en": "Play Slow (S)", "es": "Reproducir Lento (S)", "ja": "Play Slow (S)", "ar": "Play Slow (S)"},
    "Putar Normal (D)": {"en": "Play Normal (D)", "es": "Reproducir Normal (D)", "ja": "Play Normal (D)", "ar": "Play Normal (D)"},
    "Putar Cepat (F)": {"en": "Play Fast (F)", "es": "Reproducir Rapido (F)", "ja": "Play Fast (F)", "ar": "Play Fast (F)"},
    "Ulangi / Repeat (R)": {"en": "Repeat (R)", "es": "Repetir (R)", "ja": "Repeat (R)", "ar": "Repeat (R)"},
    "Acak / Shuffle (C)": {"en": "Shuffle (C)", "es": "Aleatorio (C)", "ja": "Shuffle (C)", "ar": "Shuffle (C)"},
    "Menu Looping A-B": {"en": "A-B Looping Menu", "es": "Menu Bucle A-B", "ja": "A-B Looping Menu", "ar": "A-B Looping Menu"},
    "Set Titik A Loop ([)": {"en": "Set Loop Point A ([)", "es": "Punto de Bucle A ([)", "ja": "Set Loop Point A ([)", "ar": "Set Loop Point A ([)"},
    "Set Titik B Loop (])": {"en": "Set Loop Point B (])", "es": "Punto de Bucle B (])", "ja": "Set Loop Point B (])", "ar": "Set Loop Point B (])"},
    "Hapus Loop (\\)": {"en": "Clear Loop (\\)", "es": "Borrar Bucle (\\)", "ja": "Clear Loop (\\)", "ar": "Clear Loop (\\)"},
    "Menu Online & Download": {"en": "Online & Download Menu", "es": "Menu Online y Descarga", "ja": "Online & Download Menu", "ar": "Online & Download Menu"},
    "Cari Lagu (Ctrl + F)": {"en": "Search Song (Ctrl + F)", "es": "Buscar Cancion (Ctrl + F)", "ja": "Search Song (Ctrl + F)", "ar": "Search Song (Ctrl + F)"},
    "Putar dari Link (Ctrl + L)": {"en": "Play from Link (Ctrl + L)", "es": "Reproducir desde Enlace (Ctrl+L)", "ja": "Play from Link (Ctrl + L)", "ar": "Play from Link (Ctrl + L)"},
    "Download Lagu Ini (Ctrl + D)": {"en": "Download This Song (Ctrl + D)", "es": "Descargar Esta Cancion (Ctrl+D)", "ja": "Download This Song (Ctrl + D)", "ar": "Download This Song (Ctrl + D)"},
    "Menu Tampilan & Video": {"en": "Appearance & Video Menu", "es": "Menu de Apariencia y Video", "ja": "Appearance & Video Menu", "ar": "Appearance & Video Menu"},
    "Video mode layar normal (F11)": {"en": "Normal Screen Video (F11)", "es": "Video Pantalla Normal (F11)", "ja": "Normal Screen Video (F11)", "ar": "Normal Screen Video (F11)"},
    "Video mode layar penuh (F11)": {"en": "Fullscreen Video (F11)", "es": "Video Pantalla Completa (F11)", "ja": "Fullscreen Video (F11)", "ar": "Fullscreen Video (F11)"},
    "Ubah ke Tema Terang (Light Mode)": {"en": "Change to Light Theme", "es": "Cambiar a Tema Claro", "ja": "Change to Light Theme", "ar": "Change to Light Theme"},
    "Ubah ke Tema Gelap (Dark Mode)": {"en": "Change to Dark Theme", "es": "Cambiar a Tema Oscuro", "ja": "Change to Dark Theme", "ar": "Change to Dark Theme"},
    "Ubah Warna Aksen (Custom Tema)": {"en": "Change Accent Color", "es": "Cambiar Color de Acento", "ja": "Change Accent Color", "ar": "Change Accent Color"},
    "Galeri Latar (Internal)": {"en": "Background Gallery", "es": "Galeria de Fondos", "ja": "Background Gallery", "ar": "Background Gallery"},
    "1. Gelap Abstrak": {"en": "1. Dark Abstract", "es": "1. Oscuro Abstracto", "ja": "1. Dark Abstract", "ar": "1. Dark Abstract"},
    "2. Terang Elegan": {"en": "2. Light Elegant", "es": "2. Claro Elegante", "ja": "2. Light Elegant", "ar": "2. Light Elegant"},
    "3. Neon Musik": {"en": "3. Music Neon", "es": "3. Neon Musical", "ja": "3. Music Neon", "ar": "3. Music Neon"},
    "Impor Latar Pribadi (Dari PC)": {"en": "Import Custom Background", "es": "Importar Fondo Personalizado", "ja": "Import Custom Background", "ar": "Import Custom Background"},
    "Hapus Latar Belakang": {"en": "Clear Background", "es": "Borrar Fondo", "ja": "Clear Background", "ar": "Clear Background"},
    "Menu Info & Sistem": {"en": "Info & System Menu", "es": "Menu Info y Sistema", "ja": "Info & System Menu", "ar": "Info & System Menu"},
    "Info Audio (I)": {"en": "Audio Info (I)", "es": "Informacion de Audio (I)", "ja": "Audio Info (I)", "ar": "Audio Info (I)"},
    "Jadikan Pemutar Utama (Daftarkan ke Windows)": {"en": "Set as Default Player", "es": "Establecer como Predeterminado", "ja": "Set as Default Player", "ar": "Set as Default Player"},
    "Pilih Bahasa / Language": {"en": "Choose Language / Bahasa", "es": "Elegir Idioma / Language", "ja": "Choose Language / Bahasa", "ar": "Choose Language / Bahasa"},
}
'''

with codecs.open('lang.py', 'w', encoding='utf-8') as f:
    f.write(lang_content)
