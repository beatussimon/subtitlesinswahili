import React, { useEffect, useMemo, useState } from 'react';

const apiFetch = (url, options = {}) =>
  fetch(url, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

function App() {
  const [user, setUser] = useState(null);
  const [authForm, setAuthForm] = useState({ username: '', password: '' });
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState('');
  const [subtitles, setSubtitles] = useState([]);
  const [requestTitle, setRequestTitle] = useState('');
  const [commentDrafts, setCommentDrafts] = useState({});
  const [uploadFile, setUploadFile] = useState(null);
  const [notice, setNotice] = useState('');

  const loadData = async (category = '') => {
    const [catRes, subRes, meRes] = await Promise.all([
      apiFetch('/api/categories/', { headers: {} }),
      fetch(`/api/subtitles/${category ? `?category=${category}` : ''}`, { credentials: 'include' }),
      fetch('/api/auth/me/', { credentials: 'include' }),
    ]);

    if (catRes.ok) {
      const catPayload = await catRes.json();
      setCategories(catPayload.categories);
    }

    if (subRes.ok) {
      const subPayload = await subRes.json();
      setSubtitles(subPayload.subtitles);
    }

    if (meRes.ok) {
      const mePayload = await meRes.json();
      setUser(mePayload.authenticated ? mePayload : null);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const subtitleCountLabel = useMemo(() => `${subtitles.length} subtitles`, [subtitles]);

  const submitAuth = async (mode) => {
    const response = await apiFetch(`/api/auth/${mode}/`, {
      method: 'POST',
      body: JSON.stringify(authForm),
    });

    if (!response.ok) {
      setNotice('Authentication failed.');
      return;
    }

    setNotice(mode === 'register' ? 'Account created.' : 'Welcome back.');
    setAuthForm({ username: '', password: '' });
    await loadData(activeCategory);
  };

  const logout = async () => {
    await apiFetch('/api/auth/logout/', { method: 'POST', body: JSON.stringify({}) });
    setUser(null);
    setNotice('Logged out.');
  };

  const toggleBookmark = async (subtitleId) => {
    const response = await fetch(`/api/subtitles/${subtitleId}/bookmark/`, {
      method: 'POST',
      credentials: 'include',
    });
    if (response.ok) {
      setNotice('Bookmark updated.');
      await loadData(activeCategory);
    }
  };

  const postComment = async (subtitleId) => {
    const response = await apiFetch(`/api/subtitles/${subtitleId}/comments/create/`, {
      method: 'POST',
      body: JSON.stringify({ body: commentDrafts[subtitleId] || '' }),
    });

    if (response.ok) {
      setCommentDrafts((prev) => ({ ...prev, [subtitleId]: '' }));
      setNotice('Comment posted.');
      await loadData(activeCategory);
    }
  };

  const submitRequest = async () => {
    const response = await apiFetch('/api/requests/create/', {
      method: 'POST',
      body: JSON.stringify({ requested_title: requestTitle }),
    });

    if (response.ok) {
      setRequestTitle('');
      setNotice('Subtitle request sent.');
    }
  };

  const uploadForTranslation = async () => {
    if (!uploadFile) {
      setNotice('Choose an SRT first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', uploadFile);
    const response = await fetch('/api/upload/', {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });

    if (response.ok) {
      setNotice('Translation job queued. Payout is TSh 1000.');
      setUploadFile(null);
    } else {
      setNotice('Upload failed. Login first or verify SRT format.');
    }
  };

  return (
    <main style={{ margin: '2rem auto', maxWidth: 980, fontFamily: 'Arial, sans-serif' }}>
      <h1>Swahili Subtitle Hub</h1>
      <p>Browse categories, bookmark favorites, request new movies, and download after login.</p>
      <p><strong>{subtitleCountLabel}</strong></p>

      {!user ? (
        <section style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          <input
            aria-label="username"
            placeholder="username"
            value={authForm.username}
            onChange={(e) => setAuthForm((prev) => ({ ...prev, username: e.target.value }))}
          />
          <input
            aria-label="password"
            type="password"
            placeholder="password"
            value={authForm.password}
            onChange={(e) => setAuthForm((prev) => ({ ...prev, password: e.target.value }))}
          />
          <button type="button" onClick={() => submitAuth('login')}>Login</button>
          <button type="button" onClick={() => submitAuth('register')}>Register</button>
        </section>
      ) : (
        <section style={{ marginBottom: '1rem' }}>
          <span>Logged in as <strong>{user.username}</strong>. </span>
          <button type="button" onClick={logout}>Logout</button>
        </section>
      )}

      <section style={{ marginBottom: '1rem' }}>
        <strong>Categories:</strong>{' '}
        <button type="button" onClick={() => { setActiveCategory(''); loadData(''); }}>All</button>
        {categories.map((category) => (
          <button
            key={category.id}
            type="button"
            onClick={() => {
              setActiveCategory(category.slug);
              loadData(category.slug);
            }}
            style={{ marginLeft: '0.5rem' }}
          >
            {category.name}
          </button>
        ))}
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2>Subtitle Requests</h2>
        <input
          aria-label="request-title"
          placeholder="Movie title to request"
          value={requestTitle}
          onChange={(e) => setRequestTitle(e.target.value)}
        />
        <button type="button" onClick={submitRequest}>Request Subtitle</button>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2>Translate on the fly (Feature)</h2>
        <input aria-label="subtitle-file" type="file" accept=".srt" onChange={(e) => setUploadFile(e.target.files?.[0] || null)} />
        <button type="button" onClick={uploadForTranslation}>Upload for Translation (TSh 1000)</button>
      </section>

      <section>
        <h2>Subtitle Library</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '0.75rem' }}>
          {subtitles.map((subtitle) => (
            <article key={subtitle.id} style={{ border: '1px solid #ddd', borderRadius: 8, padding: '0.75rem' }}>
              <h3>{subtitle.title} ({subtitle.movie_year})</h3>
              <small>{subtitle.category} • {subtitle.language}</small>
              <p>{subtitle.synopsis}</p>
              <p><strong>Translation fee:</strong> TSh {subtitle.translation_fee_tsh}</p>
              <p>Bookmarks: {subtitle.bookmarks_count} • Comments: {subtitle.comments_count}</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                <a href={`/api/subtitles/${subtitle.id}/download/`}>Download</a>
                <button type="button" onClick={() => toggleBookmark(subtitle.id)}>Bookmark</button>
              </div>
              <textarea
                aria-label={`comment-${subtitle.id}`}
                placeholder="Leave a comment"
                value={commentDrafts[subtitle.id] || ''}
                onChange={(e) => setCommentDrafts((prev) => ({ ...prev, [subtitle.id]: e.target.value }))}
                style={{ width: '100%', marginTop: '0.5rem' }}
              />
              <button type="button" onClick={() => postComment(subtitle.id)}>Post Comment</button>
            </article>
          ))}
        </div>
      </section>

      {notice && <p role="status">{notice}</p>}
    </main>
  );
}

export default App;
