from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HIST_ROOT = PROJECT_ROOT / "data" / "plots" / "historical"

EXPECTED_WEEKS = range(1, 10)   # adjust upward later as needed
EXPECTED_FUNCTIONS = range(1, 9)

def main() -> None:
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Historical plots root: {HIST_ROOT}\n")

    if not HIST_ROOT.exists():
        print("Historical plots folder does not exist.")
        return

    missing_any = False

    for week in EXPECTED_WEEKS:
        week_dir = HIST_ROOT / f"week_{week:02d}"
        print(f"Week {week:02d}:")
        if not week_dir.exists():
            print("  Missing entire folder")
            missing_any = True
            print()
            continue

        found = 0
        for func in EXPECTED_FUNCTIONS:
            fname = week_dir / f"function_{func}_week{week:02d}.png"
            if fname.exists():
                print(f"  OK   function_{func}_week{week:02d}.png")
                found += 1
            else:
                print(f"  MISS function_{func}_week{week:02d}.png")
                missing_any = True

        print(f"  Summary: {found}/8 found\n")

    if missing_any:
        print("Audit complete: some plots are missing.")
    else:
        print("Audit complete: all expected plots are present.")

if __name__ == "__main__":
    main()