"""Small, dependency-free XLSX writer for immutable evidence tables.

All strings are inline strings, never formulas or external links.
"""

import math
import re
from io import BytesIO
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


def xml(value):
    return escape(re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(value)))


def workbook(tables):
    output = BytesIO()
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/package/2006/relationships"
    office = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
            + "".join(
                f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                for i in range(1, len(tables) + 1)
            )
            + "</Types>",
        )
        archive.writestr(
            "_rels/.rels",
            f'<Relationships xmlns="{rel}"><Relationship Id="rId1" Type="{office}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        )
        archive.writestr(
            "xl/workbook.xml",
            f'<workbook xmlns="{ns}" xmlns:r="{office}"><sheets>'
            + "".join(
                f'<sheet name="{xml(name)}" sheetId="{i}" r:id="rId{i}"/>'
                for i, (name, _) in enumerate(tables, 1)
            )
            + "</sheets></workbook>",
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            f'<Relationships xmlns="{rel}">'
            + "".join(
                f'<Relationship Id="rId{i}" Type="{office}/worksheet" Target="worksheets/sheet{i}.xml"/>'
                for i in range(1, len(tables) + 1)
            )
            + f'<Relationship Id="styles" Type="{office}/styles" Target="styles.xml"/></Relationships>',
        )
        archive.writestr(
            "xl/styles.xml",
            f'<styleSheet xmlns="{ns}"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF075985"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf/></cellStyleXfs><cellXfs count="2"><xf fontId="0" fillId="0" borderId="0" numFmtId="0" xfId="0"><alignment vertical="top" wrapText="1"/></xf><xf fontId="1" fillId="2" borderId="0" numFmtId="0" xfId="0" applyFill="1" applyFont="1"><alignment vertical="top" wrapText="1"/></xf></cellXfs></styleSheet>',
        )
        for index, (_, rows) in enumerate(tables, 1):
            widths = [32, 110] if len(rows[0]) == 2 else [25] * len(rows[0])
            body = []
            for number, row in enumerate(rows, 1):
                cells = []
                for value in row:
                    if value is None:
                        cells.append("<c/>")
                    elif isinstance(value, (int, float)):
                        cells.append(f"<c><v>{value}</v></c>")
                    else:
                        cells.append(
                            f'<c t="inlineStr" s="{int(number == 1)}"><is><t xml:space="preserve">{xml(value)}</t></is></c>'
                        )
                height = max(
                    45,
                    max(
                        (
                            math.ceil(len(str(v or "")) / (widths[i] - 3)) * 18
                            for i, v in enumerate(row)
                        ),
                        default=45,
                    ),
                )
                body.append(
                    f'<row r="{number}" ht="{min(409, height)}" customHeight="1">{"".join(cells)}</row>'
                )
            columns = "".join(
                f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>'
                for i, width in enumerate(widths, 1)
            )
            archive.writestr(
                f"xl/worksheets/sheet{index}.xml",
                f'<worksheet xmlns="{ns}"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>{columns}</cols><sheetData>{"".join(body)}</sheetData></worksheet>',
            )
    return output.getvalue()
