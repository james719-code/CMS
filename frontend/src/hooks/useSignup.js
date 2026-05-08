import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export const useSignup = () => {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        student_id: ''
    });
    const [error, setError] = useState('');
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Basic client-side validation
            if (!formData.email.endsWith('@parsu.edu.ph')) {
                setError('Please use your institutional email (@parsu.edu.ph)');
                return;
            }

            await register(formData);
            navigate('/login'); // Redirect to login after successful registration
        } catch (err) {
            setError(err.response?.data?.email?.[0] || err.response?.data?.student_id?.[0] || 'Registration failed. Please try again.');
        }
    };

    return {
        formData,
        error,
        handleChange,
        handleSubmit
    };
};
