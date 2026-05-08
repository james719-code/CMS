import { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';

export const useStatistics = (type = 'admin', organizationId = null) => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchStats = useCallback(async () => {
        try {
            setLoading(true);
            let endpoint = '/api/statistics/admin/';
            if (type === 'officer' && organizationId) {
                endpoint = `/api/statistics/officer/${organizationId}/`;
            }
            const response = await api.get(endpoint);
            setStats(response.data);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to fetch statistics');
        } finally {
            setLoading(false);
        }
    }, [type, organizationId]);

    useEffect(() => {
        fetchStats();
    }, [fetchStats]);

    return {
        stats,
        loading,
        error,
        refetch: fetchStats
    };
};

export default useStatistics;
