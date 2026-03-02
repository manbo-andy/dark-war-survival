import { Routes, Route } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import DashboardPage from "./pages/DashboardPage";
import PlayersPage from "./pages/PlayersPage";
import ScanPage from "./pages/ScanPage";
import ReportsPage from "./pages/ReportsPage";
import EventsPage from "./pages/EventsPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="players" element={<PlayersPage />} />
        <Route path="scan" element={<ScanPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="events" element={<EventsPage />} />
      </Route>
    </Routes>
  );
}
