import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import ClaimSubmission from './pages/ClaimSubmission';
import ClaimResult from './pages/ClaimResult';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Landing Page is now the absolute front door */}
        <Route path="/" element={<LandingPage />} />
        
        {/* The internal SaaS tool pages */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/submit" element={<ClaimSubmission />} />
        <Route path="/claim/:id" element={<ClaimResult />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;