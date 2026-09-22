# Global Motor Manufacturers Australia - Server Downtime Analysis

This repository analyses server failure and downtime records for Global Motor
Manufacturers Australia. The work supports the Fujitsu server-refresh planning
meeting by identifying recurring failure causes, offices with higher downtime,
monthly trends, and possible remediation actions.

## Project files

### Source data and supporting information

- `Task Data_ Server Down Data.xlsx` - source workbook. The analysis reads the
  `Fail Logs` worksheet, including asset ID, failure date, office, event notes,
  and downtime in minutes.
- `Additional Information_ Key Operational and Strategic Changes Document.docx.pdf`
  - client context used to identify operational and strategic risks, including
  unsupported servers, network-capacity changes, office consolidation, deferred
  cloud migration, and increasing environmental complexity.

### Analysis notebooks

- `server_downtime_analysis.ipynb` - main exploratory data-analysis notebook.
  It cleans the fail logs, calculates summaries, and creates charts.
- `server_downtime_analysis.executed.ipynb` - saved version of the analysis
  notebook with executed outputs.
- `machine_learning_server_downtime.ipynb` - machine-learning notebook. It
  cleans the data, extracts a compact feature set, performs a time-based split,
  compares several regression models, evaluates mean absolute error, and creates
  December predictions.

### Recommendations

- `suggestion.md` - three recommendations for reducing server downtime:
  server-capacity upgrades, proactive monitoring and maintenance, and network
  and disaster-recovery resilience.

### Generated analysis outputs

The `output/` directory contains the exploratory-analysis results:

- `downtime_by_office.png` - downtime comparison by office.
- `downtime_by_month.png` - monthly downtime trend.
- `downtime_by_cause.png` - downtime by failure cause.
- `server_failure_overview.png` - overview visualization of the failure data.
- `office_summary.csv` - incident count and downtime totals by office.
- `cause_summary.csv` - incident count and downtime totals by failure cause.
- `month_summary.csv` - incident count and downtime totals by month.

The `output/ml/` directory contains machine-learning results:

- `model_metrics.csv` - MAE, RMSE, and R-squared for every evaluated model.
- `december_predictions.csv` - actual downtime, predicted downtime, and absolute
  error for each December test incident.
- `december_predictions.png` - actual-versus-predicted December plot.
- `feature_importance.csv` - feature importance for the selected tree model,
  when feature importance is available.

## Data-analysis workflow

The exploratory analysis follows these steps:

1. Load the `Fail Logs` worksheet from the Excel workbook.
2. Remove empty rows and convert asset IDs, dates, and downtime values to
   suitable numeric or datetime types.
3. Fill missing office and event-note values with `Unknown`.
4. Remove records without a valid asset ID, failure date, or downtime value.
5. Restrict the analysis to the July-December 2019 reporting period.
6. Group the records by office, failure cause, and month.
7. Export summary CSV files and charts to `output/`.

The cleaned dataset contains 40 incidents, representing 6,384 minutes of
recorded downtime, or approximately 106.4 hours. The average incident downtime
is approximately 159.6 minutes. December is the peak downtime month in the
current data.

## Machine-learning workflow

The prediction notebook uses downtime minutes as the target. The model input
uses a compact five-feature set to reduce overfitting on the small dataset:

- `Asset ID`
- `Office`
- `Event Notes`
- `fail_month_number`
- `fail_day_of_week`

The workflow:

1. Cleans and validates the source data.
2. Extracts the selected categorical and numeric features.
3. Separates July-November records for training and December records for the
   final time-based test set.
4. Applies median imputation to numeric values and most-frequent imputation
   plus one-hot encoding to categorical values.
5. Compares a mean baseline, cause-median baseline, Random Forest, Extra Trees,
   Gradient Boosting, Decision Tree, and multiple parameter configurations.
6. Calculates:
   - Mean Absolute Error (MAE)
   - Root Mean Squared Error (RMSE)
   - R-squared
7. Displays the model ranking and the selected model parameters.
8. Exports December predictions and absolute errors to `output/ml/`.

MAE is the primary metric because it reports the average prediction error in
minutes and is less dominated by a small number of very large errors than
RMSE. The December test set contains only eight records, so its MAE can change
substantially when one incident is predicted poorly. A mean baseline may
therefore outperform more complex models on this small dataset.

The current notebook is configured to use the regularized Random Forest for
the final prediction output, while still displaying the full model comparison.
The selected configuration is:

- `n_estimators=500`
- `max_depth=3`
- `min_samples_leaf=2`
- `max_features=0.7`
- `random_state=42`
- `n_jobs=-1`

The model result should be interpreted as an initial benchmark rather than a
production forecasting system. More historical incidents and additional
predictive fields such as severity, server age, users affected, resource
utilisation, repair team, and repair complexity would be needed to reliably
reduce the MAE.

## Running the notebooks

Open the notebooks in Jupyter or Visual Studio Code and run them from the
first cell in order. Running from the beginning is important because later
cells depend on variables created during data loading, cleaning, feature
extraction, and train/test splitting.

The notebooks require Python packages including:

- `pandas`
- `numpy`
- `matplotlib`
- `scikit-learn`
- `openpyxl`

The Excel reader requires a compatible `openpyxl` installation. If the
workbook cannot be loaded, upgrade `openpyxl` in the selected Python
environment before rerunning the notebook.

## Key planning considerations

The supporting client document and the failure analysis indicate these risks:

- 50% of servers are out of support.
- Network-capacity upgrades are planned in phases, leaving some locations
  exposed during the transition.
- Four offices were closed and staff were consolidated into the remaining
  offices.
- Cloud migration was deferred by one year because of implementation costs.
- The environment is becoming more complex because of additional toolsets and
  increased reliance on commercial off-the-shelf solutions.

These findings support prioritising server refresh, capacity planning,
proactive monitoring, network redundancy, tested backups, and disaster
recovery during the planning meeting.
