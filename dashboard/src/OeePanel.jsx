import { usePolling } from "./usePolling";

function MetricBar({ label, value }) {
  const displayValue = value ?? 0;
  const color = displayValue >= 85 ? "#4caf50" : displayValue >= 60 ? "#ffb300" : "#f44336";

  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span>{label}</span>
        <span>{value !== null ? `${value}%` : "—"}</span>
      </div>
      <div style={{ background: "#2a2e3a", borderRadius: 4, height: 8 }}>
        <div
          style={{
            width: `${displayValue}%`,
            background: color,
            height: "100%",
            borderRadius: 4,
            transition: "width 0.5s ease",
          }}
        />
      </div>
    </div>
  );
}

export default function OeePanel() {
  const { data, error } = usePolling("/metrics/oee");

  if (error) {
    return (
      <div className="panel">
        <h2>OEE</h2>
        <p style={{ color: "#f44336" }}>Error reaching API: {error}</p>
      </div>
    );
  }

  if (!data || data.oee === null) {
    return (
      <div className="panel">
        <h2>OEE</h2>
        <p style={{ color: "#a0a4b0" }}>Waiting for data...</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>OEE — {data.units_produced} units produced</h2>
      <MetricBar label="Availability" value={data.availability} />
      <MetricBar label="Performance" value={data.performance} />
      <MetricBar label="Quality" value={data.quality} />
      <div style={{ marginTop: 20, fontSize: "1.8rem", fontWeight: 600 }}>
        {data.oee}% <span style={{ fontSize: "0.9rem", color: "#a0a4b0", fontWeight: 400 }}>Overall OEE</span>
      </div>
    </div>
  );
}