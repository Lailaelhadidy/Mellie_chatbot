from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import requests
import re
import wikipedia

wikipedia.set_lang("en")
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

import os
from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


def clean_query_for_wikipedia(user_input):
    # Remove unnecessary phrases and clean the query
    cleaned_query = re.sub(r"what is |who is |tell me about |the capital of ", "", user_input.lower()).strip()
    return cleaned_query


def search_wikipedia(query):
    try:
        # Specific handling for 'capital of France' to ensure correct result
        if "capital of france" in query.lower():
            summary = wikipedia.summary("Paris", sentences=2)
            return f"📚 Here\"s what I found on Wikipedia about Paris:\n{summary} 😊"

        # First, try a direct summary of the query
        summary = wikipedia.summary(query, sentences=2)
        return f"📚 Here\"s what I found on Wikipedia:\n{summary} 😊"
    except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError):
        try:
            # If direct summary fails, search for the query
            search_results = wikipedia.search(query)
            if not search_results:
                return "❌ Sorry, I couldn\"t find anything on that topic in Wikipedia. 😊"

            # Iterate through search results to find a relevant one
            for result_title in search_results:
                try:
                    # Try to get a summary for each search result
                    summary = wikipedia.summary(result_title, sentences=2)
                    # Check if the original query (or parts of it) is present in the result title or summary
                    if query.lower() in result_title.lower() or any(
                            word in summary.lower() for word in query.lower().split()):
                        return f"📚 Here\"s what I found on Wikipedia about {result_title}:\n{summary} 😊"
                except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError):
                    continue  # Skip this result if it causes an error and try the next one

            # If no highly relevant result is found, return the summary of the first search result
            if search_results:
                summary = wikipedia.summary(search_results[0], sentences=2)
                return f"📚 Here\"s what I found on Wikipedia about {search_results[0]}:\n{summary} 😊"
            else:
                return "❌ Sorry, I couldn\"t find anything on that topic in Wikipedia. 😊"
        except Exception as e:
            return f"⚠️ Oops! Something went wrong during search: {str(e)}"
    except Exception as e:
        return f"⚠️ Oops! Something went wrong: {str(e)}"


def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        print(f"DEBUG: Weather API URL: {url}")
        response = requests.get(url)
        print(f"DEBUG: Weather API Response Status: {response.status_code}")
        data = response.json()
        print(f"DEBUG: Weather API Response Data: {data}")

        if data.get("cod") != 200:
            return "😕 Sorry, I couldn't find the weather for that city. Please check the name and try again."

        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        return (
            f"🌤️ The weather in {city.title()} is currently {description}.\n"
            f"🌡️ Temperature: {temp}°C\n"
            f"💧 Humidity: {humidity}%\n"
            f"🌬️ Wind Speed: {wind_speed} m/s"
        )
    except Exception as e:
        return "⚠️ Oops! Something went wrong while fetching the weather."


def extract_city(text):
    # Improved regex to capture city names more reliably
    match = re.search(r"weather(?:\s+in)?\s+([a-zA-Z\s]+)", text.lower())
    if match:
        city = match.group(1).strip().title()
        # Basic validation to avoid capturing very short or irrelevant strings
        if len(city) > 2 and not any(char.isdigit() for char in city):
            return city
    return None  # Return None if no city is found


intro = (
    "This is a friendly and intelligent assistant named Millie, designed to help Layla with questions and conversations.\n"
    "Millie speaks in a warm, cheerful tone, always uses emojis, and remembers the user's name is Layla.\n"
    "Example 1:\n"
    "User: Hello Millie\n"
    "Millie: Hello Layla! 😊 How’s your day going?\n"
    "Example 2:\n"
    "User: My name is Layla\n"
    "Millie: Nice to meet you, Layla! 🌟 What would you like to chat about?\n"
    "Example 3:\n"
    "User: Recommend me a movie\n"
    "Millie: I’d love to! 🎬 How about a romantic classic like 'The Notebook'?\n"
)

chat_history_ids = None  # to keep track of chat context

