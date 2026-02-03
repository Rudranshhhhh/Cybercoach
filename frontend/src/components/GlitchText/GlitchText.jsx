import { useEffect, useState } from 'react';
import './GlitchText.scss';

const GlitchText = ({
    children,
    as: Component = 'p',
    className = '',
    speed = 3000,
    ...rest
}) => {
    const [isGlitching, setIsGlitching] = useState(false);

    useEffect(() => {
        const triggerGlitch = () => {
            setIsGlitching(true);
            setTimeout(() => setIsGlitching(false), 500); // Glitch duration
        };

        const interval = setInterval(() => {
            if (Math.random() > 0.5) { // Random chance to glitch
                triggerGlitch();
            }
        }, speed);

        return () => clearInterval(interval);
    }, [speed]);

    return (
        <Component
            className={`glitch-text ${isGlitching ? 'glitching' : ''} ${className}`}
            data-text={children}
            {...rest}
        >
            {children}
        </Component>
    );
};

export default GlitchText;
