"""
SA2-only Airbnb + ABS visualisation with Seaborn.

Inputs expected in the same folder as this script:
  - listings.csv
  - 32350DS0001_2024.xlsx
  - SA2 shapefile folder, e.g. SA2_2021_AUST_SHP_GDA2020/SA2_2021_AUST_GDA2020.shp

Outputs:
  - outputs_sa2_seaborn/sa2_joined_summary.csv
  - several PNG plots

Run:
  pip install pandas geopandas seaborn matplotlib openpyxl
  python airbnb_abs_visualisation_sa2_final.py
"""

from pathlib import Path
import warnings

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore", category=UserWarning)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs_sa2_seaborn"
OUTPUT_DIR.mkdir(exist_ok=True)

LISTINGS_FILE = BASE_DIR / "listings.csv"
ABS_FILE = BASE_DIR / "32350DS0001_2024.xlsx"

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["axes.titlesize"] = 15
plt.rcParams["axes.labelsize"] = 11


def find_sa2_shapefile() -> Path:
    candidates = list(BASE_DIR.rglob("SA2_2021_AUST_GDA2020.shp"))
    if not candidates:
        candidates = list(BASE_DIR.rglob("*SA2*2021*.shp"))
    if not candidates:
        raise FileNotFoundError(
            "Cannot find SA2 shapefile. Put the unzipped SA2_2021_AUST_SHP_GDA2020 folder in this repo."
        )
    return candidates[0]


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False),
        errors="coerce",
    )


def read_abs_sa2_population() -> pd.DataFrame:
    """
    ABS Table 3 has two useful header rows:
      row 5 = age-group labels including 'Total persons'
      row 6 = units such as 'no.'

    Reading with header=6 loses the age names and gives columns like no., no..1, no..18.
    Therefore we read with header=5, drop the unit row, and rename the geography columns.
    """
    df = pd.read_excel(ABS_FILE, sheet_name="Table 3", header=5)

    # Drop the first row after the header because it contains units: no., no., no.
    df = df[df["Total persons"].astype(str).str.lower().ne("no.")].copy()

    rename_map = {
        "Unnamed: 0": "ST_CODE",
        "Unnamed: 1": "ST_NAME",
        "Unnamed: 2": "GCCSA_CODE",
        "Unnamed: 3": "GCCSA_NAME",
        "Unnamed: 4": "SA4_CODE",
        "Unnamed: 5": "SA4_NAME",
        "Unnamed: 6": "SA3_CODE",
        "Unnamed: 7": "SA3_NAME",
        "Unnamed: 8": "SA2_CODE",
        "Unnamed: 9": "SA2_NAME",
        "Total persons": "population",
    }
    df = df.rename(columns=rename_map)

    required = ["SA2_CODE", "SA2_NAME", "population"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"ABS file missing expected columns after parsing: {missing}. Found: {list(df.columns)}")

    age_cols = [
        "0–4", "5–9", "10–14", "15–19", "20–24", "25–29", "30–34", "35–39",
        "40–44", "45–49", "50–54", "55–59", "60–64", "65–69", "70–74", "75–79",
        "80–84", "85 and over",
    ]
    for col in ["population"] + age_cols:
        if col in df.columns:
            df[col] = to_numeric(df[col])

    df["SA2_CODE"] = df["SA2_CODE"].astype(str).str.replace(r"\.0$", "", regex=True)

    # Keep NSW only because the Airbnb file is Sydney/NSW.
    if "ST_NAME" in df.columns:
        df = df[df["ST_NAME"].eq("New South Wales")].copy()

    # Useful age summaries
    df["children_0_14"] = df[["0–4", "5–9", "10–14"]].sum(axis=1, min_count=1)
    df["young_adults_20_34"] = df[["20–24", "25–29", "30–34"]].sum(axis=1, min_count=1)
    df["older_65_plus"] = df[["65–69", "70–74", "75–79", "80–84", "85 and over"]].sum(axis=1, min_count=1)

    df["pct_children_0_14"] = df["children_0_14"] / df["population"] * 100
    df["pct_young_adults_20_34"] = df["young_adults_20_34"] / df["population"] * 100
    df["pct_older_65_plus"] = df["older_65_plus"] / df["population"] * 100

    keep_cols = [
        "SA2_CODE", "SA2_NAME", "population",
        "children_0_14", "young_adults_20_34", "older_65_plus",
        "pct_children_0_14", "pct_young_adults_20_34", "pct_older_65_plus",
    ]
    return df[keep_cols].dropna(subset=["SA2_CODE", "population"])


