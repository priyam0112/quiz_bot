from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)
        current_question_id = -1

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to the session.
    '''
    if current_question_id is None:
        return False, "No current question ID is provided"
    
    if not answer:
        return False, "Answer cannot be empty"

    try:
        session_key = f"answer_for_question_{current_question_id}"
        session[session_key] = answer
        session.modified = True 
    except Exception as e:
        return False, f"Failed to record answer: {str(e)}"

    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id is None or current_question_id >= len(PYTHON_QUESTION_LIST) - 1:
        next_question_id = 0
    else:
        next_question_id = current_question_id + 1

    if next_question_id < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_question_id]
        return next_question, next_question_id
    else:
        return None, None


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = 0

    for question_id, question_data in enumerate(PYTHON_QUESTION_LIST):
        answer_key = f"answer_for_question_{question_id}"

        if answer_key in session:
            user_answer = session[answer_key]
            correct_answer = question_data.get('correct_answer')

            if user_answer == correct_answer:
                correct_answers += 1

    if total_questions > 0:
        score_percentage = (correct_answers / total_questions) * 100
    else:
        score_percentage = 0.0

    if score_percentage >= 70:
        final_response = f"Congratulations! You scored {score_percentage:.2f}%. You passed the quiz."
    else:
        final_response = f"Unfortunately, you scored {score_percentage:.2f}%. You did not pass the quiz."
    return final_response
