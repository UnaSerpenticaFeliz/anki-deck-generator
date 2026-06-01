# apps/generator-app/src/generator_app/services/generator.py
import logging
import genanki

from generator_app.config import AppSettings, InputFileConfig
from generator_app.services.parser import process_single_csv_file

logger = logging.getLogger(__name__)


def generate_decks_and_packages(settings: AppSettings) -> None:
    """Orchestriert den gesamten Generierungs- und Paketierungsprozess."""
    for language_folder, configs in settings.file_configurations.items():
        global_media_files: list[str] = []
        all_generated_decks: list[genanki.Deck] = []

        # 1. Alle Subdecks für diese Sprache einsammeln
        for config in configs:
            sub_deck = process_single_csv_file(config, global_media_files)
            if sub_deck:
                all_generated_decks.append(sub_deck)

        if not all_generated_decks:
            logger.warning("Keine Decks für den Ordner '%s' generiert.", language_folder)
            continue
            
        # 2. Export nach .apkg ausführen
        mapping = settings.source_mappings[language_folder]
        output_filename = mapping.output_filename
        
        logger.info("Erzeuge Paket für '%s' -> Exportiere nach '%s'...", language_folder, output_filename)
        
        try:
            package = genanki.Package(all_generated_decks)
            if mapping.generate_audio:
                package.media_files = global_media_files

            package.write_to_file(output_filename)
            logger.info("Erfolg! Paket '%s' wurde erstellt.\n", output_filename)
        except Exception as e:
            logger.critical("Das Anki-Paket '%s' konnte nicht geschrieben werden: %s", output_filename, e)
