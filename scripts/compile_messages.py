import os
import polib


def compile_po_to_mo():
    """
    Compiles all .po files in the locales directory into .mo files.
    """
    locales_dir = os.path.join(os.path.dirname(__file__), "..", "locales")
    for lang in os.listdir(locales_dir):
        lang_dir = os.path.join(locales_dir, lang)
        if os.path.isdir(lang_dir):
            lc_messages_dir = os.path.join(lang_dir, "LC_MESSAGES")
            if os.path.isdir(lc_messages_dir):
                po_file_path = os.path.join(lc_messages_dir, "messages.po")
                if os.path.exists(po_file_path):
                    print(f"Compiling {po_file_path}...")
                    po_file = polib.pofile(po_file_path)
                    mo_file_path = os.path.join(lc_messages_dir, "messages.mo")
                    po_file.save_as_mofile(mo_file_path)
                    print(f"Successfully compiled to {mo_file_path}")


if __name__ == "__main__":
    compile_po_to_mo()
