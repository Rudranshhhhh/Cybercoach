import './GradientText.scss';

function GradientText({
    children,
    colors = ["#667BFE", "#A18CFE", "#2455C6", "#667BFE"],
    animationSpeed = 8,
    showBorder = false,
    className = ""
}) {
    const gradientStyle = {
        background: `linear-gradient(90deg, ${colors.join(', ')})`,
        backgroundSize: '300% 100%',
        WebkitBackgroundClip: 'text',
        backgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        animation: `gradientFlow ${animationSpeed}s ease infinite`,
        display: 'inline-block'
    };

    return (
        <span
            style={gradientStyle}
            className={`gradient-text-animated ${showBorder ? 'with-border' : ''} ${className}`}
        >
            {children}
        </span>
    );
}

export default GradientText;
