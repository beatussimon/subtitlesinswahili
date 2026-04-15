// api.js

// Function to handle API fetch calls
const fetchAPI = async (url, options = {}) => {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch API Error:', error);
    }
};

// Function to get subtitles
export const getSubtitles = async (language) => {
    const url = `https://example.com/api/subtitles?lang=${language}`;
    return await fetchAPI(url);
};

// Function to get all available languages
export const getLanguages = async () => {
    const url = 'https://example.com/api/languages';
    return await fetchAPI(url);
};

// Function to get specific subtitle by ID
export const getSubtitleById = async (id) => {
    const url = `https://example.com/api/subtitles/${id}`;
    return await fetchAPI(url);
};
