import os
import subprocess
import tempfile
import shutil
import logging

from flask import Flask, request, render_template, send_file, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Limite adaptee au plan gratuit Render (512 Mo RAM)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 Mo
LOG_FILE = "calibre.log"


def _ebook_convert_cmd():
    """Retourne la commande ebook-convert, en tenant compte du binaire
    portable Calibre (calibre-bin/) installe au build."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "calibre-bin", "ebook-convert"),
        os.path.join(base_dir, "calibre-bin", "calibre", "ebook-convert"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return [p]
    return ["ebook-convert"]


def _run_calibre(args, timeout=300):
    """Lance ebook-convert en redirigeant la sortie vers un fichier
    (evite de stocker de gros stderr en memoire sur Render free)."""
    cmd = _ebook_convert_cmd() + args
    with open(LOG_FILE, "a") as log:
        log.write("\n--- cmd: " + " ".join(cmd) + " ---\n")
        log.flush()
        return subprocess.run(
            cmd,
            stdout=log,
            stderr=log,
            timeout=timeout,
        )


def _tail_log(n=40):
    """Renvoie les dernieres lignes de calibre.log pour le diagnostic."""
    try:
        with open(LOG_FILE) as f:
            lines = f.read().splitlines()
        return "\n".join(lines[-n:])
    except Exception:
        return ""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process_epub():
    if "epub" not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400

    file = request.files["epub"]
    if not file.filename.endswith(".epub"):
        return jsonify({"error": "Le fichier doit etre au format .epub"}), 400

    processor_mode = request.form.get("processor", "python")

    tmp_dir = tempfile.mkdtemp(prefix="lirecouleur_")
    try:
        input_path = os.path.join(tmp_dir, "input.epub")
        temp_docx = os.path.join(tmp_dir, "temp.docx")
        colored_docx = os.path.join(tmp_dir, "colored.docx")
        output_path = os.path.join(tmp_dir, "output.epub")
        file.save(input_path)

        file_size = os.path.getsize(input_path)
        if file_size > MAX_FILE_SIZE:
            return jsonify({"error": "Fichier trop volumineux (max 20 Mo sur le plan gratuit)"}), 400

        # Step 1: EPUB -> DOCX
        logger.info("Conversion EPUB -> DOCX")
        result = _run_calibre([input_path, temp_docx])
        if result.returncode != 0:
            return jsonify({"error": "La conversion EPUB vers DOCX a echoue.<br><pre>" + _tail_log() + "</pre>"}), 500

        # Step 2: Traitement du DOCX
        logger.info("Traitement du document (mode=%s)", processor_mode)
        if processor_mode == "libreoffice":
            try:
                from processor_libreoffice import process_docx_libreoffice
                process_docx_libreoffice(temp_docx, colored_docx)
            except RuntimeError as e:
                return jsonify({"error": str(e)}), 500
        else:
            from processor import process_docx
            process_docx(temp_docx, colored_docx)

        # Step 3: DOCX -> EPUB
        logger.info("Conversion DOCX -> EPUB")
        result = _run_calibre([colored_docx, output_path])
        if result.returncode != 0:
            return jsonify({"error": "La conversion DOCX vers EPUB a echoue.<br><pre>" + _tail_log() + "</pre>"}), 500

        # Step 4: Envoi du fichier
        original_name = os.path.splitext(file.filename)[0]
        response = send_file(
            output_path,
            as_attachment=True,
            download_name=f"{original_name}_lirecouleur.epub",
            mimetype="application/epub+zip",
            max_age=0,
        )
        response.call_on_close(lambda: shutil.rmtree(tmp_dir, ignore_errors=True))
        return response

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Le traitement a depasse le temps limite. Le fichier est peut-etre trop volumineux."}), 500
    except Exception as e:
        logger.exception("Erreur lors du traitement")
        return jsonify({"error": "Une erreur interne est survenue. Reessayez avec un fichier plus petit."}), 500


@app.route("/health")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
