# Final Exam Answer Key

## Question 1: Bash Commands (15 points total)

### 1a. (5 points) Create warnings.log file
```bash
cat 2025.03.15_app.log | grep "WARNING" > warnings.log
```
**Alternative acceptable answers:**
- `grep "WARNING" 2025.03.15_app.log > warnings.log`
- Any command that extracts lines containing "WARNING" (case-sensitive) and writes to warnings.log

### 1b. (5 points) Count ERROR042 lines
```bash
cat 2025.03.15_app.log | grep "ERROR042" | wc -l
```
**Alternative acceptable answers:**
- `grep -c "ERROR042" 2025.03.15_app.log`
- `grep ERROR042 2025.03.15_app.log | wc -l`

### 1c. (5 points) Count ERROR lines without WARNING
```bash
cat 2025.03.15_app.log | grep "ERROR" | grep -v "WARNING" | wc -l
```
**Alternative acceptable answers:**
- `grep "ERROR" 2025.03.15_app.log | grep -v "WARNING" | wc -l`
- Any command that finds lines with ERROR but not WARNING and counts them

## Question 2: Docker Path (5 points)

**Answer:** `/project/files/files/processed/final.pdf`

**Explanation:** When running `make interactive`, the volume mount is `-v $(shell pwd):/project/files`, which mounts the current directory to `/project/files` inside the container. The file `final.pdf` is at `files/processed/final.pdf` relative to the root, so inside the container it's at `/project/files/files/processed/final.pdf`.

## Question 3: Fill in the Blank (2 points)

**Answer:** `pyproject.toml`

**Explanation:** `requirements.txt` is the dependency file format used by `pip`, and `pyproject.toml` is the dependency file format used by `uv`.

## Question 4: List PDF Files (5 points)

```bash
ls ../files/archive/*.pdf
```
**Alternative acceptable answers:**
- `ls files/archive/*.pdf` (if they interpret relative from /log_files correctly)
- Any command that lists PDF files in the files/archive directory using a relative path

## Question 5: Flask Route Responses (6 points total)

### 5a. (3 points) GET /api/students/mike
**Body:** `{"mike": "mathematics"}`  
**Status Code:** `200`

### 5b. (3 points) GET /api/students/david
**Body:** `{"error": "Student not found"}`  
**Status Code:** `404`

## Question 6: DRY Acronym (1 point)

**Answer:** Don't Repeat Yourself

## Question 7: Complete Flask Route (5 points)

```python
if student_data is not None:
    return jsonify({"name": student_data[0], "year": student_data[1]}), 200
else:
    return jsonify({"error": "Student not found"}), 404
```

**Note:** The `registrar_api_call` function returns a tuple `(name, year, gpa)` if the student exists, or `None` if the student doesn't exist. Students should only write the code that goes in the "# CODE GOES HERE" section.

## Question 8: Unit Test (5 points)

```python
def test_calculate_score():
    assert calculate_score(10, 2, 5) == 25
```

**Alternative acceptable answers:**
- Any valid test using `assert` that tests the function
- Test name must be `test_calculate_score`
- Any test case that verifies the function works

## Question 9: LLM vs AI Agent (2 points)

**Answer:** An LLM (Large Language Model) is a neural network trained on text data that can generate text based on patterns it learned. An AI Agent is a system that uses LLMs (or other AI models) along with tools and decision-making capabilities to perform tasks, make decisions, and interact with external systems. Agents can take actions beyond just generating text, such as calling APIs, executing code, or manipulating data.

**Key points:**
- LLM = text generation model
- Agent = LLM + tools + decision-making + action-taking

## Question 10: Docker vs Docker Compose (2 points)

**Answer:** Docker is used to build and run individual containers, while Docker Compose is used to orchestrate multiple containers together, defining their relationships, networking, and dependencies in a single configuration file.

**Alternative acceptable answers:**
- Docker = single containers; Docker Compose = multiple containers/services
- Docker Compose manages multi-container applications

## Question 11: Piecewise Function (5 points)

```python
def piecewise(positive_func, negative_func, cutoff):
    def result_func(value):
        if value >= cutoff:
            return positive_func(value)
        else:
            return negative_func(value)
    return result_func
```

**Key points:**
- Function takes three arguments: `positive_func`, `negative_func`, `cutoff`
- Returns a function that takes `value`
- Uses `cutoff` (not `breakpoint` - the question uses `cutoff` consistently)
- Returns `positive_func(value)` if `value >= cutoff`, else `negative_func(value)`

