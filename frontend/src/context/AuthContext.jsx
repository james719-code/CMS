import React, { createContext, useState, useContext } from 'react';
import api from '../api/axios';
import { jwtDecode } from "jwt-decode";

const AuthContext = createContext();

const clearStoredAuth = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
};

const getInitialUser = () => {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    try {
        const decoded = jwtDecode(token);
        if (decoded.exp * 1000 < Date.now()) {
            clearStoredAuth();
            return null;
        }

        const storedUser = localStorage.getItem('user_data');
        return storedUser ? JSON.parse(storedUser) : null;
    } catch (error) {
        console.error("Invalid token", error);
        clearStoredAuth();
        return null;
    }
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(getInitialUser);
    const [loading] = useState(false);

    const logout = () => {
        clearStoredAuth();
        setUser(null);
    };

    const login = async (email, password) => {
        try {
            const response = await api.post('/api/login/', { email, password });
            const { access, refresh, ...userData } = response.data;

            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
            localStorage.setItem('user_data', JSON.stringify(userData));

            setUser(userData);
            return userData;
        } catch (error) {
            console.error("Login failed", error);
            throw error;
        }
    };

    const register = async (data) => {
        await api.post('/api/register/', data);
        return true;
    };

    const refreshUserData = async () => {
        try {
            const response = await api.get('/api/accounts/me/');
            const userData = { ...user, ...response.data };
            localStorage.setItem('user_data', JSON.stringify(userData));
            setUser(userData);
        } catch (error) {
            console.error("Failed to refresh user data", error);
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, register, loading, refreshUserData }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
