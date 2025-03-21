# import ollama
# import json
# import os

# # Load JSON data
# with open('results/files_data.json', 'r') as file:
#     data = json.load(file)

# # Initialize the Ollama client
# client = ollama.Client()

# conversation_history = [

#     {"role": "user", "content": "What is the capital of France?"},

#     {"role": "assistant", "content": "Paris"}

# ]

# directory = "temp"
# if not os.path.exists(directory):
#     os.mkdir(directory)
# with open("temp/check.txt", 'w') as f:
#     pass



# def _clean_summary(summary_text: str) -> str:
#     """
#     Clean and standardize LLM-generated summaries by:
#     1. Removing redundant markdown formatting
#     2. Fixing common punctuation issues
#     3. Truncating to reasonable length
#     """
#     # Remove common LLM artifacts
#     clean_text = summary_text.replace("**", "").replace("__", "").strip()

#     # Fix sentence spacing
#     clean_text = ". ".join([s.strip() for s in clean_text.split(". ")])

#     # Truncate to 3 sentences max
#     sentences = clean_text.split(". ")[:3]
#     return ". ".join(sentences) + ("." if not clean_text.endswith(".") else "")

# def _format_technical_summary(raw_summary: str) -> str:
#     """
#     Structure technical summary into standardized sections
#     using markdown formatting with error checking
#     """
#     sections = [
#         "Architectural Overview",
#         "Implementation Details",
#         "Dependency Landscape",
#         "Domain-Specific Features"
#     ]

#     formatted = []
#     for section in sections:
#         # Find section content using case-insensitive search
#         start_idx = raw_summary.lower().find(section.lower())
#         if start_idx == -1:
#             continue

#         content = raw_summary[start_idx+len(section):]
#         end_idx = content.find("\n\n")
#         formatted.append(f"## {section}\n{content[:end_idx].strip()}")

#     return "\n\n".join(formatted) if formatted else raw_summary

# def _categorize_dependencies(raw_deps: str) -> dict:
#     """
#     Categorize dependencies from free-text LLM response into:
#     - Core
#     - Development
#     - Testing
#     - Runtime
#     """
#     categories = {
#         "Core": ["framework", "library", "engine", "platform"],
#         "Development": ["compiler", "transpiler", "builder", "bundler"],
#         "Testing": ["test", "mock", "stub", "assert"],
#         "Runtime": ["server", "environment", "container", "vm"]
#     }

#     deps = [d.strip("- ") for d in raw_deps.split("\n") if d.strip()]
#     categorized = {k: [] for k in categories}

#     for dep in deps:
#         found = False
#         for cat, keywords in categories.items():
#             if any(kw in dep.lower() for kw in keywords):
#                 categorized[cat].append(dep)
#                 found = True
#                 break
#         if not found:
#             categorized["Core"].append(dep)  # Default category

#     return {k: v for k, v in categorized.items() if v}


# def summarize_file(filename, content, project_context=""):
#     context_prompt = f"""
#     Project Overview: {project_context}
#     File Role: {_get_file_role(filename)}

#     Summarize this file's purpose considering:
#     - Its relationship to other project files
#     - Key functionality implemented
#     - Architectural role in system
#     - Notable data structures/algorithms

#     Keep summary under 40 words, technical and precise.

#     File: {filename}
#     Content:
#     {content}... [truncated]
#     """

#     response = client.generate(
#         model='llama3.2:latest',
#         prompt=context_prompt,
#         system="You are a senior software architect analyzing code components"
#     )
#     return _clean_summary(response['response'])

# def _get_file_role(filename):
#     """Determine file's architectural role from path"""
#     if 'test' in filename.lower():
#         return "Testing component"
#     if 'util' in filename.lower():
#         return "Utility functions"
#     if 'api' in filename.lower():
#         return "Service interface"
#     return "Core application logic"

# def summarize_the_entire_thing(content):
#     structured_prompt = f"""
#     Analyze this software project and produce a structured summary covering:

#     1. Architectural Overview:
#     - System type (monolithic, microservices, etc.)
#     - Key components and their interactions

