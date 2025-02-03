from flask import Flask, request, jsonify, render_template
from model import SpellGrammarChecker

app = Flask(__name__)
checker = SpellGrammarChecker()
mistake_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/correct-text', methods=['POST'])
def correct_text_api():
    """API endpoint to correct text and provide insights."""
    data = request.get_json()
    text = data.get('text', '')
    correction = checker.correct_text(text)

    # Count mistakes
    mistake_count = text.count(" ") - correction["corrected_text"].count(" ")
    mistake_history.append(mistake_count)

    return jsonify({
        "original_text": correction["original_text"],
        "corrected_text": correction["corrected_text"],
        "highlighted_mistakes": correction["highlighted_mistakes"],
        "learning_insights": correction["learning_insights"],
        "mistakes_made": mistake_count,
        "total_mistakes": sum(mistake_history)
    })

if __name__ == "__main__":
    app.run(debug=True)
