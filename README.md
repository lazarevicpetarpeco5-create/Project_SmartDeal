# SmartDeal – Human-in-the-Loop AI Asistent & CRM Gateway

**SmartDeal** je namizna aplikacija (GUI), namenjena avtomatizaciji obdelave transkriptov prodajnih ali podpornih sestankov. Z uporabo umetne inteligence (OpenAI) pretvori nedokončana besedila pogovorov v strukturirane podatke, omogoča pregled in ročne popravke s strani uporabnika (*Human-in-the-Loop*), izvoz v uradna PDF poročila ter neposredno sinhronizacijo s CRM sistemom.

---

## 💻 Navodila za Končne Uporabnike

Za uporabo aplikacije **ne potrebujete** nameščenega Pythona ali programerskih orodij.

### 🪟 Za Windows uporabnike:
1. Prenesite datoteko **`SmartDeal.exe`** iz mape `dist/`.
2. Dvokliknite na `SmartDeal.exe` za zagon aplikacije.
3. Ob prvem zagonu kliknite gumb **⚙ Nastavitve API/CRM** v zgornjem desnem kotu ter vnesite vaše API ključe in CRM URL.
4. Nastavitve se samodejno shranijo v lokalno datoteko `config.json` ob aplikaciji.

### 🐧 Za Linux uporabnike:
1. Prenesite izvršljivo datoteko **`SmartDeal`** iz mape `dist/`.
2. V terminalu omogočite pravice za izvajanje (če je potrebno):
   ```bash
   chmod +x SmartDeal