#     2. Implementation Details:
#     - Primary programming paradigms used
#     - Notable design patterns

#     3. Dependency Landscape:
#     - Core frameworks and libraries
#     - External service integrations

#     4. Domain-Specific Features:
#     - Unique business logic components
#     - Specialized algorithms/data structures

#     Project Content:
#     {str(content)}... [truncated]
#     """

#     response = client.chat(
#         model='llama3.2:latest',
#         messages=[{"role": "user", "content": structured_prompt}]
#     )
#     return _format_technical_summary(response['message']['content'])


# def get_dependencies(content):
#     analysis_prompt = f"""
#     Identify dependencies by analyzing:
#     1. Direct imports/requires
#     2. Configuration files (package.json, requirements.txt)
#     3. Build tool configurations
#     4. Implicit framework requirements

#     Categorize as:
#     - Core dependencies
#     - Development tools
#     - Testing frameworks
#     - Runtime requirements

#     Project Content:
#     {content}
#     """

#     response = client.chat(
#         model='llama3.2:latest',
#         messages=[{
#             "role": "system",
#             "content": "You are a dependency analysis expert with 10 years experience in software composition analysis"
#         }, {
#             "role": "user",
#             "content": analysis_prompt
#         }]
#     )
#     return _categorize_dependencies(response['message']['content'])


# def create_the_summaries(data):
#     file_summaries = {}
#     for filename, content in data.items():
#         file_summaries[filename] = summarize_file(filename, content)

#     return file_summaries


# if __name__ == "__main__":
#     file_summaries = create_the_summaries(data)
#     # Save summaries to JSON file
#     with open('results/final_summaries.json', 'w') as f:
#         json.dump(file_summaries, f)

#     with open('results/full_project.txt', 'w') as f:
#         f.write(summarize_the_entire_thing(data))

#     with open('results/dependencies.json', 'w') as f:
#         json.dump((get_dependencies(data)), f)
#     # Print the summaries
#     for filename, summary in file_summaries.items():
#         print(f"File: {filename}\nSummary: {summary}\n")


import google.generativeai as genai
import json
import os

# Load JSON data
with open('results/files_data.json', 'r') as file:
    data = json.load(file)

# Initialize Gemini client
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))  # Set via environment variable
client = genai.GenerativeModel('gemini-2.0-flash')  # Using latest Flash model [2][5]

conversation_history = [
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "Paris"}
]

# ... (directory setup remains unchanged) ...
directory = "temp"
if not os.path.exists(directory):
    os.mkdir(directory)
with open("temp/check.txt", 'w') as f:
    pass



def _clean_summary(summary_text: str) -> str:
    """
    Clean and standardize LLM-generated summaries by:
    1. Removing redundant markdown formatting
    2. Fixing common punctuation issues
    3. Truncating to reasonable length
    """
    # Remove common LLM artifacts
    clean_text = summary_text.replace("**", "").replace("__", "").strip()

    # Fix sentence spacing
    clean_text = ". ".join([s.strip() for s in clean_text.split(". ")])

    # Truncate to 3 sentences max
    sentences = clean_text.split(". ")[:3]
    return ". ".join(sentences) + ("." if not clean_text.endswith(".") else "")

def _format_technical_summary(raw_summary: str) -> str:
    """
    Structure technical summary into standardized sections
    using markdown formatting with error checking
    """
    sections = [
        "Architectural Overview",
        "Implementation Details",
        "Dependency Landscape",
        "Domain-Specific Features"
    ]

    formatted = []
    for section in sections:
        # Find section content using case-insensitive search
        start_idx = raw_summary.lower().find(section.lower())
        if start_idx == -1:
            continue

        content = raw_summary[start_idx+len(section):]
        end_idx = content.find("\n\n")
        formatted.append(f"## {section}\n{content[:end_idx].strip()}")

    return "\n\n".join(formatted) if formatted else raw_summary

