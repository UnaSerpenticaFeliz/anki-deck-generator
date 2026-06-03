# apps/generator-app/src/generator_app/app.py
import logging
import argparse
from generator_app.config import AppSettings, load_yaml_config
from generator_app.services.generator import generate_decks_and_packages

# Globaler Logger-Kontext für die Konsole
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def parse_arguments() -> argparse.Namespace:
    """Processes the CLI arguments for dynamic configurations."""
    parser = argparse.ArgumentParser(description="Anki Deck Generator")
    parser.add_index = parser.add_argument(
        "-c","--config",
        type=str,
        default="config.yaml",
        help="Name of the configuration yaml file"
    )
    return parser.parse_args()

def run() -> None:
    """Zentraler Startpunkt des Programms."""
    args = parse_arguments()
    logging.info(f"Start main application with configuration {args.config}")

    try:
        config_data = load_yaml_config(args.config)
        settings = AppSettings(**config_data)
    except Exception as e:
        logging.error(f"Error while loading the configuration: {e}")
    
    
    if not settings.file_configurations:
        logging.error("Keine passenden Konfigurationen gefunden. Abbruch.")
        return

    # Startet den entkoppelten Service
    generate_decks_and_packages(settings)


if __name__ == "__main__":
    run()
