import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import DepartmentsPage from './pages/DepartmentsPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>University Club Management System</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<DepartmentsPage />} />
          </Routes>
        </main>
        <footer className="App-footer">
          <p>&copy; 2024 University CMS. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
