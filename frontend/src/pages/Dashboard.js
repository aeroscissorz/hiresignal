import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { supabase } from '../supabase';

const BOT_USERNAME = process.env.REACT_APP_BOT_USERNAME || 'Job55Bot';

function Dashboard({ session }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [linking, setLinking] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [skillKeywords, setSkillKeywords] = useState('');
  const [scoreThreshold, setScoreThreshold] = useState(3);
  const [isActive, setIsActive] = useState(true);

  useEffect(() => { fetchProfile(); }, [session]);

  const fetchProfile = async () => {
    try {
      const { data, error } = await supabase.from('users').select('*').eq('id', session.user.id).single();
      if (error && error.code !== 'PGRST116') throw error;
      if (data) {
        setProfile(data);
        setSkillKeywords(data.skill_keywords?.join(', ') || '');
        setScoreThreshold(data.score_threshold || 3);
        setIsActive(data.is_active ?? true);
      }
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true); setError(''); setSuccess('');
    try {
      const keywords = skillKeywords.split(',').map(k => k.trim().toLowerCase()).filter(k => k);
      const { error } = await supabase.from('users').upsert({
        id: session.user.id, email: session.user.email,
        skill_keywords: keywords, score_threshold: scoreThreshold, is_active: isActive,
      });
      if (error) throw error;
      setSuccess('Settings saved!');
      fetchProfile();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) { setError(err.message); }
    finally { setSaving(false); }
  };

  const handleConnectTelegram = async () => {
    setLinking(true); setError('');
    try {
      const linkCode = crypto.randomUUID().replace(/-/g, '').slice(0, 24);
      const { error } = await supabase.from('users').update({ telegram_link_code: linkCode }).eq('id', session.user.id);
      if (error) throw error;
      window.open(`https://t.me/${BOT_USERNAME}?start=${linkCode}`, '_blank');
      let attempts = 0;
      const check = setInterval(async () => {
        attempts++;
        const { data } = await supabase.from('users').select('telegram_chat_id').eq('id', session.user.id).single();
        if (data?.telegram_chat_id) { clearInterval(check); setSuccess('Telegram connected!'); fetchProfile(); setLinking(false); }
        else if (attempts > 30) { clearInterval(check); setLinking(false); }
      }, 2000);
    } catch (err) { setError(err.message); setLinking(false); }
  };

  const handleDisconnect = async () => {
    const { error } = await supabase.from('users').update({ telegram_chat_id: null }).eq('id', session.user.id);
    if (!error) { setSuccess('Disconnected'); fetchProfile(); }
  };

  const handleSignOut = () => supabase.auth.signOut();
  const parsedKeywords = skillKeywords.split(',').map(k => k.trim()).filter(k => k);
  const telegramConnected = !!profile?.telegram_chat_id;

  if (loading) return <div className="loading-container"><div className="spinner"></div></div>;

  return (
    <div className="dashboard">
      <nav className="navbar scrolled">
        <div className="navbar-content">
          <Link to="/" className="logo">
            <div className="logo-icon">⚡</div>
            <span>HireSignal</span>
          </Link>
          <div className="nav-right">
            <div className="user-info" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div className="user-avatar">{session.user.email?.charAt(0).toUpperCase()}</div>
              <span className="user-email">{session.user.email}</span>
            </div>
            <button onClick={handleSignOut} className="btn btn-ghost">Sign out</button>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
          <p>Manage your alerts and skill keywords</p>
        </div>

        {error && <div className="alert alert-error"><span>⚠️</span>{error}</div>}
        {success && <div className="alert alert-success"><span>✓</span>{success}</div>}

        {/* Status */}
        <div className="status-card">
          <div className="status-info">
            <div className={`status-icon ${isActive && telegramConnected ? 'active' : 'inactive'}`}>
              {isActive && telegramConnected ? '📡' : '⏸️'}
            </div>
            <div className="status-text">
              <h3>Alert Status</h3>
              <span className={`status-badge ${isActive && telegramConnected ? 'active' : 'inactive'}`}>
                <span className="status-badge-dot"></span>
                {!telegramConnected ? 'Connect Telegram' : isActive ? 'Active' : 'Paused'}
              </span>
            </div>
          </div>
          <label className="toggle">
            <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} disabled={!telegramConnected} />
            <span className="toggle-track"></span>
          </label>
        </div>

        {/* Telegram */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <div className="card-icon">📱</div>
              <div className="card-title-text">
                <h3>Telegram Notifications</h3>
                <p>{telegramConnected ? 'Connected and ready' : 'Connect to receive alerts'}</p>
              </div>
            </div>
            {telegramConnected && <span className="status-badge active"><span className="status-badge-dot"></span>Connected</span>}
          </div>
          {telegramConnected ? (
            <button className="btn btn-secondary btn-block" onClick={handleDisconnect}>Disconnect Telegram</button>
          ) : (
            <button className="btn btn-primary btn-block" onClick={handleConnectTelegram} disabled={linking}>
              {linking ? 'Waiting for connection...' : '📲 Connect Telegram'}
            </button>
          )}
          {linking && <p style={{ marginTop: '16px', fontSize: '14px', color: 'var(--text-muted)', textAlign: 'center' }}>Click "Start" in Telegram to complete</p>}
        </div>

        {/* Skills */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <div className="card-icon">🎯</div>
              <div className="card-title-text">
                <h3>Your Skills</h3>
                <p>Keywords we'll match against opportunities</p>
              </div>
            </div>
          </div>
          <form onSubmit={handleSave}>
            <div className="form-group">
              <label>Skill Keywords <span className="label-hint">(comma-separated)</span></label>
              <textarea
                value={skillKeywords}
                onChange={(e) => setSkillKeywords(e.target.value)}
                placeholder="python, react, node.js, aws, machine learning, data science..."
              />
              {parsedKeywords.length > 0 && (
                <div className="keywords-container">
                  {parsedKeywords.map((kw, i) => <span key={i} className="keyword-tag">{kw}</span>)}
                  <span className="keyword-count">{parsedKeywords.length} keywords</span>
                </div>
              )}
            </div>
            <div className="form-group">
              <label>Alert Sensitivity</label>
              <select value={scoreThreshold} onChange={(e) => setScoreThreshold(parseInt(e.target.value))}>
                <option value={1}>Very High - More alerts</option>
                <option value={2}>High</option>
                <option value={3}>Balanced (recommended)</option>
                <option value={4}>Low</option>
                <option value={5}>Very Low - Only best matches</option>
              </select>
            </div>
            <button type="submit" className="btn btn-primary btn-block" disabled={saving}>
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </form>
        </div>

        {/* Info */}
        <div className="card" style={{ background: 'var(--bg-secondary)' }}>
          <div className="card-header">
            <div className="card-title">
              <div className="card-icon">💡</div>
              <div className="card-title-text">
                <h3>How Scoring Works</h3>
                <p>Understanding your alerts</p>
              </div>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div style={{ padding: '16px', background: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>💼</div>
              <div style={{ fontWeight: '600', marginBottom: '4px' }}>Hiring Keywords</div>
              <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>+2 points each</div>
            </div>
            <div style={{ padding: '16px', background: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>🛠️</div>
              <div style={{ fontWeight: '600', marginBottom: '4px' }}>Your Skills</div>
              <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>+1 point each</div>
            </div>
            <div style={{ padding: '16px', background: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>📊</div>
              <div style={{ fontWeight: '600', marginBottom: '4px' }}>Threshold</div>
              <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Score ≥ {scoreThreshold} triggers alert</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
