import { Header, HeaderName, HeaderGlobalBar } from '@carbon/react';
import { useNavigate } from 'react-router-dom';
import './Header.scss';

function AppHeader() {
    const navigate = useNavigate();

    return (
        <Header aria-label="CyberCoach">
            <HeaderName href="#" prefix="" onClick={(e) => { e.preventDefault(); navigate('/'); }}>
                <img src="/logo.svg" alt="CyberCoach Logo" className="header-logo" />
                <span className="header-title">CyberCoach</span>
            </HeaderName>
            <HeaderGlobalBar>
                <div className="auth-buttons">
                    <button className="auth-btn login-btn" onClick={() => navigate('/login')}>
                        Login
                    </button>
                    <button className="auth-btn signup-btn" onClick={() => navigate('/signup')}>
                        Sign Up
                    </button>
                </div>
            </HeaderGlobalBar>
        </Header>
    );
}

export default AppHeader;
