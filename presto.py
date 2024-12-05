import re
import unicodedata

def segment_words(sentence):
    """
    Segmente une phrase en mots en tenant compte des caractères spéciaux et combinaisons spécifiques.
    """
    words = []
    current_word = ""
    i = 0
    while i < len(sentence):
        char = sentence[i]
        # Détection de combinaisons spécifiques comme ";)" ou ":)"
        if i + 1 < len(sentence) and char in ";:" and sentence[i + 1] == ")":
            if current_word:
                words.append(current_word)
                current_word = ""
            words.append(char + sentence[i + 1])  # Ajouter ";)" ou ":)"
            i += 2
            continue

        # Gestion des guillemets ou ponctuations séparées
        if char in ("'", '"', ".", "!", "?", ",", "(", ")", ";", ":"):
            if current_word:
                words.append(current_word)
                current_word = ""
            words.append(char)  # Traiter ponctuation comme un mot séparé
        elif char.isalnum() or unicodedata.category(char).startswith("M"):  # Lettres, chiffres, caractères combinés
            current_word += char
        else:
            if current_word:
                words.append(current_word)
                current_word = ""
            if not char.isspace():
                words.append(char)
        i += 1

    if current_word:  # Ajouter le dernier mot si nécessaire
        words.append(current_word)
    return words


def parse_presto_labels(sentence, target):
    words = segment_words(sentence)
    print(f"Segmented words: {words}")

    # Extraire la tâche principale
    task = target.split("(")[0].strip()

    # Initialisation des labels
    labels = [0] * len(words)

    def label_words(value, label, labels, words):
        value_words = segment_words(value)
        print(f"Labeling {value_words} with {label}")
        for i in range(len(words) - len(value_words) + 1):
            if words[i:i + len(value_words)] == value_words:
                for j in range(len(value_words)):
                    labels[i + j] = label
                print(f"Labeled: {words[i:i + len(value_words)]} at indices {i}-{i + len(value_words) - 1}")
                return
        print(f"No match for {value_words} in {words}")

    def process_nested(content, parent_label=None):
        while "«" in content and "»" in content:
            start = content.find("«")
            end = content.find("»", start)
            if start == -1 or end == -1:
                break

            label = content[:start].strip().split()[-1]
            value = content[start + 1:end].strip()

            full_label = f"{parent_label}__{label}" if parent_label else label
            print(f"Labeling '{value}' with '{full_label}' (parent: {parent_label})")

            label_words(value, full_label, labels, words)

            content = content[end + 1:].strip()

        nested_start = content.find("(")
        nested_end = content.rfind(")")
        if nested_start != -1 and nested_end != -1 and nested_end > nested_start:
            nested_content = content[nested_start + 1:nested_end].strip()
            process_nested(nested_content, parent_label=label)

    nested_content_start = target.find("(")
    nested_content_end = target.rfind(")")
    if nested_content_start != -1 and nested_content_end != -1 and nested_content_end > nested_content_start:
        nested_content = target[nested_content_start + 1:nested_content_end].strip()
        process_nested(nested_content)

    return {
        "sentence": sentence,
        "words": words,
        "labels": labels,
        "task": task,
    }
