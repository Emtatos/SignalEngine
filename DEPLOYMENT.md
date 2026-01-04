# Deployment Guide

Detta dokument beskriver hur du deployar Stock AI Predictor till Render.

## Förutsättningar

1. Ett GitHub-konto
2. Ett Render-konto (gratis tier tillgänglig)
3. OpenAI API-nyckel

## Steg 1: Förbered GitHub Repository

### 1.1 Skapa nytt repository på GitHub

1. Gå till https://github.com/new
2. Namnge ditt repository (t.ex., `stock-ai-predictor`)
3. Välj "Public" eller "Private"
4. **Markera INTE** "Initialize with README" (vi har redan en)
5. Klicka "Create repository"

### 1.2 Pusha koden till GitHub

```bash
cd stock-ai-predictor
git init
git add .
git commit -m "Initial commit: Stock AI Predictor"
git branch -M main
git remote add origin https://github.com/DITT-ANVÄNDARNAMN/stock-ai-predictor.git
git push -u origin main
```

## Steg 2: Deploy till Render

### 2.1 Skapa Web Service

1. Gå till https://render.com/
2. Logga in eller skapa ett konto
3. Klicka på "New +" i övre högra hörnet
4. Välj "Web Service"
5. Anslut ditt GitHub-konto om du inte redan gjort det
6. Välj ditt `stock-ai-predictor` repository
7. Konfigurera servicen:

**Basic Settings:**
- **Name**: `stock-ai-predictor` (eller valfritt namn)
- **Region**: Välj närmaste region (t.ex., Frankfurt för Europa)
- **Branch**: `main`
- **Root Directory**: Lämna tomt
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

**Plan:**
- Välj "Free" för att börja (kan uppgraderas senare)

8. Klicka på "Advanced" för att lägga till miljövariabler

### 2.2 Konfigurera Environment Variables

Under "Environment Variables", lägg till följande:

**Obligatoriska:**
```
OPENAI_API_KEY = din_openai_api_nyckel
```

**Valfria (men rekommenderade):**
```
FINNHUB_API_KEY = din_finnhub_api_nyckel
NEWS_API_KEY = din_news_api_nyckel
REDDIT_CLIENT_ID = ditt_reddit_client_id
REDDIT_CLIENT_SECRET = din_reddit_client_secret
```

9. Klicka "Create Web Service"

Render kommer nu att:
- Klona ditt repository
- Installera dependencies
- Starta Streamlit-appen
- Ge dig en publik URL (t.ex., `https://stock-ai-predictor.onrender.com`)

### 2.3 Vänta på deployment

Första deployment tar vanligtvis 5-10 minuter. Du kan följa processen i Render's logs.

## Steg 3: Konfigurera Cron Jobs (Valfritt men rekommenderat)

För att automatisera dagliga uppdateringar och veckovisa prediktioner:

### 3.1 Daglig Uppdatering

1. I Render dashboard, klicka "New +" → "Cron Job"
2. Välj samma repository
3. Konfigurera:
   - **Name**: `stock-ai-daily-update`
   - **Command**: `python run_daily_update.py`
   - **Schedule**: `0 9 * * *` (kör kl 09:00 UTC varje dag)
4. Lägg till samma environment variables som för web service
5. Klicka "Create Cron Job"

### 3.2 Veckovis Prediktion

1. Skapa en ny Cron Job
2. Konfigurera:
   - **Name**: `stock-ai-weekly-prediction`
   - **Command**: `python run_weekly_prediction.py`
   - **Schedule**: `0 10 * * 0` (kör kl 10:00 UTC varje söndag)
3. Lägg till environment variables
4. Klicka "Create Cron Job"

### 3.3 Veckovis Utvärdering

1. Skapa en ny Cron Job
2. Konfigurera:
   - **Name**: `stock-ai-evaluation`
   - **Command**: `python run_evaluation.py`
   - **Schedule**: `0 11 * * 1` (kör kl 11:00 UTC varje måndag)
3. Lägg till environment variables
4. Klicka "Create Cron Job"

## Steg 4: Verifiera Deployment

