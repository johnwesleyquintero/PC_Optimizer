# Data Analysis Playground & Ideas

*Inspired by Google Sheets workflows, CSVAnalyzer, and the needs of SentinelPC.*

This document serves as a brainstorming space and scratchpad for data analysis ideas, potential workflows, code snippets, and integration points related to personal projects.

---

## Core Concepts (from Sheets Example)

A typical workflow often involves:

1.  **Authentication:** Securely connecting to data sources.
2.  **Data Loading:** Retrieving data (e.g., from Sheets, CSVs, logs).
3.  **Data Cleaning/Merging:** Preparing data (handling missing values, combining sources).
4.  **Calculation/Analysis:** Deriving metrics, performing statistical analysis, identifying patterns.
5.  **Output/Reporting:** Storing results, generating reports, or visualizing findings.

---

## Brainstorming Areas

### 1. SentinelPC Data & Analysis

*   **What data can SentinelPC generate/collect?**
    *   Optimization logs (timestamp, action taken, result/status, duration).
    *   Before/After system metrics (e.g., free disk space, maybe RAM usage if tracked).
    *   Configuration settings used during a run.
    *   Benchmark results (if integrated or run separately).
    *   Error logs.
*   **Potential Analysis Ideas:**
    *   Track effectiveness of `clean_temp_files` over time (space recovered).
    *   Correlate specific optimization actions with perceived performance improvements (requires manual input or benchmark data).
    *   Analyze frequency of errors or specific warnings.
    *   Compare performance metrics based on different configuration profiles.
    *   Visualize optimization run times.
    *   Identify which optimization steps take the longest.
*   **Tooling Integration:**
    *   Can SentinelPC export its run logs/results as a CSV compatible with `CSVAnalyzer`?
    *   Could `CSVAnalyzer` be used directly within SentinelPC for post-run analysis (maybe via a CLI flag)?
    *   Use `run_tasks.bat` log (`run_tasks.log`) as input? (Might be too unstructured).

### 2. General Analysis Workflows & Snippets

*   **Standard EDA Checklist:**
    *   Load data (`CSVAnalyzer.load_data`)
    *   Basic info (`.info()`, `.describe()`)
    *   Check missing values (`CSVAnalyzer.handle_missing_values`)
    *   Check duplicates (`CSVAnalyzer.remove_duplicates`)
    *   Explore distributions (histograms)
    *   Explore correlations (heatmaps)
*   **Time Series Ideas:**
    *   Plotting metrics over time (e.g., disk space, benchmark scores).
    *   Calculating rolling averages/medians.
    *   Identifying trends or seasonality (if applicable).
*   **Code Snippets (Examples):**

    ```python
    # Example using CSVAnalyzer
    # from tools.csv_analyzer import CSVAnalyzer
    # analyzer = CSVAnalyzer('path/to/sentinelpc_log.csv')
    # analyzer.load_data()
    # analyzer.handle_missing_values(strategy='drop')
    # stats = analyzer.get_basic_statistics()
    # print(stats)
    # analyzer.df.plot(kind='line', x='timestamp', y='disk_space_saved') # Requires matplotlib
    ```

    ```python
    # Example: Parsing a simple SentinelPC log line (hypothetical)
    # import re
    # log_line = "2024-07-29 10:30:00 | INFO | Cleaned 500 MB from Temp"
    # pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\w+) \| Cleaned (\d+) MB from (\w+)"
    # match = re.search(pattern, log_line)
    # if match:
    #     timestamp, level, amount, source = match.groups()
    #     print(f"Time: {timestamp}, Amount: {amount} MB")
    ```

### 3. Potential Data Sources

*   SentinelPC Logs (`.log` format - needs parsing, or dedicated `.csv` export)
*   System Performance Counters (`psutil`?)
*   Benchmark Output Files (Game FPS logs, rendering times, etc.)
*   Google Sheets (as per original example)
*   Manual Entry CSVs
*   Web Scraping (if relevant)

### 4. Metrics & KPIs to Track

*   Disk Space Recovered (MB/GB)
*   Optimization Duration (seconds/minutes)
*   Specific Error Counts
*   Benchmark Scores (FPS, ms, etc.)
*   Resource Usage (CPU %, RAM MB) - *Harder to track reliably*
*   ACoS, ROAS, CTR (from Sheets example - for other types of analysis)

### 5. Visualization Ideas

*   Line charts (time-based metrics)
*   Bar charts (comparisons, counts)
*   Histograms (distributions)
*   Scatter plots (correlations)
*   Maybe integrate simple plots into `CSVAnalyzer` using `matplotlib`?

---

## Action Items / Next Steps

*   `[ ]` Define a structured log format (or CSV export) for SentinelPC runs.
*   `[ ]` Explore adding basic plotting capabilities to `CSVAnalyzer`.
*   `[ ]` Test parsing `run_tasks.log` (likely difficult due to mixed output).
*   `[ ]` Consider adding a `--analyze-log <logfile>` flag to SentinelPC CLI?

---

*This is a living document. Add ideas freely!*