# pytest.mark gibi özellikleri kullanabilmek için pytest'i içe aktarır.
import pytest

# analyzer.py içindeki test edilecek fonksiyonları içe aktarır.
from analyzer import (
    analyze_file,
    calculate_risk_score,
    check_file_name,
    detect_file_type,
)


# ---------------------------------------------------------------
# check_file_name testleri
# ---------------------------------------------------------------

def test_double_extension_is_flagged():
    # Eylem: Belge gibi görünen ama son uzantısı .exe olan bir adı kontrol eder.
    findings = check_file_name("fatura.pdf.exe")

    # Kontrol: Tam olarak bir bulgu üretilmiş olmalı.
    assert len(findings) == 1

    # Kontrol: Mesaj metni yerine "code" alanına bakarız; mesaj değişse bile test bozulmaz.
    assert findings[0]["code"] == "misleading_double_extension"


def test_normal_pdf_name_has_no_findings():
    # Sıradan bir belge adı hiçbir bulgu üretmemeli (boş liste).
    assert check_file_name("rapor.pdf") == []


def test_uppercase_double_extension_is_flagged():
    # Uzantılar küçük harfe çevrildiği için büyük harfli ad da yakalanmalı.
    findings = check_file_name("FOTO.JPG.EXE")

    assert len(findings) == 1
    assert findings[0]["code"] == "misleading_double_extension"


def test_executable_before_document_is_not_flagged():
    # Ters sıra (önce .exe, sonra .pdf) yanıltıcı çift uzantı sayılmaz.
    # Bu test, kuralın sırayı gerçekten dikkate aldığını doğrular.
    assert check_file_name("setup.exe.pdf") == []


# ---------------------------------------------------------------
# detect_file_type testleri
# ---------------------------------------------------------------

def test_png_signature_is_detected(tmp_path):
    # Kurulum: Geçici klasörde bir dosya yolu oluşturur.
    sample = tmp_path / "ornek.png"

    # Kurulum: PNG imzasını ve ardından birkaç dolgu baytı yazar.
    sample.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)

    # Eylem + Kontrol: İçeriğe bakıldığında tip "png" olmalı.
    assert detect_file_type(sample) == "png"


def test_pdf_signature_is_detected(tmp_path):
    sample = tmp_path / "belge.pdf"

    # PDF dosyaları "%PDF-" ile başlar; arkasındaki sürüm numarası önemsizdir.
    sample.write_bytes(b"%PDF-1.7\n")

    assert detect_file_type(sample) == "pdf"


def test_empty_file_is_detected(tmp_path):
    sample = tmp_path / "bos.txt"

    # Hiç bayt yazmadan boş bir dosya oluşturur.
    sample.write_bytes(b"")

    assert detect_file_type(sample) == "empty"


# ---------------------------------------------------------------
# calculate_risk_score testleri
# ---------------------------------------------------------------

def test_risk_score_without_findings_is_one():
    # Bulgu yoksa başlangıç skoru olan 1 dönmeli.
    assert calculate_risk_score([]) == 1


def test_risk_score_uses_highest_severity():
    # Fonksiyon yalnızca "severity" anahtarını okuduğu için
    # sahte bulgularda başka alana gerek yoktur.
    findings = [
        {"severity": "low"},     # 2 puan
        {"severity": "medium"},  # 3 puan
    ]

    # Skorlar toplanmaz; en yüksek önem derecesinin puanı alınır.
    assert calculate_risk_score(findings) == 3


def test_unknown_severity_raises_error():
    # Yazım hatalı bir önem derecesi şu an KeyError'a yol açıyor.
    # pytest.raises, bloğun içinde bu hatanın oluşmasını bekler;
    # hata oluşmazsa test başarısız olur.
    with pytest.raises(KeyError):
        calculate_risk_score([{"severity": "meduim"}])


# ---------------------------------------------------------------
# Bilinen açık: .pdf gibi görünen çalıştırılabilir dosya
# ---------------------------------------------------------------

# xfail = "başarısız olması beklenen test".
# strict=True sayesinde açığı kapattığın gün test geçerse pytest seni uyarır;
# o zaman bu işareti silersin.
@pytest.mark.xfail(strict=True, reason="MZ imzası henüz tanınmıyor (Faz 1)")
def test_executable_disguised_as_pdf_is_flagged(tmp_path):
    sample = tmp_path / "fatura.pdf"

    # Windows programları "MZ" baytlarıyla başlar.
    sample.write_bytes(b"MZ" + b"\x00" * 62)

    # analyze_file tüm kontrolleri birlikte çalıştırır.
    result = analyze_file(sample)

    # En az bir bulgu üretilmiş olmalı.
    assert result["findings"]