import os
import json

# Try to import Gemini SDK
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Default interview questions based on common skills
DEFAULT_QUESTIONS = {
    "Python": [
        {
            "question": "What is the difference between a list and a tuple in Python?",
            "answer": "Lists are mutable, meaning their elements can be modified. Tuples are immutable. Lists use brackets [] and tuples use parentheses ()."
        },
        {
            "question": "Explain Python generators and the 'yield' keyword.",
            "answer": "Generators allow you to declare a function that behaves like an iterator. The 'yield' keyword suspends function execution and returns a value to the caller, saving memory because it doesn't hold the entire list in memory."
        }
    ],
    "SQL": [
        {
            "question": "Explain the difference between WHERE and HAVING clauses.",
            "answer": "WHERE filter rows before any groupings are made. HAVING filters groups created by GROUP BY."
        },
        {
            "question": "What are primary keys and foreign keys?",
            "answer": "A primary key uniquely identifies a row in a table. A foreign key links a column in one table to the primary key of another table to establish a database relationship."
        }
    ],
    "Machine Learning": [
        {
            "question": "What is overfitting and how do you prevent it?",
            "answer": "Overfitting happens when a model learns the training data noise rather than the signal. Prevent it with regularization (L1/L2), cross-validation, simplifying the model, or using early stopping."
        },
        {
            "question": "Explain the difference between supervised and unsupervised learning.",
            "answer": "Supervised learning uses labeled training data to predict output values. Unsupervised learning analyzes unlabeled data to find hidden patterns or groupings (clustering)."
        }
    ],
    "Deep Learning": [
        {
            "question": "What is the purpose of an activation function in neural networks?",
            "answer": "Activation functions introduce non-linearity into the network, allowing it to learn complex, non-linear relationships in the data."
        }
    ],
    "Docker": [
        {
            "question": "What is the difference between an Image and a Container in Docker?",
            "answer": "An image is a read-only blueprint that contains the operating system, code, and configurations. A container is a running instance of that image."
        }
    ],
    "Kubernetes": [
        {
            "question": "What is a Pod in Kubernetes?",
            "answer": "A Pod is the smallest deployable unit in Kubernetes, representing a single instance of a running process in your cluster, containing one or more containers."
        }
    ],
    "AWS": [
        {
            "question": "What is AWS IAM and why is it important?",
            "answer": "IAM (Identity and Access Management) allows you to securely manage access to AWS services and resources by creating users, groups, and setting fine-grained permissions."
        }
    ],
    "React": [
        {
            "question": "Explain the virtual DOM in React.",
            "answer": "React creates a lightweight in-memory representation of the DOM. When state changes, it updates the virtual DOM, compares it with the real DOM (diffing), and patches only the changed nodes for fast rendering."
        }
    ],
    "JavaScript": [
        {
            "question": "What is a closure in JavaScript?",
            "answer": "A closure is the combination of a function bundled together with references to its surrounding state (the lexical environment), allowing an inner function to access the scope of an outer function."
        }
    ],
    "Node.js": [
        {
            "question": "Explain the event loop in Node.js.",
            "answer": "The event loop allows Node.js to perform non-blocking I/O operations despite JavaScript being single-threaded, by offloading tasks to the system kernel and processing callbacks when ready."
        }
    ],
    "Git": [
        {
            "question": "Explain the difference between git merge and git rebase.",
            "answer": "Git merge combines changes from two branches by creating a new merge commit. Git rebase applies the commits of one branch on top of another, preserving a clean linear history."
        }
    ]
}

def generate_interview_prep(role: str, missing_skills: list) -> list:
    """Generates custom interview questions and answers based on the missing skills."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if HAS_GEMINI and gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            You are an expert technical interviewer for the '{role}' position.
            The applicant is missing or has weak knowledge in these areas: {missing_skills}.
            
            Generate 5 highly relevant technical interview questions and detailed answers designed to test their potential in these missing skills.
            Make sure to return ONLY a valid JSON array of objects, each containing "question" and "answer" keys.
            
            Format:
            [
                {{"question": "Q1 text", "answer": "A1 text"}},
                ...
            ]
            """
            
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text.strip())
            if isinstance(data, list):
                return data
        except Exception as e:
            print(f"Gemini interview prep generation failed: {e}")
            
    # Default fallback: Extract questions related to missing skills
    questions = []
    for skill in missing_skills:
        if skill in DEFAULT_QUESTIONS:
            questions.extend(DEFAULT_QUESTIONS[skill])
            
    # If not enough, fill in with generic Software Engineering questions
    if len(questions) < 3:
        questions.extend(DEFAULT_QUESTIONS["Git"])
        questions.extend(DEFAULT_QUESTIONS["Python"])
        
    return questions[:5]
