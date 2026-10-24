import sys
import os
import winreg
import random
import time
import urllib.request
import json
import tempfile
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QSlider, QLabel, QListWidget, 
                             QMenu, QMessageBox, QInputDialog, QFileDialog, QColorDialog)
from PyQt6.QtGui import QKeySequence, QShortcut, QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal, QSettings, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaMetaData
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from bass_engine import BassEngine

APP_VERSION = "2.1.0"
GITHUB_REPO = "Mahfud-PG/pc-player"

class UpdateCheckerThread(QThread):
    update_found = pyqtSignal(str, str, str)  # version, notes, download_url
    no_update = pyqtSignal(str)              # current_version
    error_occurred = pyqtSignal(str)

    def __init__(self, current_version, repo_name, silent=True):
        super().__init__()
        self.current_version = current_version
        self.repo_name = repo_name
        self.silent = silent

    def run(self):
        try:
            url = f"https://api.github.com/repos/{self.repo_name}/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "PCPlayer-App"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                tag = data.get("tag_name", "").lstrip("v")
                body = data.get("body", "Pembaruan versi baru tersedia.")
                assets = data.get("assets", [])
                dl_url = None
                for a in assets:
                    name = a.get("name", "").lower()
                    if name.endswith(".exe"):
                        dl_url = a.get("browser_download_url")
                        break

                def parse_ver(v_str):
                    parts = []
                    for part in v_str.split("."):
                        digits = "".join(c for c in part if c.isdigit())
                        if digits:
                            parts.append(int(digits))
                    return parts

                remote_v = parse_ver(tag)
                local_v = parse_ver(self.current_version)

                if dl_url and remote_v > local_v:
                    self.update_found.emit(tag, body, dl_url)
                else:
                    self.no_update.emit(self.current_version)
        except Exception as e:
            self.error_occurred.emit(str(e))

class UpdateDownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, download_url):
        super().__init__()
        self.download_url = download_url

    def run(self):
        try:
            dest_file = os.path.join(tempfile.gettempdir(), "PC_Player_Update.exe")
            req = urllib.request.Request(self.download_url, headers={"User-Agent": "PCPlayer-App"})
            with urllib.request.urlopen(req, timeout=30) as resp, open(dest_file, "wb") as out:
                total = int(resp.info().get("Content-Length", 0))
                downloaded = 0
                chunk_sz = 131072
                while True:
                    chunk = resp.read(chunk_sz)
                    if not chunk:
                        break
                    out.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = int((downloaded / total) * 100)
                        self.progress.emit(pct)
            self.finished.emit(dest_file)
        except Exception as e:
            self.error_occurred.emit(str(e))

try:
    import yt_dlp
    import imageio_ffmpeg
except ImportError:
    pass

class URLFetchThread(QThread):
    finished_signal = pyqtSignal(str, str, str, str) # title, stream_url, original_url, error
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'extractor_args': {'youtube': ['player_client=android,web']}
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                title = info.get('title', 'Unknown Web Media')
                
                stream_url = None
                for fmt in info.get('formats', []):
                    if 'manifest_url' in fmt:
                        stream_url = fmt['manifest_url']
                        break
                if not stream_url:
                    stream_url = info.get('url')
                    
                original_url = info.get('webpage_url', self.url)
                self.finished_signal.emit(title, stream_url, original_url, "")
        except Exception as e:
            self.finished_signal.emit("", "", "", str(e))

class DownloadThread(QThread):
    finished_signal = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            ffmpeg_loc = imageio_ffmpeg.get_ffmpeg_exe()
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {'youtube': ['player_client=android,web']},
                'ffmpeg_location': ffmpeg_loc,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished_signal.emit("Berhasil diunduh ke folder Downloads.")
        except Exception as e:
            self.finished_signal.emit(f"Gagal mengunduh: {str(e)}")

class PCPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Player")
        self.setGeometry(100, 100, 800, 600)
        self.setAcceptDrops(True)
        
        # Audio & Media Setup
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.bass_engine = BassEngine.get_instance()
        self.is_bass_active = False
        self.current_pitch = 0 # Semitones: -12 to +12
        
        self.settings = QSettings("MahfudPG", "PCPlayer")
        
        self.current_language = self.settings.value("language", "id")

        # Default Volume
        saved_volume = self.settings.value("volume", 1.0, type=float)
        self.audio_output.setVolume(saved_volume)
        
        self.playlist_files = []
        self.current_index = -1
        
        self.loop_a = -1
        self.loop_b = -1
        
        self.original_urls = {}
        
        # Status Pemutaran
        self.is_repeat = False
        self.is_shuffle = False
        
        # Load Theme
        theme_str = self.settings.value("is_dark_theme", "true")
        self.is_dark_theme = (theme_str.lower() == "true")
        
        self.accent_color = self.settings.value("accent_color", "#1db954")
        self.wallpaper_path = self.settings.value("wallpaper_path", "")
        
        self.init_ui()
        
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        self.bg_label.lower()
        self.apply_wallpaper()
        
        self.apply_theme()
        self.setup_shortcuts()
        
        # Connect signals
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.status_changed)

        # Timer untuk sinkronisasi posisi BASS engine
        self.bass_poll_timer = QTimer(self)
        self.bass_poll_timer.setInterval(200)
        self.bass_poll_timer.timeout.connect(self.on_bass_poll)

        self.last_batch_time = time.time()
        
        # Cek riwayat pemutaran terakhir
        QTimer.singleShot(500, self.prompt_resume_playback)

        # Cek pembaruan otomatis di latar belakang secara hening setelah antarmuka aktif
        QTimer.singleShot(2500, lambda: self.check_for_updates(silent=True))

        # Cek argumen jika dibuka via Open With atau Folder (Double Click)
        if len(sys.argv) > 1:
            for i in range(1, len(sys.argv)):
                path = sys.argv[i]
                if os.path.isdir(path):
                    self.add_folder_to_playlist(path)
                elif os.path.exists(path):
                    self.add_file_to_playlist(path)
            
            if self.playlist_files:
                self.play_track(0)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Video Widget
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        self.video_widget.hide()
        main_layout.addWidget(self.video_widget, stretch=3)
        
        # Playlist Area
        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.playlist_double_clicked)
        main_layout.addWidget(self.playlist_widget, stretch=2)
        
        # Timeline
        timeline_layout = QHBoxLayout()
        self.time_label_current = QLabel("00:00")
        self.timeline_slider = QSlider(Qt.Orientation.Horizontal)
        self.timeline_slider.sliderMoved.connect(self.set_position)
        self.time_label_total = QLabel("00:00")
        
        timeline_layout.addWidget(self.time_label_current)
        timeline_layout.addWidget(self.timeline_slider)
        timeline_layout.addWidget(self.time_label_total)
        main_layout.addLayout(timeline_layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("⏮")
        self.play_btn = QPushButton("▶")
        self.stop_btn = QPushButton("⏹")
        self.next_btn = QPushButton("⏭")
        
        self.prev_btn.clicked.connect(self.play_prev)
        self.play_btn.clicked.connect(self.toggle_play)
        self.stop_btn.clicked.connect(self.stop_media)
        self.next_btn.clicked.connect(self.play_next)
        
        # Volume
        self.vol_label = QLabel("Volume")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.audio_output.volume() * 100))
        self.volume_slider.valueChanged.connect(self.set_volume)
        
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(self.next_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.volume_slider, stretch=1)
        controls_layout.addWidget(self.vol_label)
        
        main_layout.addLayout(controls_layout)
        
        # Apply initial translations
        self.update_ui_texts()
        
    def setup_shortcuts(self):
        # Mendaftarkan shortcut secara global di dalam aplikasi
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.toggle_play)
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.set_sleep_timer)
        QShortcut(QKeySequence(Qt.Key.Key_G), self, self.play_next)
        QShortcut(QKeySequence(Qt.Key.Key_A), self, self.play_prev)
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, self.volume_up)
        QShortcut(QKeySequence(Qt.Key.Key_Down), self, self.volume_down)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self.forward_5s)
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self.backward_5s)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.exit_fullscreen)
        
        # Shortcut Kecepatan Pemutaran
        QShortcut(QKeySequence(Qt.Key.Key_S), self, self.speed_slow)
        QShortcut(QKeySequence(Qt.Key.Key_D), self, self.speed_normal)
        QShortcut(QKeySequence(Qt.Key.Key_F), self, self.speed_fast)
        
        # Shortcut Repeat & Shuffle
        QShortcut(QKeySequence(Qt.Key.Key_R), self, self.toggle_repeat)
        QShortcut(QKeySequence("C"), self).activated.connect(self.toggle_shuffle)
        
        # Shortcut Transpose Nada
        QShortcut(QKeySequence("1"), self, self.pitch_down)
        QShortcut(QKeySequence("2"), self, self.pitch_reset)
        QShortcut(QKeySequence("3"), self, self.pitch_up)
        
        # Shortcut A-B Loop
        QShortcut(QKeySequence("["), self).activated.connect(self.set_loop_a)
        QShortcut(QKeySequence("]"), self).activated.connect(self.set_loop_b)
        QShortcut(QKeySequence("\\"), self).activated.connect(self.clear_loop)
        
        # Shortcut Search & Download
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.search_song)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.download_current)
        
        # Shortcut Layar Penuh
        QShortcut(QKeySequence("F11"), self).activated.connect(self.toggle_fullscreen)
        
        # Shortcut Info Audio
        QShortcut(QKeySequence(Qt.Key.Key_I), self, self.show_audio_info)
        
        # Shortcut Paste URL
        QShortcut(QKeySequence("Ctrl+L"), self, self.prompt_url)
        
        # Shortcut Hapus Playlist
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self, self.remove_selected_item)
        QShortcut(QKeySequence("Ctrl+Delete"), self, self.clear_playlist)
        
        # Shortcut Save/Load Playlist
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_playlist)
        QShortcut(QKeySequence("Ctrl+O"), self, self.load_playlist)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_1:
            self.pitch_down()
            return
        elif key == Qt.Key.Key_2:
            self.pitch_reset()
            return
        elif key == Qt.Key.Key_3:
            self.pitch_up()
            return
        super().keyPressEvent(event)

    def prompt_url(self):
        url, ok = QInputDialog.getText(self, "Putar dari Link", "Masukkan URL (YouTube, Radio Streaming, dll):")
        if ok and url:
            self.setWindowTitle("PC Player [Memproses URL... Mohon tunggu]")
            self.fetch_thread = URLFetchThread(url)
            self.fetch_thread.finished_signal.connect(self.on_url_fetched)
            self.fetch_thread.start()

    def check_for_updates(self, silent=True):
        if hasattr(self, 'update_checker') and self.update_checker.isRunning():
            return
        self.update_checker = UpdateCheckerThread(APP_VERSION, GITHUB_REPO, silent=silent)
        self.update_checker.update_found.connect(self.on_update_found)
        self.update_checker.no_update.connect(lambda cur_v: self.on_no_update(cur_v, silent))
        self.update_checker.error_occurred.connect(lambda err: self.on_update_error(err, silent))
        self.update_checker.start()

    def on_update_found(self, tag, notes, dl_url):
        title = self.tr("Pembaruan Tersedia")
        msg = f"Pembaruan PC Player v{tag} telah tersedia!\nVersi Anda saat ini: v{APP_VERSION}\n\nCatatan Rilis:\n{notes}\n\nApakah Anda ingin mengunduh dan memperbarui sekarang?"
        reply = QMessageBox.question(
            self,
            title,
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.start_downloading_update(dl_url, tag)

    def on_no_update(self, cur_v, silent):
        if not silent:
            QMessageBox.information(self, self.tr("Versi Terbaru"), f"Anda sudah menggunakan versi terbaru PC Player (v{cur_v}).")

    def on_update_error(self, err, silent):
        if not silent:
            QMessageBox.warning(self, "Pembaruan", f"Gagal memeriksa pembaruan:\n{err}")

    def start_downloading_update(self, dl_url, tag):
        self.notify("Pembaruan", f"Mengunduh pembaruan v{tag}...")
        self.update_dl_thread = UpdateDownloadThread(dl_url)
        self.update_dl_thread.progress.connect(self.on_update_dl_progress)
        self.update_dl_thread.finished.connect(self.on_update_dl_finished)
        self.update_dl_thread.error_occurred.connect(self.on_update_dl_error)
        self.update_dl_thread.start()

    def on_update_dl_progress(self, pct):
        self.setWindowTitle(f"PC Player [Mengunduh Pembaruan: {pct}%]")

    def on_update_dl_finished(self, new_exe_path):
        self.update_title()
        current_exe = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
        
        if getattr(sys, "frozen", False):
            bat_path = os.path.join(tempfile.gettempdir(), "pcplayer_apply_update.bat")
            bat_content = f'''@echo off
timeout /t 2 /nobreak >nul
copy /y "{new_exe_path}" "{current_exe}" >nul
explorer.exe "{current_exe}"
del "%~f0"
'''
            try:
                with open(bat_path, "w", encoding="utf-8") as f:
                    f.write(bat_content)
                QMessageBox.information(
                    self,
                    "Memasang Pembaruan",
                    "Pembaruan berhasil diunduh!\nAplikasi akan memulai ulang secara otomatis untuk menerapkan versi baru."
                )
                subprocess.Popen(["cmd.exe", "/c", bat_path], creationflags=subprocess.CREATE_NO_WINDOW)
                QApplication.quit()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Gagal menerapkan pembaruan: {e}")
        else:
            QMessageBox.information(
                self,
                "Pembaruan Berhasil Diunduh",
                f"File versi baru telah tersimpan di:\n{new_exe_path}"
            )

    def on_update_dl_error(self, err):
        self.update_title()
        QMessageBox.warning(self, "Error Unduh", f"Gagal mengunduh pembaruan:\n{err}")

    def notify(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        msg.show()
        QTimer.singleShot(800, msg.accept)

    def on_url_fetched(self, title, stream_url, original_url, error):
        self.update_title() # Kembalikan judul normal
        if error:
            self.notify("Error", f"Gagal memuat URL:\n{error}")
            return
            
        display_name = f"[Web] {title}"
        self.playlist_files.append(stream_url)
        self.original_urls[stream_url] = original_url
        self.playlist_widget.addItem(display_name)
        
        # Putar otomatis jika sedang tidak memutar apapun
        if self.player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
            self.play_track(len(self.playlist_files) - 1)

    def toggle_repeat(self):
        self.is_repeat = not self.is_repeat
        self.update_title()
        
    def toggle_shuffle(self):
        self.is_shuffle = not self.is_shuffle
        self.update_title()
        
    def pitch_down(self):
        self.set_pitch(self.current_pitch - 1)

    def pitch_up(self):
        self.set_pitch(self.current_pitch + 1)

    def pitch_reset(self):
        self.set_pitch(0)

    def set_pitch(self, semitones):
        self.current_pitch = max(-12, min(12, int(semitones)))
        self.bass_engine.set_pitch(float(self.current_pitch))
        self.update_title()
        
        # Audio & Screen reader feedback
        if self.current_pitch == 0:
            msg = self.tr("Nada Normal (0)")
        elif self.current_pitch > 0:
            msg = self.tr(f"Nada +{self.current_pitch}")
        else:
            msg = self.tr(f"Nada {self.current_pitch}")
            
        if not self.is_bass_active and self.current_index >= 0:
            msg += " (Video/Streaming tidak mendukung transpose)"
            
        self.notify(self.tr("Transpose"), msg)

    def update_title(self):
        title = "PC Player"
        status = []
        if self.current_pitch != 0:
            sign = "+" if self.current_pitch > 0 else ""
            status.append(f"Nada: {sign}{self.current_pitch}")
        if self.is_repeat:
            status.append("Repeat: ON")
        if self.is_shuffle:
            status.append("Shuffle: ON")
            
        if status:
            title += " [" + ", ".join(status) + "]"
        self.setWindowTitle(title)

    def show_audio_info(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState and self.current_index == -1:
            QMessageBox.information(self, "Info Audio", "Tidak ada lagu yang sedang diputar.")
            return
            
        meta = self.player.metaData()
        info = []
        
        if meta:
            title = meta.stringValue(QMediaMetaData.Key.Title)
            if title: info.append(f"Judul: {title}")
            
            author = meta.stringValue(QMediaMetaData.Key.Author)
            if author: info.append(f"Artis: {author}")
            
            codec = meta.stringValue(QMediaMetaData.Key.AudioCodec)
            if codec: info.append(f"Codec: {codec}")
            
            bit_rate = meta.value(QMediaMetaData.Key.AudioBitRate)
            if bit_rate:
                try:
                    info.append(f"Bitrate: {int(bit_rate)//1000} kbps")
                except:
                    pass
            
        if not info:
            info.append("Informasi metadata lengkap tidak tersedia untuk file ini.")
            
        # Menggunakan MessageBox agar otomatis dibacakan oleh Screen Reader
        QMessageBox.information(self, "Info Detail Audio", ", ".join(info))

    def volume_up(self):
        new_vol = min(100, self.volume_slider.value() + 5)
        self.volume_slider.setValue(new_vol)
        
    def volume_down(self):
        new_vol = max(0, self.volume_slider.value() - 5)
        self.volume_slider.setValue(new_vol)
        
    def smooth_seek(self, position):
        if self.is_currently_playing():
            def _do_seek():
                self.set_position(position)
                self.do_fade_in(lambda: None, fast=True)
            self.do_fade_out(_do_seek, fast=True)
        else:
            self.set_position(position)

    def forward_5s(self):
        cur_pos = self.bass_engine.get_position_ms() if self.is_bass_active else self.player.position()
        dur = self.bass_engine.get_duration_ms() if self.is_bass_active else self.player.duration()
        new_pos = min(dur, cur_pos + 5000)
        self.smooth_seek(new_pos)
        
    def backward_5s(self):
        cur_pos = self.bass_engine.get_position_ms() if self.is_bass_active else self.player.position()
        new_pos = max(0, cur_pos - 5000)
        self.smooth_seek(new_pos)
        
    def exit_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()

    def speed_slow(self):
        self.player.setPlaybackRate(0.5)
        self.bass_engine.set_playback_rate(0.5)
        
    def speed_normal(self):
        self.player.setPlaybackRate(1.0)
        self.bass_engine.set_playback_rate(1.0)
        
    def speed_fast(self):
        self.player.setPlaybackRate(1.5)
        self.bass_engine.set_playback_rate(1.5)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'bg_label'):
            self.bg_label.resize(self.size())

    def apply_wallpaper(self):
        if self.wallpaper_path and os.path.exists(self.wallpaper_path):
            pixmap = QPixmap(self.wallpaper_path)
            self.bg_label.setPixmap(pixmap)
            self.bg_label.show()
        else:
            self.bg_label.clear()
            self.bg_label.hide()
            
    def apply_theme(self):
        window_bg = "transparent" if (hasattr(self, 'wallpaper_path') and self.wallpaper_path) else ("#2b2b2b" if self.is_dark_theme else "#f0f0f0")
        list_bg = "rgba(30, 30, 30, 0.7)" if (hasattr(self, 'wallpaper_path') and self.wallpaper_path and self.is_dark_theme) else ("rgba(255, 255, 255, 0.7)" if (hasattr(self, 'wallpaper_path') and self.wallpaper_path) else ("#1e1e1e" if self.is_dark_theme else "#ffffff"))
        text_color = "white" if self.is_dark_theme else "black"
        
        self.setStyleSheet(f"""
            QWidget {{ background-color: {window_bg}; color: {text_color}; }}
            QPushButton {{ background-color: {"#444" if self.is_dark_theme else "#e0e0e0"}; border: 1px solid {"#555" if self.is_dark_theme else "#ccc"}; padding: 5px; border-radius: 3px; }}
            QPushButton:hover {{ background-color: {"#555" if self.is_dark_theme else "#d0d0d0"}; }}
            QListWidget {{ background-color: {list_bg}; color: {text_color}; border: 1px solid {"#444" if self.is_dark_theme else "#ccc"}; }}
            QListWidget::item:selected {{ background-color: {self.accent_color}; color: {"black" if self.is_dark_theme else "white"}; }}
            QSlider::handle:horizontal {{ background-color: {self.accent_color}; }}
            QMessageBox {{ background-color: {"#2b2b2b" if self.is_dark_theme else "#f0f0f0"}; color: {text_color}; }}
        """)
        
        if hasattr(self, 'centralWidget') and self.centralWidget():
            self.centralWidget().setStyleSheet("background-color: transparent;")

    def toggle_fullscreen(self):
        if self.video_widget.isVisible():
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        else:
            self.notify("Info", "Layar penuh hanya berlaku saat memutar video.")

    def set_loop_a(self):
        cur_pos = self.bass_engine.get_position_ms() if self.is_bass_active else self.player.position()
        self.loop_a = cur_pos
        self.notify("A-B Loop", "Titik A ditandai.")
        
    def set_loop_b(self):
        cur_pos = self.bass_engine.get_position_ms() if self.is_bass_active else self.player.position()
        if self.loop_a != -1 and cur_pos > self.loop_a:
            self.loop_b = cur_pos
            self.notify("A-B Loop", "Titik B ditandai. Looping aktif.")
        else:
            self.notify("Error", "Tandai Titik A terlebih dahulu, dan pastikan Titik B berada setelah Titik A.")
            
    def clear_loop(self):
        self.loop_a = -1
        self.loop_b = -1
        self.notify("A-B Loop", "Looping dibatalkan.")

    def search_song(self):
        text, ok = QInputDialog.getText(self, "Cari Lagu", "Ketik judul lagu atau penyanyi (Mencari di YouTube):")
        if ok and text:
            search_query = f"ytsearch1:{text}"
            self.notify("Mencari", f"Sedang mencari '{text}' di YouTube. Harap tunggu...")
            self.fetch_thread = URLFetchThread(search_query)
            self.fetch_thread.finished_signal.connect(self.on_url_fetched)
            self.fetch_thread.start()

    def download_current(self):
        if self.current_index >= 0 and self.current_index < len(self.playlist_files):
            current_path = self.playlist_files[self.current_index]
            original_url = self.original_urls.get(current_path)
            if original_url:
                self.notify("Download", "Memulai proses download di latar belakang. Kecepatan sangat bergantung pada server YouTube dan koneksi Anda. Silakan cek folder Downloads nanti.")
                self.download_thread = DownloadThread(original_url)
                self.download_thread.finished_signal.connect(lambda msg: self.notify("Info Download", msg))
                self.download_thread.start()
            else:
                self.notify("Download Error", "Ini adalah file lokal. Hanya tautan streaming yang dapat diunduh.")

    def tr(self, text):
        import lang
        lang_code = getattr(self, "current_language", "id")
        if lang_code == "id" or text not in lang.TRANSLATIONS:
            return text
        return lang.TRANSLATIONS[text].get(lang_code, text)

    def set_language(self, lang_code):
        self.current_language = lang_code
        self.settings.setValue("language", lang_code)
        self.update_ui_texts()
        self.notify(self.tr("Bahasa / Language"), self.tr("Bahasa telah diubah / Language has been changed."))

    def update_ui_texts(self):
        self.prev_btn.setAccessibleName(self.tr("Trek Sebelumnya"))
        self.play_btn.setAccessibleName(self.tr("Mainkan / Jeda"))
        self.stop_btn.setAccessibleName(self.tr("Berhenti"))
        self.next_btn.setAccessibleName(self.tr("Trek Berikutnya"))
        self.vol_label.setText(self.tr("Volume"))
        self.setWindowTitle("PC Player")

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        
        # 1. Sub-menu Pemutaran
        playback_menu = context_menu.addMenu(self.tr("Menu Pemutaran"))
        sleep_action = playback_menu.addAction(self.tr("Pengatur Waktu Tidur (Ctrl+T)"))
        playback_menu.addSeparator()
        play_pause_action = playback_menu.addAction(self.tr("Mainkan / Jeda (Spasi)"))
        prev_action = playback_menu.addAction(self.tr("Lagu Sebelumnya (A)"))
        next_action = playback_menu.addAction(self.tr("Lagu Berikutnya (G)"))
        playback_menu.addSeparator()
        pitch_down_action = playback_menu.addAction(self.tr("Turunkan Nada (1)"))
        pitch_reset_action = playback_menu.addAction(self.tr("Reset Nada Asli (2)"))
        pitch_up_action = playback_menu.addAction(self.tr("Naikkan Nada (3)"))
        playback_menu.addSeparator()
        slow_action = playback_menu.addAction(self.tr("Putar Lambat (S)"))
        normal_action = playback_menu.addAction(self.tr("Putar Normal (D)"))
        fast_action = playback_menu.addAction(self.tr("Putar Cepat (F)"))
        playback_menu.addSeparator()
        repeat_action = playback_menu.addAction(self.tr("Ulangi / Repeat (R)"))
        shuffle_action = playback_menu.addAction(self.tr("Acak / Shuffle (C)"))
        
        # 2. Sub-menu Looping A-B
        loop_menu = context_menu.addMenu(self.tr("Menu Looping A-B"))
        loop_a_action = loop_menu.addAction(self.tr("Set Titik A Loop ([)"))
        loop_b_action = loop_menu.addAction(self.tr("Set Titik B Loop (])"))
        loop_clear_action = loop_menu.addAction(self.tr("Hapus Loop (\\)"))
        
        # 3. Sub-menu Online & Download
        online_menu = context_menu.addMenu(self.tr("Menu Online & Download"))
        search_action = online_menu.addAction(self.tr("Cari Lagu (Ctrl + F)"))
        url_action = online_menu.addAction(self.tr("Putar dari Link (Ctrl + L)"))
        download_action = online_menu.addAction(self.tr("Download Lagu Ini (Ctrl + D)"))
        
        # 4. Sub-menu Tampilan & Video
        appearance_menu = context_menu.addMenu(self.tr("Menu Tampilan & Video"))
        if self.isFullScreen():
            fullscreen_action = appearance_menu.addAction(self.tr("Video mode layar normal (F11)"))
        else:
            fullscreen_action = appearance_menu.addAction(self.tr("Video mode layar penuh (F11)"))
        appearance_menu.addSeparator()
        if self.is_dark_theme:
            theme_action = appearance_menu.addAction(self.tr("Ubah ke Tema Terang (Light Mode)"))
        else:
            theme_action = appearance_menu.addAction(self.tr("Ubah ke Tema Gelap (Dark Mode)"))
            
        accent_action = appearance_menu.addAction(self.tr("Ubah Warna Aksen (Custom Tema)"))
        
        wp_menu = appearance_menu.addMenu(self.tr("Galeri Latar (Internal)"))
        wp1_action = wp_menu.addAction(self.tr("1. Gelap Abstrak"))
        wp2_action = wp_menu.addAction(self.tr("2. Terang Elegan"))
        wp3_action = wp_menu.addAction(self.tr("3. Neon Musik"))
        
        wp1_action.setCheckable(True)
        wp2_action.setCheckable(True)
        wp3_action.setCheckable(True)
        
        if self.wallpaper_path:
            if "1_dark_gradient.jpg" in self.wallpaper_path: wp1_action.setChecked(True)
            elif "2_light_gradient.jpg" in self.wallpaper_path: wp2_action.setChecked(True)
            elif "3_neon_vibes.jpg" in self.wallpaper_path: wp3_action.setChecked(True)
        
        wp_custom_action = appearance_menu.addAction(self.tr("Impor Latar Pribadi (Dari PC)"))
        wp_clear_action = appearance_menu.addAction(self.tr("Hapus Latar Belakang"))
        
        # 5. Sub-menu Info & Sistem
        sys_menu = context_menu.addMenu(self.tr("Menu Info & Sistem"))
        
        lang_menu = sys_menu.addMenu(self.tr("Pilih Bahasa / Language"))
        lang_id_action = lang_menu.addAction("🇮🇩 Bahasa Indonesia")
        lang_en_action = lang_menu.addAction("🇬🇧 English")
        
        info_action = sys_menu.addAction(self.tr("Info Audio (I)"))
        update_action = sys_menu.addAction(self.tr("Periksa Pembaruan..."))
        register_action = sys_menu.addAction(self.tr("Jadikan Pemutar Utama (Daftarkan ke Windows)"))
        
        context_menu.setStyleSheet("""
            QMenu { background-color: #2b2b2b; color: white; border: 1px solid #444; font-size: 14px;}
            QMenu::item { padding: 8px 25px; }
            QMenu::item:selected { background-color: #1db954; color: black; }
        """ if self.is_dark_theme else "")
        
        action = context_menu.exec(self.mapToGlobal(event.pos()))
        
        if action == lang_id_action:
            self.set_language("id")
        elif action == lang_en_action:
            self.set_language("en")
        elif action == sleep_action:
            self.set_sleep_timer()
        elif action == play_pause_action:
            self.toggle_play()
        elif action == next_action:
            self.play_next()
        elif action == prev_action:
            self.play_prev()
        elif action == pitch_down_action:
            self.pitch_down()
        elif action == pitch_reset_action:
            self.pitch_reset()
        elif action == pitch_up_action:
            self.pitch_up()
        elif action == slow_action:
            self.speed_slow()
        elif action == normal_action:
            self.speed_normal()
        elif action == fast_action:
            self.speed_fast()
        elif action == repeat_action:
            self.toggle_repeat()
        elif action == shuffle_action:
            self.toggle_shuffle()
        elif action == search_action:
            self.search_song()
        elif action == url_action:
            self.prompt_url()
        elif action == download_action:
            self.download_current()
        elif action == loop_a_action:
            self.set_loop_a()
        elif action == loop_b_action:
            self.set_loop_b()
        elif action == loop_clear_action:
            self.clear_loop()
        elif action == info_action:
            self.show_audio_info()
        elif action == update_action:
            self.check_for_updates(silent=False)
        elif action == theme_action:
            self.is_dark_theme = not self.is_dark_theme
            self.settings.setValue("is_dark_theme", str(self.is_dark_theme).lower())
            self.apply_theme()
        elif action == accent_action:
            self.choose_accent_color()
        elif action == wp1_action:
            self.set_builtin_wallpaper("1_dark_gradient.jpg")
        elif action == wp2_action:
            self.set_builtin_wallpaper("2_light_gradient.jpg")
        elif action == wp3_action:
            self.set_builtin_wallpaper("3_neon_vibes.jpg")
        elif action == wp_custom_action:
            self.choose_custom_wallpaper()
        elif action == wp_clear_action:
            self.wallpaper_path = ""
            self.settings.setValue("wallpaper_path", "")
            self.apply_wallpaper()
            self.apply_theme()
        elif action == fullscreen_action:
            self.toggle_fullscreen()
        elif action == register_action:
            self.register_to_windows()

    def choose_accent_color(self):
        color = QColorDialog.getColor(initial=QColor(self.accent_color), parent=self, title="Pilih Warna Aksen")
        if color.isValid():
            self.accent_color = color.name()
            self.settings.setValue("accent_color", self.accent_color)
            self.apply_theme()
            
    def set_builtin_wallpaper(self, filename):
        import sys
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        full_path = os.path.join(base_path, "assets", "wallpapers", filename)
        if os.path.exists(full_path):
            self.wallpaper_path = full_path
            self.settings.setValue("wallpaper_path", self.wallpaper_path)
            self.apply_wallpaper()
            self.apply_theme()
        else:
            self.notify("Error", f"Wallpaper bawaan tidak ditemukan di {full_path}")
            
    def choose_custom_wallpaper(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Wallpaper", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.wallpaper_path = path
            self.settings.setValue("wallpaper_path", self.wallpaper_path)
            self.apply_wallpaper()
            self.apply_theme()

    def register_to_windows(self):
        try:
            exe_path = sys.executable
            if "python" in exe_path.lower() and not getattr(sys, 'frozen', False):
                exe_path = os.path.abspath(__file__)
            else:
                exe_path = sys.executable
                
            prog_id = "PCPlayer.Media"
            
            # Register ProgID for Files
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}")
            winreg.SetValue(key, "", winreg.REG_SZ, "PC Player Media File")
            winreg.CloseKey(key)
            
            key_cmd = winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\shell\open\command")
            winreg.SetValue(key_cmd, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
            winreg.CloseKey(key_cmd)
            
            # Register Applications for "Open With" list
            app_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\Applications\PC Player.exe")
            winreg.SetValueEx(app_key, "FriendlyAppName", 0, winreg.REG_SZ, "PC Player")
            winreg.CloseKey(app_key)
            
            app_cmd_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\Applications\PC Player.exe\shell\open\command")
            winreg.SetValue(app_cmd_key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
            winreg.CloseKey(app_cmd_key)
            
            app_supp_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\Applications\PC Player.exe\SupportedTypes")
            
            extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.opus', '.mp4', '.webm', '.aac', '.avi', '.mkv']
            for ext in extensions:
                # 1. Default ProgID
                key_ext = winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{ext}")
                winreg.SetValue(key_ext, "", winreg.REG_SZ, prog_id)
                winreg.CloseKey(key_ext)
                
                # 2. OpenWithProgIds
                key_openwith = winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{ext}\OpenWithProgids")
                winreg.SetValueEx(key_openwith, prog_id, 0, winreg.REG_SZ, "")
                winreg.CloseKey(key_openwith)
                
                # 3. SupportedTypes
                winreg.SetValueEx(app_supp_key, ext, 0, winreg.REG_SZ, "")
                
            winreg.CloseKey(app_supp_key)
            
            # Force Context Menu for Audio and Video
            for sys_type in ['audio', 'video']:
                key_sfa = winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\SystemFileAssociations\{sys_type}\shell\PlayWithPCPlayer")
                winreg.SetValue(key_sfa, "", winreg.REG_SZ, "Putar dengan PC Player")
                winreg.SetValueEx(key_sfa, "Icon", 0, winreg.REG_SZ, f'"{exe_path}"')
                key_sfa_cmd = winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\SystemFileAssociations\{sys_type}\shell\PlayWithPCPlayer\command")
                winreg.SetValue(key_sfa_cmd, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
                winreg.CloseKey(key_sfa_cmd)
                winreg.CloseKey(key_sfa)
                
            # Register for Folders (Directory context menu)
            key_dir = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\Directory\shell\PlayWithPCPlayer")
            winreg.SetValue(key_dir, "", winreg.REG_SZ, "Putar dengan PC Player")
            winreg.SetValueEx(key_dir, "Icon", 0, winreg.REG_SZ, f'"{exe_path}"')
            
            key_dir_cmd = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\Directory\shell\PlayWithPCPlayer\command")
            winreg.SetValue(key_dir_cmd, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
            winreg.CloseKey(key_dir_cmd)
            winreg.CloseKey(key_dir)
                
            QMessageBox.information(self, "Sukses", "Berhasil mendaftarkan PC Player ke Windows secara permanen!\n\nKlik Kanan pada file lagu akan selalu menampilkan 'Putar dengan PC Player'.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mendaftarkan ke Windows:\n{str(e)}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                if os.path.isdir(path):
                    self.add_folder_to_playlist(path)
                else:
                    self.add_file_to_playlist(path)
        
        if self.playlist_files and self.current_index == -1:
            self.play_track(0)

    def add_folder_to_playlist(self, folder_path):
        supported_ext = ('.mp3', '.wav', '.flac', '.ogg', '.m4a', '.opus', '.mp4', '.webm', '.aac', '.avi', '.mkv')
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(supported_ext):
                    self.add_file_to_playlist(os.path.join(root, file))

    def add_file_to_playlist(self, path):
        name = os.path.basename(path)
        self.playlist_files.append(path)
        self.playlist_widget.addItem(name)

    def remove_selected_item(self):
        selected_items = self.playlist_widget.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            row = self.playlist_widget.row(item)
            self.playlist_widget.takeItem(row)
            del self.playlist_files[row]
            
            if row == self.current_index:
                self.stop_media()
                self.current_index = -1
            elif row < self.current_index:
                self.current_index -= 1

    def clear_playlist(self):
        self.stop_media()
        self.playlist_widget.clear()
        self.playlist_files.clear()
        self.current_index = -1

    def save_playlist(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Simpan Playlist", "", "Playlist Files (*.m3u)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for path in self.playlist_files:
                        f.write(path + "\n")
                QMessageBox.information(self, "Sukses", "Playlist berhasil disimpan!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menyimpan playlist:\n{str(e)}")

    def load_playlist(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Buka Playlist", "", "Playlist Files (*.m3u)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        path = line.strip()
                        if path:
                            if path.startswith("http://") or path.startswith("https://"):
                                self.playlist_files.append(path)
                                self.playlist_widget.addItem(f"[Web] {path}")
                            elif os.path.exists(path):
                                self.add_file_to_playlist(path)
                if self.playlist_files and self.current_index == -1:
                    self.play_track(0)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal memuat playlist:\n{str(e)}")

    def playlist_double_clicked(self, item):
        idx = self.playlist_widget.row(item)
        self.play_track(idx)

    def play_track(self, index):
        def _switch_track():
            if 0 <= index < len(self.playlist_files):
                self.current_index = index
                raw_path = self.playlist_files[index]
                clean_path = raw_path.strip().strip('"').strip("'")
                norm_path = os.path.normpath(clean_path)
                
                is_video = norm_path.lower().endswith(('.mp4', '.webm', '.avi', '.mkv'))
                is_url = norm_path.startswith("http://") or norm_path.startswith("https://")

                if is_video:
                    self.video_widget.show()
                else:
                    self.video_widget.hide()

                # Gunakan BASS Engine untuk file audio lokal agar mendukung real-time Transpose
                use_bass = False
                if not is_video and not is_url and self.bass_engine.initialized:
                    if os.path.exists(norm_path):
                        use_bass = self.bass_engine.load_file(norm_path)

                if use_bass:
                    self.player.stop()
                    self.is_bass_active = True
                    dur = self.bass_engine.get_duration_ms()
                    self.update_duration(dur)
                    
                    def _play():
                        self.bass_engine.play()
                        self.play_btn.setText("⏸")
                        self.bass_poll_timer.start()
                    self.do_fade_in(_play)
                else:
                    self.bass_engine.stop()
                    self.is_bass_active = False
                    self.bass_poll_timer.stop()
                    if is_url:
                        self.player.setSource(QUrl(raw_path))
                    else:
                        self.player.setSource(QUrl.fromLocalFile(norm_path))
                        
                    def _play():
                        self.player.play()
                        self.play_btn.setText("⏸")
                    self.do_fade_in(_play)

                self.playlist_widget.setCurrentRow(index)
                
        if getattr(self, "fade_timer", None) and self.fade_timer.isActive():
            self.fade_timer.stop()
            self.audio_output.setVolume(self.volume_slider.value() / 100.0)
            self.bass_engine.set_volume(self.volume_slider.value() / 100.0)
            _switch_track()
        elif self.is_currently_playing():
            self.do_fade_out(_switch_track)
        else:
            _switch_track()

    def is_currently_playing(self):
        if self.is_bass_active:
            return self.bass_engine.is_playing()
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def is_currently_paused(self):
        if self.is_bass_active:
            return self.bass_engine.is_paused()
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState

    def on_bass_poll(self):
        if not self.is_bass_active:
            self.bass_poll_timer.stop()
            return

        pos = self.bass_engine.get_position_ms()
        dur = self.bass_engine.get_duration_ms()

        # Looping A-B
        if self.loop_a != -1 and self.loop_b != -1 and self.loop_b > self.loop_a:
            if pos >= self.loop_b:
                self.bass_engine.set_position_ms(self.loop_a)
                pos = self.loop_a

        self.timeline_slider.blockSignals(True)
        self.timeline_slider.setValue(pos)
        self.timeline_slider.blockSignals(False)
        self.time_label_current.setText(self.format_time(pos))

        # Check end of track
        if self.bass_engine.is_stopped() and pos >= max(0, dur - 500) and dur > 0:
            self.bass_poll_timer.stop()
            if self.is_repeat:
                self.bass_engine.set_position_ms(0)
                self.bass_engine.play()
                self.bass_poll_timer.start()
            else:
                self.play_next()

    def toggle_play(self):
        if getattr(self, "fade_timer", None) and self.fade_timer.isActive():
            return
            
        if self.is_currently_playing():
            def _pause():
                if self.is_bass_active:
                    self.bass_engine.pause()
                    self.bass_poll_timer.stop()
                else:
                    self.player.pause()
                self.play_btn.setText("▶")
            self.do_fade_out(_pause)
        else:
            if self.current_index == -1 and self.playlist_files:
                self.play_track(0)
            else:
                def _play():
                    if self.is_bass_active:
                        self.bass_engine.play()
                        self.bass_poll_timer.start()
                    else:
                        self.player.play()
                    self.play_btn.setText("⏸")
                self.do_fade_in(_play)

    def stop_media(self):
        if getattr(self, "fade_timer", None) and self.fade_timer.isActive():
            return
            
        def _stop():
            if self.is_bass_active:
                self.bass_engine.stop()
                self.bass_poll_timer.stop()
            else:
                self.player.stop()
            self.play_btn.setText("▶")
            self.timeline_slider.setValue(0)
            self.time_label_current.setText("00:00")
            
        if self.is_currently_playing():
            self.do_fade_out(_stop)
        else:
            _stop()

    def do_fade_out(self, callback, fast=False):
        self.fade_timer = QTimer(self)
        self.fade_timer.setInterval(10 if fast else 25)
        self.current_fade_vol = self.audio_output.volume()
        steps = 5 if fast else 15
        self.fade_step_val = self.current_fade_vol / steps if steps > 0 else 0
        
        def step():
            self.current_fade_vol -= self.fade_step_val
            if self.current_fade_vol <= 0:
                self.audio_output.setVolume(0)
                self.bass_engine.set_volume(0)
                self.fade_timer.stop()
                callback()
            else:
                self.audio_output.setVolume(self.current_fade_vol)
                self.bass_engine.set_volume(self.current_fade_vol)
        
        self.fade_timer.timeout.connect(step)
        self.fade_timer.start()

    def do_fade_in(self, callback, fast=False):
        target_vol = self.volume_slider.value() / 100.0
        self.audio_output.setVolume(0)
        self.bass_engine.set_volume(0)
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
                self.bass_engine.set_volume(target_vol)
                self.fade_timer.stop()
            else:
                self.audio_output.setVolume(self.current_fade_vol)
                self.bass_engine.set_volume(self.current_fade_vol)
                
        self.fade_timer.timeout.connect(step)
        self.fade_timer.start()

    def play_next(self):
        if self.is_shuffle and len(self.playlist_files) > 1:
            next_idx = self.current_index
            while next_idx == self.current_index:
                next_idx = random.randint(0, len(self.playlist_files) - 1)
            self.play_track(next_idx)
        elif self.current_index < len(self.playlist_files) - 1:
            self.play_track(self.current_index + 1)
        else:
            self.stop_media()

    def play_prev(self):
        cur_pos = self.bass_engine.get_position_ms() if self.is_bass_active else self.player.position()
        if cur_pos > 3000:
            self.set_position(0)
        elif self.current_index > 0:
            self.play_track(self.current_index - 1)

    def set_position(self, position):
        if self.is_bass_active:
            self.bass_engine.set_position_ms(position)
        else:
            self.player.setPosition(position)

    def update_position(self, position):
        if self.loop_a != -1 and self.loop_b != -1 and self.loop_b > self.loop_a:
            if position >= self.loop_b:
                self.player.setPosition(self.loop_a)
                position = self.loop_a

        self.timeline_slider.blockSignals(True)
        self.timeline_slider.setValue(position)
        self.timeline_slider.blockSignals(False)
        self.time_label_current.setText(self.format_time(position))

    def update_duration(self, duration):
        self.timeline_slider.setRange(0, duration)
        self.time_label_total.setText(self.format_time(duration))

    def format_time(self, ms):
        s = ms // 1000
        m = s // 60
        s = s % 60
        return f"{m:02}:{s:02}"

    def set_volume(self, value):
        volume = value / 100
        self.audio_output.setVolume(volume)
        self.bass_engine.set_volume(volume)
        self.settings.setValue("volume", volume)

    def status_changed(self, status):
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
                self.do_fade_in(_play)


    def prompt_resume_playback(self):
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
                f"Terdapat riwayat pemutaran sebelumnya:\n'{filename}'\ndi menit {time_str}.\n\nIngin melanjutkan pemutaran ini?", 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.playlist_files = last_playlist
                for path in self.playlist_files:
                    self.playlist_widget.addItem(os.path.basename(path))
                
                self.current_index = last_index
                self.play_track(last_index)
                if last_position > 0:
                    QTimer.singleShot(600, lambda: self.set_position(last_position))
                
                self.playlist_widget.setCurrentRow(last_index)
            else:
                self.settings.remove("last_playlist")
                self.settings.remove("last_index")
                self.settings.remove("last_position")

    def closeEvent(self, event):
        cur_pos = self.bass_engine.get_position_ms() if self.is_bass_active else self.player.position()
        if self.playlist_files and self.current_index >= 0:
            self.settings.setValue("last_playlist", self.playlist_files)
            self.settings.setValue("last_index", self.current_index)
            self.settings.setValue("last_position", cur_pos)
        else:
            self.settings.remove("last_playlist")
            self.settings.remove("last_index")
            self.settings.remove("last_position")
            
        if getattr(self, "is_closing", False):
            self.bass_engine.stop()
            event.accept()
            return
            
        if self.is_currently_playing():
            event.ignore()
            self.is_closing = True
            def _close():
                self.player.stop()
                self.bass_engine.stop()
                self.close()
            self.do_fade_out(_close)
        else:
            self.bass_engine.stop()
            event.accept()

    def set_sleep_timer(self):
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        
        if getattr(self, "sleep_timer", None) and self.sleep_timer.isActive():
            reply = QMessageBox.question(self, "Sleep Timer Aktif", "Timer tidur sedang berjalan. Apakah Anda ingin membatalkannya?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.sleep_timer.stop()
                self.notify("Sleep Timer", "Timer tidur berhasil dibatalkan.")
            return

        minutes, ok = QInputDialog.getInt(self, "Pengatur Waktu Tidur", "Masukkan waktu sebelum pemutaran berhenti otomatis (menit):", 30, 1, 1440)
        if ok and minutes > 0:
            self.sleep_timer = QTimer(self)
            self.sleep_timer.setSingleShot(True)
            self.sleep_timer.timeout.connect(self.pause_for_sleep_timer)
            self.sleep_timer.start(minutes * 60 * 1000)
            self.notify("Sleep Timer", f"Pemutaran akan dijeda otomatis dalam {minutes} menit.")

    def pause_for_sleep_timer(self):
        if getattr(self, "fade_timer", None) and self.fade_timer.isActive():
            self.fade_timer.stop()
            
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            def _pause():
                self.player.pause()
                self.play_btn.setText("?")
            self.do_fade_out(_pause)

def main():
    app = QApplication(sys.argv)
    
    SERVER_NAME = "PCPlayer_SingleInstance_Server"
    
    # Cek apakah sudah ada instance PC Player yang berjalan
    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)
    if socket.waitForConnected(500):
        # Jika ya, kirim argumen (file) ke instance utama dan tutup instance baru ini
        if len(sys.argv) > 1:
            args_str = "|".join(sys.argv[1:])
            socket.write(args_str.encode('utf-8'))
            socket.waitForBytesWritten(1000)
        sys.exit(0)
        
    # Jika belum ada, buat server penampung file baru
    server = QLocalServer()
    QLocalServer.removeServer(SERVER_NAME)
    server.listen(SERVER_NAME)
    
    player = PCPlayer()
    
    def handle_new_connection():
        while server.hasPendingConnections():
            client_socket = server.nextPendingConnection()
            if client_socket.waitForReadyRead(200):
                data = client_socket.readAll().data().decode('utf-8')
                if data:
                    paths = data.split("|")
                    first_new_idx = len(player.playlist_files)
                    added = False
                    for path in paths:
                        if os.path.isdir(path):
                            player.add_folder_to_playlist(path)
                            added = True
                        elif os.path.exists(path):
                            player.add_file_to_playlist(path)
                            added = True
                            
                    if added:
                        now = time.time()
                        if now - player.last_batch_time > 0.5:
                            player.play_track(first_new_idx)
                        player.last_batch_time = now
                        player.showNormal()
                        player.activateWindow()
                        player.raise_()
            client_socket.disconnectFromServer()
            
    server.newConnection.connect(handle_new_connection)
    
    player.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
