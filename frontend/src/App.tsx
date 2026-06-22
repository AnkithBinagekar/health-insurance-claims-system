import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ClaimSubmission from './pages/ClaimSubmission';
import ClaimResult from './pages/ClaimResult';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/submit" element={<ClaimSubmission />} />
        <Route path="/claim/:id" element={<ClaimResult />} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;