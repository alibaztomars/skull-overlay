# Skull Overlay - Ekran Efekti Uygulaması

Windows için tuş kombinasyonuyla ekrana siyah-beyaz filtre ve skull görseli ekleyen uygulama.

## Özellikler

- Belirlenen tuş kombinasyonuna basınca ekran siyah-beyaz olur
- `skulls` klasöründen rastgele bir görsel ekranın altına eklenir
- `musics` klasöründen rastgele bir müzik 1-2 saniye çalar
- Sistem tepsisinden ayarlar yapılabilir

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. `skulls` klasörüne PNG/JPG formatında skull görselleri ekleyin
3. `musics` klasörüne MP3/WAV/OGG formatında müzik dosyaları ekleyin

## Kullanım

Uygulamayı başlatın:
```bash
python skull_overlay.py
```

Varsayılan tuş kombinasyonu: `Ctrl+Shift+S`

## Ayarlar

Sistem tepsisindeki ikona sağ tıklayarak:
- Hotkey değiştirme
- Müzik çalma süresi
- Görsel gösterim süresi
- **Sadece Patlama Kısmı** modu (açık/kapalı)
- **Patlamadan Önce Başlat** modu (açık/kapalı)
- Önden başlama süresi (varsayılan 5 saniye)
- Çıkış

## Müzik Segmentleri

`music_config.json` dosyasında şarkıların hangi saniyelerden çalacağını ayarlayabilirsiniz:

```json
{
  "songs": [
    {
      "file": "song1.mp3",
      "segments": [
        {"start": 31, "name": "intro"},
        {"start": 143, "name": "drop", "is_drop": true}
      ]
    }
  ]
}
```

- `start`: Şarkının kaçıncı saniyeden başlayacağı (patlama anı)
- `is_drop`: true ise bu segment "patlama kısmı" olarak işaretlenir
- **Sadece Patlama Kısmı** modu açıksa, sadece `is_drop: true` olan segmentler çalınır
- Mod kapalıysa, tüm segmentlerden rastgele biri seçilir

### Patlamadan Önce Başlat Modu

Bu mod açıkken:
- Müzik, patlama kısmından 5 saniye (ayarlanabilir) önce başlar
- Skull edit tam patlama anında ekrana gelir
- Örnek: Drop 2:23'te (143s) ise, müzik 2:18'den (138s) başlar ve 5 saniye sonra skull çıkar
- Eğer drop 5 saniyeden önce başlıyorsa, müzik 0. saniyeden başlar

## Not

Müzik ve skull imageleri kendiniz images ve skulls dosyaları altına koymalısınız

Uygulama yönetici yetkisi gerektirebilir (keyboard kütüphanesi için).
