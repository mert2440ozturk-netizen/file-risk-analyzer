from pathlib import Path
import hashlib

def check_file_name(file_name):
    suffixes = Path(file_name).suffixes

    #Listedeki her uzantıyı küçük harfe çevirerek yeni liste oluşturur.
    suffixes = [suffix.lower() for suffix in suffixes]

    executable_extension = {".exe",".com",".bat",".cmd",".scr"}
    document_extension = {".pdf",".doc",".docx",".xls",".xlsx",".txt",".jpg",".jpeg",".png"}

    findings = []

    if len(suffixes) >= 2:
        last_extension = suffixes[-1]
        previous_extension = suffixes[-2]

        if (
            last_extension in executable_extension
            and previous_extension in document_extension
        ):
            findings.append({
                "code": "misleading_double_extension",
                "severity": "medium",
                "message": (
                    "Misleading double extension: A file named like a document or image, "
                    "but with an executable file type as its final extension. "
                )
            })

    return findings

def detect_file_type(file_path):
    path =Path(file_path)

    #Dosyayı yalnızca okumak için, ikili veri modunda açar.
    #İş bitince, hata çıksa bile dosyanın kapatılmasını sağlar.
    with path.open("rb") as file:
        header = file.read(16)

    if not header:
        return "empty"

    #startswith: Okunan verinin belirtilen baytlarla başlayıp başlamadığını kontrol eder.
    if header.startswith(b"%PDF-"):
        return "pdf"

    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"

    if header.startswith((b"PK\x03\x04", b"PK\x05\x06")):
        return "zip_container"

    return "unknown"

def check_extension_match(extension, detected_type):
    expected_extensions = {
        "png": {".png", ".apng"},
        "pdf": {".pdf"}
    }

    findings = []

    if detected_type not in expected_extensions:
        return findings

    allowed_extensions = expected_extensions[detected_type]

    if extension.lower() not in allowed_extensions:
        findings.append({
            "code": "extension_mismatch",
            "severity": "low",
            "message": (
                f"Extension-content mismatch: Extension "
                f"'{extension or '(no)'}', but the initial signature "
                f"'{detected_type}' It indicates the type. "
            )
        })

    return findings

def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with Path(file_path).open("rb") as file:
        while True:
            # Dosyayı her seferinde en fazla 1 MiB okuyarak belleği sınırlı kullanır.
            chunk = file.read(1024 * 1024)

            # Okunacak veri kalmadığında döngüden çıkar.
            if not chunk:
                break

            #Okunan parçayı özet hesabına ekler.
            sha256.update(chunk)

    #Hesaplanan özeti onaltılık metin olarak döndürür.
    return sha256.hexdigest()

def analyze_file(file_analyzer):
    path = Path(file_analyzer)

    if not path.is_file():
        raise ValueError("The selected path is not an existing file.")

    file_size =path.stat().st_size
    extension = path.suffix.lower()
    detected_type = detect_file_type(path)
    file_hash = calculate_sha256(path)

    findings = check_file_name(path.name)
    findings.extend(check_extension_match(extension, detected_type))

    return {
        "name": path.name,
        "extension": extension,
        "size_bytes": file_size,
        "detected_type": detected_type,
        "sha256": file_hash,
        "findings": findings,
    }

if __name__ == "__main__":
    entered_path = input("Select the full path of the file to be examined: ")

    #strip() dıştaki boşlukları, strip('"') ise kopyalanmış yolun etrafındaki çift tırnakları temizler.
    entered_path = entered_path.strip().strip('"')

    try:
        result = analyze_file(entered_path)

        for key, value in result.items():
            if key != "findings":
                print(f"{key}: {value}")

        print("Findings: ")

        if not result["findings"]:
            print("No findings found")
        else:
            for findings in result["findings"]:
                print(
                    f"- [{findings['severity']}] "
                    f"{findings['message']} "
                )

    except (OSError, ValueError) as error:
        print(f"analiz tamamlanamadı: {error}")

