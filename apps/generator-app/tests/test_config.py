import pytest
from pydantic import ValidationError
from generator_app.config import MappingConfig, InputFileConfig

def test_mapping_config_valid():
    """Testet, ob ein gültiges Ordner-Mapping akzeptiert wird."""
    mapping = MappingConfig(model_key="test_model", output_filename="spanisch.apkg")
    assert mapping.model_key == "test_model"
    assert mapping.output_filename == "spanisch.apkg"

def test_mapping_config_invalid_filename():
    """Testet, ob ein zu kurzer Dateiname von Pydantic blockiert wird."""
    with pytest.raises(ValidationError):
        # Der Name ist kürzer als min_length=5, muss einen Fehler werfen!
        MappingConfig(model_key="test_model", output_filename=".apk")

def test_input_file_config_invalid_deck_id():
    """Testet, ob eine negative Deck-ID sauber blockiert wird."""
    with pytest.raises(ValidationError):
        # deck_id muss laut Field(..., gt=0) positiv sein!
        InputFileConfig(
            model_key="test_model",
            file_name="apps/generator-app/config.yaml", # irgendeine existierende Datei
            deck_name="Test Deck",
            deck_id=-100,
            output_filename="test.apkg"
        )
