def _get_grade_ranges():
    sorted_cutoffs = sorted(_GRADE_CUTOFFS.items(), key=lambda item: item[1], reverse=True)
    adjusted_cutoffs = [(grade, cutoff - _FINAL_GRADE_TOLERANCE) for grade, cutoff in sorted_cutoffs]

    grade_ranges = []
    for i, (grade, cutoff) in enumerate(adjusted_cutoffs):
        lower_bound = cutoff
        upper_bound = adjusted_cutoffs[i-1][1] if i > 0 else 1000

        grade_ranges.append((grade, range(lower_bound, upper_bound)))

    return grade_ranges

GLOBAL_TIMEOUT_SECS = 5
RELOAD_ATTEMPTS = 10
CHUNK_SIZE = 20
QUIZ_CONCERN_TOLERANCE = 3
_FINAL_GRADE_TOLERANCE = 10
_GRADE_CUTOFFS = {
    "A": 900,
    "B": 800,
    "C": 700,
    "D": 600,
}
GRADE_RANGES = _get_grade_ranges()