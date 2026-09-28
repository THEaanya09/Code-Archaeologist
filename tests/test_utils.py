from app.utils import lexical_score, tokenize


def test_tokenize_removes_generic_words():
    assert "why" not in tokenize("Why did Flask do this?")
    assert "flask" not in tokenize("Why did Flask do this?")


def test_relevant_question_scores_positive():
    score = lexical_score(
        "Why did Flask remove flask.ext import namespace?",
        "The flask.ext namespace was deprecated and new imports had mostly stopped.",
    )
    assert score >= 0.5


def test_unrelated_question_scores_zero():
    score = lexical_score(
        "Why did Flask switch from PostgreSQL to MongoDB?",
        "The flask.ext namespace was deprecated and removed in 1.0.",
    )
    assert score == 0.0
