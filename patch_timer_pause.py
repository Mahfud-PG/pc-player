import codecs

with codecs.open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        if ok and minutes > 0:
            self.sleep_timer = QTimer(self)
            self.sleep_timer.setSingleShot(True)
            self.sleep_timer.timeout.connect(self.stop_media)
            self.sleep_timer.start(minutes * 60 * 1000)'''

replacement = '''        if ok and minutes > 0:
            self.sleep_timer = QTimer(self)
            self.sleep_timer.setSingleShot(True)
            self.sleep_timer.timeout.connect(self.pause_for_sleep_timer)
            self.sleep_timer.start(minutes * 60 * 1000)'''

c = c.replace(target, replacement)

# Add pause_for_sleep_timer method
target_class_end = '''            self.sleep_timer.start(minutes * 60 * 1000)
            self.notify("Sleep Timer", f"Pemutaran akan berhenti otomatis dalam {minutes} menit.")'''

replace_class_end = '''            self.sleep_timer.start(minutes * 60 * 1000)
            self.notify("Sleep Timer", f"Pemutaran akan dijeda otomatis dalam {minutes} menit.")

    def pause_for_sleep_timer(self):
        if getattr(self, "fade_timer", None) and self.fade_timer.isActive():
            self.fade_timer.stop()
            
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            def _pause():
                self.player.pause()
                self.play_btn.setText("?")
            self.do_fade_out(_pause)'''

c = c.replace(target_class_end, replace_class_end)

with codecs.open('main.py', 'w', encoding='utf-8') as f:
    f.write(c)
