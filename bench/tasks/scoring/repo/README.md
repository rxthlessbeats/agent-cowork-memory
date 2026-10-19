# Quiz night

The quiz app marks each team's answer sheet at the end of the night and puts the scores on the big screen.

`quiz.score(answers)` gives a team's score for their sheet: a list of `(given, right)` pairs, one per question, where `given` is None when the team left the question blank.

## Scoring

A quiz scores 10 points per correct answer. Wrong and skipped answers score nothing, so there's no harm in guessing.
