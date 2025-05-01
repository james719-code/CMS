import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import EventsPage from './pages/EventsPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="" element={<EventsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
