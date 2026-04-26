import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { Landing } from "./Landing";
import { Workspace } from "./Workspace";
import { Analysis } from "./Analysis";
import { Plan } from "./Plan";
import { Summary } from "./Summary";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/assess" element={<Workspace />} />
        <Route path="/analyse" element={<Analysis />} />
        <Route path="/plan" element={<Plan />} />
        <Route path="/report" element={<Summary />} />
        {/* Re-route to assess if they go to workspace directly */}
        <Route path="/workspace" element={<Navigate to="/assess" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
