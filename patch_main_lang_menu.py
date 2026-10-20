import codecs

with codecs.open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        lang_menu = sys_menu.addMenu(self.tr("Pilih Bahasa / Language"))
        lang_id_action = lang_menu.addAction("???? Bahasa Indonesia")
        lang_en_action = lang_menu.addAction("???? English")
        lang_es_action = lang_menu.addAction("???? Español (Spanish)")
        lang_ja_action = lang_menu.addAction("???? ??? (Japanese)")
        lang_ar_action = lang_menu.addAction("???? ??????? (Arabic)")'''

replacement = '''        lang_menu = sys_menu.addMenu(self.tr("Pilih Bahasa / Language"))
        lang_id_action = lang_menu.addAction("???? Bahasa Indonesia")
        lang_en_action = lang_menu.addAction("???? English")'''

c = c.replace(target, replacement)

target2 = '''        elif action == lang_es_action:
            self.set_language("es")
        elif action == lang_ja_action:
            self.set_language("ja")
        elif action == lang_ar_action:
            self.set_language("ar")'''
replacement2 = ''

c = c.replace(target2, replacement2)

with codecs.open('main.py', 'w', encoding='utf-8') as f:
    f.write(c)
