# Stock AI Predictor 📈

Ett AI-drivet aktieanalysprogram som använder mönsterigenkänning från nyheter, sociala medier och marknadsdata för att prediktera aktierörelser. Programmet undviker klassiska matematiska modeller och fokuserar istället på AI-baserad sentiment-analys och korrelationsidentifiering.

## Funktioner

- **AI-Driven Mönsterigenkänning**: Använder OpenAI's GPT-modeller för att identifiera mönster i marknadsdata
- **Multi-Source Data Collection**: Samlar data från aktiepriser, nyheter, Reddit och andra källor
- **Sentiment Analys**: Analyserar sentiment från nyheter och sociala medier
- **Korrelationsanalys**: Identifierar instrument som rör sig i motsatta eller liknande riktningar
- **Adaptiva Strategier**: Växlar automatiskt mellan olika strategier baserat på marknadsförhållanden
- **Veckovis Träffsäkerhetsrapportering**: Utvärderar och rapporterar prediktionsprestanda
- **Interaktiv Dashboard**: Streamlit-baserat användargränssnitt

## Systemarkitektur

Programmet består av flera komponenter:

### Data Collection Layer
- **yfinance**: Hämtar historiska aktiepriser (gratis)
- **Finnhub API**: Nyheter och sentiment (optional)
- **News API**: Ytterligare nyhetskällor (optional)
- **Reddit API (PRAW)**: Social media sentiment (optional)

### AI Analysis Engine
- **OpenAI GPT-4.1-mini**: Sentiment analys och mönsterigenkänning
- **Pattern Recognition**: Identifierar korrelationer och trender
- **Strategy Selection**: Väljer optimal strategi baserat på marknadsförhållanden

### Database Layer
- **SQLite**: Lokal databas för all historisk data
- Lagrar priser, nyheter, social media, prediktioner och resultat

### Presentation Layer
- **Streamlit**: Interaktiv web-baserad dashboard
- Visualisering av prediktioner, prestanda och marknadsinsikter

## Installation

### Förutsättningar

- Python 3.11 eller senare
- OpenAI API-nyckel (obligatorisk)
- Finnhub, News API, Reddit API-nycklar (valfria men rekommenderade)

### Steg 1: Klona Repository

```bash
git clone https://github.com/ditt-användarnamn/stock-ai-predictor.git
cd stock-ai-predictor
```

### Steg 2: Installera Dependencies

```bash
pip install -r requirements.txt
```

### Steg 3: Konfigurera Miljövariabler

Kopiera `.env.example` till `.env` och fyll i dina API-nycklar:

```bash
cp .env.example .env
```

Redigera `.env` och lägg till dina API-nycklar:

```
OPENAI_API_KEY=din_openai_api_nyckel
FINNHUB_API_KEY=din_finnhub_api_nyckel
NEWS_API_KEY=din_news_api_nyckel
REDDIT_CLIENT_ID=ditt_reddit_client_id
REDDIT_CLIENT_SECRET=din_reddit_client_secret
```

#### Hur man får API-nycklar:

**OpenAI** (Obligatorisk):
1. Gå till https://platform.openai.com/
2. Skapa ett konto eller logga in
3. Navigera till API Keys
4. Skapa en ny API-nyckel

**Finnhub** (Valfri):
1. Gå till https://finnhub.io/
2. Registrera ett gratis konto
3. Kopiera din API-nyckel från dashboard

**News API** (Valfri):
1. Gå till https://newsapi.org/
2. Registrera ett gratis konto
3. Kopiera din API-nyckel

**Reddit API** (Valfri):
1. Gå till https://www.reddit.com/prefs/apps
2. Klicka "create another app"
3. Välj "script" som app-typ
4. Kopiera client ID och secret

### Steg 4: Initiera Databas och Lägg Till Instrument

Starta Streamlit-appen:

```bash
streamlit run app.py
```

Gå till "Settings" i sidomenyn och lägg till instrument du vill följa, t.ex.:
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Google)
- TSLA (Tesla)
- AMZN (Amazon)

## Användning

### Daglig Datainsamling

Kör detta script dagligen för att samla in ny data:

```bash
python run_daily_update.py
```

Detta script:
- Hämtar senaste aktiepriser
- Samlar nyheter från de senaste 24 timmarna
- Samlar social media-poster
- Analyserar sentiment för all ny data

### Veckovis Prediktion

Kör detta script varje söndag för att generera prediktioner för kommande vecka:

```bash
python run_weekly_prediction.py
```

Detta script:
- Analyserar all insamlad data
- Identifierar korrelationer mellan instrument
- Genererar prediktioner för varje instrument
- Väljer optimal strategi för varje prediktion

### Utvärdering av Prediktioner

Kör detta script för att utvärdera tidigare prediktioner:

```bash
python run_evaluation.py
```

Detta script:
- Jämför prediktioner mot faktiska resultat
- Beräknar träffsäkerhet per strategi
- Uppdaterar prestanda-statistik

### Streamlit Dashboard

Starta dashboarden:

```bash
streamlit run app.py
```

Öppna webbläsaren på `http://localhost:8501`

#### Dashboard-sektioner:

**Overview**: Visar aktuella prediktioner och övergripande prestanda

