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
# 1. Installer les dependances Python
pip install -r requirements.txt

# 2. Lancer l'app (1 worker : l'app est CPU-bound)
gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 300 app:app
```

Ouvrir http://localhost:5000

## Deploiement sur Render (plan gratuit)

L'application fonctionne **100% en Python, sans Calibre**. Elle manipule
directement le contenu XHTML de l'epub (un fichier ZIP) pour appliquer la
coloration syllabique via des `<span style="color:...">`, puis re-zippe l'epub.
Cela evite la dependance a Calibre/Qt/libOpenGL, indisponibles ou instables
sur Render free (systeme de fichiers en lecture seule).

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
- `build.sh` installe uniquement les paquets Python (pas de Calibre)
- `start.sh` lance gunicorn directement
- `$PORT` est injecte automatiquement par Render
- L'app s'eteindra apres 15 min d'inactivite (normal sur free) et se relancera au prochain acces

### Limites hebergement gratuit (512 Mo RAM)

- **Taille max du fichier : 20 Mo** (definie dans `app.py`, adaptee a la RAM disponible)
- **1 seul worker gunicorn** : le traitement est CPU-bound
- Si le traitement depasse la RAM, reduisez la taille/longueur du livre

## Architecture

```
epub input (zip) -> libs Python (ebooklib + lxml) -> coloration des syllabes dans le XHTML -> epub output (re-zippe)
```

## Fichiers

- `app.py` - Backend Flask
- `epub_processor.py` - Coloration syllabique directe de l'epub (ebooklib + lxml + pyphen)
- `build.sh` - Script de build Render (install des dependances Python)
- `start.sh` - Script de demarrage (lance gunicorn)
- `render.yaml` - Config Render Blueprint
- `templates/index.html`, `static/style.css` - Frontend
