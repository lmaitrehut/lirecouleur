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

Render Free ne supportant ni Docker ni l'installation via `apt-get` (systeme de fichiers en lecture seule). On utilise donc le **runtime Python natif** avec **Calibre portable** (binaire autonome installe sans root dans `calibre-bin/`) pendant le build.

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
   - **Start Command**: `./start.sh`
   - **Instance Type**: `Free`
4. **Create Web Service**

### Remarques plan gratuit

- Render installe automatiquement les dependances Python depuis `requirements.txt`
- **Calibre est telecharge en mode "isolated"** dans `calibre-bin/` pendant le build (aucun droit root requis, le binaire embarque ses dependances)
- Le dossier `calibre-bin/` est cree au build et persiste au runtime (comme le venv Python)
- `start.sh` verifie la presence de `ebook-convert` puis lance gunicorn
- `$PORT` est injecte automatiquement par Render
- L'app s'eteindra apres 15 min d'inactivite (normal sur free) et se relancera au prochain acces

### Version Calibre et libraries systeme

Les versions recentes de Calibre (>= 6) exigent des bibliotheques systeme
(`libOpenGL.so.0`, `libxcb-cursor`, etc.) indisponibles sur Render free
(systeme de fichiers en lecture seule, pas d'`apt-get`).

On fixe donc **Calibre 5.44.0** (via l'argument `version=5.44.0` dans `build.sh`),
qui ne requiert que GLIBC >= 2.27 et fonctionne sans ces libraries GUI.

Si une future version 5.x pose probleme, ajustez le numéro de version dans
`build.sh`. Si un jour Render permet d'installer les libraries systeme,
vous pourriez revenir a une version recente.


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
- `build.sh` - Script de build Render (installe Calibre portable dans `calibre-bin/` puis les dependances Python)
- `start.sh` - Script de demarrage : verifie `ebook-convert` portable puis lance gunicorn
- `render.yaml` - Config Render Blueprint
- `templates/index.html`, `static/style.css` - Frontend
