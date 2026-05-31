# anki-deck-generator/apps/generator-app/src/generator_app/app.py
import csv
import logging
from pathlib import Path
import genanki


from generator_app.config import SETTINGS, InputFileConfig
from generator_app.models import get_genanki_model
from generator_app.services.audio import clean_cloze_text, get_or_generate_audio


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def read_csv_data_and_add_to_subdecks(
    file_configurations: list[InputFileConfig],
    media_files_pool: list[str],
    #cloze_model: genanki.Model,
) -> list[genanki.Deck]:
    """Liest CSV-Konfigurationen ein und generiert eine Liste von Anki-Subdecks."""
    all_generated_decks: list[genanki.Deck] = []

    for config in file_configurations:
        # Konvertierung in Path-Objekt für modernere Pfad-Operationen
        file_path = Path(config.file_name)

        audio_dir = file_path.parent / "audio"

        cloze_model = get_genanki_model(
            model_id=config.model_id,
            model_name=config.model_name,
            card_style=config.css_content,
            fields=config.fields,
            qfmt=config.qfmt_content,
            afmt=config.afmt_content,
            is_cloze=config.is_cloze,
        )

        if not file_path.exists():
            logging.warning("Überspringe: '%s' nicht gefunden.", file_path)
            continue

        logging.info("Verarbeite '%s' -> %s", file_path.name, config.deck_name)
        sub_deck = genanki.Deck(config.deck_id, config.deck_name)

        try:
            with open(file_path, mode="r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                
                for row_number, row in enumerate(reader, start=1):
                    # Validierung: Fehlt eine Spalte in der Zeile?
                    required_fields = ["main_topic", "cloze_test", "translation", "hint", "extra"]
                    if not all(field in row for field in required_fields):
                        logging.error("Fehlerhaftes Spaltenformat in %s, Zeile %d", file_path.name, row_number)
                        continue


                    text_cleaned:str = clean_cloze_text(row["cloze_test"].strip())

                    if config.generate_audio:
                        audio_anki_tag = get_or_generate_audio(text_cleaned, audio_dir, media_files_pool)
                    else:
                        audio_anki_tag = ""


                    note = genanki.Note(
                        model=cloze_model,
                        fields=[
                            row["main_topic"].strip(),
                            row["cloze_test"].strip(),
                            row["translation"].strip(),
                            row["hint"].strip(),
                            row["extra"].strip(),
                            audio_anki_tag
                        ],
                    )
                    sub_deck.add_note(note)

            all_generated_decks.append(sub_deck)

        except (IOError, csv.Error) as e:
            logging.error("Fehler beim Lesen der Datei %s: %s", file_path.name, e)

    return all_generated_decks


def run() -> None:
    logging.info("Starte Hauptanwendung...")
    
    if not SETTINGS.file_configurations:
        logging.error("Keine passenden Konfigurationen gefunden.")
        return
    

    

    # Wir iterieren über das von dir gebaute Dictionary (Sprachordner und die zugehörigen Decks)
    for language_folder, configs in SETTINGS.file_configurations.items():
        

        # Zentraler Sammeltopf für alle MP3-Pfade (wichtig für den genanki-Export)
        global_media_files: list[str] = []

        # 1. Alle Subdecks für diesen spezifischen Sprachordner generieren
        all_generated_decks = read_csv_data_and_add_to_subdecks(
            configs,
            global_media_files,
        )
        
        if not all_generated_decks:
            logging.warning("Keine Decks für den Ordner '%s' generiert.", language_folder)
            continue
            
        # 2. Den schönen Ausgabe-Namen zielsicher aus dem source_mapping holen!
        output_filename = SETTINGS.source_mappings[language_folder].output_filename

        generate_audio:bool = SETTINGS.source_mappings[language_folder].generate_audio
        
        logging.info("Erzeuge Paket für '%s' -> Exportiere nach '%s'...", language_folder, output_filename)
        
        try:
            package = genanki.Package(all_generated_decks)

            if generate_audio:
                package.media_files = global_media_files

            package.write_to_file(output_filename)
            logging.info("Erfolg! Paket '%s' wurde erstellt.\n", output_filename)
        except Exception as e:
            logging.critical("Das Anki-Paket '%s' konnte nicht geschrieben werden: %s", output_filename, e)


if __name__ == "__main__":
    run()
