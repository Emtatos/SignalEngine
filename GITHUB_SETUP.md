# GitHub Setup Guide

Detta dokument beskriver hur du laddar upp Stock AI Predictor till GitHub.

## Metod 1: Via GitHub Web Interface (Enklast)

### Steg 1: Skapa nytt repository på GitHub

1. Gå till https://github.com/new
2. Fyll i följande:
   - **Repository name**: `stock-ai-predictor`
   - **Description**: "AI-driven stock market prediction using pattern recognition from news and social media"
   - **Visibility**: Välj "Public" eller "Private"
   - **VIKTIGT**: Markera INTE "Add a README file" (vi har redan en)
   - Markera INTE "Add .gitignore" (vi har redan en)
   - Markera INTE "Choose a license" (vi har redan en)
3. Klicka "Create repository"

### Steg 2: Pusha din lokala kod

GitHub visar nu instruktioner. Använd dessa kommandon i din terminal:

```bash
cd /path/to/stock-ai-predictor

# Lägg till GitHub som remote
git remote add origin https://github.com/DITT-ANVÄNDARNAMN/stock-ai-predictor.git

# Pusha koden
git push -u origin main
```

Om du blir ombedd att logga in:
- **Username**: Ditt GitHub-användarnamn
- **Password**: Använd en Personal Access Token (inte ditt lösenord)

### Steg 3: Skapa Personal Access Token (om behövs)

Om du inte har en Personal Access Token:

1. Gå till https://github.com/settings/tokens
2. Klicka "Generate new token" → "Generate new token (classic)"
3. Ge token ett namn (t.ex., "Stock AI Predictor")
4. Välj scope: `repo` (full control of private repositories)
5. Klicka "Generate token"
6. **VIKTIGT**: Kopiera token omedelbart (den visas bara en gång)
7. Använd denna token som lösenord när du pushar

## Metod 2: Via GitHub CLI (Rekommenderat)

Om du har GitHub CLI installerat:

```bash
cd /path/to/stock-ai-predictor

# Logga in på GitHub (om inte redan gjort)
gh auth login

# Skapa repository och pusha
gh repo create stock-ai-predictor --public --source=. --push

# Eller för privat repository:
gh repo create stock-ai-predictor --private --source=. --push
```

## Metod 3: Via SSH (För avancerade användare)

### Steg 1: Konfigurera SSH-nyckel

Om du inte redan har en SSH-nyckel:

```bash
# Generera SSH-nyckel
ssh-keygen -t ed25519 -C "din@email.com"

# Starta ssh-agent
eval "$(ssh-agent -s)"

# Lägg till nyckel
ssh-add ~/.ssh/id_ed25519

# Kopiera public key
cat ~/.ssh/id_ed25519.pub
```

### Steg 2: Lägg till SSH-nyckel på GitHub

1. Gå till https://github.com/settings/keys
2. Klicka "New SSH key"
3. Klistra in din public key
4. Klicka "Add SSH key"

### Steg 3: Pusha med SSH

```bash
cd /path/to/stock-ai-predictor

# Lägg till remote med SSH
git remote add origin git@github.com:DITT-ANVÄNDARNAMN/stock-ai-predictor.git

# Pusha
git push -u origin main
```

## Verifiera Upload

Efter lyckad upload:

1. Gå till https://github.com/DITT-ANVÄNDARNAMN/stock-ai-predictor
2. Du bör se alla filer och README.md visas automatiskt
3. Kontrollera att följande finns:
   - ✓ README.md (med projektbeskrivning)
   - ✓ app.py (huvudapplikation)
   - ✓ requirements.txt (dependencies)
   - ✓ models/ (databas-modeller)
   - ✓ utils/ (verktyg och AI-analys)
   - ✓ DEPLOYMENT.md (deployment-guide)
   - ✓ LICENSE (MIT-licens)

## Uppdatera Repository

När du gör ändringar i framtiden:

```bash
# Lägg till ändringar
git add .

# Commit med beskrivande meddelande
git commit -m "Beskrivning av ändringar"

# Pusha till GitHub
git push
```

## Vanliga Problem och Lösningar

### Problem: "Permission denied (publickey)"

**Lösning**: Du behöver konfigurera SSH-nyckel eller använda HTTPS med Personal Access Token.

### Problem: "Repository not found"

**Lösning**: Kontrollera att repository-namnet är korrekt och att du har rätt behörigheter.

### Problem: "Failed to push some refs"

**Lösning**: Någon annan har pushat ändringar. Kör:
```bash
git pull --rebase origin main
git push
```

### Problem: "Support for password authentication was removed"

**Lösning**: GitHub kräver inte längre lösenord. Använd Personal Access Token istället.

## Rekommenderade GitHub Settings

### 1. Branch Protection

För att skydda main branch:

1. Gå till repository Settings → Branches
2. Klicka "Add rule"
3. Branch name pattern: `main`
4. Aktivera:
   - ✓ Require pull request reviews before merging
   - ✓ Require status checks to pass before merging

### 2. Repository Topics

Lägg till topics för bättre upptäckbarhet:

1. Gå till repository huvudsida
2. Klicka på kugghjulet vid "About"
3. Lägg till topics:
   - `stock-market`
   - `ai`
   - `machine-learning`
   - `streamlit`
   - `python`
   - `trading`
   - `sentiment-analysis`

### 3. Repository Description

Uppdatera beskrivningen:
```
AI-driven stock market prediction using pattern recognition from news and social media. Built with Streamlit, OpenAI, and Python.
```

### 4. GitHub Pages (Valfritt)

Om du vill ha en projektwebbplats:

1. Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main`, folder: `/docs` (skapa docs-mapp först)

## Nästa Steg

Efter GitHub-upload:
1. ✓ Verifiera att alla filer är uppladdade
2. → Fortsätt till DEPLOYMENT.md för Render-deployment
3. → Dela ditt projekt med andra
4. → Acceptera contributions via Pull Requests

## Collaboration

Om du vill ha bidrag från andra:

### 1. Skapa CONTRIBUTING.md

```markdown
# Contributing

Vi välkomnar bidrag! Följ dessa steg:

1. Fork repository
2. Skapa en feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit dina ändringar (`git commit -m 'Add AmazingFeature'`)
4. Push till branch (`git push origin feature/AmazingFeature`)
5. Öppna en Pull Request
```

### 2. Skapa Issue Templates

1. Gå till Settings → Features → Issues → Set up templates
2. Lägg till "Bug report" och "Feature request" templates

### 3. Lägg till Code of Conduct

GitHub kan generera en automatiskt via Settings → Community.

## Support

Om du behöver hjälp:
- GitHub Docs: https://docs.github.com/
- GitHub CLI Docs: https://cli.github.com/manual/
- SSH Setup: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

Lycka till med din GitHub-upload! 🚀
