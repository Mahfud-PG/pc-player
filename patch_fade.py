import codecs

with codecs.open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = '''    def play_track(self, index):
        if 0 <= index < len(self.playlist_files):
            self.current_index = index
            path = self.playlist_files[index]
            
            if path.lower().endswith(('.mp4', '.webm', '.avi', '.mkv')) or "video" in path.lower():
                self.video_widget.show()
            else:
                self.video_widget.hide()
                
            if path.startswith("http://") or path.startswith("https://"):
                self.player.setSource(QUrl(path))
            else:
                self.player.setSource(QUrl.fromLocalFile(path))
                
            self.player.play()
            self.play_btn.setText("?")
            
            self.playlist_widget.setCurrentRow(index)

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_btn.setText("?")
        else:
            if self.current_index == -1 and self.playlist_files:
                self.play_track(0)
            else:
                self.player.play()
                self.play_btn.setText("?")

    def stop_media(self):
        self.player.stop()
        self.play_btn.setText("?")
        self.timeline_slider.setValue(0)
        self.time_label_current.setText("00:00")'''

replacement = '''    def play_track(self, index):
        if getattr(self, "fade_timer", None) and self.fade_timer.isActive():
            self.fade_timer.stop()
            self.audio_output.setVolume(self.volume_slider.value() / 100.0)
            
        if 0 <= index < len(self.playlist_files):
            self.current_index = index
            path = self.playlist_files[index]
            
            if path.lower().endswith(('.mp4', '.webm', '.avi', '.mkv')) or "video" in path.lower():
                self.video_widget.show()
            else:
                self.video_widget.hide()
                
            if path.startswith("http://") or path.startswith("https://"):
                self.player.setSource(QUrl(path))
            else:
                self.player.setSource(QUrl.fromLocalFile(path))
                
            def _play():
                self.player.play()
                self.play_btn.setText("?")
            self.do_fade_in(_play)
            
            self.playlist_widget.setCurrentRow(index)

    def toggle_play(self):
        if getattr(self, "fade_timer", None) and self.fade_timer.isActive():
            return
            
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            def _pause():
                self.player.pause()
                self.play_btn.setText("?")
                self.audio_output.setVolume(self.volume_slider.value() / 100.0)
            self.do_fade_out(_pause)
        else:
            if self.current_index == -1 and self.playlist_files:
                self.play_track(0)
            else:
                def _play():
                    self.player.play()
                    self.play_btn.setText("?")
                self.do_fade_in(_play)

    def stop_media(self):
        if getattr(self, "fade_timer", None) and self.fade_timer.isActive():
            return
            
        def _stop():
            self.player.stop()
            self.play_btn.setText("?")
            self.timeline_slider.setValue(0)
            self.time_label_current.setText("00:00")
            self.audio_output.setVolume(self.volume_slider.value() / 100.0)
            
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.do_fade_out(_stop)
        else:
            _stop()

    def do_fade_out(self, callback):
        self.fade_timer = QTimer(self)
        self.fade_timer.setInterval(25)
        self.current_fade_vol = self.audio_output.volume()
        steps = 15
        self.fade_step_val = self.current_fade_vol / steps if steps > 0 else 0
        
        def step():
            self.current_fade_vol -= self.fade_step_val
            if self.current_fade_vol <= 0:
                self.audio_output.setVolume(0)
                self.fade_timer.stop()
                callback()
            else:
                self.audio_output.setVolume(self.current_fade_vol)
        
        self.fade_timer.timeout.connect(step)
        self.fade_timer.start()

    def do_fade_in(self, callback):
        target_vol = self.volume_slider.value() / 100.0
        self.audio_output.setVolume(0)
        callback()
        
        self.fade_timer = QTimer(self)
        self.fade_timer.setInterval(25)
        self.current_fade_vol = 0.0
        steps = 15
        self.fade_step_val = target_vol / steps if steps > 0 else 0
        
        def step():
            self.current_fade_vol += self.fade_step_val
            if self.current_fade_vol >= target_vol:
                self.audio_output.setVolume(target_vol)
                self.fade_timer.stop()
            else:
                self.audio_output.setVolume(self.current_fade_vol)
                
        self.fade_timer.timeout.connect(step)
        self.fade_timer.start()'''

c = c.replace(target, replacement)

with codecs.open('main.py', 'w', encoding='utf-8') as f:
    f.write(c)
