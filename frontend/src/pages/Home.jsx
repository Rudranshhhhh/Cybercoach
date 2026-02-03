import AppHeader from '../components/Header';
import RotatingText from '../components/RotatingText';
import Galaxy from '../components/Galaxy/Galaxy';
import { useNavigate } from 'react-router-dom';
import './Home.scss';

function Home() {
    const navigate = useNavigate();

    const rotatingTexts = [
        'Phishing',
        'Spam Email',
        'Click Bait'
    ];

    return (
        <div className="app">
            <Galaxy
                mouseRepulsion
                mouseInteraction
                density={1.5}
                glowIntensity={0.3}
                saturation={0}
                hueShift={140}
                twinkleIntensity={0.3}
                rotationSpeed={0.1}
                repulsionStrength={2}
                starSpeed={0.5}
                speed={1}
            />
            <AppHeader />
            <main className="main-content">
                <section className="hero">
                    <div className="hero-content">
                        <h1 className="hero-title hero-rotating-text">
                            <span className="hero-static-text">CyberCoach</span>
                            <RotatingText
                                texts={rotatingTexts}
                                mainClassName="hero-dynamic-text"
                                rotationInterval={2500}
                                staggerDuration={0.02}
                                staggerFrom="first"
                                splitBy="words"
                            />
                        </h1>
                        <p className="hero-subtitle">
                            Cybercode is an interactive platform that helps users identify phishing emails, messages, and links through short, real-world inspired quizzes.
                            By highlighting common red flags like urgency and impersonation, it builds practical cybersecurity awareness through hands-on learning.
                        </p>
                        <div className="hero-actions">
                            <button className="get-started-btn" onClick={() => navigate('/login')}>
                                Phish or Legit?
                            </button>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}

export default Home;
