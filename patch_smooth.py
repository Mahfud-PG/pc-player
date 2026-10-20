import codecs

with codecs.open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def get_indent(line):
    return len(line) - len(line.lstrip())

# 1. Replace play_track
start_idx = -1
for i, l in enumerate(lines):
    if l.startswith("    def play_track(self, index):"):
        start_idx = i
        break
end_idx = start_idx + 1
while end_idx < len(lines) and (lines[end_idx].strip() == "" or get_indent(lines[end_idx]) > 4):
    end_idx += 1

replacement_play_track = '''    def play_track(self, index):
        def _switch_track():
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
                
        if getattr(self, "fade_timer", None) and self.fade_timer.isActive():
            self.fade_timer.stop()
            self.audio_output.setVolume(self.volume_slider.value() / 100.0)
            _switch_track()
        elif self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.do_fade_out(_switch_track)
        else:
            _switch_track()
'''
lines[start_idx:end_idx] = [replacement_play_track + "\n"]

# 2. Replace forward_5s and backward_5s
start_idx = -1
for i, l in enumerate(lines):
    if l.startswith("    def forward_5s(self):"):
        start_idx = i
        break
end_idx = start_idx + 1
while end_idx < len(lines) and (lines[end_idx].strip() == "" or get_indent(lines[end_idx]) > 4):
    end_idx += 1

replacement_seek = '''    def smooth_seek(self, position):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            def _do_seek():
                self.player.setPosition(position)
                self.do_fade_in(lambda: None, fast=True)
            self.do_fade_out(_do_seek, fast=True)
        else:
            self.player.setPosition(position)

    def forward_5s(self):
        new_pos = min(self.player.duration(), self.player.position() + 5000)
        self.smooth_seek(new_pos)
        
    def backward_5s(self):
        new_pos = max(0, self.player.position() - 5000)
        self.smooth_seek(new_pos)
'''
lines[start_idx:end_idx] = [replacement_seek + "\n"]

# 3. Replace do_fade_out and do_fade_in to support 'fast'
start_idx = -1
for i, l in enumerate(lines):
    if l.startswith("    def do_fade_out(self, callback):"):
        start_idx = i
        break
end_idx = start_idx + 1
while end_idx < len(lines) and (lines[end_idx].strip() == "" or get_indent(lines[end_idx]) > 4):
    end_idx += 1

replacement_fade_out = '''    def do_fade_out(self, callback, fast=False):
        self.fade_timer = QTimer(self)
        self.fade_timer.setInterval(10 if fast else 25)
        self.current_fade_vol = self.audio_output.volume()
        steps = 5 if fast else 15
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
'''
lines[start_idx:end_idx] = [replacement_fade_out + "\n"]

start_idx = -1
for i, l in enumerate(lines):
    if l.startswith("    def do_fade_in(self, callback):"):
        start_idx = i
        break
end_idx = start_idx + 1
while end_idx < len(lines) and (lines[end_idx].strip() == "" or get_indent(lines[end_idx]) > 4):
    end_idx += 1

replacement_fade_in = '''    def do_fade_in(self, callback, fast=False):
        target_vol = self.volume_slider.value() / 100.0
        self.audio_output.setVolume(0)
        callback()
        
        self.fade_timer = QTimer(self)
        self.fade_timer.setInterval(10 if fast else 25)
        self.current_fade_vol = 0.0
        steps = 5 if fast else 15
        self.fade_step_val = target_vol / steps if steps > 0 else 0
        
        def step():
            self.current_fade_vol += self.fade_step_val
            if self.current_fade_vol >= target_vol:
                self.audio_output.setVolume(target_vol)
                self.fade_timer.stop()
            else:
                self.audio_output.setVolume(self.current_fade_vol)
                
        self.fade_timer.timeout.connect(step)
        self.fade_timer.start()
'''
lines[start_idx:end_idx] = [replacement_fade_in + "\n"]

# 4. Add closeEvent at the end of PCPlayer class
# Find def status_changed
start_idx = -1
for i, l in enumerate(lines):
    if l.startswith("    def status_changed(self, status):"):
        start_idx = i
        break
end_idx = start_idx + 1
while end_idx < len(lines) and (lines[end_idx].strip() == "" or get_indent(lines[end_idx]) > 4):
    end_idx += 1

close_event_code = '''
    def closeEvent(self, event):
        if getattr(self, "is_closing", False):
            event.accept()
            return
            
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            event.ignore()
            self.is_closing = True
            def _close():
                self.player.stop()
                self.close()
            self.do_fade_out(_close)
        else:
            event.accept()
'''
lines.insert(end_idx, close_event_code + "\n")

with codecs.open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
