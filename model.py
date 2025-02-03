from transformers import T5ForConditionalGeneration, T5Tokenizer
from symspellpy import SymSpell, Verbosity
import pkg_resources
import difflib

class SpellGrammarChecker:
    def __init__(self):
        # Load Pre-trained Grammar Correction Model
        model_name = "vennify/t5-base-grammar-correction"
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)

        # Load SymSpell for Spelling Correction
        self.symspell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        dictionary_path = pkg_resources.resource_filename(
            "symspellpy", "frequency_dictionary_en_82_765.txt"
        )
        self.symspell.load_dictionary(dictionary_path, term_index=0, count_index=1)

        # List of personal pronouns that should NOT be modified
        self.protected_words = {"she", "he", "they", "i", "we", "you"}

    def correct_spelling(self, text):
        """Fixes spelling errors using SymSpell."""
        words = text.split()
        corrected_words = []
        for word in words:
            if word.lower() in self.protected_words:  # Do not change protected words
                corrected_words.append(word)
            else:
                suggestions = self.symspell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2)
                corrected_word = suggestions[0].term if suggestions else word
                corrected_words.append(corrected_word)
        return " ".join(corrected_words)

    def correct_grammar(self, text):
        """Fixes grammar errors using the T5 model while preserving sentence meaning."""
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model.generate(
            **inputs, 
            max_length=len(text.split()) + 5,  # Restrict output length
            num_return_sequences=1,  # Ensure only one output is generated
            repetition_penalty=2.5,  # Prevents repeating words
            no_repeat_ngram_size=3,  # Avoids generating duplicate phrases
        )
        corrected_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Preserve protected words (e.g., "She", "He", "They") to prevent bad substitutions
        original_words = text.split()
        corrected_words = corrected_text.split()

        for i, word in enumerate(original_words):
            if word.lower() in self.protected_words and i < len(corrected_words):
                corrected_words[i] = word  # Keep the original pronoun

        return " ".join(corrected_words)

    def correct_text(self, text):
        """Applies spelling correction first, then grammar correction."""
        original_text = text
        corrected_spelling = self.correct_spelling(text)
        corrected_text = self.correct_grammar(corrected_spelling)

        return {
            "original_text": original_text,
            "corrected_text": corrected_text,
            "highlighted_mistakes": self.highlight_changes(original_text, corrected_text),
            "learning_insights": self.explain_corrections(original_text, corrected_text)
        }

    def highlight_changes(self, original, corrected):
        """Highlights corrected words with proper spacing and formatting."""
        original_words = original.split()
        corrected_words = corrected.split()
        diff = difflib.ndiff(original_words, corrected_words)

        changes = []
        for word in diff:
            if word.startswith("- "):  # Incorrect word (removed)
                changes.append(f"<del style='color: red;'>{word[2:]}</del>")
            elif word.startswith("+ "):  # Corrected word (added)
                changes.append(f" → <ins style='color: green;'>{word[2:]}</ins>")
        return " ".join(changes)

    def explain_corrections(self, original, corrected):
        """Provides clear explanations for corrections, grouping related words."""
        explanations = {}
        original_words = original.split()
        corrected_words = corrected.split()
        diff = difflib.ndiff(original_words, corrected_words)

        for word in diff:
            if word.startswith("- "):  # Incorrect word
                explanations[word[2:]] = f"❌ '{word[2:]}' is incorrect."
            elif word.startswith("+ "):  # Corrected word
                incorrect_word = list(explanations.keys())[-1] if explanations else None
                if incorrect_word:
                    explanations[incorrect_word] += f" ✅ '{word[2:]}' is the correct form."
                else:
                    explanations[word[2:]] = f"✅ '{word[2:]}' was added."

        return list(explanations.values())  # Convert back to a list for JSON response
