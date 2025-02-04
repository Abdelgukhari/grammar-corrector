import unittest
from model import SpellGrammarChecker

class TestSpellGrammarChecker(unittest.TestCase):
    def setUp(self):
        """Initialize the spell and grammar checker before each test."""
        self.checker = SpellGrammarChecker()

    def test_spell_correction(self):
        """Test spelling correction only."""
        text = "Ths is a smple sentnce."
        expected = "This is a simple sentence."
        corrected = self.checker.correct_spelling(text)
        self.assertEqual(corrected, expected)

    def test_grammar_correction(self):
        """Test grammar correction only."""
        text = "She go to school every day."
        expected = "She goes to school every day."
        corrected = self.checker.correct_grammar(text)
        self.assertEqual(corrected, expected)

    def test_full_correction(self):
        """Test spelling and grammar correction together."""
        text = "She go to scool evryday."
        expected = "She goes to school every day."
        corrected = self.checker.correct_text(text)["corrected_text"]
        self.assertEqual(corrected, expected)

    def test_remove_repeated_words(self):
        """Ensure repeated words are removed correctly."""
        text = "They they saw the evidance."
        expected = "They saw the evidence."
        corrected = self.checker.remove_repeated_words(text)
        self.assertEqual(corrected, expected)

    def test_highlighted_mistakes(self):
        """Test if mistakes are correctly highlighted."""
        text = "He dont like pizza."
        corrected_text = self.checker.correct_text(text)
        self.assertIn("<del style='color: red;'>dont</del>", corrected_text["highlighted_mistakes"])
        self.assertIn("<ins style='color: green;'>doesn't</ins>", corrected_text["highlighted_mistakes"])

if __name__ == '__main__':
    unittest.main()
