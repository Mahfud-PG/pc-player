"""
BASS Player Engine with Real-Time Pitch Shifting (Transpose) for PC Player
Supports -12 to +12 semitones real-time pitch shifting using BASS_FX without changing tempo.
"""

import os
import sys
import ctypes
import threading
import time

# BASS Constants
BASS_UNICODE = 0x80000000
BASS_STREAM_DECODE = 0x200000
BASS_FX_FREESOURCE = 0x10000
BASS_POS_BYTE = 0
BASS_ACTIVE_STOPPED = 0
BASS_ACTIVE_PLAYING = 1
BASS_ACTIVE_STALLED = 2
BASS_ACTIVE_PAUSED = 3

BASS_ATTRIB_VOL = 2
BASS_ATTRIB_TEMPO = 0x10000
BASS_ATTRIB_TEMPO_PITCH = 0x10001
BASS_ATTRIB_TEMPO_FREQ = 0x10002

class BassEngine:
    _instance = None

    def __init__(self):
        self.initialized = False
        self.channel = 0
        self.current_file = ""
        self.current_pitch = 0.0 # Semitones (-12 to +12)
        self.current_volume = 1.0 # 0.0 to 1.0
        self.current_playback_rate = 1.0 # 1.0 = normal
        self._lock = threading.RLock()
        
        self._init_dlls()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = BassEngine()
        return cls._instance

    def _init_dlls(self):
        if getattr(sys, "frozen", False):
            base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        bass_dir = os.path.join(base_dir, "bass")
        bass_dll_path = os.path.join(bass_dir, "bass.dll")
        bass_fx_path = os.path.join(bass_dir, "bass_fx.dll")

        if not os.path.exists(bass_dll_path) or not os.path.exists(bass_fx_path):
            print("BASS DLLs not found at:", bass_dir)
            return

        try:
            self.bass = ctypes.WinDLL(bass_dll_path)
            self.bass_fx = ctypes.WinDLL(bass_fx_path)

            # Prototypes
            self.bass.BASS_Init.restype = ctypes.c_int
            self.bass.BASS_Init.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_void_p]

            self.bass.BASS_StreamCreateFile.restype = ctypes.c_ulong
            self.bass.BASS_StreamCreateFile.argtypes = [ctypes.c_int, ctypes.c_wchar_p, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_ulong]

            self.bass.BASS_StreamCreateURL.restype = ctypes.c_ulong
            self.bass.BASS_StreamCreateURL.argtypes = [ctypes.c_char_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_void_p]

            self.bass_fx.BASS_FX_TempoCreate.restype = ctypes.c_ulong
            self.bass_fx.BASS_FX_TempoCreate.argtypes = [ctypes.c_ulong, ctypes.c_ulong]

            self.bass.BASS_ChannelPlay.restype = ctypes.c_int
            self.bass.BASS_ChannelPlay.argtypes = [ctypes.c_ulong, ctypes.c_int]

            self.bass.BASS_ChannelPause.restype = ctypes.c_int
            self.bass.BASS_ChannelPause.argtypes = [ctypes.c_ulong]

            self.bass.BASS_ChannelStop.restype = ctypes.c_int
            self.bass.BASS_ChannelStop.argtypes = [ctypes.c_ulong]

            self.bass.BASS_ChannelIsActive.restype = ctypes.c_ulong
            self.bass.BASS_ChannelIsActive.argtypes = [ctypes.c_ulong]

            self.bass.BASS_ChannelSetAttribute.restype = ctypes.c_int
            self.bass.BASS_ChannelSetAttribute.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_float]

            self.bass.BASS_ChannelGetAttribute.restype = ctypes.c_int
            self.bass.BASS_ChannelGetAttribute.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.c_float)]

            self.bass.BASS_ChannelGetLength.restype = ctypes.c_int64
            self.bass.BASS_ChannelGetLength.argtypes = [ctypes.c_ulong, ctypes.c_ulong]

            self.bass.BASS_ChannelGetPosition.restype = ctypes.c_int64
            self.bass.BASS_ChannelGetPosition.argtypes = [ctypes.c_ulong, ctypes.c_ulong]

            self.bass.BASS_ChannelSetPosition.restype = ctypes.c_int
            self.bass.BASS_ChannelSetPosition.argtypes = [ctypes.c_ulong, ctypes.c_int64, ctypes.c_ulong]

            self.bass.BASS_ChannelBytes2Seconds.restype = ctypes.c_double
            self.bass.BASS_ChannelBytes2Seconds.argtypes = [ctypes.c_ulong, ctypes.c_int64]

            self.bass.BASS_ChannelSeconds2Bytes.restype = ctypes.c_int64
            self.bass.BASS_ChannelSeconds2Bytes.argtypes = [ctypes.c_ulong, ctypes.c_double]

            self.bass.BASS_StreamFree.restype = ctypes.c_int
            self.bass.BASS_StreamFree.argtypes = [ctypes.c_ulong]

            self.bass.BASS_Free.restype = ctypes.c_int

            # Initialize BASS device
            init_res = self.bass.BASS_Init(-1, 44100, 0, 0, 0)
            if init_res or self.bass.BASS_ErrorGetCode() == 14: # 14 = ALREADY initialized
                self.initialized = True
                self._load_plugins(bass_dir)
        except Exception as e:
            print("Failed to initialize BASS:", e)

    def _load_plugins(self, bass_dir):
        plugins = ['bassflac.dll', 'bassopus.dll', 'bass_aac.dll', 'basswma.dll', 'basshls.dll']
        for p in plugins:
            p_path = os.path.join(bass_dir, p)
            if os.path.exists(p_path):
                try:
                    self.bass.BASS_PluginLoad(ctypes.c_wchar_p(p_path), BASS_UNICODE)
                except Exception:
                    pass

    def load_file(self, filepath):
        with self._lock:
            self.stop()
            if not self.initialized:
                return False

            flags = BASS_STREAM_DECODE | BASS_UNICODE
            src_stream = self.bass.BASS_StreamCreateFile(0, ctypes.c_wchar_p(filepath), 0, 0, flags)
            if not src_stream:
                err = self.bass.BASS_ErrorGetCode()
                print(f"BASS_StreamCreateFile error: {err} for {filepath}")
                return False

            # Wrap in tempo stream for pitch and tempo control
            tempo_stream = self.bass_fx.BASS_FX_TempoCreate(src_stream, BASS_FX_FREESOURCE)
            if not tempo_stream:
                self.bass.BASS_StreamFree(src_stream)
                return False

            self.channel = tempo_stream
            self.current_file = filepath

            # Re-apply current attributes
            self.set_pitch(self.current_pitch)
            self.set_volume(self.current_volume)
            self.set_playback_rate(self.current_playback_rate)
            return True

    def play(self):
        with self._lock:
            if self.channel:
                return bool(self.bass.BASS_ChannelPlay(self.channel, 0))
            return False

    def pause(self):
        with self._lock:
            if self.channel:
                return bool(self.bass.BASS_ChannelPause(self.channel))
            return False

    def stop(self):
        with self._lock:
            if self.channel:
                self.bass.BASS_ChannelStop(self.channel)
                self.bass.BASS_StreamFree(self.channel)
                self.channel = 0

    def is_playing(self):
        if self.channel:
            return self.bass.BASS_ChannelIsActive(self.channel) == BASS_ACTIVE_PLAYING
        return False

    def is_paused(self):
        if self.channel:
            return self.bass.BASS_ChannelIsActive(self.channel) == BASS_ACTIVE_PAUSED
        return False

    def is_stopped(self):
        if self.channel:
            return self.bass.BASS_ChannelIsActive(self.channel) == BASS_ACTIVE_STOPPED
        return True

    def set_pitch(self, semitones):
        """Semitones from -12.0 to +12.0"""
        with self._lock:
            self.current_pitch = max(-12.0, min(12.0, float(semitones)))
            if self.channel:
                return bool(self.bass.BASS_ChannelSetAttribute(
                    self.channel,
                    BASS_ATTRIB_TEMPO_PITCH,
                    ctypes.c_float(self.current_pitch)
                ))
            return True

    def get_pitch(self):
        return self.current_pitch

    def set_volume(self, volume):
        """Volume 0.0 to 1.0"""
        with self._lock:
            self.current_volume = max(0.0, min(1.0, float(volume)))
            if self.channel:
                return bool(self.bass.BASS_ChannelSetAttribute(
                    self.channel,
                    BASS_ATTRIB_VOL,
                    ctypes.c_float(self.current_volume)
                ))
            return True

    def set_playback_rate(self, rate):
        """Rate 0.5 to 2.0 (1.0 = normal). In BASS_FX tempo attribute is percentage change (-50% to +100%)"""
        with self._lock:
            self.current_playback_rate = rate
            tempo_pct = (rate - 1.0) * 100.0
            if self.channel:
                return bool(self.bass.BASS_ChannelSetAttribute(
                    self.channel,
                    BASS_ATTRIB_TEMPO,
                    ctypes.c_float(tempo_pct)
                ))
            return True

    def get_duration_ms(self):
        if self.channel:
            length_bytes = self.bass.BASS_ChannelGetLength(self.channel, BASS_POS_BYTE)
            if length_bytes > 0:
                seconds = self.bass.BASS_ChannelBytes2Seconds(self.channel, length_bytes)
                return int(seconds * 1000)
        return 0

    def get_position_ms(self):
        if self.channel:
            pos_bytes = self.bass.BASS_ChannelGetPosition(self.channel, BASS_POS_BYTE)
            if pos_bytes >= 0:
                seconds = self.bass.BASS_ChannelBytes2Seconds(self.channel, pos_bytes)
                return int(seconds * 1000)
        return 0

    def set_position_ms(self, ms):
        with self._lock:
            if self.channel:
                seconds = ms / 1000.0
                pos_bytes = self.bass.BASS_ChannelSeconds2Bytes(self.channel, ctypes.c_double(seconds))
                if pos_bytes >= 0:
                    return bool(self.bass.BASS_ChannelSetPosition(self.channel, pos_bytes, BASS_POS_BYTE))
        return False
