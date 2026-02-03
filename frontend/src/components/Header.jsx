import { useState, useEffect, useRef } from 'react';
import { Header, HeaderName, HeaderGlobalBar } from '@carbon/react';
import { useNavigate } from 'react-router-dom';
import './Header.scss';

function AppHeader() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [showDropdown, setShowDropdown] = useState(false);
    const dropdownRef = useRef(null);

    // Check for logged in user on mount and when localStorage changes
    useEffect(() => {
        const checkUser = () => {
            const userData = localStorage.getItem('user');
            if (userData) {
                try {
                    setUser(JSON.parse(userData));
                } catch (e) {
                    setUser(null);
                }
            } else {
                setUser(null);
            }
        };

        checkUser();

        // Listen for storage changes (for multi-tab support)
        window.addEventListener('storage', checkUser);

        // Custom event for same-tab updates
        window.addEventListener('userLoggedIn', checkUser);

        return () => {
            window.removeEventListener('storage', checkUser);
            window.removeEventListener('userLoggedIn', checkUser);
        };
    }, []);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
        setShowDropdown(false);
        navigate('/');
    };

    const getInitials = (name, email) => {
        if (name) {
            return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        }
        return email ? email[0].toUpperCase() : 'U';
    };

    return (
        <Header aria-label="CyberCoach">
            <HeaderName href="#" prefix="" onClick={(e) => { e.preventDefault(); navigate('/'); }}>
                <img src="/logo.svg" alt="CyberCoach Logo" className="header-logo" />
                <span className="header-title">CyberCoach</span>
            </HeaderName>
            <HeaderGlobalBar>
                {user ? (
                    <div className="user-menu" ref={dropdownRef}>
                        <button
                            className="user-avatar-btn"
                            onClick={() => setShowDropdown(!showDropdown)}
                        >
                            <div className="user-avatar">
                                {getInitials(user.name, user.email)}
                            </div>
                        </button>

                        {showDropdown && (
                            <div className="user-dropdown">
                                <div className="user-info">
                                    <div className="user-name">{user.name || 'User'}</div>
                                    <div className="user-email">{user.email}</div>
                                </div>
                                <div className="dropdown-divider"></div>
                                <button className="dropdown-item" onClick={handleLogout}>
                                    Logout
                                </button>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="auth-buttons">
                        <button className="auth-btn login-btn" onClick={() => navigate('/login')}>
                            Login
                        </button>
                        <button className="auth-btn signup-btn" onClick={() => navigate('/signup')}>
                            Sign Up
                        </button>
                    </div>
                )}
            </HeaderGlobalBar>
        </Header>
    );
}

export default AppHeader;
