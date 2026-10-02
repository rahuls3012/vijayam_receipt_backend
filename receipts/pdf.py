from io import BytesIO
from django.conf import settings
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from .utils import inr

NAVY, INK, MUTED = HexColor("#1B2A6B"), HexColor("#1A1D29"), HexColor("#6B7280")


def build_receipt_pdf(r) -> bytes:
    I = settings.INSTITUTE
    buf = BytesIO()
    W, H = landscape(A5)
    c = canvas.Canvas(buf, pagesize=(W, H))
    c.setTitle(f"Receipt {r.receipt_no}")

    # double border
    c.setStrokeColor(NAVY); c.setLineWidth(2); c.rect(14, 14, W - 28, H - 28)
    c.setLineWidth(0.5); c.rect(19, 19, W - 38, H - 38)

    # letterhead
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W / 2, H - 50, I["trust"].upper())
    c.setFillColor(MUTED); c.setFont("Helvetica", 8.5)
    c.drawCentredString(W / 2, H - 63, f"(Reg No. {I['reg_no']})")
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 23)
    c.drawCentredString(W / 2, H - 90, I["name"].upper())
    c.setFillColor(INK); c.setFont("Helvetica", 10)
    c.drawCentredString(W / 2, H - 104, I["place"])
    c.setFillColor(MUTED); c.setFont("Helvetica", 8.5)
    c.drawCentredString(W / 2, H - 118, f"Cell: {I['cell_1']}   |   Cell: {I['cell_2']} ({I['cell_2_note']})")
    c.setStrokeColor(NAVY); c.setLineWidth(0.8); c.line(34, H - 127, W - 34, H - 127)

    # receipt badge, serial no, date
    c.setFillColor(NAVY); c.roundRect(W / 2 - 48, H - 160, 96, 24, 4, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(W / 2, H - 153, "RECEIPT")
    c.setFillColor(INK); c.setFont("Helvetica", 10); c.drawString(36, H - 153, "Sl No.")
    c.setFont("Helvetica-Bold", 14); c.drawString(70, H - 154, str(r.receipt_no))
    c.setFont("Helvetica", 10); c.drawRightString(W - 108, H - 153, "Date:")
    c.setFont("Helvetica-Bold", 11); c.drawRightString(W - 36, H - 153, r.date.strftime("%d-%m-%Y"))

    # fields
    def field(label, value, y):
        c.setFillColor(MUTED); c.setFont("Helvetica-Oblique", 9); c.drawString(36, y, label)
        c.setFillColor(INK); c.setFont("Helvetica-Bold", 10.5)
        lines = simpleSplit(value, "Helvetica-Bold", 10.5, W - 36 - 190) or [""]
        for i, ln in enumerate(lines[:2]):
            yy = y - i * 17
            c.drawString(192, yy, ln)
            c.setStrokeColor(MUTED); c.setLineWidth(0.6); c.setDash(1, 2)
            c.line(190, yy - 3, W - 36, yy - 3); c.setDash()
        return y - 17 * min(len(lines), 2) - 8

    y = H - 192
    y = field("Received with thanks from M/s.", r.received_from, y)
    y = field("Rupees", r.amount_in_words, y)
    y = field("Towards", r.towards, y)
    y = field("Payment mode", r.get_payment_mode_display(), y)

    # amount box, balance, signature
    c.setStrokeColor(NAVY); c.setLineWidth(1.4); c.rect(36, 44, 150, 36)
    c.setFillColor(NAVY); c.rect(36, 44, 34, 36, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 12); c.drawCentredString(53, 58, "Rs.")
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 15); c.drawString(78, 57, f"{inr(r.amount)}/-")
    c.setFillColor(MUTED); c.setFont("Helvetica-Oblique", 9); c.drawString(204, 58, "Balance :")
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 10.5)
    c.drawString(248, 58, f"Rs. {inr(r.balance)}/-" if r.balance else "Nil")
    c.setStrokeColor(INK); c.setLineWidth(0.6); c.line(W - 190, 62, W - 36, 62)
    c.setFont("Helvetica-Bold", 9.5); c.drawCentredString(W - 113, 66, r.cashier)
    c.setFillColor(MUTED); c.setFont("Helvetica-Oblique", 9); c.drawCentredString(W - 113, 50, "Cashier")
    c.setFont("Helvetica", 7); c.drawCentredString(W / 2, 27, "This is a computer-generated receipt.")

    c.showPage(); c.save()
    return buf.getvalue()
