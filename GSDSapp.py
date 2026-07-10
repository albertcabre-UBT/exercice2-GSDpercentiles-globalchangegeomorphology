import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Grain Size Distribution Analyzer", layout="wide")

st.title("Grain Size Distribution Analyzer")
st.markdown(
    """
    Paste your grain-size measurement data directly from Excel into the table
    below. Each **row** represents one sample (distribution), and each
    **column** represents one individual measurement. The number of
    measurements per sample can vary, since not all samples have the same
    number of data points.

    The app automatically computes the **D16, D50, and D84** percentiles for
    each sample, and lets you plot the cumulative distribution function (CDF)
    of the samples you choose.
    """
)

# ----------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------
N_SAMPLES = 10
MAX_COLUMNS = 500
DEFAULT_COLUMNS = 60

# ----------------------------------------------------------------------------
# 1. Data input
# ----------------------------------------------------------------------------
st.subheader("1. Input data")
st.caption(
    "Rows are fixed at 10 samples. Columns represent individual measurements "
    "within each sample and can be extended up to 500, since the number of "
    "measurements per sample is variable. Leave unused cells empty."
)

n_cols = st.number_input(
    "Number of measurement columns",
    min_value=1,
    max_value=MAX_COLUMNS,
    value=DEFAULT_COLUMNS,
    step=1,
    help="Set this to at least the number of measurements in your largest sample.",
)

if "data" not in st.session_state:
    row_labels = [f"Sample {i + 1}" for i in range(N_SAMPLES)]
    col_labels = [f"M{i + 1}" for i in range(DEFAULT_COLUMNS)]
    st.session_state["data"] = pd.DataFrame(
        np.nan, index=row_labels, columns=col_labels
    )

current_df = st.session_state["data"]
current_n_cols = current_df.shape[1]

if n_cols != current_n_cols:
    if n_cols > current_n_cols:
        new_cols = [f"M{i + 1}" for i in range(current_n_cols, n_cols)]
        for c in new_cols:
            current_df[c] = np.nan
    else:
        keep_cols = [f"M{i + 1}" for i in range(n_cols)]
        current_df = current_df[keep_cols]
    st.session_state["data"] = current_df

edited_df = st.data_editor(
    st.session_state["data"],
    num_rows="fixed",
    use_container_width=True,
    key="grain_data_editor",
)

st.session_state["data"] = edited_df

# ----------------------------------------------------------------------------
# 2. Percentile calculations
# ----------------------------------------------------------------------------
st.subheader("2. Percentiles (D16, D50, D84)")

distributions = {}
stats_rows = []

for row_label in edited_df.index:
    values = pd.to_numeric(edited_df.loc[row_label], errors="coerce").dropna().values
    if len(values) >= 2:
        values_sorted = np.sort(values)
        d16 = float(np.percentile(values_sorted, 16))
        d50 = float(np.percentile(values_sorted, 50))
        d84 = float(np.percentile(values_sorted, 84))
        distributions[row_label] = values_sorted
        stats_rows.append(
            {"Sample": row_label, "N": len(values_sorted), "D16": d16, "D50": d50, "D84": d84}
        )

if stats_rows:
    stats_df = pd.DataFrame(stats_rows).set_index("Sample")
    st.dataframe(
        stats_df.style.format({"D16": "{:.3f}", "D50": "{:.3f}", "D84": "{:.3f}"}),
        use_container_width=True,
    )
else:
    st.info("Enter at least 2 numeric values in one row to see percentile results.")

# ----------------------------------------------------------------------------
# 3. CDF plot
# ----------------------------------------------------------------------------
st.subheader("3. Cumulative Distribution Function (CDF) plot")

if distributions:
    selected = st.multiselect(
        "Select which sample(s) you want to plot:",
        options=list(distributions.keys()),
        default=list(distributions.keys()),
    )

    log_x = st.checkbox("Use logarithmic scale for grain size axis (X)", value=False)

    if selected:
        fig = go.Figure()
        for name in selected:
            vals = distributions[name]
            n = len(vals)
            cdf = np.arange(1, n + 1) / n * 100  # cumulative percentage
            fig.add_trace(
                go.Scatter(
                    x=vals,
                    y=cdf,
                    mode="lines+markers",
                    name=name,
                )
            )

        fig.update_layout(
            xaxis_title="Grain size",
            yaxis_title="Cumulative percentage (%)",
            legend_title="Sample",
            template="plotly_white",
            height=550,
        )
        if log_x:
            fig.update_xaxes(type="log")

        for y_ref, label in [(16, "D16"), (50, "D50"), (84, "D84")]:
            fig.add_hline(
                y=y_ref,
                line_dash="dot",
                line_color="gray",
                opacity=0.5,
                annotation_text=label,
                annotation_position="right",
            )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Select at least one sample to display its CDF.")
else:
    st.info("Add data above to generate the plot.")

st.markdown("---")
st.caption(
    "D16, D50 and D84 are the grain sizes below which 16%, 50%, and 84% of the "
    "sample falls, respectively. They are commonly used in sedimentology to "
    "estimate the mean grain size and sorting of a sample."
)
