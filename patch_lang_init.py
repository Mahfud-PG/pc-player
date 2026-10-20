import codecs

with codecs.open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        # Default Volume
        saved_volume = self.settings.value("volume", 1.0, type=float)
        self.audio_output.setVolume(saved_volume)'''

replacement = '''        self.current_language = self.settings.value("language", "id")

        # Default Volume
        saved_volume = self.settings.value("volume", 1.0, type=float)
        self.audio_output.setVolume(saved_volume)'''

c = c.replace(target, replacement)

with codecs.open('main.py', 'w', encoding='utf-8') as f:
    f.write(c)
