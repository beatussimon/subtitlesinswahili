import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from './App';

describe('Swahili subtitle hub', () => {
  beforeEach(() => {
    global.fetch = jest.fn((url) => {
      if (url.includes('/api/categories/')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ categories: [{ id: 1, name: 'Action', slug: 'action' }] }) });
      }
      if (url.includes('/api/subtitles/')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              subtitles: [
                {
                  id: 1,
                  title: 'Fast Horizon',
                  movie_year: 2023,
                  synopsis: 'A thriller.',
                  language: 'Swahili',
                  category: 'Action',
                  translation_fee_tsh: 1000,
                  bookmarks_count: 0,
                  comments_count: 0,
                },
              ],
            }),
        });
      }
      if (url.includes('/api/auth/me/')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ authenticated: false }) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
    delete global.fetch;
  });

  test('renders catalog and translation feature', async () => {
    render(<App />);

    expect(screen.getByText('Swahili Subtitle Hub')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText('Fast Horizon (2023)')).toBeInTheDocument());
    expect(screen.getByRole('button', { name: 'Upload for Translation (TSh 1000)' })).toBeInTheDocument();
  });

  test('shows srt upload input', () => {
    render(<App />);
    expect(screen.getByLabelText('subtitle-file')).toBeInTheDocument();
  });

  test('can type request title', () => {
    render(<App />);
    const requestInput = screen.getByLabelText('request-title');
    fireEvent.change(requestInput, { target: { value: 'Inception' } });
    expect(requestInput).toHaveValue('Inception');
  });
});
