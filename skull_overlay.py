import os
import random
import threading
import time
import json
from pathlib import Path
from PIL import Image, ImageGrab, ImageEnhance
import pygame
import keyboard
from pystray import Icon, Menu, MenuItem
from PIL import Image as PILImage
import tkinter as tk
from tkinter import simpledialog, messagebox

class SkullOverlay:
    def __init__(self):
        self.running = True
        self.config_file = Path("config.json")
        self.music_config_file = Path("music_config.json")
        
        # Varsayılan ayarlar
        self.hotkey = "ctrl+shift+s"
        self.music_duration = 1.5  # saniye
        self.skull_display_time = 2.0  # saniye
        self.skulls_folder = Path("skulls")
        self.musics_folder = Path("musics")
        self.drop_only_mode = False  # Sadece patlama kısmı modu
        self.pre_drop_mode = False  # Patlamadan önce başlat modu
        self.pre_drop_seconds = 5.0  # Patlamadan kaç saniye önce başlayacak
        self.music_segments = {}  # Şarkı segmentleri
    
        # Ayarları yükle
        self.load_config()
        self.load_music_config()
        
        # Pygame ses için
        pygame.mixer.init()
        
        # Sistem tepsisi ikonu
        self.setup_tray_icon()
        
    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.hotkey = config.get('hotkey', self.hotkey)
                    self.music_duration = config.get('music_duration', self.music_duration)
                    self.skull_display_time = config.get('skull_display_time', self.skull_display_time)
                    self.drop_only_mode = config.get('drop_only_mode', self.drop_only_mode)
                    self.pre_drop_mode = config.get('pre_drop_mode', self.pre_drop_mode)
                    self.pre_drop_seconds = config.get('pre_drop_seconds', self.pre_drop_seconds)
            except Exception as e:
                print(f"Config yükleme hatası: {e}")
    
    def save_config(self):
        config = {
            'hotkey': self.hotkey,
            'music_duration': self.music_duration,
            'skull_display_time': self.skull_display_time,
            'drop_only_mode': self.drop_only_mode,
            'pre_drop_mode': self.pre_drop_mode,
            'pre_drop_seconds': self.pre_drop_seconds
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Config kaydetme hatası: {e}")
    
    def load_music_config(self):
        if self.music_config_file.exists():
            try:
                with open(self.music_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for song in data.get('songs', []):
                        filename = song['file']
                        self.music_segments[filename] = song['segments']
            except Exception as e:
                print(f"Müzik config yükleme hatası: {e}")
    
    def setup_tray_icon(self):
        # Basit bir ikon oluştur (skull simgesi)
        icon_image = PILImage.new('RGB', (64, 64), color='black')
        
        self.icon = Icon("SkullOverlay", icon_image, "Skull Overlay", self.create_menu())
    
    def create_menu(self):
        drop_text = "✓ Sadece Patlama Kısmı" if self.drop_only_mode else "Sadece Patlama Kısmı"
        pre_drop_text = "✓ Patlamadan Önce Başlat" if self.pre_drop_mode else "Patlamadan Önce Başlat"
        return Menu(
            MenuItem(f'Hotkey: {self.hotkey}', self.change_hotkey),
            MenuItem(f'Müzik Süresi: {self.music_duration}s', self.change_music_duration),
            MenuItem(f'Görsel Süresi: {self.skull_display_time}s', self.change_display_time),
            Menu.SEPARATOR,
            MenuItem(drop_text, self.toggle_drop_mode),
            MenuItem(pre_drop_text, self.toggle_pre_drop_mode),
            MenuItem(f'Önden Başlama: {self.pre_drop_seconds}s', self.change_pre_drop_seconds),
            Menu.SEPARATOR,
            MenuItem('Çıkış', self.quit_app)
        )
    
    def update_menu(self):
        self.icon.menu = self.create_menu()
        
    def change_hotkey(self):
        def ask():
            root = tk.Tk()
            root.withdraw()
            new_hotkey = simpledialog.askstring(
                "Hotkey Değiştir",
                "Yeni hotkey girin (örn: ctrl+shift+s):",
                initialvalue=self.hotkey
            )
            if new_hotkey:
                try:
                    keyboard.remove_hotkey(self.hotkey)
                except:
                    pass
                self.hotkey = new_hotkey
                keyboard.add_hotkey(self.hotkey, self.on_hotkey)
                self.save_config()
                self.update_menu()
                messagebox.showinfo("Başarılı", f"Hotkey değiştirildi: {self.hotkey}")
            root.destroy()
        
        threading.Thread(target=ask, daemon=True).start()
        
    def change_music_duration(self):
        def ask():
            root = tk.Tk()
            root.withdraw()
            new_duration = simpledialog.askfloat(
                "Müzik Süresi",
                "Müzik çalma süresi (saniye):",
                initialvalue=self.music_duration,
                minvalue=0.1,
                maxvalue=10.0
            )
            if new_duration:
                self.music_duration = new_duration
                self.save_config()
                self.update_menu()
                messagebox.showinfo("Başarılı", f"Müzik süresi: {self.music_duration}s")
            root.destroy()
        
        threading.Thread(target=ask, daemon=True).start()
        
    def change_display_time(self):
        def ask():
            root = tk.Tk()
            root.withdraw()
            new_time = simpledialog.askfloat(
                "Görsel Süresi",
                "Görsel gösterim süresi (saniye):",
                initialvalue=self.skull_display_time,
                minvalue=0.5,
                maxvalue=10.0
            )
            if new_time:
                self.skull_display_time = new_time
                self.save_config()
                self.update_menu()
                messagebox.showinfo("Başarılı", f"Görsel süresi: {self.skull_display_time}s")
            root.destroy()
        
        threading.Thread(target=ask, daemon=True).start()
    
    def toggle_drop_mode(self):
        self.drop_only_mode = not self.drop_only_mode
        self.save_config()
        self.update_menu()
        mode_text = "AÇIK" if self.drop_only_mode else "KAPALI"
        print(f"Sadece patlama kısmı modu: {mode_text}")
    
    def toggle_pre_drop_mode(self):
        self.pre_drop_mode = not self.pre_drop_mode
        self.save_config()
        self.update_menu()
        mode_text = "AÇIK" if self.pre_drop_mode else "KAPALI"
        print(f"Patlamadan önce başlat modu: {mode_text}")
    
    def change_pre_drop_seconds(self):
        def ask():
            root = tk.Tk()
            root.withdraw()
            new_seconds = simpledialog.askfloat(
                "Önden Başlama Süresi",
                "Patlamadan kaç saniye önce başlasın:",
                initialvalue=self.pre_drop_seconds,
                minvalue=1.0,
                maxvalue=15.0
            )
            if new_seconds:
                self.pre_drop_seconds = new_seconds
                self.save_config()
                self.update_menu()
                messagebox.showinfo("Başarılı", f"Önden başlama: {self.pre_drop_seconds}s")
            root.destroy()
        
        threading.Thread(target=ask, daemon=True).start()
        
    def quit_app(self):
        self.running = False
        keyboard.unhook_all()
        self.icon.stop()
        
    def get_random_skull(self):
        skulls = list(self.skulls_folder.glob("*.png")) + \
                 list(self.skulls_folder.glob("*.jpg")) + \
                 list(self.skulls_folder.glob("*.jpeg"))
        if skulls:
            return random.choice(skulls)
        return None
        
    def get_random_music(self):
        musics = list(self.musics_folder.glob("*.mp3")) + \
                 list(self.musics_folder.glob("*.wav")) + \
                 list(self.musics_folder.glob("*.ogg"))
        if musics:
            return random.choice(musics)
        return None
    
    def get_music_segment(self, music_path):
        """Şarkı için rastgele bir segment seç veya drop segment'i döndür"""
        filename = music_path.name
        
        if filename in self.music_segments:
            segments = self.music_segments[filename]
            
            if self.drop_only_mode:
                # Sadece drop segmentlerini filtrele
                drop_segments = [s for s in segments if s.get('is_drop', False)]
                if drop_segments:
                    selected_segment = random.choice(drop_segments)
                    return selected_segment
            else:
                # Rastgele bir segment seç
                selected_segment = random.choice(segments)
                return selected_segment
        
        return {'start': 0, 'is_drop': False}  # Config yoksa baştan başla

    def apply_grayscale_filter(self):
        # Ekran görüntüsü al
        screenshot = ImageGrab.grab()
        
        # Siyah-beyaz yap
        grayscale = screenshot.convert('L').convert('RGB')
        
        # Skull resmini ekle
        skull_path = self.get_random_skull()
        if skull_path:
            skull = Image.open(skull_path)
            
            # Skull'u ekranın altına yerleştir için boyutlandır
            screen_width, screen_height = grayscale.size
            skull_height = int(screen_height * 0.3)  # Ekranın %30'u kadar
            aspect_ratio = skull.width / skull.height
            skull_width = int(skull_height * aspect_ratio)
            
            skull = skull.resize((skull_width, skull_height), Image.Resampling.LANCZOS)
            
            # Ekranın altına ortala
            x_pos = (screen_width - skull_width) // 2
            y_pos = screen_height - skull_height - 50
            
            grayscale.paste(skull, (x_pos, y_pos), skull if skull.mode == 'RGBA' else None)
        
        return grayscale
        
    def show_overlay(self):
        # Müzik çal
        music_path = self.get_random_music()
        delay_before_visual = 0  # Görsel gösteriminden önce beklenecek süre
        
        if music_path:
            try:
                # Segment bilgisini al
                segment = self.get_music_segment(music_path)
                drop_time = segment['start']
                is_drop = segment.get('is_drop', False)
                
                # Başlangıç zamanını hesapla
                if self.pre_drop_mode and is_drop:
                    # Patlamadan önce başlat modu aktifse
                    start_time = max(0, drop_time - self.pre_drop_seconds)
                    delay_before_visual = drop_time - start_time  # Drop anına kadar bekle
                    print(f"Pre-drop modu: {start_time}s'den başlayıp {delay_before_visual}s sonra drop!")
                else:
                    start_time = drop_time
                    delay_before_visual = 0
                
                pygame.mixer.music.load(str(music_path))
                pygame.mixer.music.play(start=start_time)
                
                # Belirtilen süre sonra durdur
                total_music_time = delay_before_visual + self.music_duration
                threading.Timer(total_music_time, pygame.mixer.music.stop).start()
                
                print(f"Çalınan: {music_path.name} - Başlangıç: {start_time}s - Drop: {drop_time}s")
            except Exception as e:
                print(f"Müzik çalma hatası: {e}")
        
        # Eğer pre-drop modundaysa, drop anına kadar bekle
        if delay_before_visual > 0:
            time.sleep(delay_before_visual)
        
        # Filtrelenmiş görüntü oluştur
        overlay_image = self.apply_grayscale_filter()
        
        # Geçici dosyaya kaydet
        temp_path = Path("temp_overlay.png")
        overlay_image.save(temp_path)
        
        # Tam ekran pencere oluştur
        self.show_fullscreen_image(temp_path)
        
        # Temizlik
        time.sleep(self.skull_display_time)
        if temp_path.exists():
            temp_path.unlink()
            
    def show_fullscreen_image(self, image_path):
        # Tkinter ile tam ekran göster
        from PIL import ImageTk
        
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.attributes('-topmost', True)
        root.configure(background='black')
        
        img = Image.open(image_path)
        photo = ImageTk.PhotoImage(img)
        
        label = tk.Label(root, image=photo, bg='black')
        label.pack()
        
        # Belirtilen süre sonra kapat
        root.after(int(self.skull_display_time * 1000), root.destroy)
        
        root.mainloop()
        
    def on_hotkey(self):
        print("Hotkey basıldı! Overlay gösteriliyor...")
        threading.Thread(target=self.show_overlay, daemon=True).start()
        
    def run(self):
        # Hotkey'i kaydet
        keyboard.add_hotkey(self.hotkey, self.on_hotkey)
        
        print(f"Skull Overlay başlatıldı!")
        print(f"Hotkey: {self.hotkey}")
        print(f"Müzik klasörü: {self.musics_folder}")
        print(f"Skull klasörü: {self.skulls_folder}")
        
        # Sistem tepsisi ikonunu başlat
        self.icon.run()

if __name__ == "__main__":
    app = SkullOverlay()
    app.run()
