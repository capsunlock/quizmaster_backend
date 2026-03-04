import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from quizzes.models import Quiz, Question, Choice
from django.contrib.auth import get_user_model

User = get_user_model()

def run_bulk_import():
    import_folder = 'data_to_import'
    creator = User.objects.filter(is_superuser=True).first()
    
    if not creator:
        print("Error: No superuser found. Run 'python manage.py createsuperuser' first.")
        return

    # Keep track of stats for a nice summary at the end
    imported_count = 0
    skipped_count = 0

    # Ensure the folder exists
    if not os.path.exists(import_folder):
        print(f"Error: Folder '{import_folder}' not found.")
        return

    for filename in os.listdir(import_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(import_folder, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # --- DUPLICATE PROTECTION ---
                    # Check if a quiz with this title already exists in the DB
                    if Quiz.objects.filter(title=data['title']).exists():
                        print(f"[-] Skipping '{filename}': Quiz '{data['title']}' already exists in Database.")
                        skipped_count += 1
                        continue
                    # ----------------------------

                    # Create Quiz
                    quiz = Quiz.objects.create(
                        title=data['title'],
                        description=data['description'],
                        time_limit=data['time_limit'],
                        creator=creator
                    )

                    questions_to_create = []
                    for q_data in data['questions']:
                        # Skip diagram-based questions
                        text_lower = q_data['text'].lower()
                        if any(word in text_lower for word in ["diagram", "figure", "image", "picture"]):
                            continue

                        # Create the question
                        question = Question.objects.create(quiz=quiz, text=q_data['text'])
                        
                        # Prepare choices
                        choice_list = [
                            Choice(question=question, text=c['text'], is_correct=c['is_correct'])
                            for c in q_data['choices']
                        ]
                        Choice.objects.bulk_create(choice_list)

                    print(f"[+] Successfully imported: {data['title']}")
                    imported_count += 1

            except json.JSONDecodeError:
                print(f"[!] Error: {filename} is not a valid JSON file. Check for Python code or typos.")
            except Exception as e:
                print(f"[!] Unexpected error with {filename}: {e}")

    print(f"\n--- Import Summary ---")
    print(f"New Quizzes: {imported_count}")
    print(f"Skipped (Duplicates): {skipped_count}")

if __name__ == "__main__":
    run_bulk_import()