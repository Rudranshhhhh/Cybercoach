import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './ExamPage.scss';

const API_BASE = 'http://127.0.0.1:5000';

function ExamPage() {
    const navigate = useNavigate();
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [examCanceled, setExamCanceled] = useState(false);
    const [showExitWarning, setShowExitWarning] = useState(false);
    const [error, setError] = useState(null);

    // Quiz state
    const [sessionId, setSessionId] = useState(null);
    const [question, setQuestion] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [progress, setProgress] = useState({ current: 0, total: 5 });
    const [difficulty, setDifficulty] = useState('ADVANCED');
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [feedback, setFeedback] = useState(null);
    const [quizComplete, setQuizComplete] = useState(false);
    const [report, setReport] = useState(null);

    // Start quiz session
    const startQuiz = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/quiz/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ num_questions: 5 })
            });
            const data = await response.json();
            setSessionId(data.session_id);
            return data.session_id;
        } catch (err) {
            console.error('Failed to start quiz:', err);
            setError('Failed to start quiz. Please check your connection and try again.');
            return null;
        }
    };

    // Fetch next question
    const fetchQuestion = async (sid) => {
        setLoading(true);
        setFeedback(null);
        setSelectedAnswer(null);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/api/quiz/question`, {
                method: 'GET',
                headers: { 'X-Session-ID': sid }
            });
            const data = await response.json();

            if (data.error) {
                if (data.error.includes('completed')) {
                    setQuizComplete(true);
                    fetchReport(sid);
                } else {
                    setError(data.error);
                }
                return;
            }

            setQuestion(data.question);
            setProgress({ current: data.current_question, total: data.total_questions });
            setDifficulty(data.difficulty_level || 'ADVANCED');
        } catch (err) {
            console.error('Failed to fetch question:', err);
            setError('Failed to load question. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // Submit answer
    const submitAnswer = async (answer) => {
        if (!sessionId || !question) return;

        setSubmitting(true);
        setSelectedAnswer(answer);

        try {
            const response = await fetch(`${API_BASE}/api/quiz/answer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': sessionId
                },
                body: JSON.stringify({
                    question_id: question.id,
                    answer: answer,
                    reasoning: ''
                })
            });
            const data = await response.json();

            setFeedback({
                correct: data.correct,
                explanation: data.explanation,
                tip: data.learning_tip,
                threatVector: data.threat_vector,
                complexityScore: data.complexity_score,
                whyHard: data.why_its_hard || data.psychological_exploit
            });

            // Check if quiz is complete
            if (data.is_completed) {
                setQuizComplete(true);
                fetchReport(sessionId);
            }
        } catch (err) {
            console.error('Failed to submit answer:', err);
        } finally {
            setSubmitting(false);
        }
    };

    // Fetch final report
    const fetchReport = async (sid) => {
        try {
            const response = await fetch(`${API_BASE}/api/quiz/report`, {
                method: 'GET',
                headers: { 'X-Session-ID': sid }
            });
            const data = await response.json();
            setReport(data);
        } catch (err) {
            console.error('Failed to fetch report:', err);
        }
    };

    // Next question
    const nextQuestion = () => {
        if (sessionId) {
            fetchQuestion(sessionId);
        }
    };

    // Initialize quiz on mount
    useEffect(() => {
        const init = async () => {
            const sid = await startQuiz();
            if (sid) {
                fetchQuestion(sid);
            } else {
                setLoading(false);
            }
        };
        init();
    }, []);

    // Enter fullscreen
    const enterFullscreen = useCallback(async () => {
        try {
            const elem = document.documentElement;
            if (elem.requestFullscreen) {
                await elem.requestFullscreen();
            } else if (elem.webkitRequestFullscreen) {
                await elem.webkitRequestFullscreen();
            } else if (elem.msRequestFullscreen) {
                await elem.msRequestFullscreen();
            }
            setIsFullscreen(true);
        } catch (err) {
            console.error('Failed to enter fullscreen:', err);
        }
    }, []);

    // Exit fullscreen
    const exitFullscreen = useCallback(() => {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }, []);

    // Handle exam cancellation
    const cancelExam = useCallback(() => {
        setExamCanceled(true);
        exitFullscreen();
        setTimeout(() => {
            navigate('/test');
        }, 2000);
    }, [navigate, exitFullscreen]);

    // Show exit warning
    const handleExitClick = () => {
        setShowExitWarning(true);
    };

    // Confirm exit
    const confirmExit = () => {
        cancelExam();
    };

    // Cancel exit warning
    const cancelExit = () => {
        setShowExitWarning(false);
    };

    // Enter fullscreen on mount
    useEffect(() => {
        enterFullscreen();
    }, [enterFullscreen]);

    // Handle fullscreen change
    useEffect(() => {
        const handleFullscreenChange = () => {
            const isCurrentlyFullscreen = !!(
                document.fullscreenElement ||
                document.webkitFullscreenElement ||
                document.msFullscreenElement
            );

            if (!isCurrentlyFullscreen && isFullscreen && !examCanceled && !quizComplete) {
                cancelExam();
            }
            setIsFullscreen(isCurrentlyFullscreen);
        };

        document.addEventListener('fullscreenchange', handleFullscreenChange);
        document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
        document.addEventListener('msfullscreenchange', handleFullscreenChange);

        return () => {
            document.removeEventListener('fullscreenchange', handleFullscreenChange);
            document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
            document.removeEventListener('msfullscreenchange', handleFullscreenChange);
        };
    }, [isFullscreen, examCanceled, quizComplete, cancelExam]);

    // Handle browser back button
    useEffect(() => {
        const handlePopState = (e) => {
            e.preventDefault();
            if (!examCanceled) {
                cancelExam();
            }
        };

        window.history.pushState(null, '', window.location.pathname);
        window.addEventListener('popstate', handlePopState);

        return () => {
            window.removeEventListener('popstate', handlePopState);
        };
    }, [examCanceled, cancelExam]);

    // Handle tab close/refresh
    useEffect(() => {
        const handleBeforeUnload = (e) => {
            if (!examCanceled && !quizComplete) {
                e.preventDefault();
                e.returnValue = 'Your exam will be canceled if you leave this page.';
                return e.returnValue;
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
    }, [examCanceled, quizComplete]);

    // Difficulty badge color
    const getDifficultyColor = () => {
        switch (difficulty) {
            case 'ADVANCED': return '#ff9800';
            case 'EXPERT': return '#f44336';
            case 'ELITE': return '#9c27b0';
            default: return '#4caf50';
        }
    };

    if (examCanceled) {
        return (
            <div className="exam-page canceled">
                <div className="cancel-message">
                    <div className="cancel-icon">✕</div>
                    <h1>Exam Canceled</h1>
                    <p>You exited the exam. Redirecting back...</p>
                </div>
            </div>
        );
    }

    // Quiz Complete - Show Report
    if (quizComplete && report) {
        return (
            <div className="exam-page">
                <div className="report-container">
                    <h1 className="report-title">Threat Intelligence Report</h1>

                    <div className="report-score">
                        <div className="score-circle">
                            <span className="score-value">{report.score_percentage}%</span>
                        </div>
                        <div className="score-label">
                            <span className={`risk-badge ${report.risk_level?.toLowerCase()}`}>
                                {report.risk_level} Risk
                            </span>
                        </div>
                    </div>

                    {/* Bias Heatmap */}
                    {report.bias_heatmap && (
                        <div className="report-section">
                            <h2>🧠 Human Bias Heatmap</h2>
                            <div className="bias-grid">
                                {Object.entries(report.bias_heatmap).map(([trigger, value]) => (
                                    <div key={trigger} className="bias-item">
                                        <span className="bias-name">{trigger}</span>
                                        <div className="bias-bar">
                                            <div
                                                className="bias-fill"
                                                style={{ width: `${typeof value === 'number' ? value : value?.vulnerability_percentage || 0}%` }}
                                            />
                                        </div>
                                        <span className="bias-value">{typeof value === 'number' ? value : value?.vulnerability_percentage || 0}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Zero-Day Threat Forecast */}
                    {report.zero_day_threat_forecast && (
                        <div className="report-section threat-forecast">
                            <h2>⚠️ Zero-Day Threat Forecast</h2>
                            <div className="threat-card">
                                <div className="threat-header">
                                    <span className="threat-vector">{report.zero_day_threat_forecast.highest_risk_vector}</span>
                                    <span className="threat-probability">{report.zero_day_threat_forecast.probability}% Likely</span>
                                </div>
                                <p className="threat-scenario">{report.zero_day_threat_forecast.scenario}</p>
                            </div>
                        </div>
                    )}

                    {/* Defense Protocol */}
                    {report.defense_protocol && (
                        <div className="report-section">
                            <h2>🛡️ Defense Protocol</h2>
                            <ul className="defense-list">
                                {report.defense_protocol.map((tip, i) => (
                                    <li key={i}>{tip}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <button className="finish-btn" onClick={() => navigate('/test')}>
                        Finish & Return
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="exam-page">
            {/* Header */}
            <div className="exam-header">
                <div className="progress-info">
                    <span>Question {progress.current} of {progress.total}</span>
                    <span className="difficulty-badge" style={{ background: getDifficultyColor() }}>
                        {difficulty}
                    </span>
                </div>
                <button className="exit-btn" onClick={handleExitClick}>
                    Exit Exam
                </button>
            </div>

            {/* Exit Warning Modal */}
            {showExitWarning && (
                <div className="exit-modal-overlay">
                    <div className="exit-modal">
                        <h2>Exit Exam?</h2>
                        <p>If you exit now, your exam will be canceled and progress will be lost.</p>
                        <div className="modal-actions">
                            <button className="cancel-btn" onClick={cancelExit}>
                                Continue Exam
                            </button>
                            <button className="confirm-btn" onClick={confirmExit}>
                                Exit Exam
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Exam Content */}
            <div className="exam-content">
                {loading ? (
                    <div className="loading-state">
                        <div className="loader"></div>
                        <p>Generating adversarial scenario...</p>
                    </div>
                ) : question ? (
                    <div className="question-container">
                        {/* Dynamic prompt based on scenario type */}
                        <h2 className="question-prompt">
                            {question.scenario_type === 'email' && '📧 Is this email Phishing or Safe?'}
                            {question.scenario_type === 'popup' && '🖥️ Is this system notification Phishing or Safe?'}
                            {question.scenario_type === 'slack' && '💬 Is this Slack message Phishing or Safe?'}
                            {question.scenario_type === 'oauth_screen' && '🔐 Is this OAuth permission request Phishing or Safe?'}
                            {question.scenario_type === 'qr_poster' && '📱 Is this QR code poster Phishing or Safe?'}
                            {question.scenario_type === 'code_review' && '💻 Is this code review request Phishing or Safe?'}
                            {!question.scenario_type && 'Is this Phishing or Safe?'}
                        </h2>

                        {/* Threat Vector Badge */}
                        {question.threat_vector && question.threat_vector !== 'LEGITIMATE' && (
                            <div className="threat-vector-preview">
                                <span className="vector-icon">⚠️</span>
                                <span className="vector-name">{question.threat_vector?.replace(/_/g, ' ')}</span>
                            </div>
                        )}

                        {/* Scenario Preview - Dynamic based on type */}
                        <div className={`scenario-preview ${question.scenario_type || 'email'}`}>
                            {/* Email Format */}
                            {(question.scenario_type === 'email' || !question.scenario_type) && (
                                <div className="email-preview">
                                    <div className="email-header">
                                        <div className="email-from">
                                            <span className="label">From:</span>
                                            <span className="value">{question.content?.from || 'Unknown'}</span>
                                        </div>
                                        <div className="email-subject">
                                            <span className="label">Subject:</span>
                                            <span className="value">{question.content?.subject || 'No Subject'}</span>
                                        </div>
                                    </div>
                                    <div className="email-body">
                                        {question.content?.body || 'No content'}
                                    </div>
                                </div>
                            )}

                            {/* Popup/System Notification Format */}
                            {question.scenario_type === 'popup' && (
                                <div className="popup-preview">
                                    <div className="popup-header">
                                        <span className="popup-icon">🤖</span>
                                        <span className="popup-source">{question.content?.from || 'System Notification'}</span>
                                    </div>
                                    <div className="popup-body">
                                        {question.content?.body || 'No content'}
                                    </div>
                                    <div className="popup-actions">
                                        <button className="popup-btn approve">✓ Approve</button>
                                        <button className="popup-btn deny">✕ Deny</button>
                                    </div>
                                </div>
                            )}

                            {/* Slack/Teams Message Format */}
                            {question.scenario_type === 'slack' && (
                                <div className="slack-preview">
                                    <div className="slack-header">
                                        <div className="slack-avatar">👤</div>
                                        <div className="slack-user">{question.content?.from || 'Colleague'}</div>
                                    </div>
                                    <div className="slack-message">
                                        {question.content?.body || 'No content'}
                                    </div>
                                </div>
                            )}

                            {/* OAuth Permission Screen Format */}
                            {question.scenario_type === 'oauth_screen' && (
                                <div className="oauth-preview">
                                    <div className="oauth-header">
                                        <span className="oauth-app">{question.content?.from || 'Unknown App'}</span>
                                        <span className="oauth-action">wants access to your account</span>
                                    </div>
                                    <div className="oauth-permissions">
                                        <strong>Permissions requested:</strong>
                                        <ul>
                                            {(question.content?.permissions_requested || []).map((perm, i) => (
                                                <li key={i} className="permission-item">⚠️ {perm}</li>
                                            ))}
                                        </ul>
                                    </div>
                                    <p className="oauth-body">{question.content?.body}</p>
                                </div>
                            )}

                            {/* QR Code Poster Format */}
                            {question.scenario_type === 'qr_poster' && (
                                <div className="qr-preview">
                                    <div className="qr-poster">
                                        <div className="qr-code">📱 [QR CODE]</div>
                                        <div className="qr-text">{question.content?.body || 'Scan me!'}</div>
                                    </div>
                                    <p className="qr-context">Location: {question.content?.from || 'Office'}</p>
                                </div>
                            )}

                            {/* Code Review Format */}
                            {question.scenario_type === 'code_review' && (
                                <div className="code-preview">
                                    <div className="code-header">
                                        <span className="code-source">{question.content?.from || 'GitHub'}</span>
                                        <span className="code-title">{question.content?.subject || 'Pull Request'}</span>
                                    </div>
                                    <pre className="code-block">
                                        {question.content?.body || '// No code'}
                                    </pre>
                                </div>
                            )}

                            {/* SMS / iMessage Format */}
                            {question.scenario_type === 'sms' && (
                                <div className="sms-preview">
                                    <div className="sms-header">
                                        <div className="sms-carrier">📶 Carrier • Now</div>
                                        <div className="sms-contact">{question.content?.from || 'Unknown'}</div>
                                    </div>
                                    <div className="sms-body">
                                        <div className="sms-bubble incoming">
                                            {question.content?.body || 'No message'}
                                        </div>
                                    </div>
                                    <div className="sms-input">
                                        <span>iMessage</span>
                                    </div>
                                </div>
                            )}

                            {/* WhatsApp Format */}
                            {question.scenario_type === 'whatsapp' && (
                                <div className="whatsapp-preview">
                                    <div className="whatsapp-header">
                                        <div className="whatsapp-back">←</div>
                                        <div className="whatsapp-avatar">👤</div>
                                        <div className="whatsapp-contact">
                                            <div className="whatsapp-name">{question.content?.from || 'Unknown'}</div>
                                            <div className="whatsapp-status">online</div>
                                        </div>
                                        <div className="whatsapp-icons">📞 📹</div>
                                    </div>
                                    <div className="whatsapp-body">
                                        <div className="whatsapp-bubble incoming">
                                            {question.content?.body || 'No message'}
                                            <span className="whatsapp-time">12:34 PM</span>
                                        </div>
                                    </div>
                                    <div className="whatsapp-input">
                                        <span>📎</span>
                                        <span className="whatsapp-text-input">Type a message</span>
                                        <span>🎤</span>
                                    </div>
                                </div>
                            )}

                            {/* Meta AI Format */}
                            {question.scenario_type === 'meta_ai' && (
                                <div className="meta-ai-preview">
                                    <div className="meta-ai-header">
                                        <div className="meta-ai-logo">Ⓜ️</div>
                                        <div className="meta-ai-title">Meta AI</div>
                                        <div className="meta-ai-badge">AI Assistant</div>
                                    </div>
                                    <div className="meta-ai-body">
                                        <div className="meta-ai-bubble">
                                            <div className="meta-ai-icon">🤖</div>
                                            <div className="meta-ai-message">
                                                {question.content?.body || 'No message'}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="meta-ai-actions">
                                        <button className="meta-ai-btn">👍 Helpful</button>
                                        <button className="meta-ai-btn">👎 Not Helpful</button>
                                    </div>
                                </div>
                            )}

                            {/* AI-to-AI Chat Format */}
                            {question.scenario_type === 'ai_chat' && (
                                <div className="ai-chat-preview">
                                    <div className="ai-chat-header">
                                        <span className="ai-chain-icon">🔗</span>
                                        <span className="ai-chat-title">AI Assistant Chain</span>
                                    </div>
                                    <div className="ai-chat-body">
                                        <div className="ai-message source">
                                            <div className="ai-label">🤖 {question.content?.from || 'Source AI'}</div>
                                            <div className="ai-text">{question.content?.subject || 'Forwarding request...'}</div>
                                        </div>
                                        <div className="ai-arrow">⬇️</div>
                                        <div className="ai-message forwarded">
                                            <div className="ai-label">🤖 Your AI Assistant</div>
                                            <div className="ai-text">{question.content?.body || 'No message'}</div>
                                        </div>
                                    </div>
                                    <div className="ai-chat-actions">
                                        <button className="ai-approve-btn">✓ Approve Request</button>
                                        <button className="ai-deny-btn">✕ Deny</button>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Answer Buttons */}
                        {!feedback ? (
                            <div className="answer-buttons">
                                <button
                                    className={`answer-btn phishing ${selectedAnswer === 'Phishing' ? 'selected' : ''}`}
                                    onClick={() => submitAnswer('Phishing')}
                                    disabled={submitting}
                                >
                                    🎣 Phishing
                                </button>
                                <button
                                    className={`answer-btn safe ${selectedAnswer === 'Safe' ? 'selected' : ''}`}
                                    onClick={() => submitAnswer('Safe')}
                                    disabled={submitting}
                                >
                                    ✅ Safe
                                </button>
                            </div>
                        ) : (
                            <div className={`feedback-panel ${feedback.correct ? 'correct' : 'incorrect'}`}>
                                <div className="feedback-header">
                                    {feedback.correct ? '✓ Correct!' : '✗ Incorrect'}
                                </div>

                                {/* Threat Intelligence Badge */}
                                {feedback.threatVector && (
                                    <div className="threat-intel-badge">
                                        <span className="threat-label">🎯 Threat Vector:</span>
                                        <span className="threat-value">{feedback.threatVector.replace('_', ' ')}</span>
                                        {feedback.complexityScore && (
                                            <span className="complexity-badge">
                                                Complexity: {feedback.complexityScore}/10
                                            </span>
                                        )}
                                    </div>
                                )}

                                <p className="feedback-explanation">{feedback.explanation}</p>

                                {/* Why It's Hard */}
                                {feedback.whyHard && (
                                    <div className="why-hard-box">
                                        <strong>🧠 Why This Attack Works:</strong> {feedback.whyHard}
                                    </div>
                                )}

                                {feedback.tip && (
                                    <div className="feedback-tip">
                                        <strong>💡 Defense Tip:</strong> {feedback.tip}
                                    </div>
                                )}
                                <button className="next-btn" onClick={nextQuestion}>
                                    Next Question →
                                </button>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="error-state">
                        <p>{error || 'Failed to load question. Please try again.'}</p>
                        <button className="retry-btn" onClick={() => window.location.reload()}>Retry</button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default ExamPage;
