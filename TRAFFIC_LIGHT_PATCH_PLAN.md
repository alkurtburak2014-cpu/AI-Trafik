# Trafik Işığı Simülasyonu İçin Somut Patch Planı ("Başka" / Uygulanabilir Sürüm)

Bu doküman, önceki genel incelemeyi **somut kod seviyesine** indirir.
Amaç: doğrudan uygulanabilecek küçük ama etkili değişiklikleri sıraya koymak.

## 1) Starvation (Açlık) engeli — doğrudan controller patch'i

### Neden
Düşük yoğunluklu yolun uzun süre kırmızıda beklemesi sahada kuyruk ve güvenlik sorunu üretir.

### Yapılacak değişiklik
`SignalConfig` içine:
- `max_red: float = 75.0`

`AdaptiveSignalController` içine:
- her yol için kırmızıda kalma sayaçları (`red_elapsed_a`, `red_elapsed_b`)
- `update()` içinde aktif faza göre sayaç artışı
- `ALL_RED -> GREEN` geçişinde: herhangi bir yol `max_red` sınırını geçtiyse zorunlu öncelik

### Beklenen etki
- Adil faz dağıtımı
- Düşük yoğunluklu yolun tamamen ihmal edilmemesi

## 2) Adaptif ama sınırlandırılmış green hesaplama

### Neden
Sadece oran bazlı yaklaşım bazı senaryolarda ani sıçrama yapabilir.

### Yapılacak değişiklik
`_calc_green_duration()` içinde:
- `delta_limit` (örn. önceki green'e göre +/-8 sn) uygulayın.
- “minimum service” tabanı bırakın (zaten `min_green` var).

Örnek parametre:
- `max_green_step: float = 8.0`

### Beklenen etki
- Faz süreleri daha stabil olur.
- Sürücü davranışı açısından daha öngörülebilir sistem.

## 3) Detection ve UI döngüsünü ayırın (Thread + son sonuç cache)

### Neden
Ağır inference ana döngüyü bloke ederek FPS düşürür.

### Yapılacak değişiklik
- `DetectorWorker` adında bir thread sınıfı.
- Ana döngü sadece son güvenli sonucu okur.
- Yeni frame geldiğinde worker meşgulse frame drop (backpressure).

### Beklenen etki
- Daha akıcı ekran güncellemesi
- Gecikmenin kontrollü kalması

## 4) ROI sınırında histerezis

### Neden
Araçlar sınırda A/B arasında “zıplama” yapabilir.

### Yapılacak değişiklik
- Track başına son yol bilgisini kısa süre tutun.
- Yeni karar farklıysa en az `switch_hold_sec` kadar doğrulanmadan değiştirmeyin.

Öneri:
- `switch_hold_sec = 0.8`

### Beklenen etki
- Sayım salınımı azalır
- Yol yükleri daha tutarlı olur

## 5) Detect-only fallback'i UI’da sabit rozetle gösterin

### Neden
Terminal uyarısı operatör ekranında her zaman görünmeyebilir.

### Yapılacak değişiklik
- `draw_overlay()` içinde sağ üstte küçük durum etiketi:
  - `TRACKING: ON`
  - `TRACKING: FALLBACK (DETECT-ONLY)`

### Beklenen etki
- Operatör arıza/performans durumunu anında görür.

## 6) print -> logging geçişi

### Neden
Saha kullanımında filtrelenebilir ve zaman damgalı log gerekir.

### Yapılacak değişiklik
- `logging.basicConfig(...)`
- `print` çağrılarını `logger.info/warning/error` ile değiştirin.

### Beklenen etki
- Hata ayıklama kolaylığı
- Üretim ortamına uygun gözlemlenebilirlik

## 7) İlk eklenecek testler (yüksek ROI)

### Birim test listesi
1. `_calc_green_duration` sınırlar içinde mi (`min_green <= x <= max_green`)
2. starvation guard tetiklenince doğru yol seçiliyor mu
3. `sanitize_and_validate_rois` küçük/örtüşen ROI’leri default’a döndürüyor mu
4. `_assign_road` eşit skor sınırında fallback doğru çalışıyor mu
5. `resolve_device` CUDA yokken CPU’ya düşüyor mu

## 8) Önerilen uygulama sırası (2 sprint)

### Sprint 1 (hemen)
- Starvation guard
- Tracking fallback badge
- Logging
- İlk 3 unit test

### Sprint 2
- DetectorWorker asenkron mimari
- ROI histerezis
- Kalan testler + kısa replay testi

## 9) Done kriteri

- Sistem en az 30 dakika çalışmada kilitlenmeden devam eder.
- FPS dalgalanması gözle görülür şekilde azalır.
- Düşük yoğunluklu yol `max_red` üstünde kalmaz.
- Tracking düşse bile sistem detect-only modda kontrollü çalışır.
