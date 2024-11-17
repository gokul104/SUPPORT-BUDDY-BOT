from flask import Flask, request, jsonify, make_response
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from flask_cors import CORS
import traceback

app = Flask(__name__)
# Enable CORS for all domains and methods
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

def create_system_message():
    """Create the initial system message for MotorMate"""
    return SystemMessage(content="""
   You are a compassionate mental health counselor who provides emotional support, active listening, and thoughtful guidance. Your tone is warm, understanding, and non-judgmental. When users share their thoughts, feelings, or struggles, respond with empathy, validate their experiences, and gently encourage positive steps. Help users feel safe and heard, but avoid giving medical advice or diagnosing conditions. If users express severe distress, suggest they seek help from a mental health professional. Engage in thoughtful conversations, provide resources when appropriate, and promote self-care and mindfulness practices. 
   keep the conversations short and concise and dont repeat what you have said earlier in the conversation.
   """)


def initialize_chat():
    """Initialize the chat model with appropriate parameters"""
    try:
        return ChatOllama(
            model="mistral",
            temperature=0.7,
            streaming=False
        )
    except Exception as e:
        print(f"Error initializing chat model: {str(e)}")
        raise

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Verify content type
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'success': False
            }), 415

        # Get data from request
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'error': 'No message provided',
                'success': False
            }), 400

        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({
                'error': 'Empty message',
                'success': False
            }), 400

        # Initialize chat model
        chat_model = initialize_chat()

        # Create conversation history
        conversation = [create_system_message()]
        history = data.get('history', [])
        
        # Add previous messages if they exist
        for msg in history:
            if msg['type'] == 'human':
                conversation.append(HumanMessage(content=msg['content']))
            elif msg['type'] == 'ai':
                conversation.append(AIMessage(content=msg['content']))

        # Add new user message
        conversation.append(HumanMessage(content=user_message))

        try:
            # Get response from model
            response = chat_model.invoke(conversation)
            response_content = response.content

            # Format the conversation history
            current_history = [
                {'type': 'human', 'content': user_message},
                {'type': 'ai', 'content': response_content}
            ]

            return jsonify({
                'response': response_content,
                'history': history + current_history,
                'success': True
            })

        except Exception as chat_error:
            print(f"Error getting response from chat model: {str(chat_error)}")
            return jsonify({
                'error': 'Error generating response',
                'detail': str(chat_error),
                'success': False
            }), 500

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': 'An error occurred while processing your request. Please try again.',
            'detail': str(e),
            'success': False
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'success': False}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'success': False}), 500

if __name__ == '__main__':
    # Make sure Ollama is running before starting the server
    try:
        test_chat = initialize_chat()
        print("Successfully connected to Ollama")
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"Error: Could not initialize chat model. Make sure Ollama is running and the Mistral model is installed.")
        print(f"Error details: {str(e)}")