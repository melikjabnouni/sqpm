import OeePanel from "./OeePanel";
import SpcChart from "./SpcChart";

export default function App() {
  return (
    <div className="dashboard">
      <h1>SQPM — Line 1 Monitor</h1>
      <OeePanel />
      <SpcChart />
    </div>
  );
}