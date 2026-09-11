import os
from typing import Optional
from app.models.analysis import AnalysisResult
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _setup_slovenian_font():
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont("CustomSlovenianFont", path))
            return "CustomSlovenianFont"
    return "Helvetica"


class AIService:

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI

                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                self.client = None

    def analyze(self, transcript: str) -> AnalysisResult:
        if not transcript.strip():
            raise ValueError("Transkript ne sme biti prazen.")

        if not self.client:
            return AnalysisResult(
                summary=(
                    "Stranka sprašuje po avtomatizaciji obdelave zapiskov"
                    " sestankov in integraciji z obstoječim CRM sistemom."
                ),
                customer_sentiment="Pozitivno / Visoko zanimanje",
                main_issue=(
                    "Ročni vnos podatkov iz transkriptov zaposlenim vzame"
                    " preveč časa in povzroča napake."
                ),
                customer_needs=[
                    "Avtomatska ekstrakcija povzetka in ključnih točk",
                    "Validacija podatkov s strani človeka pred vnosom (HITL)",
                    "Direktni zapis v CRM preko REST API vmesnika",
                    "Priprava osnutka follow-up sporočila za stranko",
                ],
                recommended_action=(
                    "Pripravi ponudbo za pilotni projekt SmartDeal in posreduj"
                    " tehnično dokumentacijo API integracije."
                ),
            )

        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Deluješ kot strokovni analitik poslovnih sestankov."
                        " Analiziraj priloženi transkript in izvleči"
                        " strukturirane podatke."
                    ),
                },
                {"role": "user", "content": transcript},
            ],
            response_format=AnalysisResult,
        )
        return response.choices[0].message.parsed

    def generate_pdf(self, result_text: str, output_path: str):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )
        font_name = _setup_slovenian_font()
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontName=font_name,
            fontSize=18,
            textColor=HexColor("#16a34a"),
            spaceAfter=15,
        )

        body_style = ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=11,
            leading=16,
            textColor=HexColor("#1e293b"),
            spaceAfter=10,
        )

        elements = []
        elements.append(
            Paragraph("SmartDeal - Poročilo Analize Sestanka", title_style)
        )
        elements.append(Spacer(1, 10))

        formatted_content = result_text.replace("\n", "<br/>")
        elements.append(Paragraph(formatted_content, body_style))

        doc.build(elements)