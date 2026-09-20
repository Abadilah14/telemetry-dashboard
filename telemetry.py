from pathlib import Path
import pandas as pd
import streamlit as st


CSV_PATH = Path(__file__).with_name("telemetry_raw (1).csv")
TELEMETRY_COLUMNS = ["TEAM_ID","MISSION_TIME","PACKET_COUNT","ALTITUDE","PRESSURE","TEMPERATURE","VOLTAGE","ROLL","PITCH","YAW","GPS_LAT","GPS_LON","GPS_ALT","STATE",]
NUMERIC_COLUMNS = [column for column in TELEMETRY_COLUMNS if column not in {"TEAM_ID", "STATE"}]


def read_telemetry() -> pd.DataFrame:
	try:
		data = pd.read_csv(CSV_PATH)
	except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
		return pd.DataFrame(columns=TELEMETRY_COLUMNS)

	data.columns = data.columns.str.strip().str.upper()
	for column in NUMERIC_COLUMNS:
		data[column] = pd.to_numeric(data[column], errors="coerce")
	return data[TELEMETRY_COLUMNS]


st.set_page_config(page_title="EEPISAT Telemetry", layout="wide")
st.title("Telemetry Dashboard")
st.caption("CSV stream dipantau otomatis setiap detik")


@st.fragment(run_every="1s")
def telemetry_dashboard() -> None:
	data = read_telemetry()
	if data.empty:
		st.warning("Belum ada data telemetri yang dapat dibaca.")
		return

	latest = data.iloc[-1]
	st.subheader(f"Packet terbaru: {int(latest['PACKET_COUNT'])}")
	altitude, pressure, temperature, voltage, gps, state = st.columns(6)

	altitude.metric("Altitude", f"{latest['ALTITUDE']:.2f} m")
	pressure.metric("Pressure", f"{latest['PRESSURE']:.2f} Pa")
	temperature.metric("Temperature", f"{latest['TEMPERATURE']:.2f} °C")
	voltage.metric("Voltage", f"{latest['VOLTAGE']:.2f} V")
	gps.metric("GPS LATITUDE", f"{latest['GPS_LAT']:.4f}")
	gps.metric("GPS LONGITITUDE", f"{latest['GPS_LON']:.4f}")
	state.metric("State", latest["STATE"])

	chart_data = data.set_index("MISSION_TIME")
	chart_left, chart_right = st.columns(2)
	chart_left.subheader("Altitude terhadap Waktu")
	chart_left.line_chart(chart_data[["ALTITUDE"]], y_label="Altitude (m)")
	chart_right.subheader("Temperature terhadap Waktu")
	chart_right.line_chart(chart_data[["TEMPERATURE"]], y_label="Temperature (°C)")
	
	st.subheader("Semua Parameter Telemetri")
	st.dataframe(data, width="stretch", hide_index=True)


telemetry_dashboard()
