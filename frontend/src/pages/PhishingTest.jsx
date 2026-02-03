import { useNavigate } from 'react-router-dom';
import AppHeader from '../components/Header';
import Galaxy from '../components/Galaxy/Galaxy';
import GradientText from '../components/GradientText';
import './PhishingTest.scss';

function PhishingTest() {
    const navigate = useNavigate();

    return (
        <div className="phishing-test-page">
            <Galaxy
                mouseRepulsion
                mouseInteraction
                density={1.2}
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

            <main className="test-main-content">
                <div className="test-container">
                    <div className="test-header">
                        <h1 className="test-title">
                            {' '}
                            <GradientText
                                colors={["#667BFE", "#A18CFE", "#2455C6", "#667BFE"]}
                                animationSpeed={6}
                                showBorder={false}
                            >
                                Spot The Phish
                            </GradientText>
                        </h1>
                    </div>

                    <div className="test-description">
                        <p className="description-text">
                            This interactive assessment tests your ability to identify phishing emails
                            and protect yourself from cyber threats. You'll be presented with a series
                            of emails that you might encounter in real life, and your task is to determine
                            whether each email is legitimate or a phishing attempt.
                        </p>
                        <p className="description-text">
                            After each question, you'll receive detailed feedback explaining the key
                            indicators that reveal whether an email is safe or malicious. This helps
                            you develop the critical thinking skills needed to stay safe online.
                        </p>
                    </div>

                    <div className="test-actions">
                        <button
                            className="start-test-btn"
                            onClick={() => navigate('/exam')}
                        >
                            Start Test
                        </button>
                    </div>

                    <a
                        href="#"
                        className="back-link"
                        onClick={(e) => { e.preventDefault(); navigate('/'); }}
                    >
                        Back to Home
                    </a>
                </div>
            </main>
        </div>
    );
}

export default PhishingTest;