def load_sa2_boundaries(shapefile: Path) -> gpd.GeoDataFrame:
    sa2 = gpd.read_file(shapefile)
    rename_candidates = {
        "SA2_CODE21": "SA2_CODE",
        "SA2_NAME21": "SA2_NAME_BOUNDARY",
        "SA2_CODE_2021": "SA2_CODE",
        "SA2_NAME_2021": "SA2_NAME_BOUNDARY",
    }
    sa2 = sa2.rename(columns={k: v for k, v in rename_candidates.items() if k in sa2.columns})

    if "SA2_CODE" not in sa2.columns:
        possible = [c for c in sa2.columns if "SA2" in c.upper() and "CODE" in c.upper()]
        raise ValueError(f"Cannot find SA2 code column in shapefile. Possible columns: {possible}")

    if "SA2_NAME_BOUNDARY" not in sa2.columns:
        name_cols = [c for c in sa2.columns if "SA2" in c.upper() and "NAME" in c.upper()]
        if name_cols:
            sa2 = sa2.rename(columns={name_cols[0]: "SA2_NAME_BOUNDARY"})
        else:
            sa2["SA2_NAME_BOUNDARY"] = sa2["SA2_CODE"].astype(str)

    sa2["SA2_CODE"] = sa2["SA2_CODE"].astype(str).str.replace(r"\.0$", "", regex=True)
    return sa2[["SA2_CODE", "SA2_NAME_BOUNDARY", "geometry"]]


def build_sa2_summary() -> pd.DataFrame:
    if not LISTINGS_FILE.exists():
        raise FileNotFoundError(f"Missing listings file: {LISTINGS_FILE}")
    if not ABS_FILE.exists():
        raise FileNotFoundError(f"Missing ABS file: {ABS_FILE}")

    shapefile = find_sa2_shapefile()
    print(f"Using listings file: {LISTINGS_FILE.name}")
    print(f"Using ABS file: {ABS_FILE.name}")
    print(f"Using SA2 shapefile: {shapefile}")

    listings = pd.read_csv(LISTINGS_FILE, low_memory=False)
    abs_pop = read_abs_sa2_population()
    sa2 = load_sa2_boundaries(shapefile)

    required_listing_cols = ["id", "latitude", "longitude"]
    missing_listing_cols = [c for c in required_listing_cols if c not in listings.columns]
    if missing_listing_cols:
        raise ValueError(f"listings.csv missing columns: {missing_listing_cols}")

    listings = listings.dropna(subset=["latitude", "longitude"]).copy()

    # Numeric columns used in plots. Missing columns are created as NaN so the script remains robust.
    numeric_cols = [
        "estimated_occupancy_l365d", "availability_365", "number_of_reviews",
        "number_of_reviews_ltm", "reviews_per_month", "review_scores_rating", "price",
    ]
    for col in numeric_cols:
        if col in listings.columns:
            listings[col] = to_numeric(listings[col])
        else:
            listings[col] = pd.NA

    # Spatial join: Airbnb points to SA2 polygons.
    gdf = gpd.GeoDataFrame(
        listings,
        geometry=gpd.points_from_xy(listings["longitude"], listings["latitude"]),
        crs="EPSG:4326",
    ).to_crs(sa2.crs)

    joined_points = gpd.sjoin(
        gdf,
        sa2[["SA2_CODE", "SA2_NAME_BOUNDARY", "geometry"]],
        how="left",
        predicate="within",
    )

    match_rate = joined_points["SA2_CODE"].notna().mean() * 100
    print(f"Spatial match rate: {match_rate:.1f}%")

    # Aggregate Airbnb by SA2.
    agg = (
        joined_points.dropna(subset=["SA2_CODE"])
        .groupby(["SA2_CODE", "SA2_NAME_BOUNDARY"], as_index=False)
        .agg(
            listing_count=("id", "count"),
            occupied_nights=("estimated_occupancy_l365d", "sum"),
            avg_occupancy=("estimated_occupancy_l365d", "mean"),
            avg_availability_365=("availability_365", "mean"),
            total_reviews=("number_of_reviews", "sum"),
            avg_reviews_per_listing=("number_of_reviews", "mean"),
            avg_review_score=("review_scores_rating", "mean"),
            avg_price=("price", "mean"),
        )
    )

    df = agg.merge(abs_pop, on="SA2_CODE", how="left")
    df = df.dropna(subset=["population"])
    df = df[df["population"] > 0].copy()

    if df.empty:
        raise ValueError("No usable SA2 rows after joining. Check SA2_CODE format in shapefile and ABS file.")

    df["listings_per_1000_people"] = df["listing_count"] / df["population"] * 1000
    df["occupied_nights_per_1000_people"] = df["occupied_nights"] / df["population"] * 1000
    df["reviews_per_1000_people"] = df["total_reviews"] / df["population"] * 1000

    # Replace empty avg_price with NaN; plots do not rely on price/revenue.
    df = df.sort_values("listings_per_1000_people", ascending=False)
    df.to_csv(OUTPUT_DIR / "sa2_joined_summary.csv", index=False)
    print(f"Usable SA2 rows: {len(df)}")
    print(f"Saved joined table: {OUTPUT_DIR / 'sa2_joined_summary.csv'}")
    return df


