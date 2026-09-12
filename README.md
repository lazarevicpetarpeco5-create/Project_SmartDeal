

## 🚀 Načina Delovanja: Mock (Testni) vs. Live API

Aplikacija podpira dva načina obdelave transkriptov, kar omogoča preizkušanje vseh funkcionalnosti tudi brez aktivnega OpenAI API ključa ali plačniškega računa.

| Funkcionalnost | 🧪 Mock (Testni) Način | ⚡ Live OpenAI API Način |
| :--- | :--- | :--- |
| **Zahteva za API ključ** | Polje ostane prazno ali se vpiše `MOCK` | Zahteva veljaven OpenAI API ključ (`sk-...`) |
| **Povezava z internetom** | Ni potrebna (deluje brez povezave) | Potrebna za klic na OpenAI strežnike |
| **Hitrost obdelave** | Trenutna odzivnost | ~1-3 sekunde (odvisno od dolžine transkripta) |
| **Izvor podatkov** | Vnaprej pripravljen determinističen testni odziv | Dinamična AI ekstrakcija iz vnesenega transkripta |
| **Namen uporabe** | Testiranje GUI-ja, evaluacija, predstavitve, test CRM/PDF izvoza | Produkcijska obdelava realnih sestankov |

---

## 🛠️ Kako uporabljati MOCK Način

1. Zaženite aplikacijo `SmartDeal` (ali `SmartDeal.exe`).
2. Kliknite na gumb **⚙ Nastavitve (API / CRM)** v zgornjem desnem kotu.
3. V polje **OpenAI API Ključ** pustite prazno besedilo ali vpišite besedo `MOCK`.
4. Kliknite **Shrani nastavitve**.
5. V levo vnosno polje prilepite poljuben transkript ali besedilo.
6. Kliknite gumb **⚡ Analiziraj z AI (gpt-4o-mini)**.
7. Aplikacija bo takoj simulirala analizo ter vsa 4 polja v desnem panelu napolnila s strukturiranimi podatki, odgovornimi osebami in osnutkom follow-up e-pošte.

---

## 💻 Navodila za Končne Uporabnike

Za uporabo aplikacije **ne potrebujete** nameščenega Pythona ali dodatnih knjižnic.

### 🪟 Za Windows uporabnike:
1. V mapi poiščite datoteko **`SmartDeal.exe`**.
2. Dvokliknite na `SmartDeal.exe` za zagon aplikacije.
3. Ob prvem zagonu po potrebi kliknite gumb **⚙ Nastavitve (API / CRM)** za vnos ključev ali CRM URL-ja.
4. Nastavitve se samodejno shranijo v lokalno datoteko `config.json` ob aplikaciji.

### 🐧 Za Linux uporabnike:
1. V mapi poiščite izvršljivo datoteko **`SmartDeal`**.
2. V terminalu omogočite pravice za izvajanje (če je potrebno):
   ```bash
   chmod +x SmartDeal
