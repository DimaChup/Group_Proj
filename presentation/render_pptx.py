"""Render demetro_slides.pptx to PNG images via PowerPoint COM."""
import win32com.client
from pathlib import Path
import sys

HERE = Path(__file__).parent
PPTX = HERE / "demetro_slides.pptx"
OUT_DIR = HERE / "_rendered"
OUT_DIR.mkdir(exist_ok=True)

print(f"Opening {PPTX}...")
ppt = win32com.client.Dispatch("PowerPoint.Application")
# ppt.Visible = False  # some versions reject False
pres = ppt.Presentations.Open(str(PPTX.absolute()), WithWindow=False)

print(f"Rendering {pres.Slides.Count} slides...")
for i in range(1, pres.Slides.Count + 1):
    out_path = OUT_DIR / f"slide_{i}.png"
    pres.Slides(i).Export(str(out_path.absolute()), "PNG", 2000, 1125)
    print(f"  -> {out_path}")

pres.Close()
ppt.Quit()
print("Done.")
