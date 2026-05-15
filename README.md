# Unlocking Sydney's Ghost Homes

**Evidence for Item 13.1: Short-Term Rental Ban**  
**36104 Data Visualisation and Narratives — Assignment 3**  
**Group 1**

> This project uses Airbnb listing data, ABS population statistics, and SA2 spatial boundaries to investigate the concentration of short-term rentals in Sydney and to support evidence-based discussion around housing availability, commercial short-term rental activity, and local policy action.

---

## Live Dashboard

**Dashboard link:** https://public.tableau.com/shared/S2KJ3H663?:display_count=n&:origin=viz_share_link


---

## Project Overview

Sydney is facing strong housing affordability and rental availability pressures. At the same time, some residential properties are being used as short-term rentals rather than long-term housing. This project investigates whether Airbnb activity is concentrated in specific Sydney areas and whether short-term rental activity may represent a meaningful source of recoverable housing stock.

The project is framed around **Item 13.1: The 2026 Short-Term Rental Ban Motion**, which proposes banning short-term rentals in the City of Sydney during the housing crisis. The analysis focuses on identifying high-impact areas, measuring Airbnb intensity relative to local population, and communicating the results through a persuasive data narrative.

---

## Stakeholder and Persuasion Target

**Primary stakeholder:** City of Sydney Councillors

The dashboard and presentation are designed to provide evidence for councillors evaluating whether short-term rental restrictions could help return housing stock to long-term residential use.

**Narrative goal:** Provide clear, data-driven evidence for a **YES vote** on the short-term rental ban motion.

---

## Narrative Structure

This project follows a **What → So What → What Next** narrative arc.

### What
Airbnb listings are spatially concentrated in several high-impact Sydney areas, including central and inner-city locations.

### So What
High listing density, commercial host activity, and high availability may indicate residential properties being used as de facto tourist accommodation rather than long-term homes.

### What Next
Policy stakeholders can use the dashboard to identify priority areas, estimate recoverable housing stock, and evaluate targeted short-term rental regulation.

---

## Data Sources

| Dataset | Source | File / Format | Purpose |
|---|---|---|---|
| Airbnb Listings | Inside Airbnb | `listings.csv` | Provides listing location, host, room type, availability, occupancy, and review-related variables. |
| Population by Age and Sex | Australian Bureau of Statistics | `32350DS0001_2024.xlsx` | Provides SA2-level population and demographic statistics. |
| SA2 Boundary File | Australian Bureau of Statistics ASGS Edition 3 | `SA2_2021_AUST_SHP_GDA2020/` | Provides official SA2 polygons for spatially joining Airbnb coordinates to ABS regions. |

---

## Data Enrichment Strategy

The project satisfies the rich-data requirement by joining multiple real-world datasets rather than analysing a single CSV.

The key enrichment step is a **spatial join**:

```text
Airbnb latitude / longitude
        ↓
Converted into spatial point geometry
        ↓
Joined to ABS SA2 boundary polygon
        ↓
Each listing receives an SA2 code
        ↓
Airbnb metrics aggregated by SA2
        ↓
Joined with ABS demographic statistics
```

A direct name-based join was avoided because Airbnb neighbourhood names do not always match official ABS SA2 names. The SA2 code provides a more reliable geographic join key.

---

## Methodology

The technical workflow consists of the following stages:

1. **Load Airbnb data**  
   The `listings.csv` file is loaded and checked for valid latitude and longitude values.

2. **Load ABS population data**  
   The ABS workbook is read from the relevant SA2-level sheet containing total population and age-group variables.

3. **Load SA2 spatial boundaries**  
   The SA2 shapefile is loaded using GeoPandas.

4. **Create listing point geometry**  
   Each Airbnb listing is converted into a point using longitude and latitude.

5. **Spatially assign listings to SA2 regions**  
   A spatial join assigns each listing to the SA2 polygon that contains it.

6. **Aggregate to SA2 level**  
   Listing-level observations are grouped by SA2 to calculate listing count, listing density, commercial-host indicators, occupancy, and availability measures.

7. **Join with ABS statistics**  
   Airbnb SA2 summaries are merged with ABS demographic data using the SA2 code.

8. **Create visualisations**  
   The final dataset is used to create maps, bar charts, scatter plots, and modelling views for the dashboard and presentation.

---

## Main Metrics

| Metric | Description | Interpretation |
|---|---|---|
| `listing_count` | Number of Airbnb listings in each SA2 or neighbourhood area. | Shows raw Airbnb supply. |
| `listings_per_1000_residents` | Airbnb listings divided by population, multiplied by 1,000. | Measures Airbnb intensity relative to resident population. |
| `commercial_host_percentage` | Percentage of listings operated by hosts with multiple listings, such as 3 or more. | Indicates professionalised short-term rental activity. |
| `average_occupancy_days` | Estimated average occupied days. | Indicates how frequently listings are used. |
| `availability_365` | Number of days a listing is available in the next 365 days. | Helps identify listings potentially kept available for short-term rental use. |
| `high_availability_listings` | Listings available for more than a selected threshold, such as 180 days. | Used to estimate potentially recoverable long-term rental stock. |

---

## Derived Metrics

### Listings per 1,000 residents

```text
listings_per_1000_residents = (listing_count / population) × 1000
```

This normalises Airbnb activity by local population size. It helps distinguish genuinely high-intensity short-term rental areas from areas that simply have larger populations.

### Recoverable housing stock estimate

```text
recoverable_stock = count of listings above selected availability threshold
```

The presentation uses a threshold such as **180 available days** to identify listings that may represent properties not consistently used as long-term housing.

---

## Visualisations

The project includes at least four purposeful visualisations.

