import matplotlib
matplotlib.use("TkAgg")
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.lines import Line2D


def main():
    # ---------------------------------------------------------------------
    # 1. Load CSV
    # ---------------------------------------------------------------------
    # Make sure the filename matches your actual file name
    csv_file = "flight_data - Data.csv"  # rename your file to this, or change the string
    df = pd.read_csv(csv_file)

    # ---------------------------------------------------------------------
    # 2. Time handling
    # ---------------------------------------------------------------------
    # Parse the human-readable time into a datetime column
    df["time"] = pd.to_datetime(df["EPOCH to date"])

    # Relative time in seconds from first sample (nice for plotting on x-axis)
    df["t_rel_s"] = (df["time"] - df["time"].iloc[0]).dt.total_seconds()
    launch_time = pd.to_datetime("2025-11-22 09:57:00")
    burst_time = pd.to_datetime("2025-11-22 10:47:00")
    df["minutes_since_launch"] = (df["time"] - launch_time).dt.total_seconds() / 60.0

    # ---------------------------------------------------------------------
    # 2b. Load additional sample data (kept separate)
    # ---------------------------------------------------------------------
    samples_csv = "samples_10_hz_0.csv"
    samples_df = pd.read_csv(samples_csv)
    samples_df["time_mag"] = pd.to_datetime(samples_df["EPOCH to date"])
    samples_df["t_rel_mag_s"] = (samples_df["time_mag"] - samples_df["time_mag"].iloc[0]).dt.total_seconds()

    # ---------------------------------------------------------------------
    # 3. Accelerometer axis remap (based on your note)
    #    current y = -true z
    #    current z = -true y
    # ---------------------------------------------------------------------
    df["accel_x_true"] = df["accel_x"]
    df["accel_y_true"] = -df["accel_z"]
    df["accel_z_true"] = -df["accel_y"]

    # ---------------------------------------------------------------------
    # 4. Moving averages for accelerometer (in samples)
    # ---------------------------------------------------------------------
    window = 10  # adjust for more/less smoothing

    for axis in ["accel_x_true", "accel_y_true", "accel_z_true"]:
        df[f"{axis}_ma"] = df[axis].rolling(window, min_periods=1).mean()

    # ---------------------------------------------------------------------
    # 5. Convenience: grab every column into a dict for easy use
    #    (Everything is still also in df, this is just for convenience.)
    # ---------------------------------------------------------------------
    data = {col: df[col] for col in df.columns}

    # At this point, EVERYTHING is "ready to be plotted".
    # Example plots below just to demonstrate usage.

    

    # ---------------------------------------------------------------------
    # Plot 1: battery voltage vs relative time
    # ---------------------------------------------------------------------
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(df["t_rel_s"], data["batt_voltage"])
    ax2.set_xlabel("Time since start [s]")
    ax2.set_ylabel("Battery Voltage [V]")
    ax2.set_title("Battery Voltage vs Time")
    ax2.grid(True)
    fig2.tight_layout()
    fig2.savefig("plot1_battery_voltage.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Plot 2: supply currents vs absolute time
    # ---------------------------------------------------------------------
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(df["time"], data["i_3v3"], label="3V3 current")
    ax3.plot(df["time"], data["i_5v0"], label="5V0 current")
    ax3.plot(df["time"], data["i_vbatt"], label="Battery current")
    ax3.set_xlabel("Time of Day on Nov. 22nd, 2025")
    ax3.set_ylabel("Current [A]")
    ax3.set_title("Supply Currents vs Time")
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax3.legend()
    fig3.autofmt_xdate()
    fig3.tight_layout()
    fig3.savefig("plot2_supply_currents.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Plot 3: temperature vs altitude (no grid)
    # ---------------------------------------------------------------------
    fig4, ax4 = plt.subplots(figsize=(10, 4))
    cutoff = pd.to_datetime("2025-11-22 10:35:00")
    df_temp = df[df["time"] <= cutoff]
    if df_temp.empty:
        df_temp = df.copy()
    x = df_temp["bme_altitude"].to_numpy()
    y = df_temp["tmp1_clean"].to_numpy()
    mask = np.isfinite(x) & np.isfinite(y)
    ax4.plot(x, y)

    # Linear fit
    m, b = np.polyfit(x[mask], y[mask], 1)
    x_line = np.linspace(x[mask].min(), x[mask].max(), 100)
    y_line = m * x_line + b
    ax4.plot(x_line, y_line, color="tab:red", linestyle="--")

    ax4.text(
        0.98,
        0.98,
        f"Fit: T = {m:.3f} * Alt + {b:.3f}",
        transform=ax4.transAxes,
        va="top",
        ha="right",
        fontsize=10,
    )
    ax4.set_xlabel("BME Altitude")
    ax4.set_ylabel("TMP1 Temperature [°C]")
    ax4.set_title("Temperature vs Altitude")
    ax4.grid(False)
    fig4.tight_layout()
    fig4.savefig("plot3_temp_vs_bme_altitude.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Plot 4: BME pressure vs BME altitude (no grid)
    # ---------------------------------------------------------------------
    fig5, ax5 = plt.subplots(figsize=(10, 4))
    ax5.plot(data["bme_altitude"], data["bme_pressure"], color="tab:blue")
    ax5.set_xlabel("BME Altitude [m]")
    ax5.set_ylabel("BME Pressure [hPa]")
    ax5.set_title("BME Pressure vs Altitude")
    ax5.grid(False)
    fig5.tight_layout()
    fig5.savefig("plot4_bme_pressure_vs_altitude.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Plot 5: TMP1 and TMP2 vs time
    # ---------------------------------------------------------------------
    fig6, ax6 = plt.subplots(figsize=(10, 4))
    ax6.plot(df["time"], data["tmp1_clean"], label="TMP1 Clean")
    ax6.plot(df["time"], data["tmp2_clean"], label="TMP2 Clean")
    ax6.set_xlabel("Time of Day on Nov. 22nd, 2025")
    ax6.set_ylabel("Temperature [°C]")
    ax6.set_title("TMP1 and TMP2 vs Time")
    ax6.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax6.legend()
    fig6.autofmt_xdate()
    fig6.tight_layout()
    fig6.savefig("plot5_tmp1_tmp2_vs_time.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Plot 6: stacked altitude, temps, CPU temp (shared x-axis)
    # ---------------------------------------------------------------------
    fig7, axes7 = plt.subplots(3, 1, figsize=(11, 10), sharex=True)

    axes7[0].plot(df["time"], data["bme_altitude"], color="tab:blue", label="BME Altitude")
    axes7[0].set_ylabel("Altitude [m]")
    axes7[0].set_title("BME Altitude")
    axes7[0].legend()

    launch_time = pd.to_datetime("2025-11-22 09:57:00")
    for ax in axes7:
        ax.axvline(launch_time, color="black", linestyle="--", linewidth=1.2, alpha=0.8)
    axes7[0].text(
        launch_time,
        0.98,
        "Launch ~9:57 AM",
        transform=axes7[0].get_xaxis_transform(),
        va="top",
        ha="center",
        fontsize=10,
        backgroundcolor="white",
    )

    axes7[1].plot(df["time"], data["tmp1_clean"], color="tab:orange", label="TMP1 Clean")
    axes7[1].plot(df["time"], data["tmp2_clean"], color="tab:green", label="TMP2 Clean")
    axes7[1].set_ylabel("Temp [°C]")
    axes7[1].set_title("TMP1 and TMP2")
    axes7[1].legend()

    axes7[2].plot(df["time"], data["cpu_temp"], color="tab:gray", label="CPU Temp")
    axes7[2].set_ylabel("Temp [°C]")
    axes7[2].set_xlabel("Time of Day on Nov. 22nd, 2025")
    axes7[2].set_title("CPU Temperature")
    axes7[2].legend()
    axes7[2].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    for ax in axes7:
        ax.grid(False)

    fig7.autofmt_xdate()
    fig7.tight_layout()
    fig7.savefig("plot6_stacked_alt_temps_vs_time.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Plot 7: stacked voltages vs time (shared x-axis)
    # ---------------------------------------------------------------------
    fig8, axes8 = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

    for ax in axes8:
        ax.axvline(launch_time, color="black", linestyle="--", linewidth=1.2, alpha=0.8)

    axes8[0].plot(df["time"], data["batt_voltage"], color="tab:red", label="Battery Voltage")
    axes8[0].set_ylabel("Volts [V]")
    axes8[0].set_title("Battery Voltage")
    axes8[0].legend()
    axes8[0].text(
        launch_time,
        0.98,
        "Launch ~9:57 AM",
        transform=axes8[0].get_xaxis_transform(),
        va="top",
        ha="center",
        fontsize=10,
        backgroundcolor="white",
    )

    axes8[1].plot(df["time"], data["v_3v3"], color="tab:purple", label="3V3")
    axes8[1].plot(df["time"], data["v_5v0"], color="tab:brown", label="5V0")
    axes8[1].set_ylabel("Volts [V]")
    axes8[1].set_xlabel("Time of Day on Nov. 22nd, 2025")
    axes8[1].set_title("3V3 and 5V0")
    axes8[1].legend()
    axes8[1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    for ax in axes8:
        ax.grid(False)

    fig8.autofmt_xdate()
    fig8.tight_layout()
    fig8.savefig("plot7_stacked_voltages_vs_time.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Plot 7a: stacked altitude, temps, battery vs minutes since launch
    # ---------------------------------------------------------------------
    def last_change_idx(series):
        s = series.dropna()
        if s.empty:
            return None
        diff = s.ne(s.shift())
        idxs = diff[diff].index
        if len(idxs) == 0:
            return s.index[-1]
        return idxs.max()

    burst_minutes = (burst_time - launch_time).total_seconds() / 60.0

    fig7a, axes7a = plt.subplots(3, 1, figsize=(11, 10), sharex=True)

    axes7a[0].plot(df["minutes_since_launch"], data["bme_altitude"], color="tab:blue", label="BME Altitude")
    axes7a[0].set_ylabel("Altitude [m]")
    axes7a[0].set_title("BME Altitude")
    axes7a[0].legend()

    axes7a[1].plot(df["minutes_since_launch"], data["tmp1_clean"], color="tab:orange", label="TMP1")
    axes7a[1].plot(df["minutes_since_launch"], data["tmp2_clean"], color="tab:green", label="TMP2")
    axes7a[1].plot(df["minutes_since_launch"], data["bme_temp"], color="tab:red", label="BME Temp")
    axes7a[1].set_ylabel("Temp [°C]")
    axes7a[1].set_title("Temperatures")
    axes7a[1].legend()

    axes7a[2].plot(df["minutes_since_launch"], data["batt_voltage"], color="tab:red", label="Battery Voltage")
    axes7a[2].set_ylabel("Volts [V]")
    axes7a[2].set_xlabel("Minutes Since Launch (0 at 09:57; negative = before)")
    axes7a[2].set_title("Battery Voltage")
    axes7a[2].legend()

    for ax in axes7a:
        ax.axvline(0, color="black", linestyle="--", linewidth=1.2, alpha=0.8)
        ax.axvline(burst_minutes, color="black", linestyle="--", linewidth=1.2, alpha=0.8)
    axes7a[0].text(
        0,
        0.98,
        "Launch ~9:57 AM",
        transform=axes7a[0].get_xaxis_transform(),
        va="top",
        ha="center",
        fontsize=10,
        backgroundcolor="white",
    )
    axes7a[0].text(
        burst_minutes,
        0.9,
        "Burst ~10:47 AM",
        transform=axes7a[0].get_xaxis_transform(),
        va="top",
        ha="right",
        fontsize=10,
        backgroundcolor="white",
    )

    flat_series = [
        (axes7a[0], "bme_altitude"),
        (axes7a[1], "tmp1_clean"),
        (axes7a[1], "tmp2_clean"),
        (axes7a[1], "bme_temp"),
        (axes7a[2], "batt_voltage"),
    ]
    freeze_handles = []
    for ax, col in flat_series:
        idx_last = last_change_idx(df[col])
        if idx_last is not None and idx_last in df.index:
            handle = ax.plot(
                df.loc[idx_last, "minutes_since_launch"],
                df.loc[idx_last, col],
                marker="x",
                color="red",
                markersize=8,
                mew=2,
                linestyle="None",
            )[0]
            freeze_handles.append(handle)
    if freeze_handles:
        axes7a[0].legend([freeze_handles[0]], ["Data collection freezes"], loc="upper center")

    # End of data collection marker
    end_time = pd.to_datetime("2025-11-22 10:50:32")
    end_minutes = (end_time - launch_time).total_seconds() / 60.0
    for ax in axes7a:
        ax.axvline(end_minutes, color="gray", linestyle="--", linewidth=1.0, alpha=0.8)
    axes7a[0].text(
        end_minutes,
        0.8,
        "Data collection stops ~10:50 AM",
        transform=axes7a[0].get_xaxis_transform(),
        va="top",
        ha="right",
        fontsize=10,
        backgroundcolor="white",
    )

    fig7a.tight_layout()
    fig7a.savefig("plot7a_stack_alt_temps_batt_minutes.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Plot 8a: BME temp, TMP1 clean, TMP2 clean vs time (time of day)
    # ---------------------------------------------------------------------
    fig8a, ax8a = plt.subplots(figsize=(10, 4))
    ax8a.plot(df["time"], data["bme_temp"], label="BME Temp")
    ax8a.plot(df["time"], data["tmp1_clean"], label="TMP1 Clean")
    ax8a.plot(df["time"], data["tmp2_clean"], label="TMP2 Clean")
    ax8a.set_xlabel("Time of Day on Nov. 22nd, 2025")
    ax8a.set_ylabel("Temperature [°C]")
    ax8a.set_title("BME/TMP1/TMP2 vs Time")
    ax8a.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax8a.legend()
    fig8a.autofmt_xdate()
    fig8a.tight_layout()
    fig8a.savefig("plot8a_temps_vs_time.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Plot 8: 3V3 voltage vs 3V3 regulator temperature
    # ---------------------------------------------------------------------
    fig9, ax9 = plt.subplots(figsize=(10, 4))
    df_reg3 = df[["reg_temp_3v3", "v_3v3"]].dropna().sort_values("reg_temp_3v3")
    ax9.scatter(df_reg3["reg_temp_3v3"], df_reg3["v_3v3"], color="tab:purple", alpha=0.3, s=16, label="Samples")
    if not df_reg3.empty:
        x_min, x_max = df_reg3["reg_temp_3v3"].min(), df_reg3["reg_temp_3v3"].max()
        if x_min != x_max:
            m3, b3 = np.polyfit(df_reg3["reg_temp_3v3"], df_reg3["v_3v3"], 1)
            x_line = np.array([x_min, x_max])
            ax9.plot(x_line, m3 * x_line + b3, color="tab:purple", linewidth=1.6, label="Linear fit")
    ax9.set_xlabel("3V3 Regulator Temperature [°C]")
    ax9.set_ylabel("3V3 Voltage [V]")
    ax9.set_title("3V3 Voltage vs 3V3 Regulator Temperature")
    ax9.legend()
    ax9.grid(False)
    fig9.tight_layout()
    fig9.savefig("plot8_3v3_voltage_vs_regtemp.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Plot 9: 5V0 voltage vs 5V0 regulator temperature
    # ---------------------------------------------------------------------
    fig10, ax10 = plt.subplots(figsize=(10, 4))
    df_reg5 = df[["reg_temp_5v0", "v_5v0"]].dropna().sort_values("reg_temp_5v0")
    ax10.scatter(df_reg5["reg_temp_5v0"], df_reg5["v_5v0"], color="tab:brown", alpha=0.3, s=16, label="Samples")
    if not df_reg5.empty:
        x_min5, x_max5 = df_reg5["reg_temp_5v0"].min(), df_reg5["reg_temp_5v0"].max()
        if x_min5 != x_max5:
            m5, b5 = np.polyfit(df_reg5["reg_temp_5v0"], df_reg5["v_5v0"], 1)
            x_line5 = np.array([x_min5, x_max5])
            ax10.plot(x_line5, m5 * x_line5 + b5, color="tab:brown", linewidth=1.6, label="Linear fit")
    ax10.set_xlabel("5V0 Regulator Temperature [°C]")
    ax10.set_ylabel("5V0 Voltage [V]")
    ax10.set_title("5V0 Voltage vs 5V0 Regulator Temperature")
    ax10.legend()
    ax10.grid(False)
    fig10.tight_layout()
    fig10.savefig("plot9_5v0_voltage_vs_regtemp.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Plot 10: Magnetometer (scaled) vs time from samples_10_hz_0.csv
    # ---------------------------------------------------------------------
    fig11, axes11 = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    mag_minutes = (samples_df["time_mag"] - launch_time).dt.total_seconds() / 60.0
    colors = {"Mag_x_scaled": "tab:red", "Mag_y_scaled": "tab:green", "Mag_z_scaled": "tab:blue"}
    labels = {"Mag_x_scaled": "x-axis", "Mag_y_scaled": "y-axis", "Mag_z_scaled": "z-axis"}
    for ax in axes11:
        ax.axvline(0, color="black", linestyle="--", linewidth=1.2, alpha=0.8)
        axes11[0].text(
            0,
            0.98,
            "Launch ~9:57 AM",
            transform=axes11[0].get_xaxis_transform(),
            va="top",
            ha="center",
            fontsize=10,
            backgroundcolor="white",
        )
    for col in ["Mag_x_scaled", "Mag_y_scaled", "Mag_z_scaled"]:
        axes11[0].scatter(mag_minutes, samples_df[col], color=colors[col], alpha=0.3, s=14)
        roll = samples_df[col].rolling(10, min_periods=1).mean()
        axes11[0].plot(mag_minutes, roll, color=colors[col], linewidth=1.6)
    axes11[0].set_ylabel("Magnetic Field [uT]")
    axes11[0].set_title("RM3100 Magnetic Field Data [uT] vs Minutes Since Launch")
    handles_top = [
        Line2D([0], [0], color=colors[col], marker="o", linestyle="-", markersize=6, markerfacecolor=colors[col], alpha=0.8, label=labels[col])
        for col in ["Mag_x_scaled", "Mag_y_scaled", "Mag_z_scaled"]
    ]
    axes11[0].legend(handles=handles_top, loc="lower right")

    # Mark end of data collection
    if not samples_df.empty:
        last_time = samples_df["time_mag"].max()
        last_minutes = (last_time - launch_time).total_seconds() / 60.0
        for ax in axes11:
            ax.axvline(last_minutes, color="gray", linestyle="--", linewidth=1.0, alpha=0.8)
        axes11[0].text(
            last_minutes,
            0.98,
            "Data collection stops ~10:35 AM",
            transform=axes11[0].get_xaxis_transform(),
            va="top",
            ha="right",
            fontsize=10,
            backgroundcolor="white",
        )

    if "Magnetic_field_magnitude (uT)" in samples_df.columns:
        mag_col = "Magnetic_field_magnitude (uT)"
        axes11[1].scatter(mag_minutes, samples_df[mag_col], color="tab:purple", alpha=0.3, s=14, label="Magnitude samples")
        roll_mag = samples_df[mag_col].rolling(10, min_periods=1).mean()
        axes11[1].plot(mag_minutes, roll_mag, color="tab:purple", linewidth=1.6, label="Magnitude moving avg")
        axes11[1].set_ylabel("Magnetic Field Magnitude [uT]")
        axes11[1].set_title("Magnetic Field Magnitude vs Minutes Since Launch")
        axes11[1].legend()

    axes11[1].set_xlabel("Minutes Since Launch")

    fig11.tight_layout()
    fig11.savefig("plot10_mag_scaled_and_magnitude_vs_time.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Plot 11: 3D scatter of magnetometer scaled axes
    # ---------------------------------------------------------------------
    mag_cols = ["Mag_x_scaled", "Mag_y_scaled", "Mag_z_scaled", "time_mag"]
    df_mag3d = samples_df[mag_cols].dropna()
    fig12 = plt.figure(figsize=(8, 6))
    ax12 = fig12.add_subplot(111, projection="3d")
    if not df_mag3d.empty:
        t0 = df_mag3d["time_mag"].min()
        time_seconds = (df_mag3d["time_mag"] - t0).dt.total_seconds()
        sc = ax12.scatter(
            df_mag3d["Mag_x_scaled"],
            df_mag3d["Mag_y_scaled"],
            df_mag3d["Mag_z_scaled"],
            c=time_seconds,
            cmap="viridis",
            alpha=0.6,
            s=12,
        )
        cbar = fig12.colorbar(sc, ax=ax12, shrink=0.7, pad=0.1)
        cbar.set_label(f"Seconds since 9:55:06 AM on 11/22/25")
    ax12.set_xlabel("x-axis [uT]")
    ax12.set_ylabel("y-axis [uT]")
    ax12.set_zlabel("z-axis [uT]")
    ax12.set_title("RM3100 Magnetometer 3D Scatter")
    fig12.tight_layout()
    fig12.savefig("plot11_mag_scaled_3d.png", format="png", dpi=300, bbox_inches="tight")

    # ---------------------------------------------------------------------
    # Stacked Plot: Voltages + Currents vs Minutes Since Launch
    # ---------------------------------------------------------------------
    fig, (ax_v, ax_i) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # -------------------------
    # VOLTAGES
    # -------------------------
    ax_v.plot(df["minutes_since_launch"], df["batt_voltage"], label="Battery", linewidth=1.2)

    ax_v.set_ylabel("Voltage [V]")
    ax_v.set_title("Battery Voltage vs Time")
    ax_v.grid(True)
    ax_v.legend(loc="upper right")

    # Mark launch
    ax_v.axvline(0, color="black", linestyle="--", linewidth=1.2)
    ax_v.text(0, 0.98, "Launch ~09:57", transform=ax_v.get_xaxis_transform(),
            ha="center", va="top", backgroundcolor="white")

    # Mark burst
    burst_minutes = (burst_time - launch_time).total_seconds() / 60
    ax_v.axvline(burst_minutes, color="black", linestyle="--", linewidth=1.2)
    ax_v.text(burst_minutes, 0.98, "Burst ~10:47", transform=ax_v.get_xaxis_transform(),
            ha="right", va="top", backgroundcolor="white")

    # -------------------------
    # CURRENTS
    # -------------------------
    ax_i.plot(df["minutes_since_launch"], df["i_3v3"], label="3V3 current", linewidth=1.2)
    ax_i.plot(df["minutes_since_launch"], df["i_5v0"], label="5V0 current", linewidth=1.2)
    ax_i.plot(df["minutes_since_launch"], df["i_vbatt"], label="Battery current", linewidth=1.2)

    ax_i.set_xlabel("Minutes Since Launch")
    ax_i.set_ylabel("Current [A]")
    ax_i.set_title("Supply Currents vs Time")
    ax_i.grid(True)
    ax_i.legend(loc="upper right")

    # Mark launch + burst again
    ax_i.axvline(0, color="black", linestyle="--", linewidth=1.2)
    ax_i.axvline(burst_minutes, color="black", linestyle="--", linewidth=1.2)

    fig.tight_layout()
    fig.savefig("plot12_voltages_currents_vs_minutes.png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    main()
