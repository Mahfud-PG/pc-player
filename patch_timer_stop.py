import codecs

with codecs.open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        minutes, ok = QInputDialog.getInt(self, "Pengatur Waktu Tidur", "Masukkan waktu sebelum PC Player mati otomatis (menit):", 30, 1, 1440)
        if ok and minutes > 0:
            self.sleep_timer = QTimer(self)
            self.sleep_timer.setSingleShot(True)
            self.sleep_timer.timeout.connect(self.close)
            self.sleep_timer.start(minutes * 60 * 1000)
            self.notify("Sleep Timer", f"PC Player akan menutup otomatis dalam {minutes} menit.")'''

replacement = '''        minutes, ok = QInputDialog.getInt(self, "Pengatur Waktu Tidur", "Masukkan waktu sebelum pemutaran berhenti otomatis (menit):", 30, 1, 1440)
        if ok and minutes > 0:
            self.sleep_timer = QTimer(self)
            self.sleep_timer.setSingleShot(True)
            self.sleep_timer.timeout.connect(self.stop_media)
            self.sleep_timer.start(minutes * 60 * 1000)
            self.notify("Sleep Timer", f"Pemutaran akan berhenti otomatis dalam {minutes} menit.")'''

c = c.replace(target, replacement)

with codecs.open('main.py', 'w', encoding='utf-8') as f:
    f.write(c)
