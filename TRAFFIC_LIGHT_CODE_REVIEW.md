# Trafik Işığı Simülasyonu Kod İncelemesi

Bu doküman, paylaştığınız Python tabanlı gerçek zamanlı trafik ışığı simülasyonu kodu için **önceliklendirilmiş iyileştirme önerileri** içerir.

## 1) Kritik mantıksal iyileştirmeler

- **Sabit eşik yerine kuyruk/akış metrikleri kullanın.**
  Şu anda süre hesaplaması büyük ölçüde anlık/SMOOTH edilmiş yüke göre. Buna;
  - son N saniyede gelen araç oranı,
  - her yol için ortalama bekleme süresi,
  - üst üste kırmızıda kalma süresi (fairness)
  eklenmeli.

- **Açlık (starvation) engeli ekleyin.**
  Bir yolun yükü düşük diye uzun süre kırmızıda kalması gerçek sahada sorun yaratır. “Maksimum kırmızı süresi” kuralı koyun.

- **All-red / yellow süreleri adaptif olabilir.**
  Kavşak genişliği veya yaya geçidi senaryosuna göre bu süreleri parametreleştirmek güvenliği artırır.

## 2) Algılama ve takip kararlılığı

- **Aynı aracı çift saymayı azaltın.**
  `TrackLoadMemory` TTL yaklaşımı iyi; buna ek olarak:
  - ROI sınırı yakınında histerezis,
  - lane değişimi için minimum süre kuralı,
  - “ID kayboldu/geri geldi” durumda IoU tabanlı yeniden bağlama
  eklenebilir.

- **ROI atama için perspektif farkını telafi edin.**
  Alt merkez örneklemesi faydalı, ancak eğik kamera açılarında homografi/perspective transform ile zemin düzleminde karar daha stabil olur.

- **Model hatalarında degrade modu daha görünür olsun.**
  Takipten detect-only moda geçiş var; bunu UI’da kalıcı bir durum etiketiyle belirtin.

## 3) Performans optimizasyonu

- **Inference thread’i ayırın.**
  Ana döngüde detection yapmak FPS dalgalanması üretir. Ayrı iş parçacığı + en son sonuç cache modeli daha akıcı UI verir.

- **Dinamik `detect_every` kullanın.**
  FPS düştüğünde otomatik artır, yükseldiğinde düşür (hedef FPS kontrolü).

- **Kopya frame sayısını azaltın.**
  `copy()` işlemleri yoğun; sadece gerektiği yerde kopyalayın.

## 4) Mimari ve bakım kolaylığı

- **Tek dosyayı modüllere bölün.**
  Öneri:
  - `camera.py`
  - `detector.py`
  - `controller.py`
  - `overlay.py`
  - `config.py`
  - `main.py`

- **Argparse yerine yapılandırma dosyası (YAML/TOML).**
  Saha kullanımında ROI, model, cihaz, zamanlar profile bazlı yönetilir.

- **Daha güçlü loglama.**
  `print` yerine `logging` + seviyeler + opsiyonel JSON log formatı.

## 5) Test edilebilirlik

- **Deterministik birim testleri ekleyin.**
  Özellikle:
  - `AdaptiveSignalController._calc_green_duration`
  - `sanitize_and_validate_rois`
  - `_assign_road`
  - `resolve_device`

- **Replay testleri (video dosyasıyla).**
  Kamera bağımlı test kırılgan; sabit kısa videolarla regresyon testi daha sağlıklı.

## 6) Güvenlik ve operasyonel dayanıklılık

- **Fail-safe varsayılanı tanımlayın.**
  Algılama tamamen çökerse kontrolcü hangi güvenli faza dönecek? (örn. sabit döngü + kısa süreler)

- **Kaynak izleme ekleyin.**
  CPU/GPU sıcaklık ve kullanım bilgisi operasyonda kritik olabilir.

- **Runtime sağlık metrikleri yayınlayın.**
  Basit bir HTTP `/health` veya terminal heartbeat ile sistemin canlılığı takip edilebilir.

## 7) UI/UX iyileştirmeleri

- **Konfigürasyon ve durum bilgisi katmanlarını ayırın.**
  Ekran kalabalığını azaltmak için “debug panel” ayrı toggle olabilir.

- **Renk körlüğü dostu palet + ikonlar.**
  Sadece renge bağlı sinyal yerine sembol/etiket ekleyin.

- **Overlay ölçekleme.**
  Farklı çözünürlüklerde sabit piksel yerine oransal konumlandırma kullanın.

## 8) Hızlı kazanımlar (ilk uygulanacak 5 madde)

1. Max-red (starvation guard) ekle.
2. Detect thread + sonuç buffer yap.
3. Logging altyapısına geç.
4. Controller ve ROI fonksiyonlarına unit test yaz.
5. Detect-only fallback durumunu UI’da net göster.

## Özet

Kod tabanı güçlü bir başlangıç: kamera fallback, ROI doğrulama, tracking fallback, i18n ve adaptif sinyal mantığı gibi doğru temeller var. En büyük değer artışı; **adalet/fairness kuralları**, **asenkron inference mimarisi** ve **test kapsamı** ile gelir.
