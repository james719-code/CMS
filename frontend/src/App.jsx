import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import AdminDashboard from './pages/AdminDashboard';
import StudentDashboard from './pages/StudentDashboard';
import OrgRegistration from './pages/OrgRegistration';
import OfficerDashboard from './pages/officer/OfficerDashboard';
import NotFound from './pages/NotFound';
import Layout from './components/Layout';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Toaster } from '@/components/ui/sonner';
import { TooltipProvider } from '@/components/ui/tooltip';

const ProtectedRoute = ({ children, adminOnly = false }) => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-background">
                <div className="size-8 animate-spin rounded-full border-2 border-muted border-t-primary" />
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    if (adminOnly && !user.is_staff) {
        return <Navigate to="/dashboard" replace />;
    }

    return children;
};

function App() {
    return (
        <TooltipProvider delayDuration={150}>
            <Router>
                <AuthProvider>
                    <Routes>
                    {/* Public Routes */}
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<Signup />} />

                    {/* Protected Routes with Layout */}
                    <Route path="/" element={<Layout />}>
                        <Route index element={<Navigate to="/dashboard" replace />} />

                        {/* Student Dashboard */}
                        <Route path="dashboard" element={
                            <ProtectedRoute>
                                <StudentDashboard />
                            </ProtectedRoute>
                        } />

                        {/* Organization Registration */}
                        <Route path="register-org" element={
                            <ProtectedRoute>
                                <OrgRegistration />
                            </ProtectedRoute>
                        } />

                        {/* Admin Dashboard */}
                        <Route path="admin" element={
                            <ProtectedRoute adminOnly={true}>
                                <AdminDashboard />
                            </ProtectedRoute>
                        } />
                        <Route path="admin/*" element={
                            <ProtectedRoute adminOnly={true}>
                                <AdminDashboard />
                            </ProtectedRoute>
                        } />

                        {/* Officer Dashboard */}
                        <Route path="officer/:orgId" element={
                            <ProtectedRoute>
                                <OfficerDashboard />
                            </ProtectedRoute>
                        } />
                        <Route path="officer/:orgId/*" element={
                            <ProtectedRoute>
                                <OfficerDashboard />
                            </ProtectedRoute>
                        } />
                    </Route>

                    {/* 404 */}
                    <Route path="*" element={<NotFound />} />
                    </Routes>
                    <Toaster richColors closeButton />
                </AuthProvider>
            </Router>
        </TooltipProvider>
    );
}

export default App;
