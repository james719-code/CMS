import { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';

export const useEvents = (organizationId = null, options = {}) => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchEvents = useCallback(async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            if (organizationId) params.append('organization', organizationId);
            if (options.upcoming) params.append('upcoming', 'true');
            if (options.past) params.append('past', 'true');

            const response = await api.get(`/api/events/?${params}`);
            setEvents(response.data);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to fetch events');
        } finally {
            setLoading(false);
        }
    }, [organizationId, options.upcoming, options.past]);

    useEffect(() => {
        fetchEvents();
    }, [fetchEvents]);

    const createEvent = async (eventData) => {
        const response = await api.post('/api/events/', eventData);
        fetchEvents();
        return response.data;
    };

    const updateEvent = async (eventId, eventData) => {
        const response = await api.patch(`/api/events/${eventId}/`, eventData);
        fetchEvents();
        return response.data;
    };

    const deleteEvent = async (eventId) => {
        await api.delete(`/api/events/${eventId}/`);
        fetchEvents();
    };

    const getMyEvents = async () => {
        const response = await api.get('/api/events/my_events/');
        return response.data;
    };

    return {
        events,
        loading,
        error,
        refetch: fetchEvents,
        createEvent,
        updateEvent,
        deleteEvent,
        getMyEvents
    };
};

export default useEvents;
