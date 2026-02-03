import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './ExamPage.scss';

function ExamPage() {
    const navigate = useNavigate();
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [examCanceled, setExamCanceled] = useState(false);
    const [showExitWarning, setShowExitWarning] = useState(false);

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

    // Handle fullscreen change (user pressed Esc or exited)
    useEffect(() => {
        const handleFullscreenChange = () => {
            const isCurrentlyFullscreen = !!(
                document.fullscreenElement ||
                document.webkitFullscreenElement ||
                document.msFullscreenElement
            );

            if (!isCurrentlyFullscreen && isFullscreen && !examCanceled) {
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
    }, [isFullscreen, examCanceled, cancelExam]);

    // Handle browser back button
    useEffect(() => {
        const handlePopState = (e) => {
            e.preventDefault();
            if (!examCanceled) {
                cancelExam();
            }
        };

        // Push a state to history so we can detect back button
        window.history.pushState(null, '', window.location.pathname);
        window.addEventListener('popstate', handlePopState);

        return () => {
            window.removeEventListener('popstate', handlePopState);
        };
    }, [examCanceled, cancelExam]);

    // Handle tab close/refresh
    useEffect(() => {
        const handleBeforeUnload = (e) => {
            if (!examCanceled) {
                e.preventDefault();
                e.returnValue = 'Your exam will be canceled if you leave this page.';
                return e.returnValue;
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
    }, [examCanceled]);

    if (examCanceled) {
        return (
            <div className="exam-page canceled">
                <div className="cancel-message">
                    <div className="cancel-icon">X</div>
                    <h1>Exam Canceled</h1>
                    <p>You exited the exam. Redirecting back...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="exam-page">
            {/* Exit Button */}
            <button className="exit-btn" onClick={handleExitClick}>
                Exit Exam
            </button>

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
                <h1 className="exam-title">Phishing Awareness Test</h1>
                <p className="exam-instruction">
                    Exam is in progress. Do not exit fullscreen mode.
                </p>

                {/* Placeholder for exam questions */}
                <div className="exam-placeholder">
                    <p>Exam questions will appear here</p>
                </div>
            </div>
        </div>
    );
}

export default ExamPage;
