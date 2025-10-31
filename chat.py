import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ChatModerator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        self.banned_keywords = ["kill", "hack", "dangerous", "bomb", "harm", "hurt"]
        
        self.system_prompt = """You are a helpful and friendly AI assistant. You provide harmless and accurate information. If asked about a dangerous, harmful, or illegal activity, you refuse to provide any information and explain why."""
    
    def moderate_message(self, user_input):
        """Check if the user input contains any banned keywords."""
        user_input_lower = user_input.lower()
        for keyword in self.banned_keywords:
            if keyword in user_input_lower:
                return False, f"Your message contains a banned keyword: '{keyword}'. Please refrain from using such language."
        return True, "Input passed moderation."
        
    def moderate_output(self, ai_response):
        """Replace banned keywords in AI response with [REDACTED]"""
        moderated_response = ai_response
        for keyword in self.banned_keywords:
            if keyword in moderated_response.lower():
                moderated_response = self.replace_word_preserving_case(moderated_response, keyword)
                
        return moderated_response
    
    def replace_word_preserving_case(self, text, word):
        """Replace a word in text while preserving its original case"""
        words = text.split()
        for i, w in enumerate(words):
            if word in w.lower():
                
                cleaned_word = w.lower().strip('.,!?;:')
                if word in cleaned_word:
                    words[i] = w.lower().replace(word, '[REDACTED]')
        return ' '.join(words)
    
    def call_ai_api(self, user_input):
        """Send prompt to OpenAI API and get response"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150,
                temperature=0.7,
            )
            
            ai_response = response.choices[0].message.content.strip()
            return ai_response
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"
        
    def process_user_input(self, user_input):
        """Process user input through moderation and AI response"""
        print(f"\nUser Input: {user_input}")
        
        input_approved, input_message = self.moderate_message(user_input)
        if not input_approved:
            return input_message
        
        print("Input approved. Calling AI API...")
        
        ai_response = self.call_ai_api(user_input)
        print(f"AI Response before moderation: {ai_response}")
        
        moderated_response = self.moderate_output(ai_response)
        
        if "[REDACTED]" in moderated_response:
            print("The AI response contained inappropriate content and has been redacted.")
        else:
            print("The AI response passed moderation.")
        
        return moderated_response
    
def main():
    chat_moderator = ChatModerator()
    
    print("Welcome to the Chat Moderator!")
    print("Type 'exit' to quit.")
    print("-----------------------------------")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Exiting chat. Goodbye!")
            break
        
        if not user_input:
            print("Please enter a valid message.")
            continue
        
        result = chat_moderator.process_user_input(user_input)
        print(f"AI: {result}")
        
        
if __name__ == "__main__":
    main()