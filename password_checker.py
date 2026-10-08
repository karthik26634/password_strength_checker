import argparse
import getpass
import string
import os
import re
import math


def load_common_passwords(filename="common_passwords.txt"):
    # user ichina path exist aithe adhi, lekapothe script unna folder lo vethuku
    path = filename
    if not os.path.exists(path):
        folder = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(folder, filename)

    common = set()
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                common.add(line.strip().lower())
    except FileNotFoundError:
        print("Warning: common passwords file not found, skipping that check")
    return common


def check_basic(password):
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Use at least 8 characters")

    if len(password) >= 12:
        score += 1
    else:
        feedback.append("12+ characters is even better")

    if any(ch.isupper() for ch in password):
        score += 1
    else:
        feedback.append("Add an uppercase letter")

    if any(ch.islower() for ch in password):
        score += 1
    else:
        feedback.append("Add a lowercase letter")

    if any(ch.isdigit() for ch in password):
        score += 1
    else:
        feedback.append("Add a digit")

    if any(ch in string.punctuation for ch in password):
        score += 1
    else:
        feedback.append("Add a symbol like ! @ # $")

    return score, feedback


def has_repeated(password):
    return re.search(r"(.)\1{2,}", password) is not None


def has_sequence(password, length=4):
    p = password.lower()
    for i in range(len(p) - length + 1):
        chunk = p[i:i + length]
        if not chunk.isalnum():
            continue
        ascending = all(ord(chunk[j + 1]) - ord(chunk[j]) == 1 for j in range(length - 1))
        descending = all(ord(chunk[j]) - ord(chunk[j + 1]) == 1 for j in range(length - 1))
        if ascending or descending:
            return True
    return False


def has_keyboard_pattern(password):
    patterns = ["qwerty", "asdf", "zxcv", "qazwsx", "1qaz", "poiuy"]
    p = password.lower()
    return any(pat in p for pat in patterns)


def check_patterns(password):
    penalty = 0
    feedback = []

    if has_repeated(password):
        penalty += 1
        feedback.append("Avoid repeating the same character (aaa, 111)")
    if has_sequence(password):
        penalty += 1
        feedback.append("Avoid sequences like abcd or 1234")
    if has_keyboard_pattern(password):
        penalty += 1
        feedback.append("Avoid keyboard patterns like qwerty or asdf")

    return penalty, feedback


LEET_TABLE = str.maketrans({
    "@": "a", "4": "a", "3": "e", "1": "i",
    "0": "o", "$": "s", "5": "s", "7": "t",
})


def is_leet_common(password, common):
    lower = password.lower()
    stripped = lower.rstrip(string.digits + string.punctuation)

    for candidate in (lower, stripped):
        if not candidate:
            continue
        normalized = candidate.translate(LEET_TABLE)
        if normalized in common:
            return True
    return False


def calculate_entropy(password):
    pool = 0
    if any(ch.islower() for ch in password):
        pool += 26
    if any(ch.isupper() for ch in password):
        pool += 26
    if any(ch.isdigit() for ch in password):
        pool += 10
    if any(ch in string.punctuation for ch in password):
        pool += len(string.punctuation)

    if pool == 0:
        return 0
    return len(password) * math.log2(pool)


def estimate_crack_time(entropy, guesses_per_sec=10_000_000_000):
    entropy = min(entropy, 200)
    seconds = (2 ** entropy) / 2 / guesses_per_sec

    if seconds < 1:
        return "instantly"

    units = [("years", 31536000), ("days", 86400), ("hours", 3600), ("minutes", 60)]
    for name, size in units:
        if seconds >= size:
            value = seconds / size
            if name == "years" and value >= 1_000_000:
                return "over a million years"
            return f"about {value:,.0f} {name}"
    return f"about {seconds:.0f} seconds"


def get_rating(score):
    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    else:
        return "Strong"


def analyze(password, common):
    """Oka password ni anni checks tho analyze chesi, results dictionary ga istundi."""
    result = {"password": password}

    if password.lower() in common:
        result["rating"] = "VERY WEAK"
        result["reason"] = "Commonly used password. Attackers try these first!"
        result["entropy"] = None
        result["feedback"] = []
        return result

    if is_leet_common(password, common):
        result["rating"] = "VERY WEAK"
        result["reason"] = "Common password with simple tricks (@ for a, 0 for o, extra digits)."
        result["entropy"] = None
        result["feedback"] = []
        return result

    score, feedback = check_basic(password)
    penalty, pattern_feedback = check_patterns(password)

    result["score"] = max(score - penalty, 0)
    result["rating"] = get_rating(result["score"])
    result["entropy"] = calculate_entropy(password)
    result["crack_time"] = estimate_crack_time(result["entropy"])
    result["has_patterns"] = penalty > 0
    result["feedback"] = feedback + pattern_feedback
    return result


def print_report(result):
    """Single password kosam full report."""
    print()
    if "reason" in result:
        print("Rating:", result["rating"])
        print(result["reason"])
    else:
        print("Score:", result["score"], "/ 6")
        print("Rating:", result["rating"])
        print(f"Entropy: {result['entropy']:.1f} bits")
        print("Estimated crack time:", result["crack_time"])
        if result["has_patterns"]:
            print("Note: patterns found, so real strength is lower than entropy shows")

    if result["feedback"]:
        print("Suggestions:")
        for tip in result["feedback"]:
            print("-", tip)


def check_file(path, common):
    """File lo prathi line ni check chesi, table laaga chupistundi."""
    counts = {}
    print(f"\n{'Password':<24}{'Rating':<12}{'Entropy'}")
    print("-" * 46)

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                pwd = line.strip()
                if not pwd:
                    continue
                result = analyze(pwd, common)
                rating = result["rating"]
                counts[rating] = counts.get(rating, 0) + 1

                entropy = f"{result['entropy']:.1f} bits" if result["entropy"] is not None else "-"
                print(f"{pwd:<24}{rating:<12}{entropy}")
    except FileNotFoundError:
        print(f"Error: file '{path}' not found")
        return

    print("\nSummary:")
    for rating, count in counts.items():
        print(f"  {rating}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Password strength checker")
    parser.add_argument("-f", "--file",
                        help="file with one password per line to check")
    parser.add_argument("-p", "--password",
                        help="check this password (note: stays in shell history, hidden prompt is safer)")
    parser.add_argument("-c", "--common", default="common_passwords.txt",
                        help="common passwords list file (default: common_passwords.txt)")
    args = parser.parse_args()

    common = load_common_passwords(args.common)

    if args.file:
        check_file(args.file, common)
    elif args.password:
        print_report(analyze(args.password, common))
    else:
        pwd = getpass.getpass("Enter password: ")
        print_report(analyze(pwd, common))


if __name__ == "__main__":
    main()