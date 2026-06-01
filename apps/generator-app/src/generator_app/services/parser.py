# apps/generator-app/src/generator_app/services/parser.py
import csv
import logging
from pathlib import Path
import genanki

from generator_app.config import InputFileConfig
from generator_app.models import get_genanki_model
from generator_app.services.audio import clean_cloze_text, get_or_generate_audio

logger = logging.getLogger(__name__)


def _create_anki_note(
    row: dict[str, str], 
    config: InputFileConfig, 
    cloze_model: genanki.Model, 
    audio_dir: Path, 
    media_files_pool: list[str]
) -> genanki.Note:
    """Bereitet die Daten einer Zeile vor, regelt das Audio und baut die Anki-Note."""
    cloze_test_raw = row["cloze_test"].strip()

    audio_anki_tag = ""
    if config.generate_audio:
        text_cleaned = clean_cloze_text(cloze_test_raw)
        audio_anki_tag = get_or_generate_audio(
            text_cleaned, 
            audio_dir, 
            media_files_pool,
            config.edge_tts_voice
        )

    return genanki.Note(
        model=cloze_model,
        fields=[
            row["main_topic"].strip(),
            cloze_test_raw,
            row["translation"].strip(),
            row["hint"].strip(),
            row["extra"].strip(),
            audio_anki_tag
        ],
    )


def process_single_csv_file(config: InputFileConfig, media_files_pool: list[str]) -> genanki.Deck | None:
    """Verarbeitet eine einzelne CSV/TXT-Datei und liefert ein fertiges Subdeck zurück."""
    file_path = Path(config.file_name)
    if not file_path.exists():
        logger.warning("Überspringe: '%s' nicht gefunden.", file_path)
        return None

    logger.info("Verarbeite '%s' -> %s", file_path.name, config.deck_name)
    audio_dir = file_path.parent / "audio"
    
    cloze_model = get_genanki_model(
        model_id=config.model_id, model_name=config.model_name, card_style=config.css_content,
        fields=config.fields, qfmt=config.qfmt_content, afmt=config.afmt_content, is_cloze=config.is_cloze,
    )
    sub_deck = genanki.Deck(config.deck_id, config.deck_name)
    required_fields = ["main_topic", "cloze_test", "translation", "hint", "extra"]

    try:
        with open(file_path, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row_number, row in enumerate(reader, start=1):
                if not all(field in row for field in required_fields):
                    logger.error("Fehlerhaftes Spaltenformat in %s, Zeile %d", file_path.name, row_number)
                    continue

                note = _create_anki_note(row, config, cloze_model, audio_dir, media_files_pool)
                sub_deck.add_note(note)
        return sub_deck

    except (IOError, csv.Error) as e:
        logger.error("Fehler beim Lesen der Datei %s: %s", file_path.name, e)
        return None
