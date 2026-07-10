import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from matplotlib.ticker import LogLocator, LogFormatterMathtext
# ----------------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Grain Size Distribution(s)", layout="wide")

st.title("Grain Size Distribution(s)")
st.markdown(
    """
    Paste your grain-size measurement data directly from Excel into the table
    below. Each row represents one station (whole distribution), and each
    column represents one individual measurement. The number of
    measurements per sample can vary, since not all samples have the same
    number of data points.

    The app computes the D16, D50, and D84 percentiles for
    each sample, and allows you to the cumulative distribution function (CDF)
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
#st.caption(
#    "Rows are fixed at 10 samples. Columns represent individual measurements "
#    "within each sample and can be extended up to 500, since the number of "
#    "measurements per sample is variable. Leave unused cells empty."
#)

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
st.subheader("3. Cumulative Distribution Function (CDF) plot(s)")

if distributions:
    selected = st.multiselect(
        "Select which sample(s) you want to plot:",
        options=list(distributions.keys()),
        default=list(distributions.keys()),
    )

    if selected:
        plt.rcParams.update(
            {
                "font.size": 8,
                "axes.edgecolor": "#333333",
                "axes.linewidth": 0.8,
                "axes.grid": True,
                "grid.color": "#cccccc",
                "grid.linewidth": 0.4,
                "grid.linestyle": "--",
            }
        )

        fig, axes = plt.subplots(1, 2, figsize=(8, 4), dpi=200)

        ax1, ax2 = axes

        colors = plt.cm.tab10(np.linspace(0, 1, 10))

        for i, name in enumerate(selected):
            vals = np.sort(distributions[name])
            n = len(vals)
            cdf = np.arange(1, n + 1) / n * 100

            color = colors[list(distributions.keys()).index(name) % 10]

            ax1.step(
                vals,
                cdf,
                where="post",
                linewidth=1.5,
                label=name,
                color=color,
            )

            ax2.step(
                vals,
                cdf,
                where="post",
                linewidth=1.5,
                label=name,
                color=color,
            )

        # Log-scale axis
        ax2.set_xscale("log")

        xmin = min(np.min(distributions[s]) for s in selected)
        xmax = max(np.max(distributions[s]) for s in selected)

        xmin = 10 ** np.floor(np.log10(xmin))
        xmax = 10 ** np.ceil(np.log10(xmax))

        ax2.set_xlim(xmin, xmax)

        ax2.xaxis.set_major_locator(LogLocator(base=10))
        ax2.xaxis.set_major_formatter(LogFormatterMathtext(base=10))
        ax2.xaxis.set_minor_locator(LogLocator(base=10, subs=[]))

        for ax in [ax1, ax2]:

            for y_ref, label in [(16, "D16"), (50, "D50"), (84, "D84")]:
                ax.axhline(
                    y=y_ref,
                    color="gray",
                    linestyle=":",
                    linewidth=0.5,
                )

            ax.set_xlabel("Grain size (mm)")
            ax.set_ylabel("Cumulative percentage (%)")
            ax.set_ylim(0, 100)
            ax.set_box_aspect(1)

            ax.legend(
                fontsize=7,
                frameon=False,
            )

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

#        ax1.set_title("Linear X-axis")
#        ax2.set_title("Log X-axis")

        fig.tight_layout()

        st.pyplot(fig, use_container_width=False)

        buf = io.BytesIO()
        fig.savefig(
            buf,
            format="png",
            dpi=300,
            bbox_inches="tight",
        )
        buf.seek(0)

        st.download_button(
            label="Download plot as PNG",
            data=buf,
            file_name="grain_size_cdf.png",
            mime="image/png",
        )

    else:
        st.warning("Select at least one sample to display its CDF.")

else:
    st.info("Add data above to generate the plot.")
