import json
import uuid
import random

# Failed once I tried changing stuff
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

GUESS_WORD_API_PATH = "/getPerson"
CREATE_RAW_PATH = "/createPerson"
MAX_ATTEMPTS = 5  # Adjust this value as needed

# dynamodb_client = boto3.resource('dynamodb')
# table = dynamodb_client.Table('wordGuess')

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
        
        answer = {}
        
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

        answer['attempt_left'] = 5-n
        
        return answer
    
    elif event['rawPath'] == CREATE_RAW_PATH:
        # CreatePerson Path -- write to database
        print("Start Request for CreatePerson2")
        decodedEvent = json.loads(event['body'])
        firstName = decodedEvent['firstName']
        print("Received request with firstname =" + firstName)
        # call database
        return {"personID": str(uuid.uuid1())}