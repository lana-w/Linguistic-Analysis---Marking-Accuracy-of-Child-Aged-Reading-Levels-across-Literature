"""Creating a tree from a sentence using spacy"""
# Import required libraries
import spacy
from spacy import displacy
from pathlib import Path

# spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")

def dependency_diagram(sentence: str) -> None:
    """Takes in a sentence and returns its dependecies diagram.

    Text: The original word text.
    Lemma: The base form of the word.
    POS: The simple UPOS part-of-speech tag.
    Tag: The detailed part-of-speech tag.
    Dep: Syntactic dependency, i.e. the relation between tokens.
    Shape: The word shape – capitalization, punctuation, digits.
    is alpha: Is the token an alpha character?
    is stop: Is the token part of a stop list, i.e. the most common words of the language?
    """
    doc = nlp(sentence)
    for token in doc:
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
              token.shape_, token.is_alpha, token.is_stop)
    displacy.serve(doc, style='dep')