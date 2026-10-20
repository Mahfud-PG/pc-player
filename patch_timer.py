import codecs

with codecs.open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Add shortcut
target_shortcut = '''        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.toggle_play)'''
replace_shortcut = '''        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.toggle_play)
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.set_sleep_timer)'''
c = c.replace(target_shortcut, replace_shortcut)

# 2. Add to contextMenuEvent
target_context1 = '''        playback_menu = context_menu.addMenu("Menu Pemutaran")
        play_pause_action = playback_menu.addAction("Mainkan / Jeda (Spasi)")'''
replace_context1 = '''        playback_menu = context_menu.addMenu("Menu Pemutaran")
        sleep_action = playback_menu.addAction("Pengatur Waktu Tidur (Ctrl+T)")
        playback_menu.addSeparator()
        play_pause_action = playback_menu.addAction("Mainkan / Jeda (Spasi)")'''
c = c.replace(target_context1, replace_context1)

target_context2 = '''        if action == play_pause_action:
            self.toggle_play()'''
replace_context2 = '''        if action == sleep_action:
            self.set_sleep_timer()
        elif action == play_pause_action:
            self.toggle_play()'''
c = c.replace(target_context2, replace_context2)

# 3. Add set_sleep_timer method
# find end of class
target_class_end = '''            self.do_fade_out(_close)
        else:
            event.accept()'''
replace_class_end = '''            self.do_fade_out(_close)
        else:
            event.accept()

    def set_sleep_timer(self):
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        
        if getattr(self, "sleep_timer", None) and self.sleep_timer.isActive():
            reply = QMessageBox.question(self, "Sleep Timer Aktif", "Timer tidur sedang berjalan. Apakah Anda ingin membatalkannya?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.sleep_timer.stop()
                self.notify("Sleep Timer", "Timer tidur berhasil dibatalkan.")
            return

        minutes, ok = QInputDialog.getInt(self, "Pengatur Waktu Tidur", "Masukkan waktu sebelum PC Player mati otomatis (menit):", 30, 1, 1440)
        if ok and minutes > 0:
            self.sleep_timer = QTimer(self)
            self.sleep_timer.setSingleShot(True)
            self.sleep_timer.timeout.connect(self.close)
            self.sleep_timer.start(minutes * 60 * 1000)
            self.notify("Sleep Timer", f"PC Player akan menutup otomatis dalam {minutes} menit.")'''
c = c.replace(target_class_end, replace_class_end)

with codecs.open('main.py', 'w', encoding='utf-8') as f:
    f.write(c)
