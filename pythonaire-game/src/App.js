import React, { useState, useEffect, useCallback, useRef } from 'react';

// Main App component
const App = () => {
    // Game configuration: questions, options, and answers
    // Questions categorized by difficulty: 1 = Easy, 2 = Medium, 3 = Hard
    const allAvailableQuestions = [
        // --- Easy Questions (Level 1) ---
        {
            id: 1,
            question: "What is the keyword used to define a function in Python?",
            options: ["func", "define", "def", "function"],
            answer: "def",
            level: 1,
            concept: "function definition"
        },
        {
            id: 2,
            question: "Which of the following is used to store multiple items in a single variable, ordered and changeable?",
            options: ["Tuple", "Set", "Dictionary", "List"],
            answer: "List",
            level: 1,
            concept: "list data structure"
        },
        {
            id: 3,
            question: "What is the correct way to assign the value 'hello' to a variable named 'greeting'?",
            options: ["greeting == 'hello'", "set greeting = 'hello'", "greeting = 'hello'", "greeting: 'hello'"],
            answer: "greeting = 'hello'",
            level: 1,
            concept: "variable assignment"
        },
        {
            id: 4,
            question: "How do you print output to the console in Python?",
            options: ["console.log()", "display()", "print()", "write()"],
            answer: "print()",
            level: 1,
            concept: "print function"
        },
        {
            id: 5,
            question: "What symbol indicates a single-line comment in Python?",
            options: ["//", "/*", "#", "--"],
            answer: "#",
            level: 1,
            concept: "comments"
        },
        {
            id: 6,
            question: "Which data type is used for whole numbers (e.g., 5, -10, 0) in Python?",
            options: ["float", "string", "boolean", "int"],
            answer: "int",
            level: 1,
            concept: "integer data type"
        },
        {
            id: 7,
            question: "What does `str()` do in Python?",
            options: ["Converts to an integer", "Converts to a string", "Converts to a list", "Converts to a boolean"],
            answer: "Converts to a string",
            level: 1,
            concept: "type conversion (str())"
        },
        {
            id: 8,
            question: "What is the result of the expression `7 + 3`?",
            options: ["73", "10", "Error", "7+3"],
            answer: "10",
            level: 1,
            concept: "arithmetic operators"
        },
        {
            id: 9,
            question: "Which operator is used for addition in Python?",
            options: ["*", "/", "+", "-"],
            answer: "+",
            level: 1,
            concept: "addition operator"
        },
        {
            id: 10,
            question: "What is the correct syntax for an `if` statement in Python?",
            options: ["if (condition) { ... }", "if condition: ...", "if condition then ...", "if condition do ..."],
            answer: "if condition: ...",
            level: 1,
            concept: "if statement syntax"
        },
        {
            id: 11,
            question: "Which of these is a valid Python variable name?",
            options: ["2myVar", "my-Var", "my_Var", "my Var"],
            answer: "my_Var",
            level: 1,
            concept: "variable naming rules"
        },
        {
            id: 12,
            question: "What is the purpose of the `input()` function in Python?",
            options: ["To display output", "To convert data types", "To get user input", "To define a loop"],
            answer: "To get user input",
            level: 1,
            concept: "input function"
        },
        {
            id: 13,
            question: "How do you create an empty dictionary named 'my_dict'?",
            options: ["my_dict = []", "my_dict = ()", "my_dict = {}", "my_dict = new Dict()"],
            answer: "my_dict = {}",
            level: 1,
            concept: "dictionary creation"
        },
        {
            id: 14,
            question: "What will `5 * 2` result in?",
            options: ["52", "10", "7", "Error"],
            answer: "10",
            level: 1,
            concept: "multiplication operator"
        },
        {
            id: 15,
            question: "Which keyword is used to create a loop that executes as long as a condition is true?",
            options: ["for", "do-while", "loop", "while"],
            answer: "while",
            level: 1,
            concept: "while loop"
        },
        {
            id: 31,
            question: "What is the data type of the result of `10 / 2` in Python?",
            options: ["int", "float", "string", "boolean"],
            answer: "float",
            level: 1,
            concept: "float division"
        },
        {
            id: 32,
            question: "Which operator checks for equality (same value and type)?",
            options: ["=", "==", "!=", "=>"],
            answer: "==",
            level: 1,
            concept: "equality operator (==)"
        },
        {
            id: 33,
            question: "How do you access the first element of a list called `my_list`?",
            options: ["my_list(0)", "my_list[0]", "my_list.first()", "my_list.get(0)"],
            answer: "my_list[0]",
            level: 1,
            concept: "list indexing"
        },
        {
            id: 34,
            question: "What is a 'string' in Python?",
            options: ["A whole number", "A sequence of characters", "A true/false value", "A collection of items"],
            answer: "A sequence of characters",
            level: 1,
            concept: "string data type"
        },
        {
            id: 35,
            question: "What is the result of `len('Python')`?",
            options: ["5", "6", "7", "Error"],
            answer: "6",
            level: 1,
            concept: "len() function"
        },

        // --- Medium Questions (Level 2) ---
        {
            id: 16,
            question: "What will be the value of 'a' after this code: `a = 5; if a > 3: a = a + 2 else: a = a - 1`?",
            options: ["4", "5", "7", "6"],
            answer: "7",
            level: 2,
            concept: "conditional statements (if/else)"
        },
        {
            id: 17,
            question: "What is the correct way to import the 'math' module?",
            options: ["include math", "import math", "use math", "require math"],
            answer: "import math",
            level: 2,
            concept: "importing modules"
        },
        {
            id: 18,
            question: "Which method is used to add an item to the end of a list?",
            options: ["insert()", "add()", "append()", "put()"],
            answer: "append()",
            level: 2,
            concept: "list append method"
        },
        {
            id: 19,
            question: "What is the purpose of the 'else' keyword in a conditional statement?",
            options: ["To execute code if the 'if' condition is true", "To execute code if the 'if' condition is false", "To loop through elements", "To define a function"],
            answer: "To execute code if the 'if' condition is false",
            level: 2,
            concept: "else keyword"
        },
        {
            id: 24,
            question: "What is the correct syntax for an 'if-elif-else' block?",
            options: [
                "if condition: ... else if condition: ... else: ...",
                "if condition: ... elif condition: ... else: ...",
                "if condition ... else if ... else ...",
                "if (condition) { ... } else if (condition) { ... } else { ... }"
            ],
            answer: "if condition: ... elif condition: ... else: ...",
            level: 2,
            concept: "if-elif-else syntax"
        },
        {
            id: 25,
            question: "Which of these is used to repeat a block of code a specific number of times?",
            options: ["if statement", "function", "while loop", "for loop"],
            answer: "for loop",
            level: 2,
            concept: "for loop"
        },
        {
            id: 26,
            question: "What is the output of `type([])`?",
            options: ["<class 'tuple'>", "<class 'list'>", "<class 'dict'>", "<class 'set'>"],
            answer: "<class 'list'>",
            level: 2,
            concept: "type() function"
        },
        {
            id: 36,
            question: "What is the result of `'Py' * 3`?",
            options: ["PyPyPy", "Py3", "Error", "3Py"],
            answer: "PyPyPy",
            level: 2,
            concept: "string multiplication"
        },
        {
            id: 37,
            question: "Which comparison operator means 'not equal to'?",
            options: ["==", "=", "!=", ">="],
            answer: "!=",
            level: 2,
            concept: "comparison operators"
        },
        {
            id: 38,
            question: "What is the correct way to remove the last item from a list called `my_list`?",
            options: ["my_list.removeLast()", "my_list.delete()", "my_list.pop()", "my_list.remove(-1)"],
            answer: "my_list.pop()",
            level: 2,
            concept: "list pop method"
        },
        {
            id: 39,
            question: "How do you get the value associated with the key 'name' from a dictionary `person = {'name': 'Alice'}`?",
            options: ["person.name", "person['name']", "person->name", "person.get('name', None)"],
            answer: "person['name']",
            level: 2,
            concept: "dictionary access"
        },
        {
            id: 40,
            question: "What does `range(3)` produce in a `for` loop?",
            options: ["0, 1, 2", "1, 2, 3", "0, 1, 2, 3", "Error"],
            answer: "0, 1, 2",
            level: 2,
            concept: "range() function"
        },
        {
            id: 41,
            question: "Which keyword is used to conditionally execute a block of code if the preceding `if` or `elif` conditions were false?",
            options: ["try", "except", "finally", "else"],
            answer: "else",
            level: 2,
            concept: "else keyword in conditionals"
        },
        {
            id: 42,
            question: "What is the purpose of the `continue` statement in a loop?",
            options: ["To exit the loop", "To skip the rest of the current iteration and go to the next", "To restart the loop", "To pause the loop"],
            answer: "To skip the rest of the current iteration and go to the next",
            level: 2,
            concept: "continue statement"
        },
        {
            id: 43,
            question: "How do you create a tuple with a single item 'apple'?",
            options: ["('apple')", "('apple',)", "['apple']", "new Tuple('apple')"],
            answer: "('apple',)",
            level: 2,
            concept: "tuple creation"
        },

        // --- Hard Questions (Level 3) ---
        {
            id: 27,
            question: "What is the output of: `x = [1, 2, 3]; x.extend([4, 5]); print(x)`?",
            options: ["[1, 2, 3, 4, 5]", "[1, 2, 3], [4, 5]", "[[1, 2, 3], 4, 5]", "Error"],
            answer: "[1, 2, 3, 4, 5]",
            level: 3,
            concept: "list extend method"
        },
        {
            id: 28,
            question: "What is the output of: `a = 10; b = 3; print(a // b)`?",
            options: ["3.33", "3", "4", "Error"],
            answer: "3",
            level: 3,
            concept: "floor division"
        },
        {
            id: 29,
            question: "Which statement is used to handle exceptions in Python?",
            options: ["try/catch", "throw/catch", "try/except", "error/handle"],
            answer: "try/except",
            level: 3,
            concept: "exception handling (try/except)"
        },
        {
            id: 30,
            question: "What is the result of `['a', 'b', 'c'][1]`?",
            options: ["'a'", "'b'", "'c'", "Error"],
            answer: "'b'",
            level: 3,
            concept: "list indexing"
        },
        {
            id: 44,
            question: "Considering `x = 10` and `y = 20`, what is the output of `print(x > 5 and y < 15)`?",
            options: ["True", "False", "Error", "None"],
            answer: "False",
            level: 3,
            concept: "boolean logic (and operator)"
        },
        {
            id: 45,
            question: "What does `global` keyword do in Python?",
            options: ["Defines a constant variable", "Allows a variable inside a function to refer to a global variable", "Makes a variable accessible only within its function", "Creates a new module"],
            answer: "Allows a variable inside a function to refer to a global variable",
            level: 3,
            concept: "global keyword"
        },
        {
            id: 46,
            question: "Which built-in function returns a new sorted list from the items in an iterable?",
            options: ["list.sort()", "sort()", "sorted()", "order()"],
            answer: "sorted()",
            level: 3,
            concept: "sorted() function"
        },
        {
            id: 47,
            question: "What is a 'lambda' function in Python?",
            options: ["A function that creates lists", "An anonymous single-expression function", "A function for mathematical operations", "A function that runs in the background"],
            answer: "An anonymous single-expression function",
            level: 3,
            concept: "lambda functions"
        },
        {
            id: 48,
            question: "What is the output of `set([1, 2, 2, 3, 1])`?",
            options: ["[1, 2, 3, 1]", "{1, 2, 3, 1}", "{1, 2, 3}", "[1, 2, 3]"],
            answer: "{1, 2, 3}",
            level: 3,
            concept: "set data structure"
        },
        {
            id: 49,
            question: "What is the purpose of the `__init__` method in a Python class?",
            options: ["To delete an object", "To define class methods", "To initialize object attributes", "To import modules"],
            answer: "To initialize object attributes",
            level: 3,
            concept: "class constructor (__init__)"
        },
        {
            id: 50,
            question: "Which error occurs when you try to access a key that doesn't exist in a dictionary?",
            options: ["TypeError", "ValueError", "KeyError", "AttributeError"],
            answer: "KeyError",
            level: 3,
            concept: "KeyError"
        },
        {
            id: 51,
            question: "What is the correct way to open a file named 'data.txt' for reading?",
            options: ["open('data.txt', 'w')", "open('data.txt', 'r')", "open_file('data.txt')", "read_file('data.txt')"],
            answer: "open('data.txt', 'r')",
            level: 3,
            concept: "file handling (open())"
        },
        {
            id: 52,
            question: "In Python, what is a 'decorator'?",
            options: ["A design pattern for creating GUIs", "A function that takes another function as argument, and extends its behavior without explicitly modifying it", "A type of loop for iterating over objects", "A special kind of variable"],
            answer: "A function that takes another function as argument, and extends its behavior without explicitly modifying it",
            level: 3,
            concept: "decorators"
        },
        {
            id: 53,
            question: "What is the output of `[i*2 for i in range(3)]`?",
            options: ["[0, 1, 2]", "[0, 2, 4]", "[2, 4, 6]", "Error"],
            answer: "[0, 2, 4]",
            level: 3,
            concept: "list comprehensions"
        },
        {
            id: 54,
            question: "What is the output of `float('3.14')`?",
            options: ["3", "3.14", "Error", "314"],
            answer: "3.14",
            level: 3,
            concept: "type conversion (float())"
        }
    ];

    // Prize money for each question, reflecting the exact incremental values from the image
    const prizeMoney = [
        100,      // Question 1: $100 (Total: $100)
        100,      // Question 2: $200 (Total: $200 from image, so add $100)
        100,      // Question 3: $300 (Total: $300 from image, so add $100)
        200,      // Question 4: $500 (Total: $500 from image, so add $200)
        500,      // Question 5: $1,000 (Total: $1,000 from image, so add $500)
        1000,     // Question 6: $2,000 (Total: $2,000 from image, so add $1,000)
        2000,     // Question 7: $4,000 (Total: $4,000 from image, so add $2,000)
        4000,     // Question 8: $8,000 (Total: $8,000 from image, so add $4,000)
        8000,     // Question 9: $16,000 (Total: $16,000 from image, so add $8,000)
        16000,    // Question 10: $32,000 (Total: $32,000 from image, so add $16,000)
        32000,    // Question 11: $64,000 (Total: $64,000 from image, so add $32,000)
        61000,    // Question 12: $125,000 (Total: $125,000 from image, so add $61,000)
        125000,   // Question 13: $250,000 (Total: $250,000 from image, so add $125,000)
        250000,   // Question 14: $500,000 (Total: $500,000 from image, so add $250,000)
        500000    // Question 15: $1,000,000 (Total: $1,000,000 from image, so add $500,000)
    ];

    // Game state variables
    const [gameStarted, setGameStarted] = useState(false); // Controls if game or start screen is shown
    const [useTimer, setUseTimer] = useState(true); // User's choice for timer, default to true (Timer On)
    const [selectedDifficulty, setSelectedDifficulty] = useState(1); // Default to Easy (Level 1)
    const [questions, setQuestions] = useState([]); // Questions for the current game session
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [score, setScore] = useState(0);
    const [gameOver, setGameOver] = useState(false);
    const [correctAnswerGiven, setCorrectAnswerGiven] = useState(false); // Tracks if the selected answer is correct
    const [showIncorrectMessage, setShowIncorrectMessage] = useState(false); // Controls display of incorrect message
    const [selectedOption, setSelectedOption] = useState(null); // The option the user clicked
    const [answeredCorrectlyCount, setAnsweredCorrectlyCount] = useState(0); // Count of questions answered correctly
    const [timeLeft, setTimeLeft] = useState(60); // State for timer (in seconds)
    const timerRef = useRef(null); // Ref to hold the setInterval ID
    const [hasAnsweredCurrentQuestion, setHasAnsweredCurrentQuestion] = useState(false); // New state for manual progression

    // LLM-related states
    const [aiLifelineUsed, setAiLifelineUsed] = useState(false);
    const [showExplanationModal, setShowExplanationModal] = useState(false);
    const [explanationText, setExplanationText] = useState("");
    const [loadingAIResponse, setLoadingAIResponse] = useState(false);
    const [eliminatedOptions, setEliminatedOptions] = useState([]); // Store options eliminated by AI

    // Helper function to shuffle an array (Fisher-Yates shuffle)
    const shuffleArray = (array) => {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    };

    // Function to set up the questions for a new game based on selected difficulty
    const setupGameQuestions = useCallback((difficulty) => {
        const filteredQuestions = allAvailableQuestions.filter(q => q.level === difficulty);
        const shuffledAndSelectedQuestions = shuffleArray(filteredQuestions).slice(0, 15); // Select 15 random questions of the chosen difficulty
        setQuestions(shuffledAndSelectedQuestions);

        // Reset game states
        setCurrentQuestionIndex(0);
        setScore(0);
        setGameOver(false);
        setCorrectAnswerGiven(false);
        setShowIncorrectMessage(false);
        setSelectedOption(null);
        setAnsweredCorrectlyCount(0);
        setTimeLeft(60); // Reset timer state
        setAiLifelineUsed(false); // Reset lifeline usage
        setEliminatedOptions([]); // Clear eliminated options
        setHasAnsweredCurrentQuestion(false); // Reset for new game
        if (timerRef.current) {
            clearInterval(timerRef.current); // Clear any old timer
        }
    }, [allAvailableQuestions]);


    // Effect to manage the timer for each question
    useEffect(() => {
        // Only run timer logic if the game has started, user opted for timer, not game over, questions are loaded, and no option is selected yet
        if (gameStarted && useTimer && !gameOver && questions.length > 0 && selectedOption === null) {
            // Clear any existing timer before starting a new one
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }

            // Reset time for the current question
            setTimeLeft(60);

            // Start new timer
            timerRef.current = setInterval(() => {
                setTimeLeft(prevTime => {
                    if (prevTime <= 1) {
                        clearInterval(timerRef.current);
                        setGameOver(true); // End game if time runs out
                        return 0;
                    }
                    return prevTime - 1;
                });
            }, 1000); // Update every second
        } else {
            // If conditions are not met for timer (e.g., game not started, timer off, game over, option selected), clear the timer
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        }

        // Cleanup function for useEffect: clear timer when component unmounts or dependencies change
        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        };
    }, [currentQuestionIndex, gameOver, questions.length, selectedOption, gameStarted, useTimer]); // Dependencies to re-run this effect

    // Function to handle option clicks
    const handleOptionClick = useCallback((option) => {
        if (gameOver || selectedOption !== null || hasAnsweredCurrentQuestion) {
            // Prevent multiple selections or selections after game over or if already answered
            return;
        }

        // Clear the timer immediately when an option is clicked, if using timer
        if (useTimer && timerRef.current) {
            clearInterval(timerRef.current);
        }

        setSelectedOption(option); // Highlight the selected option
        setHasAnsweredCurrentQuestion(true); // Mark that the user has answered this question

        const currentQuestion = questions[currentQuestionIndex];
        if (option === currentQuestion.answer) {
            // Correct answer
            setCorrectAnswerGiven(true);
            setScore(prevScore => prevScore + (prizeMoney[answeredCorrectlyCount])); // Use answeredCorrectlyCount for prize
            setAnsweredCorrectlyCount(prevCount => prevCount + 1);
            // No setTimeout here - user will click Next Question button
        } else {
            // Incorrect answer
            setShowIncorrectMessage(true);
            setGameOver(true); // Game ends immediately on incorrect answer
            // Timer is already cleared
        }
    }, [currentQuestionIndex, gameOver, questions, prizeMoney, selectedOption, answeredCorrectlyCount, useTimer, hasAnsweredCurrentQuestion]);

    // Function to handle moving to the next question
    const handleNextQuestion = useCallback(() => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(prevIndex => prevIndex + 1);
            // Reset states for the new question
            setCorrectAnswerGiven(false);
            setShowIncorrectMessage(false);
            setSelectedOption(null);
            setEliminatedOptions([]); // Clear eliminated options for the new question
            setHasAnsweredCurrentQuestion(false); // Reset for the next question
            setTimeLeft(60); // Reset timer for new question (will be picked up by useEffect)
        } else {
            // All questions answered, end the game (win condition handled by isGameWon)
            setGameOver(true);
        }
    }, [currentQuestionIndex, questions.length]);


    // Function to start the game
    const startGame = useCallback((difficulty) => {
        setupGameQuestions(difficulty); // Setup questions based on chosen difficulty
        setSelectedDifficulty(difficulty); // Store selected difficulty
        setGameStarted(true); // Show game screen
    }, [setupGameQuestions]);

    // Function to reset the game (goes back to start screen)
    const resetGame = useCallback(() => {
        setGameStarted(false); // Go back to start screen
        setQuestions([]); // Clear questions to force re-setup on next start
        setCurrentQuestionIndex(0);
        setScore(0);
        setGameOver(false);
        setCorrectAnswerGiven(false);
        setShowIncorrectMessage(false);
        setSelectedOption(null);
        setAnsweredCorrectlyCount(0);
        setTimeLeft(60); // Reset timer state
        setAiLifelineUsed(false); // Reset lifeline usage
        setEliminatedOptions([]); // Clear eliminated options
        setHasAnsweredCurrentQuestion(false); // Reset for new game
        if (timerRef.current) {
            clearInterval(timerRef.current); // Ensure timer is cleared
        }
    }, []);

    // Function to toggle the timer setting on the start screen
    const toggleTimer = useCallback(() => {
        setUseTimer(prev => !prev);
    }, []);

    // --- Gemini API / LLM Feature Functions ---

    // Function for "Ask an AI" lifeline
    const askAILifeline = useCallback(async () => {
        if (aiLifelineUsed || selectedOption !== null || loadingAIResponse) {
            return; // Already used, question already answered, or AI is busy
        }
        setAiLifelineUsed(true);
        setLoadingAIResponse(true);

        const currentQuestion = questions[currentQuestionIndex];
        const prompt = `Given the Python question '${currentQuestion.question}' and the following options: ${JSON.stringify(currentQuestion.options)}. Identify two distinct options that are definitively incorrect and explain why each is incorrect. Do not reveal the correct answer. Provide your response as a JSON array where each element is an object with 'option' (the incorrect option text) and 'reason' (brief explanation). For example: [{"option": "option1", "reason": "reason1"}, {"option": "option2", "reason": "reason2"}]. If you can only identify one, provide one.`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: prompt }] });

        try {
            const payload = {
                contents: chatHistory,
                generationConfig: {
                    responseMimeType: "application/json",
                    responseSchema: {
                        type: "ARRAY",
                        items: {
                            type: "OBJECT",
                            properties: {
                                "option": { "type": "STRING" },
                                "reason": { "type": "STRING" }
                            },
                            "propertyOrdering": ["option", "reason"]
                        }
                    }
                }
            };
            // >>> IMPORTANT: FOR LOCAL HOSTING, REPLACE THE EMPTY STRING BELOW WITH YOUR ACTUAL GEMINI API KEY <<<
            const apiKey = "AIzaSyApf5dBIULpd4xeJbkEjNmns_Kgvq7litU"; // Get your key from https://aistudio.google.com/app/apikey
            // Changed API URL to relative path for proxy
            const apiUrl = `/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorBody = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, body: ${errorBody}`);
            }

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const jsonString = result.candidates[0].content.parts[0].text;
                const parsedEliminations = JSON.parse(jsonString);

                // Filter out the actual correct answer from eliminated options just in case LLM makes a mistake
                const actualIncorrectEliminations = parsedEliminations.filter(
                    item => item.option !== currentQuestion.answer && !eliminatedOptions.includes(item.option) // Ensure not already eliminated
                ).map(item => item.option).slice(0, 2); // Ensure max 2 eliminations

                setEliminatedOptions(prevEliminated => [...prevEliminated, ...actualIncorrectEliminations]);

            } else {
                console.error("Gemini API response structure unexpected:", result);
                alert("AI could not eliminate options. Try again or choose your answer!");
            }
        } catch (error) {
            console.error("Error asking AI:", error);
            alert("Failed to get AI assistance. Please check console for details. (Hint: Did you set up the proxy and API key for local hosting?)");
        } finally {
            setLoadingAIResponse(false);
        }
    }, [aiLifelineUsed, selectedOption, questions, currentQuestionIndex, loadingAIResponse, eliminatedOptions]); // Added loadingAIResponse and eliminatedOptions to dependencies

    // Function for "Explain Concept" lifeline
    const explainConcept = useCallback(async () => {
        setLoadingAIResponse(true);
        setShowExplanationModal(true);
        setExplanationText("Fetching explanation...");

        const currentQuestion = questions[currentQuestionIndex];
        // Use the 'concept' field from the question, or try to infer from question text
        const conceptToExplain = currentQuestion.concept || currentQuestion.question.split('?')[0].replace('What is the', '').replace('How do you', '').trim();

        const prompt = `Explain the Python concept of '${conceptToExplain}' in simple terms for someone who has been learning Python for about a week. Keep the explanation concise and easy to understand.`;

        let chatHistory = [];
        chatHistory.push({ role: "user", parts: [{ text: prompt }] });

        try {
            const payload = { contents: chatHistory };
            // >>> IMPORTANT: FOR LOCAL HOSTING, REPLACE THE EMPTY STRING BELOW WITH YOUR ACTUAL GEMINI API KEY <<<
            const apiKey = "AIzaSyApf5dBIULpd4xeJbkEjNmns_Kgvq7litU"; // Get your key from https://aistudio.google.com/app/apikey
            // Changed API URL to relative path for proxy
            const apiUrl = `/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorBody = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, body: ${errorBody}`);
            }

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                setExplanationText(result.candidates[0].content.parts[0].text);
            } else {
                setExplanationText("Could not generate explanation.");
                console.error("Gemini API response structure unexpected:", result);
            }
        } catch (error) {
            setExplanationText("Failed to load explanation. (Hint: Did you set up the proxy and API key for local hosting?)");
            console.error("Error explaining concept:", error);
        } finally {
            setLoadingAIResponse(false);
        }
    }, [questions, currentQuestionIndex]);

    // Function to close the explanation modal
    const closeExplanationModal = useCallback(() => {
        setShowExplanationModal(false);
        setExplanationText("");
    }, []);

    const currentQuestion = questions[currentQuestionIndex];
    // Game is won if all questions are answered correctly AND game over (i.e. all 15 questions answered)
    const isGameWon = gameOver && answeredCorrectlyCount === questions.length;
    // Show Next Question button if an answer has been selected and game is not yet over, and it was a correct answer
    const showNextButton = hasAnsweredCurrentQuestion && !gameOver && correctAnswerGiven && (currentQuestionIndex < questions.length - 1);


    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-800 via-purple-800 to-pink-800 flex items-center justify-center p-4 font-inter">
            {/* Tailwind CSS for global styles. Inter font is loaded. */}
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet" />
            <script src="https://cdn.tailwindcss.com"></script>

            <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-2xl w-full text-center flex flex-col items-center">
                <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-6 drop-shadow-lg">
                    Who wants to be a Pythonaire?
                </h1>

                {!gameStarted ? (
                    // Start Screen
                    <div className="flex flex-col items-center justify-center space-y-4">
                        <p className="text-xl text-gray-700 mb-4">Choose your game mode:</p>
                        <button
                            onClick={toggleTimer}
                            className={`px-8 py-3 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105 active:scale-95 text-xl font-bold w-64
                                ${useTimer ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-green-500 hover:bg-green-600 text-white'}
                            `}
                        >
                            Timer: {useTimer ? 'On' : 'Off'}
                        </button>
                        <div className="flex flex-col space-y-2 w-full max-w-xs">
                            <button
                                onClick={() => startGame(1)}
                                className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-8 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105 active:scale-95 text-xl"
                            >
                                Start Easy Game
                            </button>
                            <button
                                onClick={() => startGame(2)}
                                className="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-3 px-8 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105 active:scale-95 text-xl"
                            >
                                Start Medium Game
                            </button>
                            <button
                                onClick={() => startGame(3)}
                                className="bg-red-700 hover:bg-red-800 text-white font-bold py-3 px-8 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105 active:scale-95 text-xl"
                            >
                                Start Hard Game
                            </button>
                        </div>
                    </div>
                ) : (
                    // Game Screen
                    <>
                        {!gameOver && questions.length > 0 && (
                            <>
                                {/* Question display area */}
                                <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-2xl mb-8 w-full shadow-lg">
                                    <p className="text-lg md:text-xl font-semibold mb-3">
                                        Question {currentQuestionIndex + 1} of {questions.length}
                                    </p>
                                    <p className="text-2xl md:text-3xl font-bold">
                                        {currentQuestion?.question}
                                    </p>
                                </div>

                                {/* Timer Display (only if useTimer is true and question not answered) */}
                                {useTimer && selectedOption === null && (
                                    <div className={`text-3xl font-bold mb-6 ${timeLeft <= 10 ? 'text-red-600 animate-pulse' : 'text-gray-800'}`}>
                                        Time Left: {timeLeft}s
                                    </div>
                                )}

                                {/* Lifelines */}
                                <div className="flex justify-center space-x-4 mb-8 w-full max-w-sm">
                                    <button
                                        onClick={askAILifeline}
                                        disabled={aiLifelineUsed || selectedOption !== null || loadingAIResponse}
                                        className={`py-2 px-6 rounded-full shadow-md text-white font-bold transition-all duration-300 transform hover:scale-105
                                            ${aiLifelineUsed || selectedOption !== null || loadingAIResponse ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-500 hover:bg-green-600'}
                                        `}
                                    >
                                        ✨ Ask an AI {loadingAIResponse && !showExplanationModal ? '...' : ''}
                                    </button>
                                </div>


                                {/* Options container */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                                    {currentQuestion?.options.map((option, index) => {
                                        const optionLetter = String.fromCharCode(65 + index); // A, B, C, D
                                        const isCorrect = option === currentQuestion.answer;
                                        const isSelected = option === selectedOption;
                                        const isEliminated = eliminatedOptions.includes(option);

                                        let buttonClasses = "bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-4 px-6 rounded-xl shadow-md transition-all duration-300 transform hover:scale-105 active:scale-95 text-lg md:text-xl text-left";

                                        if (isEliminated && !hasAnsweredCurrentQuestion) { // Dim if AI eliminated AND user hasn't answered yet
                                            buttonClasses = "bg-gray-300 text-gray-500 font-semibold py-4 px-6 rounded-xl shadow-md text-lg md:text-xl text-left opacity-50 cursor-not-allowed";
                                        } else if (hasAnsweredCurrentQuestion) { // After answering, show feedback
                                            if (isCorrect) {
                                                buttonClasses = "bg-green-500 text-white font-semibold py-4 px-6 rounded-xl shadow-md text-lg md:text-xl text-left ring-4 ring-green-300";
                                            } else if (isSelected && !isCorrect) {
                                                buttonClasses = "bg-red-500 text-white font-semibold py-4 px-6 rounded-xl shadow-md text-lg md:text-xl text-left ring-4 ring-red-300";
                                            } else if (!isCorrect && !isSelected) {
                                                // Dim other incorrect options, but show the correct one if user was wrong
                                                buttonClasses = "bg-gray-100 text-gray-600 font-semibold py-4 px-6 rounded-xl shadow-md text-lg md:text-xl text-left opacity-70";
                                            }
                                        }
                                        // Disable buttons if already selected, game over, or AI eliminated (before answering)
                                        const isDisabled = selectedOption !== null || gameOver || (isEliminated && !hasAnsweredCurrentQuestion);

                                        return (
                                            <button
                                                key={index}
                                                className={buttonClasses}
                                                onClick={() => handleOptionClick(option)}
                                                disabled={isDisabled}
                                            >
                                                <span className="font-bold mr-2">{optionLetter}.</span> {option}
                                            </button>
                                        );
                                    })}
                                </div>

                                {/* Current Score Display */}
                                <div className="mt-8 text-2xl font-bold text-gray-700">
                                    Current Winnings: <span className="text-green-600">${score}</span>
                                </div>

                                {/* Explain Concept Button (visible after answer) */}
                                {hasAnsweredCurrentQuestion && !gameOver && (
                                    <button
                                        onClick={explainConcept}
                                        disabled={loadingAIResponse}
                                        className={`mt-4 py-2 px-6 rounded-full shadow-md text-white font-bold transition-all duration-300 transform hover:scale-105
                                            ${loadingAIResponse ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'}
                                        `}
                                    >
                                        ✨ Explain Concept {loadingAIResponse && showExplanationModal ? '...' : ''}
                                    </button>
                                )}

                                {/* Next Question Button (visible after correct answer) */}
                                {showNextButton && (
                                    <button
                                        onClick={handleNextQuestion}
                                        className="mt-4 bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-8 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105 active:scale-95 text-xl"
                                    >
                                        Next Question
                                    </button>
                                )}
                            </>
                        )}

                        {/* Game Over / Win Messages */}
                        {gameOver && (
                            <div className="mt-8 text-center w-full">
                                {isGameWon ? (
                                    <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded-lg shadow-inner mb-6">
                                        <p className="text-3xl font-bold mb-2">Congratulations!</p>
                                        <p className="text-xl">You answered all questions correctly and are a Python Millionaire!</p>
                                        <p className="text-2xl font-extrabold mt-3">Final Winnings: <span className="text-green-800">${score}</span></p>
                                    </div>
                                ) : (
                                    <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-lg shadow-inner mb-6">
                                        <p className="text-3xl font-bold mb-2">Game Over!</p>
                                        <p className="text-xl">
                                            {selectedOption === null && currentQuestionIndex < questions.length && useTimer ?
                                                "Time's up! You ran out of time." :
                                                `You answered ${answeredCorrectlyCount} questions correctly.`
                                            }
                                        </p>
                                        <p className="text-2xl font-extrabold mt-3">Final Winnings: <span className="text-red-800">${score}</span></p>
                                        {currentQuestion && showIncorrectMessage && (
                                            <p className="text-lg mt-2">The correct answer was: <span className="font-bold">{currentQuestion.answer}</span></p>
                                        )}
                                    </div>
                                )}
                                <button
                                    onClick={resetGame}
                                    className="mt-6 bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-8 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105 active:scale-95 text-xl"
                                >
                                    Play Again
                                </button>
                            </div>
                        )}

                        {/* Explanation Modal */}
                        {showExplanationModal && (
                            <div className="fixed inset-0 bg-gray-800 bg-opacity-75 flex items-center justify-center p-4 z-50">
                                <div className="bg-white rounded-xl shadow-2xl p-6 max-w-lg w-full text-left">
                                    <h2 className="text-2xl font-bold mb-4 text-gray-900">Concept Explanation</h2>
                                    {loadingAIResponse ? (
                                        <p className="text-gray-600">Loading explanation...</p>
                                    ) : (
                                        <p className="text-gray-800 whitespace-pre-wrap">{explanationText}</p>
                                    )}
                                    <button
                                        onClick={closeExplanationModal}
                                        className="mt-6 bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-6 rounded-full shadow-md transition-all duration-300"
                                    >
                                        Close
                                    </button>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default App;
