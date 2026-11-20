from pathlib import Path
import pandas as pd

workbook = Path(__file__).with_name("Molten-Salt-Corrosion-Data.xlsx")
if not workbook.exists():
    raise SystemExit(
        "Workbook not found. Download Molten-Salt-Corrosion-Data.xlsx from "
        "https://github.com/shortlab/2020-Molten-Salt-Corrosion-FPs "
        "and place it beside this script."
    )
book = pd.ExcelFile(workbook)
out = Path(__file__).with_name("extracted_sheets")
out.mkdir(exist_ok=True)
print("Workbook sheets:", book.sheet_names)
for sheet in book.sheet_names:
    frame = pd.read_excel(workbook, sheet_name=sheet)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in sheet)
    frame.to_csv(out / f"{safe}.csv", index=False)
    print(f"\\n[{sheet}] rows={len(frame)} columns={list(frame.columns)}")
    print(frame.head(10).to_string(index=False))
print(f"\\nCSV exports written to: {out}")
