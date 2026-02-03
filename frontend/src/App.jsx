import AppHeader from './components/Header';
import './App.scss';

function App() {
  return (
    <div className="app">
      <AppHeader />
      <main className="main-content">
        <section className="hero">
          <div className="hero-content">
            <h1 className="hero-title">
              Master <span className="gradient-text">Cybersecurity</span>
            </h1>
            <p className="hero-subtitle">
              Your personal AI-powered coach for learning cybersecurity skills,
              from beginner to expert.
            </p>
            <div className="hero-actions">
              <button className="get-started-btn">Get Started</button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;

