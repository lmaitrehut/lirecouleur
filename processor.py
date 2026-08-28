import re
import pyphen
from docx import Document
from docx.shared import RGBColor

try:
    dic = pyphen.Pyphen(lang="fr")
except Exception:
    try:
        dic = pyphen.Pyphen(lang="fr_FR")
    except Exception:
        dic = None

VERT = RGBColor(0, 150, 0)
BLEU = RGBColor(0, 32, 255)
ROUGE = RGBColor(220, 0, 0)
COULEURS = [BLEU, ROUGE]


def _decouper_fallback(mot):
    pattern = r"(?i)[^aeiouyàâéèêëîïôûùüç]*[aeiouyàâéèêëîïôûùüç]+(?:(?![aeiouyàâéèêëîïôûùüç])[^aeiouyàâéèêëîïôûùüç])?"
    syllabes = re.findall(pattern, mot)
    if syllabes and "".join(syllabes) == mot:
        return syllabes
    return [mot]


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


def process_docx(input_path, output_path):
    doc = Document(input_path)

    for p in doc.paragraphs:
        if not p.text.strip():
            continue
        mots = p.text.split()
        p.text = ""
        for idx_mot, mot in enumerate(mots):
            if not mot:
                continue
            syllabes = _syllabes(mot)
            est_premiere = True
            for idx_syl, syl in enumerate(syllabes):
                couleur = COULEURS[idx_syl % len(COULEURS)]
                for char in syl:
                    if est_premiere and char.isalpha():
                        run = p.add_run(char.upper())
                        run.font.color.rgb = VERT
                        est_premiere = False
                    else:
                        run = p.add_run(char)
                        if char.isalnum():
                            run.font.color.rgb = couleur
            if idx_mot < len(mots) - 1:
                p.add_run("  ")

    doc.save(output_path)
    return output_path