1. Öppna din Render URL i webbläsaren
2. Du bör se Stock AI Predictor dashboard
3. Gå till "Settings" och lägg till några instrument (t.ex., AAPL, MSFT, GOOGL)
4. Vänta på att data samlas in (kan ta några minuter första gången)

## Steg 5: Första Körningen

Efter deployment, kör följande manuellt första gången:

### Via Render Shell:

1. I Render dashboard, gå till din web service
2. Klicka på "Shell" i menyn
3. Kör:

```bash
python run_daily_update.py
python run_weekly_prediction.py
```

Detta kommer att:
- Samla in initial data för alla instrument
- Generera första veckan's prediktioner

## Troubleshooting

### Problem: "Module not found" error

**Lösning**: Kontrollera att `requirements.txt` innehåller alla nödvändiga paket och att build command är korrekt.

### Problem: Streamlit startar inte

**Lösning**: Kontrollera att start command inkluderar rätt port och address:
```
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

### Problem: Database reset efter varje deploy

**Lösning**: Render's free tier har ephemeral storage. För persistent storage, uppgradera till en betald plan eller använd en extern databas (PostgreSQL).

Alternativt, använd Render Disks:
1. I web service settings, gå till "Disks"
2. Lägg till en disk monterad på `/data`
3. Uppdatera `database.py` för att använda `/data/stock_predictor.db`

### Problem: API rate limits

**Lösning**: 
- För OpenAI: Övervaka användning på https://platform.openai.com/usage
- För Finnhub/News API: Använd free tier försiktigt eller uppgradera
- Implementera caching för att minska API-anrop

### Problem: Timeout errors

**Lösning**: Render's free tier har begränsningar. Överväg:
- Minska antalet instrument som spåras
- Optimera API-anrop
- Uppgradera till betald plan för mer resurser

## Kostnadsuppskattning

### Render (Free Tier):
- Web Service: Gratis (begränsad till 750 timmar/månad)
- Cron Jobs: Gratis (begränsade körningar)
- **Begränsningar**: 
  - Går i sleep efter 15 min inaktivitet
  - Ephemeral storage (data försvinner vid restart)

### Render (Paid):
- Starter: $7/månad per service
- Standard: $25/månad per service
- **Fördelar**:
  - Alltid aktiv
  - Persistent storage
  - Mer resurser

### API Kostnader:
- **OpenAI**: ~$5-20/månad (beroende på användning)
- **Finnhub**: Gratis tier tillgänglig
- **News API**: Gratis tier tillgänglig
- **Reddit**: Gratis

**Total uppskattad kostnad**: $5-50/månad beroende på konfiguration

## Optimeringar för Produktion

### 1. Använd Persistent Storage

Konfigurera en extern databas eller Render Disk för att bevara data mellan deploys.

### 2. Implementera Caching

Lägg till caching för API-anrop för att minska kostnader:

```python
import functools
from datetime import datetime, timedelta

@functools.lru_cache(maxsize=128)
def cached_api_call(symbol, date):
    # API call here
    pass
```

### 3. Monitoring och Logging

Lägg till logging för att övervaka systemets prestanda:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 4. Error Notifications

Konfigurera email-notifikationer för fel:
- Använd SendGrid eller liknande tjänst
- Skicka alerts när prediktioner misslyckas
- Notifiera om låg träffsäkerhet

### 5. Backup Strategy

Implementera regelbunden backup av databasen:

```bash
# Lägg till i cron job
python backup_database.py
```

## Support

Om du stöter på problem:
1. Kontrollera Render logs för felmeddelanden
2. Verifiera att alla environment variables är korrekt konfigurerade
3. Testa lokalt först innan du deployar
4. Öppna ett issue på GitHub för support

## Nästa Steg

Efter lyckad deployment:
1. Lägg till fler instrument via Settings
2. Övervaka träffsäkerhet i Performance-sektionen
3. Justera strategier baserat på resultat
4. Överväg att lägga till fler datakällor
5. Implementera email-notifikationer för prediktioner

Lycka till med din deployment! 🚀
