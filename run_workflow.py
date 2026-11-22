
"""NutriTrace AI: synthetic, non-operational end-to-end workflow."""
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path

NODES = [
    "N01 Investigation Trigger",
    "N02 Water-Quality Data",
    "N03 Satellite Imagery",
    "N04 Rainfall Data",
    "N05 Streamflow Data",
    "N06 Land Use / Agriculture",
    "N07 Watershed / Terrain",
    "N08 GIS Alignment / Segmentation",
    "N09 AI Model Training / Loading",
    "N10 Source Attribution / Ranking",
    "N11 Uncertainty Assessment",
    "N12 Sampling Plan",
    "N13 Investigation Report",
]


def run_workflow(output_dir="outputs"):
    # N01: predefined investigation request.
    request = {
        "waterbody_id": "OWASCO-INLET-DEMO",
        "latitude": 42.71,
        "longitude": -76.42,
        "mode": "SYNTHETIC_DEMONSTRATION",
    }

    # N02: synthetic water-quality measurements.
    water_quality = {
        "baseline_phosphorus_mg_l": 0.035,
        "current_phosphorus_mg_l": 0.105,
        "baseline_nitrate_mg_l": 1.2,
        "current_nitrate_mg_l": 2.4,
        "chlorophyll_a_ug_l": 22.0,
    }

    # N03: synthetic satellite reflectance measurements.
    satellite = {
        "reflectance_bands": [
            round(0.03 + i * 0.007, 4) for i in range(11)
        ],
        "source": "synthetic, not Landsat or Sentinel",
    }

    # N04: simulated daily precipitation.
    rainfall = {
        "daily_mm": [0.0, 1.2, 5.0, 27.0, 12.0]
    }

    # N05: simulated streamflow.
    streamflow = {
        "baseline_m3_s": 2.0,
        "current_m3_s": 5.0,
    }

    # N06: hypothetical land-use classifications.
    land_use = {
        "agriculture_pct": 60,
        "urban_pct": 10,
        "forest_and_other_pct": 30,
    }

    # N07: hypothetical watershed characteristics.
    terrain = {
        "drainage_area_km2": 100.0,
        "mean_slope_pct": 5.0,
    }

    # N08: combine observations into an aligned dataset.
    aligned = {
        "waterbody_id": request["waterbody_id"],
        "water_quality": water_quality,
        "satellite": satellite,
        "rainfall": rainfall,
        "streamflow": streamflow,
        "land_use": land_use,
        "terrain": terrain,
    }

    assert sum(land_use.values()) == 100
    assert all(
        math.isfinite(x) and x >= 0
        for x in [
            water_quality["current_phosphorus_mg_l"],
            water_quality["baseline_phosphorus_mg_l"],
            streamflow["current_m3_s"],
        ]
    )

    # N09: simplified rule-based demonstration.
    # This is NOT a trained AI model or RSATSIModel.
    phosphorus_ratio = (
        water_quality["current_phosphorus_mg_l"]
        / water_quality["baseline_phosphorus_mg_l"]
    )

    nitrate_ratio = (
        water_quality["current_nitrate_mg_l"]
        / water_quality["baseline_nitrate_mg_l"]
    )

    anomaly = phosphorus_ratio >= 2.0 or nitrate_ratio >= 2.0

    risk_score = min(
        100, round(20 * phosphorus_ratio + 10 * nitrate_ratio)
    )

    model = {
        "type": "illustrative rule-based placeholder",
        "trained_model_used": False,
        "phosphorus_ratio": round(phosphorus_ratio, 2),
        "nitrate_ratio": round(nitrate_ratio, 2),
        "illustrative_risk_score_0_100": risk_score,
        "candidate_anomaly": anomaly,
    }

    # N10: illustrative source screening.
    # These rankings do NOT establish pollution sources.
    source_ranking = sorted(
        [
            {
                "category": "Agricultural runoff",
                "illustrative_priority": land_use["agriculture_pct"],
            },
            {
                "category": "Urban runoff",
                "illustrative_priority": land_use["urban_pct"],
            },
            {
                "category": "Other land cover",
                "illustrative_priority": land_use["forest_and_other_pct"],
            },
        ],
        key=lambda item: item["illustrative_priority"],
        reverse=True,
    )

    # N11: uncertainty assessment.
    uncertainty = {
        "confidence": "NOT ESTABLISHED",
        "reason": (
            "Synthetic data; no external validation or live sensors"
        ),
        "source_attribution_validated": False,
    }

    # N12: proposed confirmatory sampling.
    if anomaly:
        sampling_plan = [
            "Collect upstream and downstream grab samples "
            "for total phosphorus and nitrate.",
            "Record discharge and recent precipitation.",
            "Confirm laboratory results before regulatory interpretation.",
        ]
    else:
        sampling_plan = ["Continue routine monitoring."]

    # N13: produce a simulated investigation report.
    report = {
        "title": "NutriTrace AI Synthetic Investigation Report",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            "DEMONSTRATION ONLY. No real nutrient event was detected."
        ),
        "investigation": request,
        "completed_nodes": NODES,
        "aligned_inputs": aligned,
        "model_assessment": model,
        "source_screening": source_ranking,
        "uncertainty": uncertainty,
        "sampling_plan": sampling_plan,
        "alert": {
            "status": (
                "SIMULATED REVIEW REQUIRED"
                if anomaly
                else "NO SIMULATED ANOMALY"
            ),
            "sent_to_external_agency": False,
        },
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    json_file = output_path / "nutritrace_demo_report.json"
    csv_file = output_path / "nutritrace_demo_summary.csv"

    json_file.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    with csv_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "waterbody_id",
            "phosphorus_ratio",
            "nitrate_ratio",
            "illustrative_risk_score",
            "simulated_alert",
        ])
        writer.writerow([
            request["waterbody_id"],
            round(phosphorus_ratio, 2),
            round(nitrate_ratio, 2),
            risk_score,
            report["alert"]["status"],
        ])

    print("NutriTrace synthetic workflow completed: 13/13 nodes")
    print("Alert:", report["alert"]["status"])
    print("Report:", json_file)
    print("Summary:", csv_file)

    return report


if __name__ == "__main__":
    run_workflow()
