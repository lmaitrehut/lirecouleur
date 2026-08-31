import re
import zipfile

from ebooklib import epub, ITEM_DOCUMENT
from lxml import etree

import pyphen

try:
    dic = pyphen.Pyphen(lang="fr")
except Exception:
    try:
        dic = pyphen.Pyphen(lang="fr_FR")
    except Exception:
        dic = None

XHTML = "http://www.w3.org/1999/xhtml"

COULEURS = ["#0020FF", "#DC0000"]  # bleu, rouge (alterne par syllabe)
VERT = "#009600"


def _decouper_fallback(mot):
    pattern = r"(?i)[^aeiouyàâéèêëîïôûùüç]*[aeiouyàâéèêëîïôûùüç]+(?:(?![aeiouyàâéèêëîïôûùüç])[^aeiouyàâéèêëîïôûùüç])?"
    s = re.findall(pattern, mot)
    return s if s and "".join(s) == mot else [mot]


def _syllabes(mot):
    match = re.match(r"^([^\wàâéèêëîïôûùüç]*)(.*?)([^\wàâéèêëîïôûùüç]*)$", mot, re.IGNORECASE)
    if not match:
        return [mot]
    prefixe, mot_epure, suffixe = match.groups()
    if not mot_epure:
        return [mot]
    syllabes = []
    if dic:
        decoupe = dic.inserted(mot_epure)
        if decoupe and "-" in decoupe:
            syllabes = decoupe.split("-")
    if not syllabes:
        syllabes = _decouper_fallback(mot_epure)
    if prefixe:
        syllabes[0] = prefixe + syllabes[0]
    if suffixe:
        syllabes[-1] = syllabes[-1] + suffixe
    return syllabes


def _syllabe_xml(mot):
    """Decoupe un mot en syllabes colorees.
    Retourne une liste de (texte, couleur)."""
    syllabes = _syllabes(mot)
    parts = []  # (texte, couleur)
    premiere_lettre = True
    for idx_syl, syl in enumerate(syllabes):
        couleur = COULEURS[idx_syl % len(COULEURS)]
        # trouver la premiere lettre du mot (verte + majuscule)
        if premiere_lettre:
            pos = next((i for i, c in enumerate(syl) if c.isalpha()), None)
            if pos is not None:
                parts.append((syl[pos].upper(), VERT))
                if pos > 0:
                    parts.append((syl[:pos], couleur))
                if pos + 1 < len(syl):
                    parts.append((syl[pos + 1:], couleur))
                premiere_lettre = False
            else:
                parts.append((syl, couleur))
        else:
            parts.append((syl, couleur))
    return parts


def _colorer_paragraphe(p):
    """Colore un element de paragraphe (p, div, h*, li) en re-construisant
    ses noeuds de texte, un mot a la fois."""
    text = "".join(p.itertext())
    if not text.strip():
        return

    # Supprimer tous les enfants et attributs
    for child in list(p):
        p.remove(child)
    p.text = None
    for k in list(p.keys()):
        del p.attrib[k]

    # Traiter les mots en conservant tous les espaces intermediaires tels quels.
    # On decoupe en tokens espace/non-espace.
    tokens = re.findall(r"\S+|\s+", text)
    for tok in tokens:
        if tok.isspace():
            # On conserve le(s) espace(s). L'utilisateur veut le DOUBLEMENT des
            # espaces entre les mots : on transforme un espace simple en double.
            nb = tok.count(" ")
            span = etree.SubElement(p, "{%s}span" % XHTML)
            span.text = " " * (nb * 2)
        else:
            parts = _syllabe_xml(tok)
            for txt, couleur in parts:
                span = etree.SubElement(p, "{%s}span" % XHTML)
                if couleur:
                    span.set("style", "color:%s;" % couleur)
                span.text = txt


def _colorer_document(root):
    """Parcourt tous les elements de paragraphe du document XHTML."""
    body_tags = ["{%s}p" % XHTML, "{%s}div" % XHTML, "{%s}h1" % XHTML,
                 "{%s}h2" % XHTML, "{%s}h3" % XHTML, "{%s}h4" % XHTML,
                 "{%s}li" % XHTML, "{%s}td" % XHTML]
    block_tags = set(body_tags)
    block_tags.discard(None)
    # Ne traiter que les elements sans descendants de type bloc.
    for tag in body_tags:
        for el in list(root.iter(tag)):
            descendants = list(el.iter())
            if len(descendants) > 1 and any(
                d.tag in block_tags for d in descendants[1:]
            ):
                continue
            try:
                _colorer_paragraphe(el)
            except Exception:
                continue


def _rewrite_epub(input_path, output_path, modified):
    """Re-ecrit le zip epub depuis l'original, en remplacant le contenu des
    fichiers XHTML modifies. Reproduit la structure valide (mimetype non compresse)."""
    with zipfile.ZipFile(input_path, "r") as zin, \
         zipfile.ZipFile(output_path, "w") as zout:
        items = zin.infolist()
        # ecrire le fichier mimetype en premier, sans compression
        for i in items:
            if i.filename == "mimetype":
                data = zin.read(i.filename)
                zout.writestr(zipfile.ZipInfo("mimetype"), data, compress_type=zipfile.ZIP_STORED)
                break
        for i in items:
            if i.filename == "mimetype":
                continue
            data = modified.get(i.filename)
            if data is None:
                data = zin.read(i.filename)
            zout.writestr(i, data)


def process_epub(input_path, output_path):
    """Colore l'epub d'entree et ecrit l'epub colore de sortie."""
    book = epub.read_epub(input_path)
    modified = {}

    for item in book.get_items_of_type(ITEM_DOCUMENT):
        try:
            content = item.get_body_content() or item.get_content()
            root = etree.fromstring(content)
        except Exception:
            continue
        try:
            _colorer_document(root)
            modified[item.get_name()] = etree.tostring(
                root, xml_declaration=True, encoding="utf-8", standalone=True)
        except Exception:
            continue

    _rewrite_epub(input_path, output_path, modified)
    return output_path
