// src/pages/EventsPage.js

import React, { useEffect, useState } from 'react';
import axios from 'axios';

const EventsPage = () => {
  // Set up state to hold the events data
  const [events, setEvents] = useState([]);
  const [error, setError] = useState(null);  // To hold any error message

  // Fetch events when the component mounts
  useEffect(() => {
    // Define the API URL
    const apiUrl = 'http://127.0.0.1:8000/api/events/';

    // Use Axios to make the API call
    axios.get(apiUrl)
      .then(response => {
        setEvents(response.data);  // Store the events data in state
      })
      .catch(error => {
        setError('Error fetching events');  // Handle errors
        console.error(error);
      });
  }, []);  // Empty dependency array means this runs once when the component mounts

  return (
    <div>
      <h1>Upcoming Events</h1>
      
      {error && <p>{error}</p>}  {/* Display error if it occurs */}
      
      {events.length === 0 ? (
        <p>No events available.</p>  // Show message if there are no events
      ) : (
        <ul>
          {events.map(event => (
            <li key={event.id}>
              <h2>{event.title}</h2>
              <p>{event.description}</p>
              <p>{event.date}</p>
              <p>{event.location}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default EventsPage;
