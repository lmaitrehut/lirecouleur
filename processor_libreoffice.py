import subprocess
import time
import os


def process_docx_libreoffice(input_path, output_path):
    """Apply LireCouleur formatting via LibreOffice UNO macro.

    Requires: libreoffice, python3-uno installed in the container.
    Falls back to an error if dependencies are missing.
    """
    try:
        import uno
        from com.sun.star.beans import PropertyValue
    except ImportError:
        raise RuntimeError(
            "python3-uno is not installed. "
            "Install libreoffice and python3-uno, or use the default processor."
        )

    file_url = uno.systemPathToFileUrl(os.path.abspath(input_path))

    soffice_proc = subprocess.Popen([
        "soffice", "--headless", "--invisible",
        "--accept=socket,host=127.0.0.1,port=2002;urp;"
    ])
    time.sleep(3)

    try:
        local_context = uno.getComponentContext()
        resolver = local_context.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_context
        )
        ctx = resolver.resolve(
            "uno:socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext"
        )
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

        props = (PropertyValue("Hidden", 0, True, 0),)
        doc = desktop.loadComponentFromURL(file_url, "_blank", 0, props)

        script_provider = doc.getScriptProvider()
        try:
            macro = script_provider.getScript(
                "vnd.sun.star.script:LireCouleur.ModuleMain.AideLecture"
                "?language=Basic&location=user"
            )
        except Exception:
            macro = script_provider.getScript(
                "vnd.sun.star.script:LireCouleur.ModuleMain.AideLecture"
                "?language=Basic&location=application"
            )

        macro.invoke((), (), ())
        doc.store()
        doc.close(True)

        import shutil
        uno_output = input_path
        if uno_output != output_path:
            shutil.copy2(uno_output, output_path)

        return output_path

    finally:
        soffice_proc.terminate()
