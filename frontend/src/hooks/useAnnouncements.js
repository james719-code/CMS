import { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';

export const useAnnouncements = (organizationId = null) => {
    const [announcements, setAnnouncements] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchAnnouncements = useCallback(async () => {
        try {
            setLoading(true);
            const params = organizationId ? `?organization=${organizationId}` : '';
            const response = await api.get(`/api/announcements/${params}`);
            setAnnouncements(response.data);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to fetch announcements');
        } finally {
            setLoading(false);
        }
    }, [organizationId]);

    useEffect(() => {
        fetchAnnouncements();
    }, [fetchAnnouncements]);

    const createAnnouncement = async (announcementData) => {
        const response = await api.post('/api/announcements/', {
            ...announcementData,
            organization: organizationId
        });
        fetchAnnouncements();
        return response.data;
    };

    const updateAnnouncement = async (id, announcementData) => {
        const response = await api.patch(`/api/announcements/${id}/`, announcementData);
        fetchAnnouncements();
        return response.data;
    };

    const deleteAnnouncement = async (id) => {
        await api.delete(`/api/announcements/${id}/`);
        fetchAnnouncements();
    };

    const pinAnnouncement = async (id) => {
        await api.post(`/api/announcements/${id}/pin/`);
        fetchAnnouncements();
    };

    const unpinAnnouncement = async (id) => {
        await api.post(`/api/announcements/${id}/unpin/`);
        fetchAnnouncements();
    };

    const pinnedAnnouncements = announcements.filter(a => a.is_pinned);

    return {
        announcements,
        pinnedAnnouncements,
        loading,
        error,
        refetch: fetchAnnouncements,
        createAnnouncement,
        updateAnnouncement,
        deleteAnnouncement,
        pinAnnouncement,
        unpinAnnouncement
    };
};

export default useAnnouncements;
