from pathlib import Path
import subprocess
import shutil

ROOT = Path("data/raw").resolve()

# Locate LibreOffice
soffice = shutil.which("soffice")

if not soffice:
    # Common Windows installation path
    candidate = Path(
        r"C:\Program Files\LibreOffice\program\soffice.exe"
    )
    if candidate.exists():
        soffice = str(candidate)
    else:
        raise RuntimeError(
            "LibreOffice not found. Install it or add soffice to PATH."
        )

files = list(ROOT.rglob("*.pptx"))
files += list(ROOT.rglob("*.PPTX"))

print(f"Found {len(files)} PowerPoint files.")

for pptx in files:
    pdf = pptx.with_suffix(".pdf")

    if pdf.exists():
        print(f"SKIPPED (PDF already exists): {pdf}")
        continue

    result = subprocess.run(
        [
            soffice,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(pptx.parent),
            str(pptx),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and pdf.exists():
        print(f"SUCCESS: {pptx.name} -> {pdf.name}")
    else:
        print(f"FAILED: {pptx}")
        print(result.stderr or result.stdout)

print("Conversion finished.")