print("🤖 Mellie is online! Type 'exit', 'bye', or 'quit' to end the conversation.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit', 'bye']:
        print("Millie: Goodbye! 🖐️")
        break

    if user_input.lower() in ["thanks", "thank you"]:
        print("Millie: You're welcome! 😊 Let me know if you need anything else.")
        continue

    if "good morning" in user_input.lower():
        print(f"Millie: Good morning! ☀️ How can I help you today?")
        continue
    elif "good afternoon" in user_input.lower():
        print(f"Millie: Good afternoon! 🌤️ I hope you are having a great day.")
        continue
    elif "good evening" in user_input.lower():
        print(f"Millie: Good evening! 🌙 What can I do for you?")
        continue
    elif user_input.lower() in ["hello", "hello millie", "hi", "hey"]:
        print(f"Millie: Hello! How can I help you? 😊")
        continue

    if "weather" in user_input.lower():
        city = extract_city(user_input)
        if city is None:
            print(
                "Millie: I couldn\'t determine the city. Could you please specify which city\'s weather you\'d like to know? 😊")
        else:
            print(f"Millie: {get_weather(city)} ")
        continue

    cleaned_query = clean_query_for_wikipedia(user_input)
    if cleaned_query:
        wiki_reply = search_wikipedia(cleaned_query)
        print(f"Millie: {wiki_reply} 😊")
        continue

    if user_input.lower().startswith(("what", "who", "where", "when", "why", "how")) or \
            "who is" in user_input.lower() or "what is" in user_input.lower() or "tell me about" in user_input.lower():
        # Clean the query before sending to Wikipedia
        cleaned_query = clean_query_for_wikipedia(user_input)
        if not cleaned_query:
            print("Millie: I need more information to search Wikipedia. Could you please be more specific? 😊")
            continue

        try:
            search_results = wikipedia.search(cleaned_query)
            if not search_results:
                wiki_reply = "❌ Sorry, I couldn\"t find anything on that topic in Wikipedia. 😊"
            else:
                # Try to get summary of the first search result
                summary = wikipedia.summary(search_results[0], sentences=2)
                wiki_reply = f"📚 Here\"s what I found on Wikipedia about {search_results[0]}:\n{summary} 😊"
        except wikipedia.exceptions.DisambiguationError as e:
            if e.options:
                try:
                    summary = wikipedia.summary(e.options[0], sentences=2)
                    wiki_reply = f"🔍 Your query was a bit broad, but I found this on {e.options[0]}:\n{summary} 😊"
                except:
                    wiki_reply = f"🔍 Your query was too broad. Try something more specific, like: {e.options[:2]}"
            else:
                wiki_reply = f"🔍 Your query was too broad. Try something more specific."
        except wikipedia.exceptions.PageError:
            wiki_reply = "❌ Sorry, I couldn\"t find anything on that topic in Wikipedia. 😊"
        except Exception as e:
            wiki_reply = f"⚠️ Oops! Something went wrong: {str(e)}"

        print(f"Millie: {wiki_reply} 😊")
        continue

    # DialoGPT response generation
    if chat_history_ids is None:
        # For the very first turn, include the intro
        input_text = intro + f"\nUser: {user_input}\nMillie:"
    else:
        # For subsequent turns, just append the new user input
        input_text = f"\nUser: {user_input}\nMillie:"

    new_input_ids = tokenizer.encode(input_text, return_tensors='pt')

    if chat_history_ids is None:
        chat_history_ids = new_input_ids
    else:
        chat_history_ids = torch.cat([chat_history_ids, new_input_ids], dim=-1)

    attention_mask = torch.ones_like(chat_history_ids)

    output_ids = model.generate(
        chat_history_ids,
        attention_mask=attention_mask,
        max_length=1000,
        pad_token_id=tokenizer.eos_token_id
    )

    reply = tokenizer.decode(output_ids[:, chat_history_ids.shape[-1]:][0], skip_special_tokens=True)

    print(f"Millie: {reply} ")
    chat_history_ids = output_ids










