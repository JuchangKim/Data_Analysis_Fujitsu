from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DATA_PATH = Path(__file__).resolve().with_name("Task Data_ Server Down Data.xlsx")
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

MONTH_ORDER = ["July", "August", "September", "October", "November", "December"]


def load_fail_logs(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Fail Logs")
    df = df.dropna(how="all").copy()

    df["Asset ID"] = pd.to_numeric(df["Asset ID"], errors="coerce")
    df["Downtime (Min)"] = pd.to_numeric(df["Downtime (Min)"], errors="coerce")
    df["Fail Date"] = pd.to_datetime(df["Fail Date"], errors="coerce")
    df["Office"] = df["Office"].astype(str).str.strip()
    df["Event Notes"] = df["Event Notes"].fillna("Unknown").astype(str).str.strip()
    df["Fail Month"] = df["Fail Month"].astype(str).str.strip()

    df = df.dropna(subset=["Asset ID", "Downtime (Min)", "Event Notes"]).copy()
    return df


def office_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("Office")
        .agg(
            failures=("Asset ID", "count"),
            total_downtime_minutes=("Downtime (Min)", "sum"),
            average_downtime_minutes=("Downtime (Min)", "mean"),
        )
        .sort_values(["total_downtime_minutes", "failures"], ascending=[False, False])
        .reset_index()
    )
    return summary


def cause_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("Event Notes")
        .agg(
            failures=("Asset ID", "count"),
            total_downtime_minutes=("Downtime (Min)", "sum"),
            average_downtime_minutes=("Downtime (Min)", "mean"),
        )
        .sort_values(["total_downtime_minutes", "failures"], ascending=[False, False])
        .reset_index()
    )
    return summary


def month_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("Fail Month")
        .agg(
            failures=("Asset ID", "count"),
            total_downtime_minutes=("Downtime (Min)", "sum"),
            average_downtime_minutes=("Downtime (Min)", "mean"),
        )
        .reindex(MONTH_ORDER)
        .fillna(0)
        .reset_index()
        .rename(columns={"index": "Fail Month"})
    )
    return summary


def build_charts(df: pd.DataFrame) -> None:
    office = office_summary(df)
    cause = cause_summary(df)
    month = month_summary(df)

    plt.figure(figsize=(10, 6))
    plt.bar(office["Office"], office["total_downtime_minutes"], color="tab:red")
    plt.title("Total downtime by office")
    plt.ylabel("Minutes")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "downtime_by_office.png", dpi=200)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(month["Fail Month"], month["total_downtime_minutes"], marker="o", color="tab:blue")
    plt.title("Downtime trend by month")
    plt.ylabel("Minutes")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "downtime_by_month.png", dpi=200)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.barh(cause["Event Notes"][::-1], cause["total_downtime_minutes"][::-1], color="tab:green")
    plt.title("Downtime by root cause")
    plt.xlabel("Minutes")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "downtime_by_cause.png", dpi=200)
    plt.close()


def write_outputs(df: pd.DataFrame) -> dict:
    office_df = office_summary(df)
    cause_df = cause_summary(df)
    month_df = month_summary(df)

    office_df.to_csv(OUTPUT_DIR / "office_summary.csv", index=False)
    cause_df.to_csv(OUTPUT_DIR / "cause_summary.csv", index=False)
    month_df.to_csv(OUTPUT_DIR / "month_summary.csv", index=False)

    total_failures = int(len(df))
    total_downtime = float(df["Downtime (Min)"].sum())
    average_downtime = float(df["Downtime (Min)"].mean())
    total_hours = total_downtime / 60

    top_offices = office_df.head(3).to_dict("records")
    top_causes = cause_df.head(5).to_dict("records")
    peak_month = month_df.loc[month_df["total_downtime_minutes"].idxmax()]

    summary = {
        "total_failures": total_failures,
        "total_downtime_minutes": total_downtime,
        "total_downtime_hours": total_hours,
        "average_downtime_minutes": average_downtime,
        "top_offices": top_offices,
        "top_causes": top_causes,
        "peak_month": peak_month.to_dict(),
    }

    return summary


def print_summary(summary: dict) -> None:
    print("Global Motor Manufacturers Australia - Server Downtime Analysis")
    print("=" * 72)
    print(f"Total recorded failures: {summary['total_failures']}")
    print(f"Total downtime: {summary['total_downtime_minutes']:.0f} minutes ({summary['total_downtime_hours']:.1f} hours)")
    print(f"Average downtime per incident: {summary['average_downtime_minutes']:.1f} minutes")
    print()
    print("Top offices by downtime:")
    for row in summary["top_offices"]:
        print(f"- {row['Office']}: {row['total_downtime_minutes']:.0f} minutes across {row['failures']} incidents")
    print()
    print("Top causes by downtime:")
    for row in summary["top_causes"]:
        print(f"- {row['Event Notes']}: {row['total_downtime_minutes']:.0f} minutes across {row['failures']} incidents")
    print()
    peak = summary["peak_month"]
    print(f"Peak month: {peak['Fail Month']} ({peak['total_downtime_minutes']:.0f} minutes)")


def main() -> None:
    df = load_fail_logs(DATA_PATH)
    if df.empty:
        raise ValueError("No fail log data found in the workbook.")

    build_charts(df)
    summary = write_outputs(df)
    print_summary(summary)

    print("\nOutputs written to:")
    for path in sorted(OUTPUT_DIR.iterdir()):
        print(f"- {path.name}")


if __name__ == "__main__":
    main()
