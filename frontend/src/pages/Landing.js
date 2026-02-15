import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function Landing() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="landing">
      {/* Navbar */}
      <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
        <div className="navbar-content">
          <a href="/" className="logo">
            <div className="logo-icon">⚡</div>
            <span>HireSignal</span>
          </a>
          <div className="nav-links">
            <a href="#dashboard-preview" className="nav-link">Dashboard</a>
            <a href="#features" className="nav-link">Features</a>
            <a href="#pricing" className="nav-link">Pricing</a>
          </div>
          <div className="nav-right">
            <Link to="/login" className="btn btn-ghost">Log In</Link>
            <Link to="/signup" className="btn btn-primary">Sign Up Free</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="hero">
        <div className="hero-bg"></div>
        <div className="hero-grid"></div>
        
        <div className="hero-content">
          <div className="hero-badge animate-slide-up">
            <span className="hero-badge-dot"></span>
            Real-time opportunity detection
          </div>
          
          <h1 className="animate-slide-up stagger-1">
            Never Miss a <span className="gradient-text">Freelance Gig</span> Again
          </h1>
          
          <p className="hero-subtitle animate-slide-up stagger-2">
            HireSignal monitors Reddit and Hacker News 24/7, instantly alerting you 
            when someone is looking for your exact skills. Be first to respond.
          </p>
          
          <div className="hero-cta animate-slide-up stagger-3">
            <Link to="/signup" className="btn btn-primary">
              Get Started Free
              <span>→</span>
            </Link>
            <a href="#dashboard-preview" className="btn btn-secondary">
              See Dashboard
            </a>
          </div>
        </div>
      </section>

      {/* Dashboard Preview */}
      <section className="section" id="dashboard-preview" style={{ background: 'var(--bg-secondary)' }}>
        <div className="section-header">
          <div className="section-badge">Dashboard Preview</div>
          <h2 className="section-title">Your Command Center</h2>
          <p className="section-subtitle">
            Everything you need to catch opportunities before anyone else
          </p>
        </div>
        
        <div className="dashboard-preview">
          {/* Mock Dashboard */}
          <div className="preview-container">
            <div className="preview-window">
              <div className="preview-header">
                <div className="preview-dots">
                  <span></span><span></span><span></span>
                </div>
                <div className="preview-url">app.hiresignal.com/dashboard</div>
              </div>
              
              <div className="preview-content">
                {/* Status Card */}
                <div className="preview-card preview-status">
                  <div className="preview-status-left">
                    <div className="preview-status-icon">📡</div>
                    <div>
                      <div className="preview-status-title">Alert Status</div>
                      <div className="preview-status-badge">● Active</div>
                    </div>
                  </div>
                  <div className="preview-toggle active"></div>
                </div>

                {/* Stats Row */}
                <div className="preview-stats">
                  <div className="preview-stat">
                    <div className="preview-stat-value">47</div>
                    <div className="preview-stat-label">Alerts Today</div>
                  </div>
                  <div className="preview-stat">
                    <div className="preview-stat-value">12</div>
                    <div className="preview-stat-label">High Match</div>
                  </div>
                  <div className="preview-stat">
                    <div className="preview-stat-value">3</div>
                    <div className="preview-stat-label">Responded</div>
                  </div>
                </div>

                {/* Recent Alerts */}
                <div className="preview-card">
                  <div className="preview-card-header">
                    <span>🎯</span> Recent Opportunities
                  </div>
                  <div className="preview-alerts">
                    <div className="preview-alert">
                      <div className="preview-alert-score">9</div>
                      <div className="preview-alert-content">
                        <div className="preview-alert-title">[Hiring] Senior Python Developer for AI Startup</div>
                        <div className="preview-alert-meta">r/forhire • 2 min ago • python, ai, backend</div>
                      </div>
                    </div>
                    <div className="preview-alert">
                      <div className="preview-alert-score">7</div>
                      <div className="preview-alert-content">
                        <div className="preview-alert-title">Looking for React/Node developer - Remote</div>
                        <div className="preview-alert-meta">r/freelance • 8 min ago • react, node.js</div>
                      </div>
                    </div>
                    <div className="preview-alert">
                      <div className="preview-alert-score">6</div>
                      <div className="preview-alert-content">
                        <div className="preview-alert-title">Need FastAPI expert for MVP development</div>
                        <div className="preview-alert-meta">Hacker News • 15 min ago • fastapi, python</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Skills */}
                <div className="preview-card">
                  <div className="preview-card-header">
                    <span>🛠️</span> Your Skills
                  </div>
                  <div className="preview-keywords">
                    <span className="preview-keyword">python</span>
                    <span className="preview-keyword">react</span>
                    <span className="preview-keyword">node.js</span>
                    <span className="preview-keyword">fastapi</span>
                    <span className="preview-keyword">aws</span>
                    <span className="preview-keyword">ai</span>
                    <span className="preview-keyword-add">+ Add more</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Feature highlights */}
          <div className="preview-features">
            <div className="preview-feature">
              <div className="preview-feature-icon">⚡</div>
              <h4>Instant Alerts</h4>
              <p>Get notified within 60 seconds via Telegram</p>
            </div>
            <div className="preview-feature">
              <div className="preview-feature-icon">🎯</div>
              <h4>Smart Scoring</h4>
              <p>AI-powered relevance scoring for each opportunity</p>
            </div>
            <div className="preview-feature">
              <div className="preview-feature-icon">📊</div>
              <h4>Track Everything</h4>
              <p>See all opportunities and your response rate</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="section" id="features">
        <div className="section-header">
          <div className="section-badge">Features</div>
          <h2 className="section-title">Everything You Need to Land More Gigs</h2>
          <p className="section-subtitle">Stop refreshing job boards. Let opportunities come to you.</p>
        </div>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>Smart Keyword Matching</h3>
            <p>Define your skills once. We'll match you with relevant opportunities using intelligent scoring.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Instant Telegram Alerts</h3>
            <p>Get notified within 60 seconds of a new post. Be the first freelancer to respond.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Relevance Scoring</h3>
            <p>Our algorithm scores each opportunity. Only get alerts for posts that truly match your skills.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Multiple Sources</h3>
            <p>We monitor r/forhire, r/freelance, r/startups, and Hacker News. More sources coming soon.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔒</div>
            <h3>No Spam, No Noise</h3>
            <p>Adjustable sensitivity means you control how many alerts you receive. Quality over quantity.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🌙</div>
            <h3>Set It & Forget It</h3>
            <p>Configure once, receive alerts forever. Pause anytime with one click.</p>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="section" id="pricing" style={{ background: 'var(--bg-secondary)' }}>
        <div className="section-header">
          <div className="section-badge">Pricing</div>
          <h2 className="section-title">Simple, Transparent Pricing</h2>
          <p className="section-subtitle">Start free. Upgrade when you're ready.</p>
        </div>
        
        <div className="pricing-grid">
          <div className="pricing-card">
            <div className="pricing-name">Free</div>
            <div className="pricing-price">$0<span>/month</span></div>
            <div className="pricing-desc">Perfect for trying it out</div>
            <ul className="pricing-features">
              <li><span className="pricing-check">✓</span> 10 alerts per day</li>
              <li><span className="pricing-check">✓</span> 5 skill keywords</li>
              <li><span className="pricing-check">✓</span> Telegram notifications</li>
              <li><span className="pricing-check">✓</span> Reddit monitoring</li>
            </ul>
            <Link to="/signup" className="btn btn-secondary btn-block">Get Started</Link>
          </div>
          
          <div className="pricing-card featured">
            <div className="pricing-name">Pro</div>
            <div className="pricing-price">$9<span>/month</span></div>
            <div className="pricing-desc">For serious freelancers</div>
            <ul className="pricing-features">
              <li><span className="pricing-check">✓</span> Unlimited alerts</li>
              <li><span className="pricing-check">✓</span> Unlimited keywords</li>
              <li><span className="pricing-check">✓</span> All platforms</li>
              <li><span className="pricing-check">✓</span> Priority support</li>
              <li><span className="pricing-check">✓</span> Early access to new features</li>
            </ul>
            <Link to="/signup" className="btn btn-primary btn-block">Start Free Trial</Link>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="section cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Land Your Next Gig?</h2>
          <p className="cta-subtitle">Join hundreds of freelancers who never miss an opportunity.</p>
          <Link to="/signup" className="btn btn-primary">Get Started Free →</Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-text">© 2026 HireSignal. All rights reserved.</div>
          <div className="footer-links">
            <a href="#" className="footer-link">Privacy</a>
            <a href="#" className="footer-link">Terms</a>
            <a href="#" className="footer-link">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Landing;
