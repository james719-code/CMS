import { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';

export const useOrganizations = (filters = {}) => {
    const [organizations, setOrganizations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchOrganizations = useCallback(async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            if (filters.status) params.append('status', filters.status);
            if (filters.search) params.append('search', filters.search);

            const response = await api.get(`/api/organizations/?${params}`);
            setOrganizations(response.data);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to fetch organizations');
        } finally {
            setLoading(false);
        }
    }, [filters.status, filters.search]);

    useEffect(() => {
        fetchOrganizations();
    }, [fetchOrganizations]);

    const approveOrg = async (id) => {
        await api.post(`/api/organizations/${id}/approve/`);
        fetchOrganizations();
    };

    const rejectOrg = async (id) => {
        await api.post(`/api/organizations/${id}/reject/`);
        fetchOrganizations();
    };

    const suspendOrg = async (id) => {
        await api.post(`/api/organizations/${id}/suspend/`);
        fetchOrganizations();
    };

    const reactivateOrg = async (id) => {
        await api.post(`/api/organizations/${id}/reactivate/`);
        fetchOrganizations();
    };

    const deleteOrg = async (id) => {
        await api.delete(`/api/organizations/${id}/`);
        fetchOrganizations();
    };

    return {
        organizations,
        loading,
        error,
        refetch: fetchOrganizations,
        approveOrg,
        rejectOrg,
        suspendOrg,
        reactivateOrg,
        deleteOrg
    };
};

export default useOrganizations;
