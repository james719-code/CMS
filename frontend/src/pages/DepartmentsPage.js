// src/pages/DepartmentsPage.js

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './DepartmentsPage.css';

const DepartmentsPage = () => {
  const [departments, setDepartments] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Note: The API path has been updated in backend/club/urls.py to match this structure
    // If running locally, ensure backend is running on port 8000
    const apiUrl = 'http://127.0.0.1:8000/api/departments/';

    axios.get(apiUrl)
      .then(response => {
        setDepartments(response.data);
      })
      .catch(error => {
        setError('Error fetching departments. Please ensure the backend server is running.');
        console.error(error);
      });
  }, []);

  return (
    <div className="departments-container">
      <h2>Departments</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      {departments.length === 0 && !error ? (
        <p className="no-data">No departments available.</p>
      ) : (
        <div className="departments-grid">
          {departments.map(dept => (
            <div key={dept.id} className="department-card">
              <div className="card-header">
                <h3>{dept.name}</h3>
                <span className="initials">{dept.initials}</span>
              </div>
              <div className="card-body">
                <p>{dept.description}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DepartmentsPage;
