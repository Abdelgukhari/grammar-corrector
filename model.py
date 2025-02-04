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
            if word.lower() in self.protected_words:
                corrected_words.append(word)  # Keep pronouns unchanged
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
            max_length=len(text.split()) + 5,
            num_return_sequences=1,
            repetition_penalty=2.5,
            no_repeat_ngram_size=3,
        )
        corrected_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return corrected_text

    def remove_repeated_words(self, text):
        """Ensures proper sentence structure by removing unnecessary repeated words."""
        words = text.split()
        cleaned_text = []
        prev_word = ""

        for word in words:
            if word != prev_word:
                cleaned_text.append(word)
            prev_word = word

        # Fix spacing issues around punctuation
        fixed_text = " ".join(cleaned_text)
        fixed_text = fixed_text.replace(" ,", ",").replace(" .", ".").replace(" ?", "?").replace(" !", "!")
        return fixed_text

    def correct_text(self, text):
        """Applies spelling correction first, then grammar correction, and removes repeated words."""
        original_text = text
        corrected_spelling = self.correct_spelling(text)
        corrected_grammar = self.correct_grammar(corrected_spelling)
        cleaned_text = self.remove_repeated_words(corrected_grammar)

        return {
            "original_text": original_text,
            "corrected_text": cleaned_text,
            "highlighted_mistakes": self.highlight_changes(original_text, cleaned_text),
            "learning_insights": self.explain_corrections(original_text, cleaned_text)
        }

    def highlight_changes(self, original, corrected):
        """Highlights corrected words to help users understand mistakes."""
        original_words = original.split()
        corrected_words = corrected.split()
        diff = difflib.ndiff(original_words, corrected_words)

        changes = []
        for word in diff:
            if word.startswith("- "):
                changes.append(f"<del style='color: red;'>{word[2:]}</del>")
            elif word.startswith("+ "):
                changes.append(f" → <ins style='color: green;'>{word[2:]}</ins>")
        return " ".join(changes)

    def explain_corrections(self, original, corrected):
        """Provides detailed feedback on corrections."""
        explanations = {}
        original_words = original.split()
        corrected_words = corrected.split()
        diff = difflib.ndiff(original_words, corrected_words)

        for word in diff:
            if word.startswith("- "):
                explanations[word[2:]] = f"❌ '{word[2:]}' is incorrect."
            elif word.startswith("+ "):
                incorrect_word = list(explanations.keys())[-1] if explanations else None
                if incorrect_word:
                    explanations[incorrect_word] += f" ✅ '{word[2:]}' is the correct form."
                else:
                    explanations[word[2:]] = f"✅ '{word[2:]}' was added."

        return list(explanations.values())  # Convert back to a list for JSON response
