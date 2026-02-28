let qCount = 0;

// Function to add a new question block dynamically
document.getElementById('add-q').onclick = () => {
    qCount++;
    const area = document.getElementById('questions-area');
    const div = document.createElement('div');
    div.className = 'question-card q-block';
    
    // We use a radio group unique to each question (correct-${qCount})
    div.innerHTML = `
        <div style="margin-bottom: 10px;">
            <strong>Question ${qCount}</strong>
            <input type="text" class="q-text" placeholder="Enter your question here" required style="margin-top:5px;">
        </div>
        <div class="choice-row" style="margin-bottom: 5px;">
            <input type="text" class="c-text" placeholder="Choice 1" required style="width: 70%;"> 
            <label><input type="radio" name="correct-${qCount}" value="0" checked> Correct</label>
        </div>
        <div class="choice-row">
            <input type="text" class="c-text" placeholder="Choice 2" required style="width: 70%;"> 
            <label><input type="radio" name="correct-${qCount}" value="1"> Correct</label>
        </div>
        <hr style="margin: 20px 0; border: 0; border-top: 1px solid #eee;">
    `;
    area.appendChild(div);
};

// Handle the Form Submission
document.getElementById('teacher-form').onsubmit = async (e) => {
    e.preventDefault();
    
    const questions = [];
    const questionBlocks = document.querySelectorAll('.q-block');

    if (questionBlocks.length === 0) {
        alert("Please add at least one question.");
        return;
    }

    questionBlocks.forEach((block, i) => {
        const choices = [];
        const choiceInputs = block.querySelectorAll('.c-text');
        const radios = block.querySelectorAll(`input[name="correct-${i + 1}"]`);
        
        choiceInputs.forEach((input, ci) => {
            choices.push({
                text: input.value,
                is_correct: radios[ci].checked
            });
        });

        questions.push({
            text: block.querySelector('.q-text').value,
            choices: choices
        });
    });

    const payload = {
        title: document.getElementById('title').value,
        description: document.getElementById('desc').value,
        questions: questions
    };

    try {
        const response = await fetch('/api/quizzes/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                // This grabs the CSRF token from the hidden input Django generated
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value 
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("Quiz created successfully!");
            window.location.href = '/'; // Redirect to home/quiz list
        } else {
            const errorData = await response.json();
            console.error("Submission Error:", errorData);
            alert("Failed to create quiz. Check console for details.");
        }
    } catch (error) {
        console.error("Network Error:", error);
        alert("A network error occurred.");
    }
};

// Start the page with one question block ready
document.getElementById('add-q').click();