def savefig(name: str):
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / name, bbox_inches="tight")
    plt.close()
    print(f"Saved: {OUTPUT_DIR / name}")


def plot_top_bottom_density(df: pd.DataFrame):
    top = df.nlargest(10, "listings_per_1000_people").copy()
    bottom = df[df["listing_count"] >= 3].nsmallest(10, "listings_per_1000_people").copy()
    plot_df = pd.concat([top.assign(group="Highest density"), bottom.assign(group="Lowest density")])
    plot_df["label"] = plot_df["SA2_NAME_BOUNDARY"].fillna(plot_df["SA2_NAME"])

    plt.figure(figsize=(11, 8))
    ax = sns.barplot(
        data=plot_df,
        y="label",
        x="listings_per_1000_people",
        hue="group",
        dodge=False,
    )
    ax.set_title("Airbnb Intensity by SA2: Highest vs Lowest Density")
    ax.set_xlabel("Airbnb listings per 1,000 residents")
    ax.set_ylabel("")
    ax.legend(title="SA2 group", loc="lower right")
    savefig("01_top_bottom_sa2_listing_density.png")


def plot_population_vs_listings(df: pd.DataFrame):
    plt.figure(figsize=(9.5, 6.5))
    ax = sns.scatterplot(
        data=df,
        x="population",
        y="listing_count",
        size="listings_per_1000_people",
        sizes=(25, 350),
        alpha=0.65,
    )
    ax.set_title("Population Size vs Airbnb Listing Count by SA2")
    ax.set_xlabel("SA2 population")
    ax.set_ylabel("Number of Airbnb listings")
    ax.legend(title="Listings per 1,000 people", bbox_to_anchor=(1.02, 1), loc="upper left")
    savefig("02_population_vs_listing_count_scatter.png")


