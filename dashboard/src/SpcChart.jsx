import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { usePolling } from "./usePolling";

function OutOfControlDot(props) {
  const { cx, cy, payload } = props;
  if (payload.out_of_control) {
    return <circle cx={cx} cy={cy} r={5} fill="#f44336" stroke="#fff" strokeWidth={1} />;
  }
  return <circle cx={cx} cy={cy} r={2.5} fill="#4c9aff" />;
}

export default function SpcChart() {
  const { data, error } = usePolling("/metrics/spc");

  if (error) {
    return (
      <div className="panel">
        <h2>SPC Chart — Quality Measurement</h2>
        <p style={{ color: "#f44336" }}>Error reaching API: {error}</p>
      </div>
    );
  }

  if (!data || data.points.length === 0) {
    return (
      <div className="panel">
        <h2>SPC Chart — Quality Measurement</h2>
        <p style={{ color: "#a0a4b0" }}>Waiting for data...</p>
      </div>
    );
  }

  const outOfControlCount = data.points.filter((p) => p.out_of_control).length;

  return (
    <div className="panel">
      <h2>
        SPC Chart — Quality Measurement
        {outOfControlCount > 0 && (
          <span style={{ color: "#f44336", fontWeight: 400, fontSize: "0.85rem" }}>
            {" "}
            ({outOfControlCount} out-of-control point{outOfControlCount > 1 ? "s" : ""})
          </span>
        )}
      </h2>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data.points} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2e3a" />
          <XAxis dataKey="unit_id" stroke="#a0a4b0" tick={{ fontSize: 12 }} />
          <YAxis stroke="#a0a4b0" tick={{ fontSize: 12 }} domain={["auto", "auto"]} />
          <Tooltip
            contentStyle={{ background: "#1a1d27", border: "1px solid #2a2e3a" }}
            labelFormatter={(unitId) => `Unit ${unitId}`}
          />
          <ReferenceLine y={data.center_line} stroke="#a0a4b0" strokeDasharray="4 4" label={{ value: "CL", fill: "#a0a4b0", fontSize: 11 }} />
          <ReferenceLine y={data.ucl} stroke="#f44336" strokeDasharray="4 4" label={{ value: "UCL", fill: "#f44336", fontSize: 11 }} />
          <ReferenceLine y={data.lcl} stroke="#f44336" strokeDasharray="4 4" label={{ value: "LCL", fill: "#f44336", fontSize: 11 }} />
          <Line
            type="monotone"
            dataKey="measurement"
            stroke="#4c9aff"
            strokeWidth={1.5}
            dot={<OutOfControlDot />}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}