| Visual | Purpose | Narrative Role |
|---|---|---|
| **Map of Airbnb listings** | Shows spatial clustering of Airbnb listings across Sydney. | Establishes the problem visually. |
| **Listings per 1,000 residents** | Compares short-term rental intensity across areas. | Shows where Airbnb pressure is highest relative to population. |
| **Commercial concentration vs listing intensity** | Compares commercial-host percentage, listing intensity, and occupancy. | Highlights professionalised STR activity. |
| **Inefficiency gap** | Contrasts highly occupied listings with highly available/underused listings. | Frames the housing-stock recovery argument. |
| **Recoverable homes modelling view** | Estimates how many homes could return to long-term rental under selected conditions. | Supports the policy call to action. |

---

## Dashboard Features

The final dashboard is designed as a persuasive data narrative rather than a static status dashboard.

| Feature | Implementation |
|---|---|
| Narrative flow | The dashboard guides users from spatial distribution, to intensity, to commercial concentration, to policy impact. |
| Visual tooltips | Hover interactions reveal deeper details such as listing count, commercial-host percentage, and occupancy measures. |
| Context-aware exploration | Users can compare different areas and inspect how Airbnb activity varies geographically. |
| Scenario-style modelling | Availability thresholds are used to estimate potentially recoverable housing stock. |

> Please confirm the exact implemented advanced features before final submission. The assignment requires at least three advanced features.

---

## Human-Centred Design Rationale

The dashboard is designed for non-technical council stakeholders who need to interpret evidence quickly. The design uses:

- **Clear visual hierarchy** to guide attention from the policy problem to the evidence.
- **Ranked bar charts** for comparing areas by intensity and potential impact.
- **Maps** to show spatial clustering and local relevance.
- **Scatter plots** to communicate relationships between commercial activity, occupancy, and Airbnb density.
- **Plain-language annotations** to reduce cognitive load.
- **Consistent colours and layout** to support readability and narrative continuity.

---

## Key Insights

1. Airbnb activity is not evenly distributed across Sydney.
2. Central and inner-city areas show stronger listing intensity relative to local population.
3. High commercial-host percentages suggest that parts of the STR market operate more like decentralised hotel supply than occasional home sharing.
4. Highly available listings may indicate underused residential stock that could potentially return to long-term rental supply.
5. Combining Airbnb listings with ABS population data reveals stronger policy-relevant insights than analysing listing data alone.

---

## Limitations

This analysis should be interpreted as an evidence-based exploratory study rather than a causal model of housing affordability. Key limitations include:

- Airbnb data is a snapshot and may not fully represent year-round market changes.
- Availability does not always mean a property is vacant; it indicates availability for booking on the platform.
- Occupancy estimates are derived from platform data and should be treated as approximations.
- SA2 boundaries are official statistical regions, but policy decisions may operate at suburb, council, or other administrative levels.
- The analysis focuses on short-term rental concentration and potential housing-stock recovery, not the full economic impact of tourism or host income.

---

## Repository Structure

```text
Repo/
├── README.md
├── listings.csv
├── 32350DS0001_2024.xlsx
├── SA2_2021_AUST_SHP_GDA2020/
├── airbnb_abs_visualisation.py
├── outputs_sa2_seaborn/
│   ├── sa2_joined_summary.csv
│   ├── 01_top_bottom_sa2_listing_density.png
│   ├── 02_population_vs_listing_count_scatter.png
│   ├── 03_top_sa2_occupied_nights_per_1000.png
│   ├── 04_sa2_demographic_market_heatmap.png
│   ├── 05_age_profile_high_vs_low_density.png
│   └── 06_sa2_correlation_heatmap.png
└── requirements.txt
```


## Data Dictionary

| Variable | Type | Source | Description |
|---|---|---|---|
| `id` | String / Integer | Inside Airbnb | Unique listing identifier. |
| `latitude` | Float | Inside Airbnb | Listing latitude coordinate. |
| `longitude` | Float | Inside Airbnb | Listing longitude coordinate. |
| `room_type` | String | Inside Airbnb | Listing type, such as entire home, private room, or shared room. |
| `host_id` | String / Integer | Inside Airbnb | Unique host identifier. |
| `calculated_host_listings_count` | Integer | Inside Airbnb | Number of listings associated with a host. |
| `availability_365` | Integer | Inside Airbnb | Number of days the listing is available in the next 365 days. |
| `estimated_occupancy_l365d` | Numeric | Inside Airbnb | Estimated occupancy over the last 365 days, where available. |
| `number_of_reviews` | Integer | Inside Airbnb | Total number of reviews for the listing. |
| `SA2_CODE` | String | ABS / Derived | SA2 code assigned through spatial join. |
| `SA2_NAME` | String | ABS | Name of the Statistical Area Level 2 region. |
| `population` | Integer | ABS | Total resident population of the SA2 area. |
| `listing_count` | Integer | Derived | Number of Airbnb listings in each SA2. |
| `listings_per_1000_residents` | Float | Derived | Airbnb listings per 1,000 residents. |
| `commercial_host_percentage` | Float | Derived | Percentage of listings operated by multi-listing hosts. |
| `high_availability_listings` | Integer | Derived | Count of listings above the selected availability threshold. |

---

## Team Roles

| Track | Members | Responsibilities |
|---|---|---|
| Presentation | Asher, Seyoung, Ishanka | Presentation creation and 13 May presentation delivery. |
| Coding | Miras, Raymond, Mariyam | Data cleaning and visualisation development. |
| Documentation | Saif, Arthur | Technical documentation and video walkthrough. |

---

## Credits

### Data Sources

- Inside Airbnb — Sydney listings data.
- Australian Bureau of Statistics — Regional population by age and sex, SA2, 2024.

### Tools

- Tableau Public
- Python
- pandas
- GeoPandas
- seaborn
- matplotlib
- openpyxl
- GitHub


