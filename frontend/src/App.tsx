import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import RepoDetail from "./pages/RepoDetail";
import RunDetail from "./pages/RunDetail";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Dashboard />} />
        <Route path="/repos/:id" element={<RepoDetail />} />
        <Route path="/runs/:id" element={<RunDetail />} />
      </Routes>
    </BrowserRouter>
  );
}
