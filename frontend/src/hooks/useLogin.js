import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export const useLogin = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const user = await login(email, password);
            if (user.is_staff) {
                navigate('/admin');
            } else {
                navigate('/dashboard');
            }
        } catch {
            setError('Invalid credentials');
        }
    };

    return {
        email,
        setEmail,
        password,
        setPassword,
        error,
        handleSubmit
    };
};
