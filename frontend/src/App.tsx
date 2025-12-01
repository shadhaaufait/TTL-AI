import { Routes, Route} from "react-router-dom";
import "./App.css"; // keep your existing styles
import Insights from "./components/Insights";

export default function App() {
  return (
    <div className="app-root">

      <main className="app-content">
        <Routes>
          <Route path="/" element={<Insights />} />
        </Routes>
      </main>
    </div>
  );
}
