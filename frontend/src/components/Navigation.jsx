import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
    MessageSquare, Users, Pill, Activity, LogOut, Heart, Menu, X,
    TestTubes, FileText, LayoutDashboard, Calendar, Stethoscope,
    BarChart, Shield, Settings, Sun, Moon
} from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const Navigation = () => {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const getNavItems = () => {
        if (user?.role === 'admin') {
            return [
                { path: '/admin/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
                { path: '/admin/users', icon: Users, label: 'Users' },
                { path: '/admin/roles', icon: Shield, label: 'Roles' },
                { path: '/admin/analytics', icon: BarChart, label: 'Analytics' },
                { path: '/admin/settings', icon: Settings, label: 'Settings' },
            ];
        } else if (user?.role === 'doctor') {
            return [
                { path: '/doctor/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
                { path: '/doctor/patients', icon: Users, label: 'Patients' },
                { path: '/doctor/consultations', icon: Stethoscope, label: 'Consultations' },
                { path: '/doctor/appointments', icon: Calendar, label: 'Appointments' },
                { path: '/doctor/prescriptions', icon: FileText, label: 'Prescriptions' },
            ];
        } else {
            return [
                { path: '/chatbot', icon: MessageSquare, label: 'AI Chat' },
                { path: '/health-tracking', icon: Activity, label: 'Tracking' },
                { path: '/medicines', icon: Pill, label: 'Medicines' },
                { path: '/pharmacy', icon: Pill, label: 'Pharmacy' },
                { path: '/lab-tests', icon: TestTubes, label: 'Lab Tests' },
            ];
        }
    };

    const navItems = getNavItems();

    const handleLogout = async () => {
        if (logout) {
            await logout();
        }
        navigate('/login');
    };

    return (
        <>
            {/* Desktop Navigation */}
            <nav className="hidden md:flex fixed left-0 top-0 h-screen w-20 bg-white dark:bg-[#111418] border-r border-gray-200 dark:border-[#283039] flex-col items-center py-6 z-50">
                {/* Logo */}
                <div className="mb-8">
                    <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center">
                        <Heart className="w-6 h-6 text-white" fill="white" />
                    </div>
                </div>

                {/* Nav Items */}
                <div className="flex-1 flex flex-col gap-4">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `relative w-12 h-12 rounded-xl flex items-center justify-center transition-all group ${isActive
                                    ? 'bg-primary/10 text-primary'
                                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-[#283039]'
                                }`
                            }
                        >
                            {({ isActive }) => (
                                <>
                                    <item.icon className="w-6 h-6" />
                                    {isActive && (
                                        <motion.div
                                            layoutId="activeNav"
                                            className="absolute left-0 w-1 h-8 bg-primary rounded-r-full"
                                            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                                        />
                                    )}
                                    {/* Tooltip */}
                                    <div className="absolute left-full ml-4 px-3 py-1.5 bg-gray-900 dark:bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                                        {item.label}
                                    </div>
                                </>
                            )}
                        </NavLink>
                    ))}
                </div>

                {/* Theme Toggle */}
                <button
                    onClick={toggleTheme}
                    className="w-12 h-12 rounded-xl flex items-center justify-center text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-[#283039] transition-all group mb-2"
                    title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                >
                    {theme === 'dark' ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
                    <div className="absolute left-full ml-4 px-3 py-1.5 bg-gray-900 dark:bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                        {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
                    </div>
                </button>

                {/* Logout */}
                <button
                    onClick={handleLogout}
                    className="w-12 h-12 rounded-xl flex items-center justify-center text-gray-600 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 transition-all group"
                >
                    <LogOut className="w-6 h-6" />
                    <div className="absolute left-full ml-4 px-3 py-1.5 bg-gray-900 dark:bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                        Logout
                    </div>
                </button>
            </nav>

            {/* Mobile Navigation */}
            <div className="md:hidden">
                {/* Top Bar */}
                <div className="fixed top-0 left-0 right-0 h-16 bg-white dark:bg-[#111418] border-b border-gray-200 dark:border-[#283039] flex items-center justify-between px-4 z-50">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                            <Heart className="w-5 h-5 text-white" fill="white" />
                        </div>
                        <span className="font-semibold text-lg text-gray-900 dark:text-white">MedAI</span>
                    </div>
                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        className="w-10 h-10 rounded-lg flex items-center justify-center hover:bg-gray-100 dark:hover:bg-[#283039] text-gray-900 dark:text-white"
                    >
                        {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </button>
                </div>

                {/* Mobile Menu */}
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="fixed top-16 left-0 right-0 bg-white dark:bg-[#111418] border-b border-gray-200 dark:border-[#283039] shadow-lg z-40"
                    >
                        <div className="p-4 space-y-2">
                            {navItems.map((item) => (
                                <NavLink
                                    key={item.path}
                                    to={item.path}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={({ isActive }) =>
                                        `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${isActive
                                            ? 'bg-primary/10 text-primary'
                                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-[#283039]'
                                        }`
                                    }
                                >
                                    <item.icon className="w-5 h-5" />
                                    <span className="font-medium">{item.label}</span>
                                </NavLink>
                            ))}
                            <button
                                onClick={toggleTheme}
                                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-[#283039] transition-all"
                            >
                                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                                <span className="font-medium">{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
                            </button>
                            <button
                                onClick={handleLogout}
                                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all"
                            >
                                <LogOut className="w-5 h-5" />
                                <span className="font-medium">Logout</span>
                            </button>
                        </div>
                    </motion.div>
                )}
            </div>
        </>
    );
};

export default Navigation;
