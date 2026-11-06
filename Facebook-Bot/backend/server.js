const express = require('express');
const cors = require('cors');
const app = express();
app.use(cors());
app.use(express.json());

// Fake database for now - later we connect MongoDB
let pages = [];
let messages = [];

// 1. Connect Page (simulate)
app.post('/api/pages/connect', (req, res) => {
  const newPage = { id: Date.now(), ...req.body, status: 'connected', createdAt: new Date() };
  pages.push(newPage);
  res.json({ success: true, page: newPage });
});

// 2. Get Pages
app.get('/api/pages', (req, res) => res.json(pages));

// 3. Receive Message from Customer -> Send to AI Brain -> Return Reply
app.post('/api/chat', async (req, res) => {
  const { message } = req.body;
  messages.push({ from: 'customer', text: message });

  // Call Python AI Brain (localhost:8000)
  try {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await response.json();
    messages.push({ from: 'bot', text: data.reply });
    res.json({ reply: data.reply });
  } catch (e) {
    // Fallback if AI Brain no dey run
    const fallback = `I hear you: "${message}". Our AI brain is offline, but Desito store will reply soon. What product do you want?`;
    messages.push({ from: 'bot', text: fallback });
    res.json({ reply: fallback });
  }
});

// 4. Get all messages for dashboard
app.get('/api/messages', (req, res) => res.json(messages));

app.listen(5000, () => console.log("✅ Backend running on http://localhost:5000"));