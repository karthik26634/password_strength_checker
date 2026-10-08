# Password Strength Checker

A Python command-line tool that analyzes password strength using entropy, pattern detection, and common password checks. Built as a learning project.

## Features

- Length and character type scoring (uppercase, lowercase, digits, symbols)
- Common password list check
- Leet-speak detection (`P@ssw0rd`, `passw0rd`)
- Pattern detection using regex: repeated characters, sequences (`abcd`, `1234`), keyboard patterns (`qwerty`)
- Entropy calculation and estimated crack time
- Command line options with `argparse`
- Hidden password prompt using `getpass`

## How it works

1. **Common password check:** The password is compared against a list in `common_passwords.txt`. It is also normalized (for example `@` becomes `a`, `0` becomes `o`) and checked again, so simple tricks do not fool it.
2. **Scoring:** Up to 6 points for length (8+, 12+) and character types. Patterns reduce the score.
3. **Pattern detection:** Regex finds repeated characters. Other checks find sequences and keyboard patterns.
4. **Entropy:** `entropy = length x log2(character pool size)`. Higher entropy means more guesses are needed.
5. **Crack time:** Estimated at 10 billion guesses per second, which is a worst-case scenario for fast hashes.

## Requirements

- Python 3
- No external libraries

## Usage

Hidden prompt (recommended for real passwords):

```
python password_checker.py
```

Check one password directly (test passwords only, it stays in shell history):

```
python password_checker.py -p "Xk9#mPq2!vLw"
```

Check many passwords from a file (one per line):

```
python password_checker.py -f test_passwords.txt
```

Use a custom common passwords list:

```
python password_checker.py -c my_list.txt
```

## Sample output

```
Score: 6 / 6
Rating: Strong
Entropy: 78.7 bits
Estimated crack time: about 754,567 years
```

## Limitations

- The crack time is a rough worst-case estimate. Real time depends on the hashing algorithm used.
- The included common passwords list is small (about 40 entries). Use a larger list such as SecLists for better results.
- Leet-speak detection only handles common substitutions, and extra characters only at the end of a word.

## Future improvements

- Breach check using an online API
- Substring matching for common words inside longer passwords
- GUI version

## Disclaimer

For educational purposes only. Do not enter your real passwords into any tool you do not trust.
