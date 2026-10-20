import codecs

with codecs.open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Add QTimer to __init__
target_init_end = '''        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.status_changed)

        self.last_batch_time = time.time()'''
replace_init_end = '''        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.status_changed)

        self.last_batch_time = time.time()
        
        # Cek riwayat pemutaran terakhir
        QTimer.singleShot(500, self.prompt_resume_playback)'''
c = c.replace(target_init_end, replace_init_end)

# 2. Modify status_changed to handle LoadedMedia
target_status_changed = '''    def status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.is_repeat:
                self.player.setPosition(0)
                self.player.play()
            else:
                self.play_next()'''
replace_status_changed = '''    def status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.is_repeat:
                self.player.setPosition(0)
                self.player.play()
            else:
                self.play_next()
        elif status == QMediaPlayer.MediaStatus.LoadedMedia:
            if hasattr(self, "pending_resume_position"):
                pos = self.pending_resume_position
                del self.pending_resume_position
                self.player.setPosition(pos)
                def _play():
                    self.player.play()
                    self.play_btn.setText("?")
                self.do_fade_in(_play)'''
c = c.replace(target_status_changed, replace_status_changed)

# 3. Add prompt_resume_playback and modify closeEvent
target_close_event = '''    def closeEvent(self, event):
        if getattr(self, "is_closing", False):'''
replace_close_event = '''    def prompt_resume_playback(self):
        import os
        from PyQt6.QtWidgets import QMessageBox
        
        last_playlist = self.settings.value("last_playlist", [])
        last_index = self.settings.value("last_index", -1, type=int)
        last_position = self.settings.value("last_position", 0, type=int)
        
        if last_playlist and 0 <= last_index < len(last_playlist):
            # Calculate time
            s = last_position // 1000
            m = s // 60
            s = s % 60
            time_str = f"{m:02}:{s:02}"
            
            filename = os.path.basename(last_playlist[last_index])
            
            reply = QMessageBox.question(
                self, 
                "Lanjutkan Pemutaran?", 
                f"Terdapat riwayat pemutaran sebelumnya:\\n'{filename}'\\ndi menit {time_str}.\\n\\nIngin melanjutkan pemutaran ini?", 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.playlist_files = last_playlist
                for path in self.playlist_files:
                    self.playlist_widget.addItem(os.path.basename(path))
                
                self.current_index = last_index
                path = self.playlist_files[last_index]
                
                if path.lower().endswith(('.mp4', '.webm', '.avi', '.mkv')) or "video" in path.lower():
                    self.video_widget.show()
                else:
                    self.video_widget.hide()
                    
                self.pending_resume_position = last_position
                
                if path.startswith("http://") or path.startswith("https://"):
                    self.player.setSource(QUrl(path))
                else:
                    self.player.setSource(QUrl.fromLocalFile(path))
                
                self.playlist_widget.setCurrentRow(last_index)
            else:
                self.settings.remove("last_playlist")
                self.settings.remove("last_index")
                self.settings.remove("last_position")

    def closeEvent(self, event):
        if self.playlist_files and self.current_index >= 0:
            self.settings.setValue("last_playlist", self.playlist_files)
            self.settings.setValue("last_index", self.current_index)
            self.settings.setValue("last_position", self.player.position())
        else:
            self.settings.remove("last_playlist")
            self.settings.remove("last_index")
            self.settings.remove("last_position")
            
        if getattr(self, "is_closing", False):'''
c = c.replace(target_close_event, replace_close_event)

with codecs.open('main.py', 'w', encoding='utf-8') as f:
    f.write(c)
