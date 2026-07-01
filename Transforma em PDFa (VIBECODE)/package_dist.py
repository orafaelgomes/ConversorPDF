import zipfile
from pathlib import Path

base = Path(__file__).resolve().parent
exe = base / 'dist' / 'ConversorPDFa.exe'
installer = base / 'gs10071w64.exe'
zip_path = base / 'ConversorPDFa_Package.zip'

with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    z.write(exe, exe.name)
    z.write(installer, installer.name)

print('zip created', zip_path)
