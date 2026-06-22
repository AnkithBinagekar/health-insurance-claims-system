import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ClaimSubmission from './pages/ClaimSubmission';
import ClaimResult from './pages/ClaimResult';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
        <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
          <div className="max-w-5xl mx-auto flex items-center">
            <h1 className="text-xl font-bold text-indigo-600 tracking-tight">Plum AI Pod</h1>
            <span className="ml-3 text-sm text-gray-500 font-medium">Claims Processing Engine</span>
          </div>
        </header>

        <main className="max-w-5xl mx-auto p-6">
          <Routes>
            <Route path="/" element={<ClaimSubmission />} />
            <Route path="/claim/:id" element={<ClaimResult />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;