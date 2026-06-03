import hashlib
from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel, Field, FilePath, DirectoryPath, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DATEI = Path(__file__).resolve()  # config.py
ORDNER_APP = DATEI.parent         # src/generator_app
ORDNER_SRC = ORDNER_APP.parent    # src/
PACKAGE_ROOT = ORDNER_SRC.parent  # generator-app/


class AnkiModelConfig(BaseModel):
    model_id: int = Field(..., gt=0)
    model_name: str = Field(..., min_length=3)
    fields: list[str] = Field(..., min_length=1)
    template_dir: DirectoryPath
    template_name: str
    template_lang: str = Field(default="de")
    is_cloze: bool = True


class MappingConfig(BaseModel):
    model_key: str
    output_filename: str = Field(..., min_length=5)
    generate_audio: bool = Field(default=False)
    edge_tts_voice: str = Field(default="es-ES-AlvaroNeural")


class InputFileConfig(BaseModel):
    model_key: str
    file_name: FilePath
    deck_name: str
    deck_id: int
    generate_audio: bool
    edge_tts_voice: str
    model_details: AnkiModelConfig | None = None

    # Properties für den HTML/CSS-Zugriff (bleiben exakt gleich)
    @property
    def model_id(self) -> int: return self.model_details.model_id
    @property
    def model_name(self) -> str: return self.model_details.model_name
    @property
    def fields(self) -> list[str]: return self.model_details.fields
    @property
    def is_cloze(self) -> bool: return self.model_details.is_cloze


    @property
    def _template_path(self) -> Path:
        return self.model_details.template_dir / self.model_details.template_name / self.model_details.template_lang

    @property
    def css_content(self) -> str:
        return (self._template_path / "style.css").read_text(encoding="utf-8")

    @property
    def qfmt_content(self) -> str:
        return (self._template_path / "qfmt.html").read_text(encoding="utf-8")

    @property
    def afmt_content(self) -> str:
        return (self._template_path / "afmt.html").read_text(encoding="utf-8")


class AppSettings(BaseSettings):
    anki_models: dict[str, AnkiModelConfig]
    source_mappings: dict[str, MappingConfig]
    # Wird jetzt standardmäßig leer erzeugt und dynamisch befüllt
    file_configurations: dict[str,list[InputFileConfig]] = Field(default_factory=dict)

    model_config = SettingsConfigDict(extra="ignore")

    @model_validator(mode="after")
    def discover_and_resolve_files(self) -> "AppSettings":
        """Scannt das data/-Verzeichnis dynamisch über alle Sprachen und Ordner."""
        data_root = PACKAGE_ROOT / "data"
        
        if not data_root.exists():
            return self

        # 1. Alle .txt-Dateien im gesamten data/-Ordner rekursiv finden
        for txt_file in data_root.rglob("*.txt"):
            
            # Pfad-Struktur relativ zum data/-Ordner aufteilen
            # Beispiel: ['spanish', 'pareto_sentences', '01_rules.txt']
            relative_parts = txt_file.relative_to(data_root).parts
            
            # Wenn die Datei nicht tief genug liegt (mindestens Sprache/Kategorie/Datei), überspringen
            if len(relative_parts) < 3:
                continue
                
            # Dynamische Erkennung der Hierarchie aus den Ordnernamen:
            language_folder = relative_parts[0]  # z. B. 'spanish'

            if language_folder not in self.source_mappings:
                # Ordner ohne Mapping ignorieren wir sicherheitshalber oder loggen es
                continue

            mapping:MappingConfig = self.source_mappings[language_folder]

            model_key = mapping.model_key

            category_folder = relative_parts[1]  # z. B. 'pareto_sentences'
            
            # Wunderschöne Namen für Anki formatieren (Unterstriche weg, Anfangsbuchstaben groß)
            language_name = language_folder.replace("_", " ").title()  # 'spanish' -> 'Spanish'
            category_name = category_folder.replace("_", " ").title()  # 'pareto_sentences' -> 'Pareto Sentences'
            clean_file_name = txt_file.stem.replace("_", " ").title()   # '01_rules' -> '01 Rules'
            
            # Der hardcodierte String "Spanisch" ist jetzt komplett durch {language_name} ersetzt!
            full_deck_name = f"{language_name}::{category_name}::{clean_file_name}"
            
            # Feste, reproduzierbare Deck-ID über den relativen Pfad berechnen
            relative_path_str = str(txt_file.relative_to(PACKAGE_ROOT))
            hash_object = hashlib.sha256(relative_path_str.encode("utf-8"))
            deck_id = int(hash_object.hexdigest()[:8], 16)

            

            if model_key not in self.anki_models:
                raise ValueError(f"Zentrales Modell '{model_key}' fehlt in der config.yaml!")

            # Dynamischen Eintrag erzeugen und anhängen
            config_entry = InputFileConfig(
                model_key=model_key,
                file_name=txt_file,
                deck_name=full_deck_name,
                deck_id=deck_id,
                edge_tts_voice=mapping.edge_tts_voice,
                generate_audio = mapping.generate_audio,
                model_details=self.anki_models[model_key],
            )

            # if language_folder in self.file_configurations:
            #     self.file_configurations[language_folder].append(config_entry)
            # else:
            #     self.file_configurations[language_folder] = [config_entry]
            self.file_configurations.setdefault(language_folder,[]).append(config_entry)
            
        return self



def load_yaml_config(config_filename:str = "config.yaml") -> dict[str, Any]:
    yaml_path = PACKAGE_ROOT / "config.yaml"

    if not yaml_path.exists() and not config_filename == "config.yaml":
        yaml_path = PACKAGE_ROOT / "configs" / config_filename

    if not yaml_path.exists():
        raise FileNotFoundError(
            f"Kritischer Fehler: Konfiguration '{config_filename}' wurde weder im Hauptverzeichnis "
            f"noch unter {PACKAGE_ROOT / 'configs/'} gefunden!"
        )
    
    with open(yaml_path, mode="r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

