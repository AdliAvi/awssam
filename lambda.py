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

# dynamodb_client = boto3.resource('dynamodb')
# table = dynamodb_client.Table('wordGuess')

# Global variables to store the word and the current attempt count
# word_answer = None
# current_attempts = 0

def load_words(filename, n):
    with open(filename, 'r') as f:
        words = f.read().splitlines()
    filtered_words = [word for word in words if len(word) == n]
    return filtered_words

def generate_guess_word():
    global word_answer
    words_answer = load_words("randomwords.txt", 5)
    
    if not words_answer:
        raise ValueError("No words of the specified length found in the word list.")
    
    word_answer = random.choice(words_answer)
    return word_answer

def handler(event, context):
    global current_attempts
        
    dynamodb = boto3.resource('dynamodb')
    table_name = 'simpleWordleCount'
    table = dynamodb.Table(table_name)
    
    print(event)
    
    if event['rawPath'] == GUESS_WORD_API_PATH:
        
        # Check if the game_id already exists in DynamoDB - otherwise ask them to create a new game
        # response = table.get_item(Key={'game_id': game_id})
        # if 'Item' in response:
        #     tries_left = response['Item']['tries_left']
        
        # tries_left += 1
        
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
        # Takes input: wordLength from 4 - 8 to generate the word length
        # Generate a new random game_id
        game_id = str(uuid.uuid4())  # Generate a UUID as a string
        word_len = event['queryStringParameters']['wordLength']
        
        # Generate word to guess
        secret_word = generate_guess_word()
        tries_left = 6
        
        # Update DynamoDB with the new game_id
        table.put_item(Item={'game_id': game_id, 'tries_left': tries_left, 'secret_word': secret_word})
        
        message = f"You have created a new game of wordle with {word_len} letter and {tries_left} guess. The game id is: {game_id}, use it to predict the word!"
        return {"message": message}
        
        # Increment on number of visit
        
    
    #    elif event['rawPath'] == CREATE_RAW_PATH:
        # Lets use this to try to count stuff
        #print("Start Request for CreatePerson2")
        #decodedEvent = json.loads(event['body'])
        #firstName = decodedEvent['firstName']
        #print("Received request with firstname =" + firstName)
        # call database
        #return {"personID": str(uuid.uuid1())}