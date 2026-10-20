import codecs

with codecs.open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = '''    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        
        # Sub-menu Pemutaran
        playback_menu = context_menu.addMenu("Menu Pemutaran")
        sleep_action = playback_menu.addAction("Pengatur Waktu Tidur (Ctrl+T)")
        playback_menu.addSeparator()
        play_pause_action = playback_menu.addAction("Mainkan / Jeda (Spasi)")
        prev_action = playback_menu.addAction("Lagu Sebelumnya (A)")
        next_action = playback_menu.addAction("Lagu Berikutnya (G)")
        playback_menu.addSeparator()
        slow_action = playback_menu.addAction("Putar Lambat (S)")
        normal_action = playback_menu.addAction("Putar Normal (D)")
        fast_action = playback_menu.addAction("Putar Cepat (F)")
        playback_menu.addSeparator()
        repeat_action = playback_menu.addAction("Ulangi / Repeat (R)")
        shuffle_action = playback_menu.addAction("Acak / Shuffle (C)")
        
        context_menu.addSeparator()
        
        # Fitur Streaming
        search_action = context_menu.addAction("Cari Lagu (Ctrl + F)")
        url_action = context_menu.addAction("Putar dari Link (Ctrl + L)")
        download_action = context_menu.addAction("Download Lagu Ini (Ctrl + D)")
        context_menu.addSeparator()
        
        # Fitur Putar
        loop_a_action = context_menu.addAction("Set Titik A Loop ([)")
        loop_b_action = context_menu.addAction("Set Titik B Loop (])")
        loop_clear_action = context_menu.addAction("Hapus Loop (\\)")
        context_menu.addSeparator()
        
        info_action = context_menu.addAction("Info Audio (I)")
        
        # Sub-menu Tampilan
        appearance_menu = context_menu.addMenu("Menu Tampilan")
        if self.is_dark_theme:
            theme_action = appearance_menu.addAction("Ubah ke Tema Terang (Light Mode)")
        else:
            theme_action = appearance_menu.addAction("Ubah ke Tema Gelap (Dark Mode)")
            
        accent_action = appearance_menu.addAction("Ubah Warna Aksen (Custom Tema)")
        
        wp_menu = appearance_menu.addMenu("Galeri Latar (Internal)")
        wp1_action = wp_menu.addAction("1. Gelap Abstrak")
        wp2_action = wp_menu.addAction("2. Terang Elegan")
        wp3_action = wp_menu.addAction("3. Neon Musik")
        
        wp1_action.setCheckable(True)
        wp2_action.setCheckable(True)
        wp3_action.setCheckable(True)
        
        if self.wallpaper_path:
            if "1_dark_gradient.jpg" in self.wallpaper_path: wp1_action.setChecked(True)
            elif "2_light_gradient.jpg" in self.wallpaper_path: wp2_action.setChecked(True)
            elif "3_neon_vibes.jpg" in self.wallpaper_path: wp3_action.setChecked(True)
        
        wp_custom_action = appearance_menu.addAction("Impor Latar Pribadi (Dari PC)")
        wp_clear_action = appearance_menu.addAction("Hapus Latar Belakang")
        
        # Opsi Layar Penuh Dinamis
        if self.isFullScreen():
            fullscreen_action = context_menu.addAction("Video mode layar normal (F11)")
        else:
            fullscreen_action = context_menu.addAction("Video mode layar penuh (F11)")
            
        register_action = context_menu.addAction("Jadikan Pemutar Utama (Daftarkan ke Windows)")'''

replacement = '''    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        
        # 1. Sub-menu Pemutaran
        playback_menu = context_menu.addMenu("Menu Pemutaran")
        sleep_action = playback_menu.addAction("Pengatur Waktu Tidur (Ctrl+T)")
        playback_menu.addSeparator()
        play_pause_action = playback_menu.addAction("Mainkan / Jeda (Spasi)")
        prev_action = playback_menu.addAction("Lagu Sebelumnya (A)")
        next_action = playback_menu.addAction("Lagu Berikutnya (G)")
        playback_menu.addSeparator()
        slow_action = playback_menu.addAction("Putar Lambat (S)")
        normal_action = playback_menu.addAction("Putar Normal (D)")
        fast_action = playback_menu.addAction("Putar Cepat (F)")
        playback_menu.addSeparator()
        repeat_action = playback_menu.addAction("Ulangi / Repeat (R)")
        shuffle_action = playback_menu.addAction("Acak / Shuffle (C)")
        
        # 2. Sub-menu Looping A-B
        loop_menu = context_menu.addMenu("Menu Looping A-B")
        loop_a_action = loop_menu.addAction("Set Titik A Loop ([)")
        loop_b_action = loop_menu.addAction("Set Titik B Loop (])")
        loop_clear_action = loop_menu.addAction("Hapus Loop (\\)")
        
        # 3. Sub-menu Online & Download
        online_menu = context_menu.addMenu("Menu Online & Download")
        search_action = online_menu.addAction("Cari Lagu (Ctrl + F)")
        url_action = online_menu.addAction("Putar dari Link (Ctrl + L)")
        download_action = online_menu.addAction("Download Lagu Ini (Ctrl + D)")
        
        # 4. Sub-menu Tampilan & Video
        appearance_menu = context_menu.addMenu("Menu Tampilan & Video")
        if self.isFullScreen():
            fullscreen_action = appearance_menu.addAction("Video mode layar normal (F11)")
        else:
            fullscreen_action = appearance_menu.addAction("Video mode layar penuh (F11)")
        appearance_menu.addSeparator()
        if self.is_dark_theme:
            theme_action = appearance_menu.addAction("Ubah ke Tema Terang (Light Mode)")
        else:
            theme_action = appearance_menu.addAction("Ubah ke Tema Gelap (Dark Mode)")
            
        accent_action = appearance_menu.addAction("Ubah Warna Aksen (Custom Tema)")
        
        wp_menu = appearance_menu.addMenu("Galeri Latar (Internal)")
        wp1_action = wp_menu.addAction("1. Gelap Abstrak")
        wp2_action = wp_menu.addAction("2. Terang Elegan")
        wp3_action = wp_menu.addAction("3. Neon Musik")
        
        wp1_action.setCheckable(True)
        wp2_action.setCheckable(True)
        wp3_action.setCheckable(True)
        
        if self.wallpaper_path:
            if "1_dark_gradient.jpg" in self.wallpaper_path: wp1_action.setChecked(True)
            elif "2_light_gradient.jpg" in self.wallpaper_path: wp2_action.setChecked(True)
            elif "3_neon_vibes.jpg" in self.wallpaper_path: wp3_action.setChecked(True)
        
        wp_custom_action = appearance_menu.addAction("Impor Latar Pribadi (Dari PC)")
        wp_clear_action = appearance_menu.addAction("Hapus Latar Belakang")
        
        # 5. Sub-menu Info & Sistem
        sys_menu = context_menu.addMenu("Menu Info & Sistem")
        info_action = sys_menu.addAction("Info Audio (I)")
        register_action = sys_menu.addAction("Jadikan Pemutar Utama (Daftarkan ke Windows)")'''

c = c.replace(target, replacement)

with codecs.open('main.py', 'w', encoding='utf-8') as f:
    f.write(c)
