"""Black-box contract tests for RSATSIModel 2.5.1 (ATSIModel).
Citable source: https://pypi.org (Package Scope, 
Standard ATSI Workflow, RS-ATSI Workflow, Validation Design, Plotting).
Input -> output: CHL (micrograms/L), SAL (PSU) table -> ATSI score/classes; 
CHL, SAL, Rhow_1..Rhow_11 table -> predicted CHL, ATSI and validation tables.
Written for: RSATSIModel==2.5.1, pytest==8.3.5, pandas==2.2.3, 
numpy==2.2.4, scikit-learn==1.6.1, matplotlib==3.10.1, 
openpyxl==3.1.5, scipy==1.15.2, joblib==1.4.2, threadpoolctl==3.6.0.
All samples are invented. Run: MPLBACKEND=Agg pytest -q test_rsatsimodel.py
No private implementation is imported or invoked.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
from matplotlib import pyplot as plt
from atsimodel.core import run_atsi
from atsimodel.rs_core import run_rs_atsi_pipeline
from atsimodel.utils import export_single
from atsimodel.plotting import plot_atsi_distribution, plot_chl_vs_atsi

@pytest.fixture(scope="session")
def standard_data(tmp_path_factory):
    folder = tmp_path_factory.mktemp("standard")
    df = pd.DataFrame({
        "CHL": [1.0, 3.5, 8.5, 15.1, 22.0, 35.0],
        "SAL": [5.0, 12.0, 20.0, 28.7, 31.2, 35.0],
    })
    files = {}
    for extension in ("csv", "xlsx", "txt"):
        path = folder / f"water.{extension}"
        if extension == "xlsx":
            df.to_excel(path, index=False)
        else:
            df.to_csv(path, index=False, sep="\t" if extension == "txt" else ",")
        files[extension] = path
    return df, files, folder

@pytest.fixture(scope="session")
def standard_result(standard_data):
    return run_atsi(str(standard_data[1]["csv"]))

@pytest.fixture(scope="session")
def rs_data(tmp_path_factory):
    """Synthetic multi-group calibration dataset; no real sampling records."""
    folder = tmp_path_factory.mktemp("remote")
    records = []
    for i in range(90):
        group = ("TRAIN", "TEST", "INDEPENDENT")[0 if i < 60 else 1 if i < 75 else 2]
        row = {
            "CHL": float(2.0 + (i * 7 % 37) + i * 0.013),
            "SAL": float(6 + (i * 3 % 29)),
            "SITE": f"Synthetic_{i % 5}",
            "SEASON": ("Winter", "Spring", "Summer", "Autumn")[i % 4],
            "ZONE": ("Upper", "Middle", "Lower")[i % 3],
            "SPLIT": group,
        }
        for band in range(1, 12):
            row[f"Rhow_{band}"] = float(
                0.004 + band * 0.0009 + (i * (band + 3) % 29) * 0.00015
            )
        records.append(row)
    frame = pd.DataFrame.from_records(records)
    csv_path = folder / "rs_synthetic.csv"
    frame.to_csv(csv_path, index=False)
    return frame, csv_path, folder

@pytest.fixture(scope="session")
def rs_result(rs_data):
    """Train once per pytest session and reuse all returned result tables."""
    return run_rs_atsi_pipeline(
        input_file=str(rs_data[1]),
        output_dir=str(rs_data[2] / "results"),
        target_col="CHL", sal_col="SAL", site_col="SITE",
        season_col="SEASON", zone_col="ZONE",
    )

def test_standard_returns_dataframe(standard_result):
    assert isinstance(standard_result, pd.DataFrame)
    assert len(standard_result) == 6

def test_standard_output_columns(standard_result):
    assert {"CHL", "SAL", "SAL_BIN", "CHL_TL", "CHL_TU", "ATSI", "ATSI_Class"} <= set(standard_result.columns)

def test_standard_atsi_bounded(standard_result):
    values = pd.to_numeric(standard_result["ATSI"], errors="raise")
    assert np.isfinite(values.to_numpy()).all()
    assert values.between(0, 100).all()

def test_standard_preserves_observations(standard_data, standard_result):
    original = standard_data[0]
    assert standard_result["CHL"].to_numpy(dtype=float) == pytest.approx(original["CHL"].to_numpy(), abs=1e-9)
    assert standard_result["SAL"].to_numpy(dtype=float) == pytest.approx(original["SAL"].to_numpy(), abs=1e-9)

def test_standard_threshold_order(standard_result):
    lower = pd.to_numeric(standard_result["CHL_TL"], errors="raise")
    upper = pd.to_numeric(standard_result["CHL_TU"], errors="raise")
    assert (lower <= upper).all()

def test_standard_class_present(standard_result):
    assert standard_result["ATSI_Class"].notna().all()
    assert standard_result["ATSI_Class"].astype(str).str.len().gt(0).all()

@pytest.mark.parametrize("extension", ["csv", "xlsx", "txt"])
def test_standard_supported_input_formats(standard_data, extension):
    result = run_atsi(str(standard_data[1][extension]))
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 6
    assert result["ATSI"].to_numpy(dtype=float) == pytest.approx(
        run_atsi(str(standard_data[1]["csv"]))["ATSI"].to_numpy(dtype=float), abs=1e-7
    )

def test_standard_salinity_conditions_thresholds(tmp_path):
    path = tmp_path / "salinity.csv"
    pd.DataFrame({"CHL": [10.0, 10.0, 10.0], "SAL": [0.0, 17.0, 35.0]}).to_csv(path, index=False)
    output = run_atsi(str(path))
    assert len(output) == 3
    assert output["SAL_BIN"].notna().all()
    assert output[["CHL_TL", "CHL_TU"]].nunique().max() >= 2

def test_standard_export_formats(standard_result, tmp_path):
    export_single(standard_result, out_base=str(tmp_path / "results"), formats=("xlsx", "csv", "txt", "json"))
    for ext in ("xlsx", "csv", "txt", "json"):
        assert (tmp_path / f"results.{ext}").is_file()
        assert (tmp_path / f"results.{ext}").stat().st_size > 0

def test_standard_plot_distribution(standard_result):
    plot_atsi_distribution(standard_result)
    assert plt.get_fignums(), "Histogram did not create a matplotlib figure"
    plt.close("all")

def test_standard_plot_scatter(standard_result):
    plot_chl_vs_atsi(standard_result)
    assert plt.get_fignums(), "Scatterplot did not create a matplotlib figure"
    plt.close("all")

def test_rs_returns_mapping(rs_result):
    assert isinstance(rs_result, dict)

def test_rs_predictions_schema(rs_result):
    predictions = rs_result["predictions_all"]
    assert isinstance(predictions, pd.DataFrame)
    assert {"CHL", "CHL_RS", "SAL", "ATSI_INSITU", "ATSI_RS", "DATASET", "ATSI_INSITU_CLASS", "ATSI_RS_CLASS"} <= set(predictions.columns)

def test_rs_prediction_values_finite(rs_result):
    predictions = rs_result["predictions_all"]
    assert len(predictions) > 0
    assert np.isfinite(predictions["CHL_RS"].to_numpy(dtype=float)).all()

def test_rs_atsi_scores_bounded(rs_result):
    predictions = rs_result["predictions_all"]
    for column in ("ATSI_INSITU", "ATSI_RS"):
        values = predictions[column].to_numpy(dtype=float)
        assert np.isfinite(values).all()
        assert np.all((0 <= values) & (values <= 100))

def test_rs_split_labels(rs_result):
    values = set(rs_result["predictions_all"]["DATASET"].astype(str).str.upper())
    assert {"TRAIN", "TEST", "INDEPENDENT"} <= values

@pytest.mark.parametrize("key", [
    "chl_validation_overall", "chl_validation_by_site_test",
    "chl_validation_by_site_independent", "chl_model_metrics_summary",
    "atsi_validation_overall", "atsi_validation_by_site_test",
    "atsi_validation_by_site_independent",
    "atsi_class_summary_test", "atsi_confusion_matrix_test",
    "atsi_class_summary_independent", "atsi_confusion_matrix_independent",
    "station_season_agreement_test", "station_season_agreement_independent",
    "spatial_zone_summary_test", "spatial_zone_summary_independent",
])
def test_rs_documented_validation_tables(rs_result, key):
    assert key in rs_result
    assert isinstance(rs_result[key], pd.DataFrame)

def test_rs_excel_bundle(rs_data, rs_result):
    bundle = rs_data[2] / "results" / "RS_ATSI_results_bundle.xlsx"
    assert bundle.is_file()
    assert bundle.stat().st_size > 0

def test_rs_source_data_synthetic(rs_data):
    frame = rs_data[0]
    assert len(frame) == 90
    assert {f"Rhow_{i}" for i in range(1, 12)} <= set(frame.columns)
    assert set(frame["SPLIT"]) == {"TRAIN", "TEST", "INDEPENDENT"}

@pytest.mark.xfail(strict=True, reason="The package documentation does not specify an exception type for absent CHL; contract requires clarification")
def test_invalid_missing_chl(tmp_path):
    path = tmp_path / "no_chl.csv"
    pd.DataFrame({"SAL": [30.0]}).to_csv(path, index=False)
    with pytest.raises(ValueError):
        run_atsi(str(path))

@pytest.mark.xfail(strict=True, reason="The package documentation does not specify an exception type for absent SAL; contract requires clarification")
def test_invalid_missing_sal(tmp_path):
    path = tmp_path / "no_sal.csv"
    pd.DataFrame({"CHL": [8.0]}).to_csv(path, index=False)
    with pytest.raises(ValueError):
        run_atsi(str(path))