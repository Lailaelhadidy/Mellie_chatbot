# Mellie_chatbot

👩‍💻 Overview

Millie is a personalized, emoji-friendly AI chatbot designed to engage in natural language conversation, provide real-time weather information, and fetch factual summaries from Wikipedia. The bot is powered by OpenAI's DialoGPT-medium model and integrates external knowledge sources through the Wikipedia API and OpenWeatherMap API.

🌐 Features

1. 🌤️ Weather Information

Extracts the city name from user input using regular expressions.

Uses the OpenWeatherMap API to fetch real-time weather data.

Returns temperature, humidity, description, and wind speed.

Handles API errors and city not found scenarios gracefully.

2. 📖 Wikipedia Summaries

Cleans the user query to remove filler phrases (e.g., "what is", "tell me about").

Uses the wikipedia.summary() and wikipedia.search() functions to fetch summaries.

Handles disambiguation and page errors using a fallback loop.

Returns rich summaries for educational and factual queries.

3. 🧑‍📚 Natural Conversation (DialoGPT)

Uses HuggingFace's microsoft/DialoGPT-medium model.

Maintains context across conversation turns using chat_history_ids.

Responds to casual greetings, questions, and conversation inputs.

Prepends a custom intro prompt to make the bot friendly and personalized.

4. ☺️ Personality & Emojis

Responds with emojis to sound cheerful and engaging.

Greets the user by name (Layla) using hardcoded examples.

Uses consistent tone and templates for good morning/evening greetings.
