import json
import uuid
import random
import boto3

# Failed once I tried changing stuff
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

GUESS_WORD_API_PATH = "/getPerson"
CREATE_RAW_PATH = "/createPerson"
SOLVE_PATH = "/solvePerson"
# MAX_ATTEMPTS = 5  # Adjust this value as needed

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

def generate_guess_word(word_len):
    global word_answer
    words_answer = load_words("randomwords.txt", word_len)
    
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
    
    if event['rawPath'] == SOLVE_PATH:
        
        # Check if the game_id already exists in DynamoDB - otherwise ask them to create a new game
        game_id = event['queryStringParameters']['game_id']
        response = table.get_item(Key={'game_id': game_id})
        if 'Item' in response:
            tries_left = response['Item']['tries_left']
            secret_word = response['Item']['secret_word']
            word_guess = event['queryStringParameters']['guessWord']
            word_len = response['Item']['word_len']
            
            all_words = load_words("randomwords.txt", word_len)
            
            if word_guess not in all_words:    
                message = f"The word {word_guess} is not in {word_len}-length word dictionary. Please enter a valid word from the dictionary."
                return {"message": message}
            
            else:
                tries_left = tries_left - 1
                n = 0
                answer = {}
                for char, word in zip(word_guess, secret_word):
                    n = n+1
                    char1 = str(n) + ". " + char
                    if char == word:
                        answer[char1] = "✔"
                    elif char in secret_word:
                        answer[char1] = "➕"
                    else:
                        answer[char1] = "❌"
                        
                answer['tries_left'] = tries_left
                        
                table.put_item(Item={'game_id': game_id, 'tries_left': tries_left, 'secret_word': secret_word})
                
                return answer

        else:
            return {"message": "No game_id found. Please create a new game by calling /createPerson"}
    
    elif event['rawPath'] == CREATE_RAW_PATH:
        # Takes input: wordLength from 4 - 8 to generate the word length
        # Generate a new random game_id
        game_id = str(uuid.uuid4())  # Generate a UUID as a string
        word_length_str = event['queryStringParameters'].get('wordLength', None)
        if word_length_str is not None and word_length_str.isdigit():
            word_len = int(word_length_str)
        
        # Generate word to guess
        secret_word = generate_guess_word(word_len)
        tries_left = word_len+1
        
        # Update DynamoDB with the new game_id
        table.put_item(Item={'game_id': game_id, 'tries_left': tries_left, 'secret_word': secret_word, 'word_len': word_len})
        
        message = f"You have created a new game of wordle with {word_len} letter and {tries_left} guess. The game id is: {game_id}, use it to predict the word!"
        
        out_message = {
            "word_len": word_len,
            "tries_left": tries_left,
            "game_id": game_id,
            "message": message
        }
        
        return out_message
        
        # Increment on number of visit
        
    
    #    elif event['rawPath'] == CREATE_RAW_PATH:
        # Lets use this to try to count stuff
        #print("Start Request for CreatePerson2")
        #decodedEvent = json.loads(event['body'])
        #firstName = decodedEvent['firstName']
        #print("Received request with firstname =" + firstName)
        # call database
        #return {"personID": str(uuid.uuid1())}