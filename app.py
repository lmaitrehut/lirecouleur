import os
import tempfile
import shutil
import logging

from flask import Flask, request, render_template, send_file, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Limite adaptee au plan gratuit Render (512 Mo RAM)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 Mo


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

    tmp_dir = tempfile.mkdtemp(prefix="lirecouleur_")
    try:
        input_path = os.path.join(tmp_dir, "input.epub")
        output_path = os.path.join(tmp_dir, "output.epub")
        file.save(input_path)

        file_size = os.path.getsize(input_path)
        if file_size > MAX_FILE_SIZE:
            return jsonify({"error": "Fichier trop volumineux (max 20 Mo sur le plan gratuit)"}), 400

        logger.info("Traitement de l'epub (coloration syllabique)")
        from epub_processor import process_epub as colorer
        colorer(input_path, output_path)

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

    except Exception as e:
        logger.exception("Erreur lors du traitement")
        return jsonify({"error": "Une erreur interne est survenue: " + str(e)}), 500


@app.route("/health")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
