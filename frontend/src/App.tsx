import { BrowserRouter, Navigate, Outlet, Route, Routes, useParams } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import HomePage from './pages/HomePage';
import BidNewPage from './pages/BidNewPage';
import BidsPage from './pages/BidsPage';
import BidDetailPage from './pages/BidDetailPage';
import SettingsPage from './pages/SettingsPage';
import HistoryPage from './pages/HistoryPage';

function AppLayout() {
  return (
    <div className="flex min-h-screen bg-[var(--page)]">
      <Sidebar />
      <main className="min-w-0 flex-1 px-4 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<BidNewPage />} />
          <Route path="/bids/new" element={<BidNewPage />} />
          <Route path="/bids" element={<BidsPage />} />
          <Route path="/bids/:id" element={<BidDetailPage />} />
          <Route path="/bids/:id/solution" element={<LegacyTab tab="solution" />} />
          <Route path="/bids/:id/wbs" element={<LegacyTab tab="plan" />} />
          <Route path="/bids/:id/schedule" element={<LegacyTab tab="plan" />} />
          <Route path="/bids/:id/quotation" element={<LegacyTab tab="plan" />} />
          <Route path="/bids/:id/proposal" element={<LegacyTab tab="proposal" />} />
          <Route path="/bids/:id/approvals" element={<LegacyTab tab="approval" />} />
          <Route path="/bids/:id/export" element={<LegacyTab tab="proposal" />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="*" element={<HomePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

function LegacyTab({ tab }: { tab: string }) {
  const { id } = useParams<{ id: string }>();
  return <Navigate replace to={`/bids/${id}?tab=${tab}`} />;
}
