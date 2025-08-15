const axios = require('axios');

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method Not Allowed' });
  }

  const { messages } = req.body;

  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ message: 'Invalid messages format' });
  }

  const API_KEY = process.env.GEMINI_API_KEY;
  if (!API_KEY) {
    console.error('GEMINI_API_KEY is not set in .env.development');
    return res.status(500).json({ message: 'API key not configured' });
  }

  const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${API_KEY}`;

  const contents = messages.map(msg => ({
    role: msg.sender === 'bot' ? 'model' : 'user',
    parts: [{ text: msg.text }],
  }));

  const data = {
    contents: contents,
  };

  try {
    const apiRes = await axios.post(API_URL, data, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const botResponse = apiRes.data.candidates[0]?.content?.parts[0]?.text || 'Sorry, I could not get a response.';

    res.status(200).json({ reply: botResponse });

  } catch (error) {
    console.error('Axios Error:', error.response ? error.response.data : error.message);
    res.status(500).json({ message: 'Internal Server Error' });
  }
};