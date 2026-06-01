# apps/generator-app/src/generator_app/services/audio.py
import asyncio
import hashlib
import logging
import re
from pathlib import Path
import edge_tts

# Lokaler Logger für dieses Modul
logger = logging.getLogger(__name__)


def clean_cloze_text(raw_text: str) -> str:
    """
    Säubert den Anki-Lückentext für eine flüssige Sprachausgabe.
    Entfernt Hinweise und bricht verlässlich nicht bei mehreren Lücken aus.
    """
    # 1. Schritt: Entfernt Tipps/Hinweise, behält aber die Anki-Struktur für Schritt 2 bei.
    # Macht aus: "El {{c1::libro::Nomen}} es rojo." -> "El {{c1::libro}} es rojo."
    text_without_hints = re.sub(r"\{\{c(\d+)::([^{}:]+?)::[^}]+?\}\}", r"{{c\1::\2}}", raw_text)
    
    # 2. Schritt: Holt das reine Wort aus den verbliebenen Standard-Klammern heraus.
    # Macht aus: "El {{c1::libro}} es rojo." -> "El libro es rojo."
    clean_text = re.sub(r"\{\{c\d+::([^{}:]+?)\}\}", r"\1", text_without_hints)
    
    return clean_text.strip()


async def _generate_audio_file(text: str, output_path: Path, voice:str) -> None:
    """Führt den asynchronen Download von den Microsoft-Servern aus."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def get_or_generate_audio(
        text_es: str, 
        audio_dir: Path, 
        media_files_pool: list[str],
        voice:str, 
    ) -> str:
    """Prüft lokale Audios oder generiert diese dynamisch via edge-tts."""
    audio_dir.mkdir(parents=True, exist_ok=True)

    text_hash = hashlib.md5(text_es.encode("utf-8")).hexdigest()
    filename = f"audio_{text_hash}.mp3"
    full_audio_path = audio_dir / filename

    if full_audio_path.exists():
        logger.debug("Audio bereits vorhanden für: '%s'", text_es[:20])
    else:
        logger.info("Generiere neues Audio für: '%s...'", text_es[:30])
        asyncio.run(_generate_audio_file(text_es, full_audio_path,voice))

    media_files_pool.append(str(full_audio_path))
    return f"[sound:{filename}]"