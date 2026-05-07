import streamlit as st
import pandas as pd
import queue

from streamlit_autorefresh import st_autorefresh
from traffic_engine import TrafficDataGenerator, ParallelAnalyzer


# ================= PAGE CONFIG ================= #
st.set_page_config(
    page_title="Real-Time Traffic Control Room",
    layout="wide"
)


# ================= CLEAN UI STYLE ================= #
st.markdown("""
<style>

/* Push content down so title visible */
.block-container {
    padding-top: 2.2rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* Compact font + dark theme */
html, body, [class*="css"] {
    font-size: 13px;
    background-color: #0b0f1a;
}

/* Title style */
.title {
    text-align: center;
    font-size: 28px;
    font-weight: 800;
    color: #38bdf8;
    padding: 8px;
    border-bottom: 1px solid #1e293b;
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 12px;
    color: #94a3b8;
    margin-top: -6px;
}

</style>
""", unsafe_allow_html=True)


# ================= TITLE ================= #
st.markdown("""
<div class="title">
🚦 Real-Time Traffic Streaming Control Room
</div>

<div class="subtitle">
🟢 System Active | 🟡 Monitoring | 🔴 Alerts Enabled
</div>
""", unsafe_allow_html=True)


# ================= STATE ================= #
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.queue = queue.Queue(maxsize=1000)
    st.session_state.results = {}


# ================= SIDEBAR ================= #
with st.sidebar:
    st.header("⚙ Control Panel")

    def start():
        st.session_state.started = True

        st.session_state.producer = TrafficDataGenerator(st.session_state.queue)
        st.session_state.consumer = ParallelAnalyzer(
            st.session_state.queue,
            st.session_state.results
        )

        st.session_state.producer.start()
        st.session_state.consumer.start(4)

    def stop():
        st.session_state.started = False

        if "producer" in st.session_state:
            st.session_state.producer.stop()

        if "consumer" in st.session_state:
            st.session_state.consumer.stop()

    st.button("▶ Start System", on_click=start)
    st.button("■ Stop System", on_click=stop)

    st.divider()

    st.metric("Status", "LIVE" if st.session_state.started else "OFFLINE")
    st.metric("Queue", st.session_state.queue.qsize())


# ================= AUTO REFRESH ================= #
if st.session_state.started:
    st_autorefresh(interval=500, key="refresh")


# ================= TOP METRICS ================= #
q = st.session_state.queue.qsize()

c1, c2, c3, c4 = st.columns(4)

c1.metric("SYSTEM", "ACTIVE" if st.session_state.started else "OFF")
c2.metric("QUEUE", q)
c3.metric("PROCESSED", len(st.session_state.results))
c4.metric("WORKERS", "4")

st.divider()


# ================= MAIN LAYOUT ================= #
left, right = st.columns([3.5, 1.5])


# ================= LEFT: LIVE STREAM ================= #
with left:

    st.subheader("📡 Live Traffic Stream")

    rows = []
    latest = list(st.session_state.results.items())[-5:]

    for cam, data in latest:

        speed = data["actual_speed"]
        anomaly = data["is_anomaly"]

        # 🚦 Traffic Light Logic
        if anomaly:
            status = "🔴 CRITICAL"
        elif speed < 40:
            status = "🟡 SLOW"
        else:
            status = "🟢 CLEAR"

        rows.append([
            cam,
            data["worker"],
            speed,
            data["vehicle_count"],
            status
        ])

    df = pd.DataFrame(rows, columns=[
        "Camera",
        "Worker",
        "Speed",
        "Vehicles",
        "Status"
    ])

    st.dataframe(df, use_container_width=True, height=240)


# ================= RIGHT: SYSTEM HEALTH ================= #
with right:

    st.subheader("🧠 System Health")

    if q < 30:
        st.success("🟢 NORMAL FLOW")
    elif q < 70:
        st.warning("🟡 MODERATE LOAD")
    else:
        st.error("🔴 HIGH TRAFFIC")

    st.progress(min(q / 100, 1.0))

    st.caption("Queue pressure indicator")


st.divider()


# ================= WORKERS ================= #
st.subheader("👷 Worker Activity")

cols = st.columns(4)
colors = ["🟢", "🟡", "🔵", "🟣"]

if "consumer" in st.session_state:
    for i, (w, v) in enumerate(st.session_state.consumer.worker_stats.items()):
        with cols[i]:
            st.metric(f"{colors[i]} {w}", v)


st.divider()


# ================= LOGS ================= #
st.subheader("📜 System Logs")

log_box = st.container(height=140)

with log_box:
    st.write("System running in real-time streaming mode...")

    for cam, data in list(st.session_state.results.items())[:3]:
        st.write(f"{cam} → {data['worker']} | {data['actual_speed']} km/h")


st.caption("Real-Time Traffic Control Room — Parallel Streaming System 🚀")