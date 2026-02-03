import { Header, HeaderName, HeaderGlobalBar } from '@carbon/react';
import './Header.scss';

function AppHeader() {
    return (
        <Header aria-label="CyberCoach">
            <HeaderName href="/" prefix="">
                <img src="/logo.svg" alt="CyberCoach Logo" className="header-logo" />
                <span className="header-title">CyberCoach</span>
            </HeaderName>
            <HeaderGlobalBar>
                <div className="auth-buttons">
                    <button className="auth-btn login-btn">Login</button>
                    <button className="auth-btn signup-btn">Sign Up</button>
                </div>
            </HeaderGlobalBar>
        </Header>
    );
}

export default AppHeader;