def _categorize_dependencies(raw_deps: str) -> dict:
    """
    Categorize dependencies from free-text LLM response into:
    - Core
    - Development
    - Testing
    - Runtime
    """
    categories = {
        "Core": ["framework", "library", "engine", "platform"],
        "Development": ["compiler", "transpiler", "builder", "bundler"],
        "Testing": ["test", "mock", "stub", "assert"],
        "Runtime": ["server", "environment", "container", "vm"]
    }

    deps = [d.strip("- ") for d in raw_deps.split("\n") if d.strip()]
    categorized = {k: [] for k in categories}

    for dep in deps:
        found = False
        for cat, keywords in categories.items():
            if any(kw in dep.lower() for kw in keywords):
                categorized[cat].append(dep)
                found = True
                break
        if not found:
            categorized["Core"].append(dep)  # Default category

    return {k: v for k, v in categorized.items() if v}

def _get_file_role(filename):
    """Determine file's architectural role from path"""
    if 'test' in filename.lower():
        return "Testing component"
    if 'util' in filename.lower():
        return "Utility functions"
    if 'api' in filename.lower():
        return "Service interface"
    return "Core application logic"

def summarize_file(filename, content, project_context=""):
    context_prompt = f"""PROJECT OVERVIEW: {project_context}
    FILE ROLE: {_get_file_role(filename)}

    Analyze this source file considering:
    - Key functionality and architectural role
    - Data structures/algorithms used
    - Dependencies and relationships

    Provide a concise technical summary under 40 words."""

    response = client.generate_content(
        contents=[context_prompt, f"File: {filename}\nContent:\n{content[:10000]}..."],
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 200
        },
        safety_settings={
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE"
        }
    )
    return _clean_summary(response.text)  # Updated response structure [2][5]

def summarize_the_entire_thing(content):
    # structured_prompt = """Analyze this software project and produce a structured technical report covering:
    # 1. Architectural Patterns (monolithic/microservices)
    # 2. Implementation Strategies (paradigms, design patterns)
    # 3. Dependency Graph (core vs external)
    # 4. Domain-Specific Innovations"""

    # response = client.generate_content(
    #     contents=[structured_prompt, str(content)[:100000]],
    #     generation_config={
    #         "temperature": 0.1,
    #         "max_output_tokens": 1000
    #     },
    #     system_instruction="You are a senior software architect with 15+ years experience in system analysis"
    # )
    # return _format_technical_summary(response.text)
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',  # Verified model name [1][6]
        system_instruction="You are a senior software architect with 15+ years experiencein system analysis"
    )

    structured_prompt = """Analyze this software project..."""  # Your existing prompt

    response = model.generate_content(
        contents=[structured_prompt, str(content)[:100000]],
        generation_config={
            "temperature": 0.1,
            "max_output_tokens": 1000
        }
    )
    return _format_technical_summary(response.text)


def get_dependencies(content):
    analysis_prompt = """Identify and categorize dependencies from:
    1. Direct imports/requires
    2. Config files (package.json, requirements.txt)
    3. Build tool configurations
    4. Implicit framework requirements

    Output categories: Core, Development, Testing, Runtime"""

    response = client.generate_content(
        contents=[analysis_prompt, str(content)],
        generation_config={
            "temperature": 0,
            "response_mime_type": "application/json"  # Leverage Gemini's structured output [2][6]
        }
    )

    try:
        return json.loads(response.text)  # Direct JSON parsing with Gemini's improved formatting [6]
    except json.JSONDecodeError:
        return _categorize_dependencies(response.text)  # Fallback to original method

# ... (remaining helper functions unchanged except client references) ...
def create_the_summaries(data):
    file_summaries = {}
    for filename, content in data.items():
        file_summaries[filename] = summarize_file(filename, content)

    return file_summaries


if __name__ == "__main__":
    file_summaries = create_the_summaries(data)
    # Save summaries to JSON file
    with open('results/final_summaries.json', 'w') as f:
        json.dump(file_summaries, f)

    with open('results/full_project.txt', 'w') as f:
        f.write(summarize_the_entire_thing(data))

    with open('results/dependencies.json', 'w') as f:
        json.dump((get_dependencies(data)), f)
    # Print the summaries
    for filename, summary in file_summaries.items():
        print(f"File: {filename}\nSummary: {summary}\n")
