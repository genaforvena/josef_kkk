# AI Call Assistant

## Overview

This project implements an AI-powered assistant to help with phone calls. It uses speech recognition to transcribe the user's speech, employs the Ollama AI model to generate appropriate responses, and utilizes text-to-speech to vocalize these responses.

## Features

- Real-time speech recognition and translation
- AI-generated responses using Ollama API
- Text-to-speech output
- Interactive mode allowing user to stop speech recognition and AI response
- Conversation history tracking

## Prerequisites

- Python 3.7+
- A microphone for speech input
- Ollama installed and running locally

## Installation

1. Clone this repository
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:
   ```
   python main.py [--instruction "Your custom instruction"]
   ```

2. The assistant will start the conversation. Press Enter to stop speech recognition and get Ollama's response.

3. The assistant will then:
   - Listen to and transcribe your speech
   - Translate the speech (if applicable)
   - Generate a response using Ollama
   - Speak the response

4. Press Space to stop the AI's response at any time.

5. After each interaction, you can continue speaking. Press Enter again to stop speech recognition and get the next response.

## Important Notes

- The default instruction sets the AI as an actor rehearsing a part in a phone conversation, replying in English only.
- You can customize the AI's behavior by providing a different instruction when starting the script.
- This tool is meant to assist with calls, not to fully automate them. Maintain oversight throughout the conversation.
- Ensure you have the legal right to record and use AI assistance for your calls in your jurisdiction.

## Usage

1. Run the script:
   ```
   python main.py [--instruction "Your custom instruction"]
   ```

2. The assistant will start the conversation. Press Enter to stop speech recognition and get Ollama's response.

3. The assistant will then:
   - Listen to and transcribe your speech
   - Translate the speech (if applicable)
   - Generate a response using Ollama
   - Speak the response

4. Press Space to stop the AI's response at any time.

5. After each interaction, you can continue speaking. Press Enter again to stop speech recognition and get the next response.

## Important Notes

- The default instruction sets the AI as an actor rehearsing a part in a phone conversation, replying in English only.
- You can customize the AI's behavior by providing a different instruction when starting the script.
- This tool is meant to assist with calls, not to fully automate them. Maintain oversight throughout the conversation.
- Ensure you have the legal right to record and use AI assistance for your calls in your jurisdiction.
