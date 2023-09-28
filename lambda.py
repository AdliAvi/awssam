import json
import uuid
import random
import boto3

# Failed once I tried changing stuff
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

GUESS_WORD_API_PATH = "/getPerson"
CREATE_RAW_PATH = "/createPerson"
MAX_ATTEMPTS = 5  # Adjust this value as needed

# Global variables to store the word and the current attempt count
word_answer = None
current_attempts = 0

def load_words(filename, n):
    with open(filename, 'r') as f:
        words = f.read().splitlines()
    filtered_words = [word for word in words if len(word) == n]
    return filtered_words

def generate_guess_word():
    global word_answer
    words_answer = load_words("randomwords.txt", 5)
    word_answer = random.choice(words_answer)

def handler(event, context):
    global current_attempts
    
    dynamodb = boto3.resource('dynamodb')
    table_name = "wordleGuess"
    table = dynamodb.Table(table_name)
    
    print(event)
    
    if event['rawPath'] == GUESS_WORD_API_PATH:
        if word_answer is None:
            generate_guess_word()
        
        if current_attempts >= MAX_ATTEMPTS:
            return {"message": "You have used all your attempts."}
        
        # Increment the attempt count
        current_attempts += 1
        
        # GetPerson call database
        print("This is the Guess Word Inputted")
        word_guess = event['queryStringParameters']['guessWord']
        print("Received guess word " + word_guess)
        
        # temporary game id to block github check
        game_id = "asd"
        
        answer = {}
        
        response = table.get_item(Key={'game_id': game_id})
        if 'Item' in response:
            tries_left = response['Item']['tries_left']
            
            n = 0        
            for char, word in zip(word_answer, word_guess):
                n += 1
                char1 = str(n) + ". " + word
                if char == word:
                    answer[char1] = "✔"
                elif word in word_answer:
                    answer[char1] = "➕"
                else:
                    answer[char1] = "❌"

            tries_left += 1
            
            return {"answer": answer, "tries_left": tries_left}
        else:
            return {"message": "Game not found"}
    
    #elif event['rawPath'] == CREATE_RAW_PATH:
        # Create a DB table to store the word and game id to use continously
    