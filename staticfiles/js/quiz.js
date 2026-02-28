document.getElementById('quiz-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const answers = [];
    const questionBlocks = document.querySelectorAll('.question-card');
    
    // 1. Gather the answers from the radio buttons
    for (let [key, value] of formData.entries()) {
        if (key.startsWith('q-')) {
            answers.push({
                question: parseInt(key.replace('q-', '')),
                selected_choice: parseInt(value)
            });
        }
    }

    // 2. Validation: Ensure every question has been answered
    if (answers.length < questionBlocks.length) {
        alert("Please answer all questions before submitting.");
        return;
    }

    // 3. Get the Quiz ID from the hidden input field
    const quizIdElement = document.getElementById('quiz-id');
    if (!quizIdElement) {
        console.error("Error: Missing hidden input field with id='quiz-id'");
        return;
    }
    const quizId = quizIdElement.value;

    try {
        // 4. Send the data to the API
        const response = await fetch('/api/quizzes/submit/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                // This grabs the CSRF token from the form for Django security
                'X-CSRFToken': formData.get('csrfmiddlewaretoken') 
            },
            body: JSON.stringify({ 
                quiz: parseInt(quizId), 
                answers: answers 
            })
        });

        if (response.ok) {
            const data = await response.json();
            // 5. Redirect to the results page with the score as a URL parameter
            window.location.href = `/results/?score=${data.score}`;
        } else {
            const errorData = await response.json();
            console.error("Submission failed:", errorData);
            alert("There was an error submitting your quiz. Please try again.");
        }
    } catch (error) {
        console.error("Network error:", error);
        alert("A network error occurred. Please check your connection.");
    }
});