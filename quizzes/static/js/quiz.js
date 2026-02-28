document.getElementById('quiz-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const formData = new FormData(e.target);
    const answers = [];
    const questionBlocks = document.querySelectorAll('.question-card');
    
    // Gather the answers from the radio buttons
    for (let [key, value] of formData.entries()) {
        if (key.startsWith('q-')) {
            answers.push({
                question: parseInt(key.replace('q-', '')),
                selected_choice: parseInt(value)
            });
        }
    }

    // Validation: Ensure every question has been answered
    if (answers.length < questionBlocks.length) {
        alert("Please answer all questions before submitting.");
        return;
    }

    // Get the Quiz ID from the hidden input field
    const quizIdElement = document.getElementById('quiz-id');
    if (!quizIdElement) {
        console.error("Error: Missing hidden input field with id='quiz-id'");
        return;
    }
    const quizId = quizIdElement.value;

    // Visual Feedback: Disable button while sending
    submitBtn.disabled = true;
    submitBtn.innerText = "Submitting...";

    try {
        // Send the data to the API
        // NOTE: Ensure your urls.py has a path for 'quizzes/api/submit/'
        const response = await fetch('/quizzes/api/submit/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken') 
            },
            body: JSON.stringify({ 
                quiz: parseInt(quizId), 
                answers: answers 
            })
        });

        if (response.ok) {
            const data = await response.json();
    
            // Check if we actually got an ID back
            if (data.attempt_id) {
            // Option A: Go to the detailed results page
             window.location.href = `/quizzes/results/${data.attempt_id}/`;
        } else {
        // Option B: Emergency Backup (If ID is missing, just go to the leaderboard)
        console.error("ID was missing, redirecting to leaderboard instead.");
        window.location.href = `/quizzes/leaderboard/`;
    }
}
    } catch (error) {
        console.error("Network error:", error);
        alert("A network error occurred. Please check your connection.");
        submitBtn.disabled = false;
        submitBtn.innerText = "Submit Exam";
    }
});