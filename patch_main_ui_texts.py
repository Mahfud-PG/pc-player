import codecs

with codecs.open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

target_set_lang = '''    def set_language(self, lang_code):
        self.current_language = lang_code
        self.settings.setValue("language", lang_code)
        self.notify("Bahasa / Language", f"Bahasa telah diubah / Language has been changed.")'''

replace_set_lang = '''    def set_language(self, lang_code):
        self.current_language = lang_code
        self.settings.setValue("language", lang_code)
        self.update_ui_texts()
        self.notify("Bahasa / Language", f"Bahasa telah diubah / Language has been changed.")

    def update_ui_texts(self):
        self.prev_btn.setAccessibleName(self.tr("Trek Sebelumnya"))
        self.play_btn.setAccessibleName(self.tr("Mainkan / Jeda"))
        self.stop_btn.setAccessibleName(self.tr("Berhenti"))
        self.next_btn.setAccessibleName(self.tr("Trek Berikutnya"))
        self.vol_label.setText(self.tr("Volume"))
        self.setWindowTitle("PC Player")'''

c = c.replace(target_set_lang, replace_set_lang)

target_init_ui_end = '''        controls_layout.addWidget(self.volume_slider, stretch=1)
        controls_layout.addWidget(self.vol_label)
        
        main_layout.addLayout(controls_layout)'''

replace_init_ui_end = '''        controls_layout.addWidget(self.volume_slider, stretch=1)
        controls_layout.addWidget(self.vol_label)
        
        main_layout.addLayout(controls_layout)
        
        # Apply initial translations
        self.update_ui_texts()'''

c = c.replace(target_init_ui_end, replace_init_ui_end)

with codecs.open('main.py', 'w', encoding='utf-8') as f:
    f.write(c)
