"""Styled Excel and CSV exports."""
import csv
import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HEADER_FILL = PatternFill("solid", fgColor="12354A")
BAND_FILL = PatternFill("solid", fgColor="F2F6F8")
THIN = Side(style="thin", color="D7E0E4")


def build_workbook(sheets, subtitle=None):
    """sheets: list of (title, headers, rows). Returns a BytesIO positioned at 0."""
    workbook = Workbook()
    workbook.remove(workbook.active)
    for title, headers, rows in sheets:
        sheet = workbook.create_sheet(title[:31])
        start = 1
        if subtitle:
            sheet.cell(1, 1, subtitle).font = Font(italic=True, color="5B6B75")
            start = 3
        for col, header in enumerate(headers, start=1):
            cell = sheet.cell(start, col, header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = HEADER_FILL
            cell.alignment = Alignment(vertical="center", horizontal="left")
        for r, row in enumerate(rows, start=start + 1):
            for c, value in enumerate(row, start=1):
                cell = sheet.cell(r, c, value)
                cell.border = Border(bottom=THIN)
                if (r - start) % 2 == 0:
                    cell.fill = BAND_FILL
        for col, header in enumerate(headers, start=1):
            longest = max([len(str(header))] + [len(str(row[col - 1])) for row in rows if col - 1 < len(row)] or [10])
            sheet.column_dimensions[get_column_letter(col)].width = min(max(longest + 3, 10), 46)
        sheet.freeze_panes = sheet.cell(start + 1, 1)
        if rows:
            sheet.auto_filter.ref = f"A{start}:{get_column_letter(len(headers))}{start + len(rows)}"
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


def build_csv(headers, rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)
    return io.BytesIO(buffer.getvalue().encode("utf-8-sig"))
