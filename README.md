# AI Call Assistant for German Bureaucracy

## Overview

This project implements an AI-powered assistant to help with phone calls to German bureaucratic offices. It uses speech recognition to transcribe the agent's speech, employs the Claude AI model to generate appropriate responses in German, and utilizes text-to-speech to vocalize these responses.

## Features

- Real-time speech recognition for German
- AI-generated responses using Claude API
- Text-to-speech output in German
- Interactive mode allowing user to accept, modify, or replace AI suggestions
- Conversation transcript saving

## Prerequisites

- Python 3.7+
- A microphone for speech input
- An Anthropic API key

## Installation

1. Clone this repository:
2. Install the required Python packages:
   ```
   pip install -r requirements.txt 
   ```

3. Set up your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY='your_api_key_here'
   ```

## Usage

1. Run the script:
   ```
   python ai_call_assistant.py
   ```

2. When prompted, enter the goal of your call in German.

3. The assistant will then:
   - Listen to and transcribe the agent's speech
   - Generate a suggested response
   - Ask if you want to use, modify, or replace the suggestion
   - Speak the chosen response

4. After each interaction, you'll be asked if you want to continue the call.

5. When the call ends, a transcript will be saved as a JSON file.

## Important Notes

- Always review the AI's suggestions before they are spoken to ensure accuracy and appropriateness.
- This tool is meant to assist with calls, not to fully automate them. Maintain oversight throughout the conversation.
- Ensure you have the legal right to record and use AI assistance for your calls in your jurisdiction.
