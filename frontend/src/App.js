import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    const uploaded = event.target.files?.[0];
    if (!uploaded) {
      return;
    }

    if (!uploaded.name.toLowerCase().endsWith('.srt')) {
      setError('Only .srt files are allowed');
      setFile(null);
      return;
    }

    setError('');
    setFile(uploaded);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please choose a valid .srt file');
      return;
    }

    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ margin: '2rem auto', maxWidth: 680 }}>
      <h1>English to Swahili Subtitle Translator</h1>
      <input aria-label="subtitle-file" type="file" accept=".srt" onChange={handleFileChange} />
      <button type="button" onClick={handleUpload} disabled={loading}>
        {loading ? 'Uploading...' : 'Upload'}
      </button>
      {error && <p role="alert">{error}</p>}
    </main>
  );
}

export default App;
