# Lire Couleur - ePub Processor

Application web de modification d'ePubs appliquant la coloration syllabique "Lire Couleur".

## Fonctionnalites

- Import de fichiers .epub
- Coloration des syllabes (bleu/rouge alterne)
- Premiere lettre verte en majuscule
- Double espacement entre les mots
- Telechargement du fichier modifie

## Test local

```bash
# 1. Installer Calibre
sudo apt-get install -y calibre

# 2. Installer les dependances Python
pip install -r requirements.txt

# 3. Lancer l'app (1 worker : l'app est CPU-bound)
gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 300 app:app
```

Ouvrir http://localhost:5000

## Deploiement sur Render (plan gratuit)

Render Free ne supportant plus Docker, on utilise le runtime Python natif avec un script de build qui installe Calibre.

### Options A - Fichier `render.yaml` (Blueprint)

1. Push le repo sur GitHub
2. Sur Render, cliquer **New +** (en haut a droite) puis **Blueprint**
3. Connecter le repo GitHub
4. Render lira automatiquement `render.yaml` et creera le Web Service
5. **Deploy Blueprint**

### Options B - Manuel via l'UI

1. **New Web Service** (pas Workflow)
2. **Connect repository** -> votre repo GitHub
3. Configure :
   - **Name**: `lirecouleur`
   - **Region**: pres de vous (ex: Frankfurt)
   - **Environment**: `Python 3`
   - **Branch**: `main`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 300 app:app`
   - **Instance Type**: `Free`
4. **Create Web Service**

### Remarques plan gratuit

- Render installe automatiquement les dependances Python depuis `requirements.txt`
- Le script `build.sh` installe Calibre systeme via apt (sudo est disponible en build)
- `$PORT` est injecte automatiquement par Render
- L'app s'eteindra apres 15 min d'inactivite (normal sur free) et se relancera au prochain acces

### Limites hebergement gratuit (512 Mo RAM)

- **Taille max du fichier : 20 Mo** (definie dans `app.py`, adaptee a la RAM disponible)
- **1 seul worker gunicorn** : le traitement est CPU-bound, plusieurs workers doubleraient la consommation RAM
- Calibre tourne en sous-processus separe a chaque etape : la memoire est liberee entre les conversions
- La sortie Calibre est redirigee vers `calibre.log` au lieu de la RAM (evite de saturer sur les gros fichiers)
- **Evitez l'option LibreOffice UNO en free** : trop lourde (legerement plus gourmande en RAM)
- Si le traitement depasse 300 s ou la RAM, reduisez la taille/longueur du livre

## Architecture

```
epub input -> Calibre (epub->docx) -> Python (coloration) -> Calibre (docx->epub) -> epub output
```

## Fichiers

- `app.py` - Backend Flask
- `processor.py` - Coloration syllabique (python-docx + pyphen)
- `processor_libreoffice.py` - Option LibreOffice UNO (non disponible en free, trop lourd)
- `build.sh` - Script de build pour Render (installe Calibre)
- `render.yaml` - Config Render Blueprint
- `templates/index.html`, `static/style.css` - Frontend
