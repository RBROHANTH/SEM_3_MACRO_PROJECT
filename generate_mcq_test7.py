import subprocess
import random
import time
import re
difficulty_levels = {
    'k1': 'k1:Remembering: Simple recall of facts',
    'k2': 'k2:Understanding: Explaining concepts',
    'k3': 'k3:Applying: Using knowledge in new situations',
    'k4': 'k4:Analyzing: Breaking down complex concepts',
    'k5': 'k5:Evaluating: Making judgments',
}
def generate_mcq(topic, difficulty):
    prompt = (
    f"Generate a multiple-choice question on the topic '{topic}' with difficulty with bloom's taxonomy difficulty level of '{difficulty}'. "
    "The question should have four options labeled A, B, C, and D. "
    "Clearly mark the correct answer in the format: Correct Answer: [Answer]"
)

    command = ["ollama", "run", "llama2", prompt]
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error generating MCQ: {e.stderr}")
        return None
def parse_correct_answer(mcq):
    match = re.search(r'Correct answer:?\s*([A-D])', mcq, re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        print("Unable to parse the correct answer.")
        return None
def ask_mcq(question):
    print(question)
    answer = input("Enter your answer (A, B, C, D): ").upper()
    return answer
def adjust_difficulty(previous_difficulty, correct, time_taken):
    difficulty_keys = list(difficulty_levels.keys())
    current_index = difficulty_keys.index(previous_difficulty)
    if correct:
        if time_taken < 10:
            print("Suspicious activity")
            return previous_difficulty, 0  
        elif 10 <= time_taken < 30:
            new_index = min(current_index + 3, len(difficulty_keys) - 1)
            return difficulty_keys[new_index], 2
        elif 30 <= time_taken < 60:
            new_index = min(current_index + 2, len(difficulty_keys) - 1)
            return difficulty_keys[new_index], 1.5
        elif 60 <= time_taken < 120:
            new_index = min(current_index + 1, len(difficulty_keys) - 1)
            return difficulty_keys[new_index], 1
        else:
            print("Time out. Moving to the next question.")
            return previous_difficulty, 0  
    else:
        new_index = max(current_index - 1, 0)  
        return difficulty_keys[new_index], 0
if __name__ == "__main__":  
    topic = input("Enter the syllabus for the questions: ")
    difficulty = random.choice(list(difficulty_levels.keys()))
    score = 0
    total_questions = 10
    for i in range(total_questions):
        print(f"\nQuestion {i + 1} (Difficulty: {difficulty_levels[difficulty]})")
        mcq = generate_mcq(topic, difficulty)
        if mcq:
            print(f"Generated MCQ:\n{mcq}")  
            correct_answer = parse_correct_answer(mcq)
            if correct_answer:
                start_time = time.time()
                answer = ask_mcq(mcq)  
                end_time = time.time()
                time_taken = end_time - start_time
                print(f"Time taken: {time_taken:.2f} seconds")
                correct = answer == correct_answer
                if correct:
                    print("Correct!")
                else:
                    print(f"Incorrect. The correct answer was: {correct_answer}")
                difficulty, earned_score = adjust_difficulty(difficulty, correct, time_taken)
                score += earned_score
            else:
                print("Skipping to the next question due to an error in parsing.")
        else:
            print("Error generating the question. Skipping to the next question.")
    print(f"\nYou scored {score} out of 20 marks .")
    if score >= 15:
        print("Level: Advanced")
    elif 8 <= score < 15:
        print("Level: Intermediate")
    else:
        print("Level: Beginner")