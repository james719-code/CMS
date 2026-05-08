import { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';

export const useMembershipRequests = (organizationId = null) => {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchRequests = useCallback(async () => {
        try {
            setLoading(true);
            const params = organizationId ? `?organization=${organizationId}` : '';
            const response = await api.get(`/api/membership-requests/${params}`);
            setRequests(response.data);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to fetch requests');
        } finally {
            setLoading(false);
        }
    }, [organizationId]);

    useEffect(() => {
        fetchRequests();
    }, [fetchRequests]);

    const approveRequest = async (requestId) => {
        await api.post(`/api/membership-requests/${requestId}/approve/`);
        fetchRequests();
    };

    const rejectRequest = async (requestId, reason = '') => {
        await api.post(`/api/membership-requests/${requestId}/reject/`, { reason });
        fetchRequests();
    };

    const createRequest = async (organizationId, message = '') => {
        await api.post('/api/membership-requests/', {
            organization: organizationId,
            message
        });
        fetchRequests();
    };

    const pendingRequests = requests.filter(r => r.status === 'pending');

    return {
        requests,
        pendingRequests,
        loading,
        error,
        refetch: fetchRequests,
        approveRequest,
        rejectRequest,
        createRequest
    };
};

export default useMembershipRequests;
