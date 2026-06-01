# Anki Deck Generator

## Who is this repository intended for?
Anyone who wants to learn a new language and likes to use Anki as a tool for it. The project is designed for generating Anki packages (*.apkg-files), which can contain multiple decks with different sublevels to learn a new language.

After generating a deck, you can import it into your Anki App on you Desktop or on your Phone.

This repository provides a standard design template for Cloze Anki Cards (cards which allow user input).

You don't have to be a Python expert to generate a deck. You can generate new decks with own designs without even changing a single line of code.

#+ How to run the code?

First, make sure that ```uv``` (ultraviolett) is installed on your system to manage dependencies and virtual environments.

Then open a terminal/console in the root directory of the project (```/anki-deck-generator```)

```bash
uv sync
```

After the dependencies are installed in your new created virtual environment, you can run the code from the root directory:

```bash
uv run --package generator-app start-app
```

## Understanding the project configuration
Well, first of all, the question is: What do you want to change?

In the standard configuration, there will generated an APKG-File with a german card design to learn spanish words with clozure cards.

To understand the project configuration you have to look at the ```config.yaml```-File in ```/anki-deck-generator/apps/generator-app``` which contains two major blocks:

```yaml
anki_models:
  cloze_spanish_standard:
    model_id: 876543210
    model_name: "CLOZE CARD SPANISH MULTI STRUCTURE"
    fields: ["main_topic", "cloze_test", "translation", "hint", "extra","audio"]
    template_dir: "apps/generator-app/templates"
    template_name: "cloze_card"
    is_cloze: true
```

The first block ***anki_models*** contains the following informations:

***<cloze_spanish_standard>***: A ***dynamic key*** to serve as a reference in the ***source_mappings block***

***model_id:*** The id of your Anki Model

***model_name:*** The name of your Anki Model

***fields:*** A list of your data columns which also happen to be the dynamic fields of your anki cards, so the field names should also the same names like in your HTML-Templates for your cards.

***template_dir:*** This is the folder where your specific card design ist distributed over three files. One HTML-File for The Question-Package
IMPORTANT: There is a naming convention for the template files:
+ ***<enter_your_template-name_here>***_afmt.html
+ ***<enter_your_template-name_here>***_qfmt.html
+ ***<enter_your_template-name_here>***.csss

***template_name***: The actual template name of your templates, also used in the files of the template_dir

***is_cloze***: If your card design is a anki close test, if so you tell Anki that you want the card type CLOZE, which means there can be user input

```yaml
source_mappings:
  spanish:
    model_key: "cloze_spanish_standard"
    output_filename: "Spanisch_Pareto_System.apkg"
    generate_audio: true
    edge_tts_voice: "es-ES-AlvaroNeural"
```
***source_mappings:*** the block name

***spanish (dynamic key)***: The name of your main data directory inside ```/anki-deck-generator/apps/generator-app/data``` directory. The folders inside your main data directory (e.g. spanish) contain subdecks which then contain file_names for your data. This is where your actually data is.\
For example if your main folder inside ```/data``` is ```spanish```, then there is a subfolder called ```01_pareto_sentences``` with a file ```00_the_30_pareto_sentences.txt```. The Code will then generate a subdeck with the name ***Spanish:01Pareto Sentences:00The 30 Pareto Sentences***
So your directory and filenames define your Subdeck-Names.

***model_key:***

***output_filename:***

***generate_audio:***

***edge_tts_voice:***

## Example: Creating your own APKG with own files
### Assuming you are a native English speaker who wants to learn French using cloze tests...