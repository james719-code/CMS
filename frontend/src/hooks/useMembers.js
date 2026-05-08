import { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';

export const useMembers = (organizationId = null) => {
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchMembers = useCallback(async () => {
        try {
            setLoading(true);
            const params = organizationId ? `?organization=${organizationId}` : '';
            const response = await api.get(`/api/memberships/${params}`);
            setMembers(response.data);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to fetch members');
        } finally {
            setLoading(false);
        }
    }, [organizationId]);

    useEffect(() => {
        fetchMembers();
    }, [fetchMembers]);

    const promoteMember = async (membershipId, position = '') => {
        await api.post(`/api/memberships/${membershipId}/promote/`, { position });
        fetchMembers();
    };

    const demoteMember = async (membershipId) => {
        await api.post(`/api/memberships/${membershipId}/demote/`);
        fetchMembers();
    };

    const deactivateMember = async (membershipId) => {
        await api.post(`/api/memberships/${membershipId}/deactivate/`);
        fetchMembers();
    };

    const addMember = async (userId, role = 'member') => {
        await api.post('/api/memberships/', {
            user: userId,
            organization: organizationId,
            role
        });
        fetchMembers();
    };

    return {
        members,
        loading,
        error,
        refetch: fetchMembers,
        promoteMember,
        demoteMember,
        deactivateMember,
        addMember
    };
};

export default useMembers;
