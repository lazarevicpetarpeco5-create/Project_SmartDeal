import json
from app.models.analysis import AnalysisResult

class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key.strip() if api_key else ""

    def analyze_transcript(self, transcript: str) -> AnalysisResult:
        # Če API ključ ni vnesen ali je nastavljen na "MOCK", uporabi simulacijo
        if not self.api_key or self.api_key.upper() == "MOCK":
            return self._get_mock_response(transcript)

        # Resnični klic na OpenAI API
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)

        system_prompt = """
        Si strokovni AI asistent za analizo poslovnih sestankov v svetovalnem podjetju.
        Iz prejetega transkripta ali zapisnika sestanka natančno izlušči ključne informacije in vrni IZKLJUČNO veljaven JSON objekt z naslednjo strukturo:

        {
            "summary": "Kratek in strukturiran povzetek glavnih tem sestanka.",
            "client_requirements": "Ključne zahteve, izraženi problemi in potrebe stranke.",
            "action_items": "Seznam naslednjih korakov z jasnimi ODGOVORNI OSEBAMI in roki.",
            "follow_up_email": "Profesionalen osnutek follow-up e-poštnega sporočila za stranko z vsemi dogovori, naslednjimi koraki in prijaznim pozdravom."
        }

        Pravila:
        1. Besedilo mora biti v slovenskem jeziku.
        2. Če katera informacija ni izrecno navedena v transkriptu, napiši 'Ni navedeno'.
        3. Ne izmišljuj si podatkov.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Transkript sestanka:\n\n{transcript}"}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        raw_json = response.choices[0].message.content
        parsed = json.loads(raw_json)
        return AnalysisResult.from_dict(parsed)

    def _get_mock_response(self, transcript: str) -> AnalysisResult:
        """Testni odziv za preverjanje GUI-ja brez delujočega API ključa."""
        return AnalysisResult(
            summary="Sestanek glede avtomatizacije obdelave zapisnikov in integracije s CRM sistemom za ABC Podjetje.",
            client_requirements="- Samodejna analiza transkriptov sestankov.\n- Ekstrakcija nalog in odgovornih oseb.\n- Human-in-the-Loop urejanje pred zapisom.\n- REST API sinhronizacija s CRM.",
            action_items="1. Maja (Stranka): Pošiljanje CRM API specifikacije (rok: jutri do 12h).\n2. Petar (Svetovalec): Priprava tehnične ponudbe, arhitekture in demo prototipa (rok: petek).",
            follow_up_email="Spoštovani Marko,\n\nhvala za vaš čas na današnjem sestanku. V nadaljevanju pošiljam kratek povzetek naših dogovorov:\n\n- Pripravili bomo predlog avtomatizacije za obdelavo transkriptov.\n- Maja nam bo do jutri do 12h poslala specifikacije vašega CRM API-ja.\n- Do petka bova s skupino pripravila tehnično ponudbo in delujoč prototip.\n\nLep pozdrav,\nPetar"
        )