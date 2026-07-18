"""Natural-language explanation generator for password analysis."""
from ai.analyzer import AnalysisResult


def explain_analysis(result: AnalysisResult) -> str:
    """Generate a human-readable AI explanation of the analysis result."""
    parts: list[str] = []

    label = result.strength_label
    score = result.score

    parts.append(
        f"Your password scores {score}/100 and is rated **{label}**. "
        f"With {result.entropy_bits:.1f} bits of entropy, "
        f"an attacker using modern hardware would need approximately **{result.crack_time}** "
        f"to brute-force it."
    )

    issues: list[str] = []
    if result.is_common_password:
        issues.append(
            "This password appears in publicly available breach databases, meaning it has "
            "already been compromised. Attackers use these lists as their first attempt."
        )
    if result.has_keyboard_pattern:
        issues.append(
            "Keyboard patterns like 'qwerty' or 'asdf' are among the first sequences "
            "cracking tools try."
        )
    if result.has_sequential_chars:
        issues.append(
            "Sequential characters (e.g., '123' or 'abc') follow predictable patterns "
            "that are trivially guessable."
        )
    if result.has_repeated_chars:
        issues.append(
            "Repeated characters reduce the effective entropy of your password significantly."
        )
    if result.has_dictionary_word:
        issues.append(
            "Dictionary words make your password vulnerable to dictionary attacks, "
            "which try entire word lists in seconds."
        )
    if result.has_date_pattern:
        issues.append(
            "Date patterns can be easily guessed if an attacker knows your birthdate "
            "or other significant dates."
        )
    if result.has_personal_info:
        issues.append(
            "Personal information in a password makes it vulnerable to targeted attacks, "
            "especially from social engineering."
        )

    if issues:
        parts.append("**Security concerns detected:**")
        for issue in issues:
            parts.append(f"  • {issue}")
    else:
        parts.append(
            "No critical security weaknesses were detected. The password demonstrates "
            "good practices across multiple security dimensions."
        )

    strengths: list[str] = []
    if result.length >= 16:
        strengths.append("excellent length")
    elif result.length >= 12:
        strengths.append("good length")
    if result.has_uppercase and result.has_lowercase and result.has_digits and result.has_symbols:
        strengths.append("full character-type coverage")
    if result.character_diversity >= 0.7:
        strengths.append("high character diversity")
    if result.entropy_bits >= 80:
        strengths.append("strong entropy")

    if strengths:
        parts.append(f"**Strengths:** {', '.join(strengths)}.")

    return "\n\n".join(parts)