**Predictions**: Detaljerad vy av alla prediktioner med filtrering

**Performance**: Analys av strategiprestanda över tid

**Market Insights**: AI-genererade marknadsinsikter

**Settings**: Lägg till nya instrument och konfigurera API:er

## Deployment på Render

### Steg 1: Förbered för Deployment

Skapa en `render.yaml` fil (redan inkluderad i projektet).

### Steg 2: Pusha till GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### Steg 3: Deploy på Render

1. Gå till https://render.com/
2. Skapa ett konto eller logga in
3. Klicka "New +" och välj "Web Service"
4. Anslut ditt GitHub-repository
5. Konfigurera:
   - **Name**: stock-ai-predictor
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
6. Lägg till Environment Variables:
   - `OPENAI_API_KEY`
   - `FINNHUB_API_KEY` (optional)
   - `NEWS_API_KEY` (optional)
   - `REDDIT_CLIENT_ID` (optional)
   - `REDDIT_CLIENT_SECRET` (optional)
7. Klicka "Create Web Service"

### Automatisering på Render

För att köra dagliga och veckovisa scripts automatiskt kan du använda Render Cron Jobs:

1. Skapa en ny "Cron Job" i Render
2. För daglig uppdatering:
   - **Command**: `python run_daily_update.py`
   - **Schedule**: `0 9 * * *` (kör kl 09:00 varje dag)
3. För veckovis prediktion:
   - **Command**: `python run_weekly_prediction.py`
   - **Schedule**: `0 10 * * 0` (kör kl 10:00 varje söndag)
4. För utvärdering:
   - **Command**: `python run_evaluation.py`
   - **Schedule**: `0 11 * * 1` (kör kl 11:00 varje måndag)

## Strategier

Programmet använder flera strategier som väljs automatiskt baserat på marknadsförhållanden:

### Momentum Strategy
Identifierar instrument med stark trend i både pris och sentiment. Predikterar fortsatt rörelse i samma riktning.

### Contrarian Strategy
Aktiveras när sentiment blir extremt. Letar efter överreaktioner och potentiella vändningar.

### Correlation Strategy
Använder identifierade korrelationer mellan instrument för att prediktera rörelser baserat på relaterade instruments beteende.

### News Impact Strategy
Analyserar hur snabbt och starkt marknaden reagerar på olika typer av nyheter och använder detta för prediktioner.

## Databasschema

### instruments
Lagrar information om spårade instrument (aktier, ETF:er, etc.)

### price_history
Historiska priser per instrument och datum

### news_items
Nyhetsartiklar med sentiment-analys

### social_posts
Social media-poster med sentiment

### predictions
Genererade prediktioner med reasoning och strategi

### results
Faktiska resultat för utvärdering

### strategy_performance
Träffsäkerhet per strategi och vecka

### correlations
Identifierade korrelationer mellan instrument

## Kostnader

### Gratis Komponenter:
- yfinance: Helt gratis
- Reddit API: Gratis
- Render: Gratis tier tillgänglig (begränsad)

### Betalda Komponenter:
- **OpenAI API**: ~$0.15-0.30 per 1M tokens (gpt-4.1-mini)
  - Uppskattat: $5-20/månad beroende på användning
- **Finnhub**: Gratis tier tillgänglig, premium från $59/mån
- **News API**: Gratis tier tillgänglig, premium från $449/mån
- **Render**: Gratis tier, premium från $7/mån

**Rekommenderad startkostnad**: ~$10-30/månad (OpenAI + Render)

## Begränsningar och Varningar

⚠️ **VIKTIGT**: Detta program är för utbildnings- och forskningsändamål. Det är INTE finansiell rådgivning.

- Prediktioner är inte garanterade och kan vara felaktiga
- Tidigare prestanda garanterar inte framtida resultat
- Använd aldrig mer kapital än du har råd att förlora
- Konsultera alltid en finansiell rådgivare innan du fattar investeringsbeslut
- API-kostnader kan variera beroende på användning

## Teknisk Stack

- **Python 3.11**
- **Streamlit**: Web UI
- **OpenAI GPT-4.1-mini**: AI-analys
- **yfinance**: Aktiedata
- **PRAW**: Reddit API
- **SQLite**: Databas
- **Plotly**: Visualisering
- **Pandas/NumPy**: Databehandling

## Bidra

Bidrag är välkomna! Öppna gärna issues eller pull requests.

## Licens

MIT License - Se LICENSE-filen för detaljer

## Support

För frågor eller problem, öppna ett issue på GitHub.

## Roadmap

Framtida förbättringar:
- [ ] Stöd för fler datakällor (Twitter/X, StockTwits)
- [ ] Backtesting-funktionalitet
- [ ] Email-notifikationer för prediktioner
- [ ] Portfolio tracking
- [ ] Risk management-verktyg
- [ ] Multi-language support
- [ ] Mobile app

## Författare

Skapat med ❤️ av AI och människor

---

**Disclaimer**: Detta verktyg är endast för informations- och utbildningsändamål. Det utgör inte finansiell rådgivning. Investeringar i värdepapper innebär risk och du kan förlora hela eller delar av ditt investerade kapital.
