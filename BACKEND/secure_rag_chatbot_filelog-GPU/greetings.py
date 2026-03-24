import re

# Greeting filter
def is_greeting(query: str) -> bool:
    greetings = {"hi", "hello", "hey", "hola", "namaste", "sup", "yo" , "listen"}
    return query.lower().strip() in greetings

# Name filter
def is_name_query(query: str) -> bool:
    query = query.strip()

    # If it's a single word
    if len(query.split()) == 1:
        # Likely a name: Starts with uppercase + rest lowercase (e.g., John, Raghavendra)
        if re.match(r"^[A-Z][a-z]+$", query):
            return True

        # Acronyms like AI, SQL, TPA (all caps) should pass
        if query.isupper():
            return False

        # Very short lowercase words (hi, ok, yo)
        if len(query) <= 3 and query.islower():
            return True

    return False
