import { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';

export const useBudget = (organizationId) => {
    const [budgets, setBudgets] = useState([]);
    const [summary, setSummary] = useState({ total_income: 0, total_expense: 0, balance: 0, transaction_count: 0 });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchBudgets = useCallback(async () => {
        if (!organizationId) return;
        try {
            setLoading(true);
            const [budgetsRes, summaryRes] = await Promise.all([
                api.get(`/api/budgets/?organization=${organizationId}`),
                api.get(`/api/budgets/summary/?organization=${organizationId}`)
            ]);
            setBudgets(budgetsRes.data);
            setSummary(summaryRes.data);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to fetch budget');
        } finally {
            setLoading(false);
        }
    }, [organizationId]);

    useEffect(() => {
        fetchBudgets();
    }, [fetchBudgets]);

    const addBudgetEntry = async (entryData) => {
        const response = await api.post('/api/budgets/', {
            ...entryData,
            organization: organizationId
        });
        fetchBudgets();
        return response.data;
    };

    const updateBudgetEntry = async (entryId, entryData) => {
        const response = await api.patch(`/api/budgets/${entryId}/`, entryData);
        fetchBudgets();
        return response.data;
    };

    const deleteBudgetEntry = async (entryId) => {
        await api.delete(`/api/budgets/${entryId}/`);
        fetchBudgets();
    };

    const incomeEntries = budgets.filter(b => b.transaction_type === 'income');
    const expenseEntries = budgets.filter(b => b.transaction_type === 'expense');

    return {
        budgets,
        summary,
        incomeEntries,
        expenseEntries,
        loading,
        error,
        refetch: fetchBudgets,
        addBudgetEntry,
        updateBudgetEntry,
        deleteBudgetEntry
    };
};

export default useBudget;
