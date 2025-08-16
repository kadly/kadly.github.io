const express = require('express');
const axios = require('axios');
const cors = require('cors');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors()); // Enable CORS for all routes
app.use(express.json());

// API endpoint for the chatbot
app.post('/api/chat', async (req, res) => {
  const { messages } = req.body;

  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ message: 'Invalid messages format' });
  }

  const API_KEY = process.env.GEMINI_API_KEY;
  if (!API_KEY) {
    console.error('GEMINI_API_KEY is not set in the .env file');
    return res.status(500).json({ message: 'API key not configured' });
  }

  const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${API_KEY}`;

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
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
