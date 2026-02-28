let qCount = 0;

// Function to add a new question block
document.getElementById('add-q').onclick = () => {
    qCount++;
    const area = document.getElementById('questions-area');
    const div = document.createElement('div');
    div.className = 'question-card q-block';
    div.dataset.qIndex = qCount;

    div.innerHTML = `
        <div class="q-header">
            <strong>Question ${qCount}</strong>
            <button type="button" class="remove-btn" onclick="this.parentElement.parentElement.remove()">
                <i class="trash-icon"></i> Delete Question
            </button>
        </div>
        <input type="text" class="q-text" placeholder="Enter question text..." required>
        
        <div class="choices-list">
            ${[0, 1, 2].map(i => createChoiceRow(qCount, i)).join('')}
        </div>
        
        <button type="button" class="add-choice-btn" onclick="addChoiceToQuestion(${qCount})">+ Add Another Choice</button>
    `;
    area.appendChild(div);
};

// Updated: Added a delete button to the choice row
function createChoiceRow(qNum, cNum) {
    return `
        <div class="choice-row">
            <input type="radio" name="correct-${qNum}" value="${cNum}" ${cNum === 0 ? 'checked' : ''}>
            <input type="text" class="c-text" placeholder="Choice text" required>
            <button type="button" class="delete-choice" onclick="removeChoice(this)">×</button>
        </div>
    `;
}

// Function to add more choices
window.addChoiceToQuestion = (qNum) => {
    const qBlock = document.querySelector(`.q-block[data-q-index="${qNum}"] .choices-list`);
    const currentChoices = qBlock.querySelectorAll('.choice-row').length;
    const newRow = document.createElement('div');
    newRow.className = 'choice-row';
    newRow.innerHTML = createChoiceRow(qNum, currentChoices);
    qBlock.appendChild(newRow);
};

// Function to remove a choice row (prevents removing if only 1 left)
window.removeChoice = (btn) => {
    const list = btn.closest('.choices-list');
    if (list.querySelectorAll('.choice-row').length > 1) {
        btn.parentElement.remove();
    } else {
        alert("A question must have at least one choice.");
    }
};

// Form Submission Logic (unchanged from previous step)
document.getElementById('teacher-form').onsubmit = async (e) => {
    e.preventDefault();
    const questions = [];

    document.querySelectorAll('.q-block').forEach((block) => {
        const choices = [];
        const textInputs = block.querySelectorAll('.c-text');
        const radios = block.querySelectorAll('input[type="radio"]');

        textInputs.forEach((input, index) => {
            choices.push({
                text: input.value,
                is_correct: radios[index].checked
            });
        });

        questions.push({
            text: block.querySelector('.q-text').value,
            choices: choices
        });
    });

    const response = await fetch('/quizzes/api/', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value 
        },
        body: JSON.stringify({
            title: document.getElementById('title').value,
            description: document.getElementById('desc').value,
            questions: questions
        })
    });

    if (response.ok) {
        alert("Quiz successfully created!");
        window.location.href = '/quizzes/';
    }
};

document.getElementById('add-q').click();