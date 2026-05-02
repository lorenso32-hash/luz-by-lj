"""
Luz By LJ — Collab/Portfolio Session Contract Generator
Run: python3 tools/build_contract_pdf.py
Output: Luz_By_LJ_Collab_Contract.pdf
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "Luz_By_LJ_Collab_Contract.pdf")

BRAND_TEAL = colors.HexColor("#00B4CC")
BRAND_DARK = colors.HexColor("#0D0D1A")
BRAND_GRAY = colors.HexColor("#444455")
LIGHT_GRAY = colors.HexColor("#CCCCCC")

SESSION = {
    "date":        "April 19, 2026",
    "location":    "Light House Studio",
    "photographer":"Lorenso Jaramillo (Luz By LJ)",
}


def build():
    styles = getSampleStyleSheet()

    title_s = ParagraphStyle("T", parent=styles["Heading1"],
        fontSize=18, leading=22, textColor=BRAND_TEAL,
        alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=2)
    sub_s = ParagraphStyle("Sub", parent=styles["Normal"],
        fontSize=9, leading=12, textColor=BRAND_GRAY,
        alignment=TA_CENTER, spaceAfter=12)
    sec_s = ParagraphStyle("Sec", parent=styles["Normal"],
        fontSize=10, leading=13, textColor=BRAND_TEAL,
        fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=3)
    body_s = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=9, leading=13, textColor=BRAND_DARK,
        alignment=TA_JUSTIFY, spaceAfter=4)
    label_s = ParagraphStyle("Label", parent=styles["Normal"],
        fontSize=8.5, leading=11, textColor=BRAND_GRAY)
    value_s = ParagraphStyle("Value", parent=styles["Normal"],
        fontSize=9, leading=11, textColor=BRAND_DARK, fontName="Helvetica-Bold")
    sig_label_s = ParagraphStyle("SigLabel", parent=styles["Normal"],
        fontSize=8, leading=10, textColor=BRAND_GRAY)
    footer_s = ParagraphStyle("Footer", parent=styles["Normal"],
        fontSize=7.5, textColor=BRAND_GRAY, alignment=TA_CENTER)

    W = letter[0]
    content_w = W - 1.7 * inch
    label_w   = 1.6 * inch
    field_w   = content_w - label_w

    story = []

    # ── Header ─────────────────────────────────────────────────────────────────
    story.append(Paragraph("LUZ BY LJ", title_s))
    story.append(Paragraph(
        "Collab &amp; Portfolio Session — Image Release &amp; Model Agreement", sub_s))
    story.append(HRFlowable(width="100%", thickness=1, color=BRAND_TEAL, spaceAfter=10))

    # ── 1. Session Details ─────────────────────────────────────────────────────
    story.append(Paragraph("1. SESSION DETAILS", sec_s))

    def detail_row(label, value, underline=False):
        t = Table(
            [[Paragraph(label, label_s), Paragraph(value, value_s)]],
            colWidths=[label_w, field_w]
        )
        style = [
            ("VALIGN",        (0,0), (-1,-1), "BOTTOM"),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
        ]
        if underline:
            style.append(("LINEBELOW", (1,0), (1,0), 0.75, BRAND_DARK))
        t.setStyle(TableStyle(style))
        story.append(t)

    detail_row("Participant Name:", "", underline=True)
    detail_row("Session Date:",     SESSION["date"])
    detail_row("Session Location:", SESSION["location"])
    detail_row("Photographer:",     SESSION["photographer"])
    story.append(Spacer(1, 4))

    # ── 2–9. Contract clauses ──────────────────────────────────────────────────
    story.append(Paragraph("2. IMAGE USE CONSENT", sec_s))
    story.append(Paragraph(
        "By signing this agreement, the Participant grants the Photographer a "
        "<b>perpetual, irrevocable, royalty-free, worldwide license</b> to use, "
        "reproduce, distribute, display, and publish images, video, and other media "
        "captured during this session for any lawful purpose, including but not "
        "limited to: portfolio display, social media, marketing materials, editorial "
        "use, and website content. This consent survives the termination of any "
        "business relationship between the parties.", body_s))

    story.append(Paragraph("3. PHOTOGRAPHER IDENTITY", sec_s))
    story.append(Paragraph(
        "For purposes of this agreement, the \"Photographer\" refers to "
        "<b>Lorenso Jaramillo</b>, operating as <i>Luz By LJ</i> or any future "
        "creative venture under his name, and any affiliated agents or assignees. "
        "Rights granted herein are tied to Lorenso Jaramillo as an individual and "
        "transfer with any rebranding or business restructuring under his direction.", body_s))

    story.append(Paragraph("4. COPYRIGHT OWNERSHIP", sec_s))
    story.append(Paragraph(
        "All photographs, video footage, and derivative works produced during this "
        "session are and shall remain the sole intellectual property of the "
        "Photographer. The Participant acquires no ownership rights, copyrights, or "
        "licensing rights to any images or media produced, except as expressly "
        "provided in a separate written agreement signed by both parties.", body_s))

    story.append(Paragraph("5. EDITING &amp; DIGITAL MANIPULATION", sec_s))
    story.append(Paragraph(
        "The Participant consents to the Photographer's full creative discretion in "
        "editing, retouching, cropping, color grading, compositing, and otherwise "
        "altering the images. The Participant waives any right to review, approve, "
        "or reject the Photographer's edits prior to use or publication.", body_s))

    story.append(Paragraph("6. PARTICIPANT COPY RESTRICTIONS", sec_s))
    story.append(Paragraph(
        "Images delivered to the Participant are for personal use. The Participant "
        "agrees: (a) not to apply additional filters, overlays, or visual alterations "
        "that materially change the Photographer's edit; (b) not to remove, obscure, "
        "or alter any watermark or branding applied by the Photographer; and "
        "(c) to credit the Photographer when sharing images publicly.", body_s))

    story.append(Paragraph("7. NO GUARANTEE OF USE", sec_s))
    story.append(Paragraph(
        "The Photographer makes no guarantee that any images produced during this "
        "session will be published, distributed, or used in any specific manner or "
        "timeframe. The Participant has no claim against the Photographer for failure "
        "to publish or use the images.", body_s))

    story.append(Paragraph("8. REVOCATION", sec_s))
    story.append(Paragraph(
        "The Participant understands that due to the perpetual and irrevocable nature "
        "of the license granted herein, revocation of consent is not available after "
        "signing except in cases where applicable law expressly provides otherwise. "
        "Requests for image removal from active platforms may be made in writing to "
        "the Photographer and will be considered on a case-by-case basis as a "
        "courtesy, not an obligation.", body_s))

    story.append(PageBreak())
    story.append(Paragraph("9. MINOR / ADULT CHAPERONE CONSENT", sec_s))
    story.append(Paragraph(
        "If the Participant is under 18 years of age, an adult chaperone or authorized "
        "representative must sign this agreement on their behalf. By signing below as "
        "Adult Chaperone, the undersigned represents that they are at least 18 years of "
        "age, were present during the session, and accept responsibility for consenting "
        "to the terms of this agreement on the Participant's behalf.", body_s))
    story.append(Spacer(1, 4))

    # ── Acknowledgement ───────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=8))
    story.append(Paragraph(
        "By signing below, the Adult Chaperone acknowledges that they have read, "
        "understood, and agree to the terms of this agreement on behalf of the "
        "Participant. Photography services for this session were provided at no charge. "
        "Any payment made was solely to cover shared studio rental costs and does not "
        "constitute compensation to the Photographer for photographic services.", body_s))
    story.append(Spacer(1, 10))

    # ── Signature Block — all underlines, no AcroForm ─────────────────────────
    half = (content_w - 0.4 * inch) / 2

    def sig_row(left_label, right_label):
        """Label row + blank underlined row."""
        labels = Table(
            [[Paragraph(left_label, sig_label_s), "", Paragraph(right_label, sig_label_s)]],
            colWidths=[half, 0.4 * inch, half]
        )
        labels.setStyle(TableStyle([
            ("VALIGN",        (0,0), (-1,-1), "BOTTOM"),
            ("BOTTOMPADDING", (0,0), (-1,-1), 1),
        ]))
        story.append(labels)

        blanks = Table(
            [["", "", ""]],
            colWidths=[half, 0.4 * inch, half],
            rowHeights=[24]
        )
        blanks.setStyle(TableStyle([
            ("LINEBELOW",     (0,0), (0,0), 0.75, BRAND_DARK),
            ("LINEBELOW",     (2,0), (2,0), 0.75, BRAND_DARK),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
        ]))
        story.append(blanks)
        story.append(Spacer(1, 6))

    sig_row("Adult Chaperone Signature", "Date")
    sig_row("Adult Chaperone Printed Name", "Relationship to Participant")

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BRAND_TEAL, spaceAfter=4))
    story.append(Paragraph(
        "Luz By LJ · Albuquerque, NM · LuzByLJ@gmail.com · @LuzByLJ", footer_s))

    # ── Build ──────────────────────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.65 * inch,
        title="Luz By LJ — Collab Session Contract",
        author="Lorenso Jaramillo",
    )
    doc.build(story)
    print(f"✓ Contract saved: {os.path.abspath(OUTPUT)}")


if __name__ == "__main__":
    build()