## Question 12: Docker ENV Variable (5 points)

**Answer:** The first approach (`ENV API_KEY=abc123` in Dockerfile) sets the environment variable at **build-time** when the Docker image is created. The second approach (`-e API_KEY=abc123` in `docker run`) sets the environment variable at **runtime** when the container is started.

**Practical implications:**
- Build-time: The value is baked into the image, making it less flexible and potentially a security risk if sensitive data is hardcoded
- Runtime: The value can be changed each time you run the container, making it more flexible and allowing different values for different environments without rebuilding the image

## Question 13: Autodocs (2 points)

**Answer:** Docstrings (or function docstrings)

**Explanation:** Autodocs systems like MkDocs extract docstrings from Python functions to generate documentation.

## Question 14: Unit Test vs Integration Test (2 points)

**Answer:** A unit test tests an individual function or component in isolation, typically with mocked dependencies. An integration test tests how multiple components work together, often using real dependencies like databases or APIs.

## Question 15: MCP Acronym (2 points)

**Answer:** Model Context Protocol

## Question 16: MCP Use (2 points)

**Answer:** MCP (Model Context Protocol) is used to provide AI agents and LLMs with access to tools and external resources, allowing them to interact with systems, databases, APIs, and other services beyond their training data. It enables agents to perform actions like querying databases, calling APIs, or executing code, rather than just generating text responses.

**Note:** Answer should be 2-3 sentences as specified in the question.

## Question 17: apply_functions (5 points)

```python
def apply_functions(func_list, value):
    results = []
    for func in func_list:
        results.append(func(value))
    return results
```

**Alternative acceptable answers:**
- List comprehension: `return [func(value) for func in func_list]`
- Any implementation that applies each function in order to the value and returns a list

## Question 18: apply_to_all (5 points)

```python
def apply_to_all(func_list, value_list):
    results = []
    for value in value_list:
        value_results = []
        for func in func_list:
            value_results.append(func(value))
        results.append(value_results)
    return results
```

**Alternative acceptable answers:**
- Nested list comprehension: `return [[func(val) for func in func_list] for val in value_list]`
- Any implementation that returns a list of lists, where each inner list contains results of applying all functions to one value

## Question 19: Flask Grades Route (5 points)

```python
@app.route('/api/students/grades', methods=['POST'])
def create_grades():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data"}), 400
    
    student_id = data.get('student_id')
    if not student_id or not validate_student_id(student_id):
        return jsonify({"error": "Invalid student_id"}), 400
    
    courses = []
    grades = []
    for key, value in data.items():
        if key != 'student_id':
            courses.append(key)
            grades.append(value)
    
    return jsonify({"student_id": student_id, "courses": courses, "grades": grades}), 200
```

**Key points:**
- POST route at `/api/students/grades`
- Validates JSON data exists
- Validates `student_id` using `validate_student_id()` helper
- Extracts all keys except `student_id` as courses
- Extracts corresponding values as grades
- Returns proper JSON structure with status 200

**Alternative acceptable answers:**
- Variations in error messages are acceptable
- Different ways to extract courses/grades (e.g., using list comprehensions)

## Question 20: logger_helper (5 points)

```python
def logger_helper(func):
    def wrapper():
        print(f"Function {func.__name__} started")
        result = func()
        print("Function Complete")
        return result
    return wrapper
```

**Key points:**
- Takes a function `func` as parameter
- Returns a function (wrapper)
- Prints "Function {function_name} started" before calling func
- Calls func() (which takes zero arguments)
- Prints "Function Complete" after func completes
- Returns the result of func()
- Uses `func.__name__` to get the function name

**Alternative acceptable answers:**
- Variations in print statements are acceptable (e.g., "Function XXX started" where XXX is the function name)
- As long as it prints before and after, and calls the function

---

## Total Points: 89 points

**Point Breakdown:**
- Q1: 15 points (3×5)
- Q2: 5 points
- Q3: 2 points
- Q4: 5 points
- Q5: 6 points (2×3)
- Q6: 1 point
- Q7: 5 points
- Q8: 5 points
- Q9: 2 points
- Q10: 2 points
- Q11: 5 points
- Q12: 5 points
- Q13: 2 points
- Q14: 2 points
- Q15: 2 points
- Q16: 2 points
- Q17: 5 points
- Q18: 5 points
- Q19: 5 points
- Q20: 5 points

**Total: 89 points**

Note: Some questions may have multiple acceptable answers. Partial credit should be given for correct concepts even if syntax is slightly off.
