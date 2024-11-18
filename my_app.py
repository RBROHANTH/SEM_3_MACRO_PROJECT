import streamlit as st
import subprocess
import random
import time
import re

# Difficulty Levels Dictionary
difficulty_levels = {
    'k1': 'k1:Remembering: Simple recall of facts',
    'k2': 'k2:Understanding: Explaining concepts',
    'k3': 'k3:Applying: Using knowledge in new situations',
    'k4': 'k4:Analyzing: Breaking down complex concepts',
    'k5': 'k5:Evaluating: Making judgments'
}

# Function to generate MCQ based on topic and difficulty
def generate_mcq(topic, difficulty):
    prompt = (
        f"Generate a multiple-choice question on the topic '{topic}' "
        f"with a Bloom's taxonomy difficulty level of '{difficulty}'. "
        "The question should have four options labeled A, B, C, and D. "
        "Clearly mark the correct answer in the format: Correct Answer: [Answer]"
    )
    command = ["ollama", "run", "llama2", prompt]
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        st.error(f"Error generating MCQ: {e.stderr}")
        return None

# Function to parse the correct answer from MCQ text
def parse_correct_answer(mcq):
    match = re.search(r'Correct answer:?\s*([A-D])', mcq, re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        st.warning("Unable to parse the correct answer.")
        return None

# Function to adjust difficulty based on previous answer correctness and time taken
def adjust_difficulty(previous_difficulty, correct, time_taken):
    difficulty_keys = list(difficulty_levels.keys())
    current_index = difficulty_keys.index(previous_difficulty)
    if correct:
        if time_taken < 10:
            st.warning("Suspicious activity detected.")
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
            st.info("Time out. Moving to the next question.")
            return previous_difficulty, 0
    else:
        new_index = max(current_index - 1, 0)
        return difficulty_keys[new_index], 0

# Main Streamlit UI
st.title("Adaptive MCQ Quiz")

topic = st.text_input("Enter the topic for the questions:")
difficulty = st.selectbox("Select initial difficulty level:", list(difficulty_levels.keys()))
total_questions = 10
score = 0

if topic:
    for i in range(total_questions):
        st.write(f"### Question {i + 1} (Difficulty: {difficulty_levels[difficulty]})")
        
        # Generate and display the MCQ
        mcq = generate_mcq(topic, difficulty)
        if mcq:
            st.write(mcq)
            correct_answer = parse_correct_answer(mcq)
            if correct_answer:
                start_time = time.time()

                # Take user input for the answer
                user_answer = st.radio("Choose your answer:", ["A", "B", "C", "D"], key=i)
                submit = st.button("Submit Answer", key=f"submit_{i}")
                
                if submit:
                    end_time = time.time()
                    time_taken = end_time - start_time
                    correct = user_answer == correct_answer
                    st.write(f"Time taken: {time_taken:.2f} seconds")

                    # Display if correct or not and adjust difficulty
                    if correct:
                        st.success("Correct!")
                    else:
                        st.error(f"Incorrect. The correct answer was: {correct_answer}")
                    difficulty, earned_score = adjust_difficulty(difficulty, correct, time_taken)
                    score += earned_score
            else:
                st.warning("Skipping to the next question due to an error in parsing.")
        else:
            st.warning("Error generating the question. Skipping to the next question.")

    # Display final score and level
    st.write(f"\n### You scored {score} out of 20 marks.")
    if score >= 15:
        st.write("**Level: Advanced**")
    elif 8 <= score < 15:
        st.write("**Level: Intermediate**")
    else:
        st.write("**Level: Beginner**")
