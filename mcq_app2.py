import streamlit as st
import subprocess
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

# Initialize session state variables
if "score" not in st.session_state:
    st.session_state.score = 0
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "k1"
if "current_question" not in st.session_state:
    st.session_state.current_question = 1
if "start_time" not in st.session_state:
    st.session_state.start_time = None

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

if topic:
    st.write(f"### Question {st.session_state.current_question} (Difficulty: {difficulty_levels[st.session_state.difficulty]})")
    
    # Generate and display the MCQ
    mcq = generate_mcq(topic, st.session_state.difficulty)
    if mcq:
        st.write(mcq)
        correct_answer = parse_correct_answer(mcq)
        if correct_answer:
            if st.session_state.start_time is None:
                st.session_state.start_time = time.time()

            # Take user input for the answer
            user_answer = st.radio("Choose your answer:", ["A", "B", "C", "D"], key=st.session_state.current_question)
            
            if st.button("Submit Answer"):
                end_time = time.time()
                time_taken = end_time - st.session_state.start_time
                st.session_state.start_time = None  # Reset start time for the next question
                correct = user_answer == correct_answer
                st.write(f"Time taken: {time_taken:.2f} seconds")

                # Display if correct or not and adjust difficulty
                if correct:
                    st.success("Correct!")
                else:
                    st.error(f"Incorrect. The correct answer was: {correct_answer}")
                
                # Adjust difficulty and update score
                st.session_state.difficulty, earned_score = adjust_difficulty(st.session_state.difficulty, correct, time_taken)
                st.session_state.score += earned_score
                
                # Move to the next question
                st.session_state.current_question += 1

    # Display final score and level after the last question
    if st.session_state.current_question > 10:
        st.write(f"\n### You scored {st.session_state.score} out of 20 marks.")
        if st.session_state.score >= 15:
            st.write("**Level: Advanced**")
        elif 8 <= st.session_state.score < 15:
            st.write("**Level: Intermediate**")
        else:
            st.write("**Level: Beginner**")
