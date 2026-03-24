import logging

logging.basicConfig(
    filename="chatbot_interactions.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filemode="a"
)

def log_interaction(question, answer, image_paths=None):
    log_entry = f"QUESTION: {question} | ANSWER: {answer}"
    if image_paths:
        image_str = ", ".join(image_paths)
        log_entry += f" | IMAGES: {image_str}"
    logging.info(log_entry)
