# apps/generator-app/src/generator_app/app.py
import logging
from generator_app.config import SETTINGS
from generator_app.services.generator import generate_decks_and_packages

# Globaler Logger-Kontext für die Konsole
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run() -> None:
    """Zentraler Startpunkt des Programms."""
    logging.info("Starte Hauptanwendung...")
    
    if not SETTINGS.file_configurations:
        logging.error("Keine passenden Konfigurationen gefunden. Abbruch.")
        return

    # Startet den entkoppelten Service
    generate_decks_and_packages(SETTINGS)


if __name__ == "__main__":
    run()
