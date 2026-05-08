import { useState } from 'react';
import api from '../api/axios';
import { useNavigate } from 'react-router-dom';

export const useOrgRegistration = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '',
        acronym: '',
        description: '',
        mission: '',
        vision: ''
    });
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('/organizations/register/', formData);
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.non_field_errors?.[0] || 'Registration failed. Ensure unique name or you might already lead an org.');
        }
    };

    return {
        formData,
        error,
        handleChange,
        handleSubmit
    };
};
