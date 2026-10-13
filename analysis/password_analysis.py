#!/usr/bin/env python3
"""Calculate password search-space size and theoretical search duration.

This is a calculator only: it does not capture packets or test passwords.
Includes preset speeds for common tools (Aircrack-ng, Hashcat, Online attacks).
"""

from math import ceil


def format_duration(seconds: float) -> str:
    """Return a readable duration for non-negative seconds."""
    seconds = max(0, float(seconds))
    if seconds == 0:
        return "0 second(s)"

    # If the time is astronomical (> 100,000 years), use scientific notation
    years, rem_year = divmod(seconds, 31_536_000)
    if years > 100_000:
        return f"{years:.2e} year(s)"

    days, rem = divmod(rem_year, 86_400)
    hours, rem = divmod(rem, 3_600)
    minutes, secs = divmod(rem, 60)

    parts = []
    if years >= 1:
        parts.append(f"{int(years):,} year(s)")
    if days >= 1:
        parts.append(f"{int(days)} day(s)")
    if hours >= 1:
        parts.append(f"{int(hours)} hour(s)")
    if minutes >= 1:
        parts.append(f"{int(minutes)} minute(s)")
    if secs >= 1 or not parts:
        parts.append(f"{int(secs)} second(s)")

    return ", ".join(parts)


def get_cracking_rate() -> tuple[str, float]:
    """Prompt user to choose a cracking tool or enter custom speed."""
    presets = {
        "1": ("Online attack (against live router/AP)", 2.0),
        "2": ("Aircrack-ng (CPU offline cracking)", 1_250.0),
        "3": ("Hashcat (GPU offline cracking - e.g., RTX GPU)", 350_000.0),
        "4": ("Custom / Manual speed", None),
    }

    print("\nSelect Cracking Method:")
    print("  [1] Online Attack (Direct against AP/Router)  -> Default: 2 checks/sec")
    print("  [2] Aircrack-ng (CPU Offline Cracking)       -> Default: 1,250 checks/sec")
    print("  [3] Hashcat (GPU Offline Cracking)           -> Default: 350,000 checks/sec")
    print("  [4] Custom (Enter your own measured rate)")

    choice = input("\nChoose method [1-4] : ").strip() or "2"

    if choice in ("1", "2", "3"):
        name, default_rate = presets[choice]
        override = input(f"Enter speed for {name} [Press Enter for default {default_rate:,.0f} checks/s]: ").strip()
        rate = float(override) if override else default_rate
        return name, rate
    else:
        name = "Custom / User-defined"
        rate = float(input("Enter measured candidate checks per second: ").strip())
        return name, rate


def main():
    print("=" * 60)
    print("Password Search-Space & Cracking Time Calculator")
    print("=" * 60)
    print("\nCommon Alphabet Sizes:")
    print("  - Digits only (0-9): 10")
    print("  - Lowercase letters (a-z): 26")
    print("  - Uppercase + Digits (A-Z, 0-9): 36")
    print("  - Full Alphanumeric (a-z, A-Z, 0-9): 62")
    print("  - Full ASCII (all printable keyboard chars): 95\n")

    # 1. Alphabet Size
    alpha_input = input("Alphabet size: ").strip() or "36"
    alphabet_size = int(alpha_input)

    # 2. Number of unknown positions
    pos_input = input("Number of unknown positions/characters (e.g. 4, 8): ").strip()
    unknown_positions = int(pos_input)

    # 3. Cracking method and rate
    method_name, rate = get_cracking_rate()

    # Calculations
    candidates = alphabet_size ** unknown_positions
    full_seconds = candidates / rate
    avg_seconds = (candidates / 2) / rate

    print("\n" + "=" * 60)
    print("Result Summary")
    print("=" * 60)
    print(f"Cracking Method:       {method_name}")
    print(f"Testing Speed:         {rate:,.2f} candidates/second")
    print(f"Total Candidates:      {candidates:,}")
    print(f"Estimated Worst-Case:  {format_duration(full_seconds)}")
    print(f"Estimated Average:     {format_duration(avg_seconds)}")
    print("=" * 60)
    print("Note: Theoretical estimate assuming continuous, constant search speed.")


if __name__ == "__main__":
    main()
