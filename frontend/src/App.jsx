import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import PhishingTest from './pages/PhishingTest';
import ExamPage from './pages/ExamPage';
import './App.scss';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/test" element={<PhishingTest />} />
        <Route path="/exam" element={<ExamPage />} />
      </Routes>
    </Router>
  );
}

export default App;
