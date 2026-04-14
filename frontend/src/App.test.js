import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from './App';

describe('App upload flow', () => {
  test('file upload component renders', () => {
    render(<App />);
    expect(screen.getByLabelText('subtitle-file')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
  });

  test('file validation only accepts .srt', () => {
    render(<App />);
    const input = screen.getByLabelText('subtitle-file');
    const invalidFile = new File(['hello'], 'notes.txt', { type: 'text/plain' });

    fireEvent.change(input, { target: { files: [invalidFile] } });

    expect(screen.getByRole('alert')).toHaveTextContent('Only .srt files are allowed');
  });

  test('API call triggered on upload and loading state shown', async () => {
    let resolveUpload;
    global.fetch = jest.fn(
      () =>
        new Promise((resolve) => {
          resolveUpload = resolve;
        })
    );

    render(<App />);
    const input = screen.getByLabelText('subtitle-file');
    const validFile = new File(['1\n00:00:01,000 --> 00:00:02,000\nHello\n'], 'sample.srt', {
      type: 'application/x-subrip',
    });

    fireEvent.change(input, { target: { files: [validFile] } });
    fireEvent.click(screen.getByRole('button', { name: 'Upload' }));

    expect(screen.getByRole('button')).toHaveTextContent('Uploading...');

    await waitFor(() => expect(global.fetch).toHaveBeenCalledTimes(1));
    resolveUpload({ ok: true });
    await waitFor(() => expect(screen.getByRole('button')).toHaveTextContent('Upload'));
    expect(global.fetch).toHaveBeenCalledWith('/api/upload/', expect.objectContaining({ method: 'POST' }));
  });
});
