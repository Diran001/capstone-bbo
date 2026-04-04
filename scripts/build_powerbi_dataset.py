import os
import json
import ast
import pandas as pd

BASE_DIR = r"C:\Users\Diran\Coursework\CapStone_BBO_git"
LOG_DIR = os.path.join(BASE_DIR, "data", "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "powerbi")
os.makedirs(OUTPUT_DIR, exist_ok=True)

rows = []
bad_files = []


def load_flexible(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    if not raw:
        raise ValueError("Empty file")

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    try:
        return ast.literal_eval(raw)
    except Exception as e:
        raise ValueError(f"Could not parse as JSON or Python literal: {e}") from e


def extract_week(data, filename):
    if isinstance(data, dict):
        if "week_processed" in data:
            return data["week_processed"]
        if "run_week" in data:
            return data["run_week"]
    try:
        return int(filename.split("week_")[1].split("_")[0])
    except Exception:
        return None


for file in sorted(os.listdir(LOG_DIR)):
    if not file.endswith(".json"):
        continue

    path = os.path.join(LOG_DIR, file)

    try:
        data = load_flexible(path)
        week = extract_week(data, file)

        if not isinstance(data, dict):
            raise ValueError("Top-level object is not a dictionary")

        proposals = data.get("proposals", [])
        summary = data.get("summary", {})
        method = data.get("method")
        settings = data.get("settings", {})

        for p in proposals:
            diag = p.get("diagnostics", {}) if isinstance(p, dict) else {}

            func_num = p.get("function") if isinstance(p, dict) else None
            func = f"F{func_num}" if func_num is not None else None

            summary_block = summary.get(str(func_num), {}) if isinstance(summary, dict) and func_num is not None else {}

            row = {
                "Week": week,
                "Function": func,
                "CurrentBest": p.get("current_best") if isinstance(p, dict) else None,
                "Evaluations": p.get("n_evaluations") if isinstance(p, dict) else None,
                "Description": p.get("description") if isinstance(p, dict) else None,
                "Acquisition": diag.get("acquisition") if isinstance(diag, dict) else None,
                "xi": diag.get("xi") if isinstance(diag, dict) else settings.get("ei_xi") or settings.get("default_ei_xi"),
                "kappa": diag.get("kappa") if isinstance(diag, dict) else settings.get("default_ucb_kappa"),
                "BestScore": diag.get("best_score") if isinstance(diag, dict) else None,
                "PredMeanScaled": diag.get("pred_mean_scaled") if isinstance(diag, dict) else None,
                "PredStdScaled": diag.get("pred_std_scaled") if isinstance(diag, dict) else None,
                "BestScaled": diag.get("y_best_scaled") if isinstance(diag, dict) else None,
                "BestOriginal": diag.get("y_best_original") if isinstance(diag, dict) else None,
                "CandidatePool": diag.get("n_candidates") if isinstance(diag, dict) else settings.get("n_candidates") or settings.get("default_n_candidates"),
                "Kernel": diag.get("kernel") if isinstance(diag, dict) else None,
                "Improved": summary_block.get("improved") if isinstance(summary_block, dict) else None,
                "OldBest": summary_block.get("old_best") if isinstance(summary_block, dict) else None,
                "NewBest": summary_block.get("new_best") if isinstance(summary_block, dict) else None,
                "NewValue": summary_block.get("new_value") if isinstance(summary_block, dict) else None,
                "Method": method,
            }

            input_array = p.get("input_array") if isinstance(p, dict) else None
            if isinstance(input_array, (list, tuple)):
                for i, val in enumerate(input_array, start=1):
                    row[f"Input_{i}"] = val

            rows.append(row)

        print(f"OK  {file}")

    except Exception as e:
        bad_files.append({"File": file, "Error": str(e)})
        print(f"BAD {file} -> {e}")

df = pd.DataFrame(rows)

if not df.empty:
    df = df.sort_values(by=["Week", "Function"])

    # Add week-on-week delta within each function
    if "CurrentBest" in df.columns:
        df["PrevCurrentBest"] = df.groupby("Function")["CurrentBest"].shift(1)
        df["DeltaVsPrevWeek"] = df["CurrentBest"] - df["PrevCurrentBest"]

dataset_path = os.path.join(OUTPUT_DIR, "bbo_powerbi_dataset.csv")
badfiles_path = os.path.join(OUTPUT_DIR, "bbo_bad_files.csv")

df.to_csv(dataset_path, index=False)
pd.DataFrame(bad_files).to_csv(badfiles_path, index=False)

print("\nDone.")
print(f"Dataset:   {dataset_path}")
print(f"Bad files: {badfiles_path}")