def plot_occupied_nights(df: pd.DataFrame):
    if df["occupied_nights"].notna().sum() == 0 or df["occupied_nights"].sum() == 0:
        print("Skipped occupied nights plot: estimated_occupancy_l365d is empty.")
        return

    top = df.nlargest(15, "occupied_nights_per_1000_people").copy()
    top["label"] = top["SA2_NAME_BOUNDARY"].fillna(top["SA2_NAME"])

    plt.figure(figsize=(10.5, 7))
    ax = sns.barplot(data=top, y="label", x="occupied_nights_per_1000_people")
    ax.set_title("Top SA2 Areas by Estimated Airbnb Occupied Nights per Resident")
    ax.set_xlabel("Estimated occupied nights per 1,000 residents")
    ax.set_ylabel("")
    savefig("03_top_sa2_occupied_nights_per_1000.png")


def plot_demographic_market_heatmap(df: pd.DataFrame):
    cols = [
        "listing_count", "listings_per_1000_people", "occupied_nights_per_1000_people",
        "avg_availability_365", "avg_reviews_per_listing", "pct_children_0_14",
        "pct_young_adults_20_34", "pct_older_65_plus",
    ]
    available_cols = [c for c in cols if c in df.columns and df[c].notna().sum() > 2]
    top = df.nlargest(20, "listings_per_1000_people").copy()
    top["SA2"] = top["SA2_NAME_BOUNDARY"].fillna(top["SA2_NAME"])

    heat = top.set_index("SA2")[available_cols]
    heat = (heat - heat.mean()) / heat.std(ddof=0)
    heat = heat.replace([float("inf"), float("-inf")], pd.NA).fillna(0)

    plt.figure(figsize=(12, 8.5))
    ax = sns.heatmap(heat, cmap="vlag", center=0, linewidths=0.4, cbar_kws={"label": "Standardised value"})
    ax.set_title("Profile of High-Airbnb-Density SA2 Areas")
    ax.set_xlabel("")
    ax.set_ylabel("")
    savefig("04_sa2_demographic_market_heatmap.png")


def plot_age_profile(df: pd.DataFrame):
    high = df.nlargest(20, "listings_per_1000_people").copy()
    low = df[df["listing_count"] >= 3].nsmallest(20, "listings_per_1000_people").copy()

    profile = pd.DataFrame({
        "Age group": ["Children 0–14", "Young adults 20–34", "Older residents 65+"],
        "High Airbnb density SA2s": [
            high["pct_children_0_14"].mean(),
            high["pct_young_adults_20_34"].mean(),
            high["pct_older_65_plus"].mean(),
        ],
        "Low Airbnb density SA2s": [
            low["pct_children_0_14"].mean(),
            low["pct_young_adults_20_34"].mean(),
            low["pct_older_65_plus"].mean(),
        ],
    }).melt(id_vars="Age group", var_name="SA2 group", value_name="Population share (%)")

    plt.figure(figsize=(9, 5.8))
    ax = sns.barplot(data=profile, x="Age group", y="Population share (%)", hue="SA2 group")
    ax.set_title("Age Profile: High vs Low Airbnb-Density SA2 Areas")
    ax.set_xlabel("")
    ax.set_ylabel("Average population share (%)")
    ax.legend(title="")
    savefig("05_age_profile_high_vs_low_density.png")


def plot_correlation_heatmap(df: pd.DataFrame):
    cols = [
        "population", "listing_count", "listings_per_1000_people", "occupied_nights_per_1000_people",
        "avg_availability_365", "total_reviews", "avg_reviews_per_listing",
        "pct_children_0_14", "pct_young_adults_20_34", "pct_older_65_plus",
    ]
    cols = [c for c in cols if c in df.columns and df[c].notna().sum() > 3]
    corr = df[cols].corr(numeric_only=True)

    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(corr, cmap="vlag", center=0, annot=True, fmt=".2f", linewidths=0.4)
    ax.set_title("Correlation Between Airbnb Intensity and SA2 Demographics")
    savefig("06_sa2_correlation_heatmap.png")


def main():
    df = build_sa2_summary()
    plot_top_bottom_density(df)
    plot_population_vs_listings(df)
    plot_occupied_nights(df)
    plot_demographic_market_heatmap(df)
    plot_age_profile(df)
    plot_correlation_heatmap(df)
    print("\nDone. Open the outputs_sa2_seaborn folder.")


if __name__ == "__main__":
    main()
