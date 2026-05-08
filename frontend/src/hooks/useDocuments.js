import { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';

export const useDocuments = (organizationId) => {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchDocuments = useCallback(async () => {
        if (!organizationId) return;
        try {
            setLoading(true);
            const response = await api.get(`/api/documents/?organization=${organizationId}`);
            setDocuments(response.data);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to fetch documents');
        } finally {
            setLoading(false);
        }
    }, [organizationId]);

    useEffect(() => {
        fetchDocuments();
    }, [fetchDocuments]);

    const uploadDocument = async (formData) => {
        formData.append('organization', organizationId);
        const response = await api.post('/api/documents/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        fetchDocuments();
        return response.data;
    };

    const updateDocument = async (id, data) => {
        const response = await api.patch(`/api/documents/${id}/`, data);
        fetchDocuments();
        return response.data;
    };

    const deleteDocument = async (id) => {
        await api.delete(`/api/documents/${id}/`);
        fetchDocuments();
    };

    return {
        documents,
        loading,
        error,
        refetch: fetchDocuments,
        uploadDocument,
        updateDocument,
        deleteDocument
    };
};

export default useDocuments;
