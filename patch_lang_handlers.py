import codecs

with codecs.open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        if action == sleep_action:
            self.set_sleep_timer()'''

replacement = '''        if action == lang_id_action:
            self.set_language("id")
        elif action == lang_en_action:
            self.set_language("en")
        elif action == lang_es_action:
            self.set_language("es")
        elif action == lang_ja_action:
            self.set_language("ja")
        elif action == lang_ar_action:
            self.set_language("ar")
        elif action == sleep_action:
            self.set_sleep_timer()'''

c = c.replace(target, replacement)

with codecs.open('main.py', 'w', encoding='utf-8') as f:
    f.write(c)
