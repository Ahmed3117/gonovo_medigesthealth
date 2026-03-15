"""
MEDIGEST Health Platform — Comprehensive API Endpoint Test Script
Tests all API endpoints end-to-end with dummy data seeding.

Usage:
    python manage.py shell < test_all_endpoints.py
"""
import json
import uuid
import traceback
from datetime import timedelta, datetime
from io import BytesIO

from django.test import RequestFactory
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Allow Django test client's 'testserver' hostname
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

# ═══════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════
client = Client()

PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"
SKIP = "\033[93m⊘ SKIP\033[0m"

results = {'pass': 0, 'fail': 0, 'skip': 0}

def test(name, response, expected_codes=None):
    """Helper to check response status and print result."""
    if expected_codes is None:
        expected_codes = [200, 201]
    code = response.status_code
    if code in expected_codes:
        results['pass'] += 1
        print(f"  {PASS} {name} — {code}")
        return True
    else:
        results['fail'] += 1
        body = ''
        try:
            body = response.json()
        except:
            body = response.content[:200]
        print(f"  {FAIL} {name} — {code} {body}")
        return False

# ═══════════════════════════════════════════════════════
# SEED DATA
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  MEDIGEST API — Seeding Test Data")
print("="*60 + "\n")

from books.models import Book, Specialty, Topic, UserBookAccess
from questions.models import Question, QuizSession, UserQuestionAttempt
from flashcards.models import Flashcard, UserFlashcardProgress
from learning.models import (
    UserTopicProgress, UserHighlight, UserNote, UserBookmark,
    UserLearningPlanTopic, UserStudySession, RecentActivity,
)
from certificates.models import (
    CMEActivity, UserCMECredit, CMESubmission,
    UserCOREProgress, Certificate,
)
from webhooks.models import WebhookLog
from support.models import FAQCategory, FAQ, ContactMethod

# Create test user
test_email = 'apitest@medigest.com'
test_password = 'TestPass123!'
user, created = User.objects.get_or_create(
    email=test_email,
    defaults={
        'first_name': 'API',
        'last_name': 'Tester',
    }
)
if created:
    user.set_password(test_password)
    user.save()
    print(f"  Created test user: {test_email}")
else:
    print(f"  Using existing user: {test_email}")

# Create books FIRST (Specialty requires a book FK)
book, _ = Book.objects.get_or_create(
    slug='internal-medicine-essentials',
    defaults={
        'title': 'Internal Medicine Essentials',
        'description': 'Comprehensive guide to IM',
        'price': 99.99,
        'product_id': 'PROD-001',
    }
)
book2, _ = Book.objects.get_or_create(
    slug='cardiology-review',
    defaults={
        'title': 'Cardiology Review',
        'description': 'Board-style cardiology',
        'price': 79.99,
        'product_id': 'PROD-002',
    }
)
print(f"  Books: {book.title}, {book2.title}")

# Create specialties (requires book FK)
spec, _ = Specialty.objects.get_or_create(
    name='Cardiology',
    book=book,
    defaults={
        'slug': 'cardiology',
        'description': 'Heart and vascular system',
        'is_core_specialty': True,
        'core_display_order': 1,
    }
)
spec2, _ = Specialty.objects.get_or_create(
    name='Pulmonology',
    book=book,
    defaults={
        'slug': 'pulmonology',
        'description': 'Respiratory system',
        'is_core_specialty': True,
        'core_display_order': 2,
    }
)
print(f"  Specialties: {spec.name}, {spec2.name}")

# Grant access to book for user
access, _ = UserBookAccess.objects.get_or_create(
    user=user,
    book=book,
    defaults={'order_id': 'TEST-ORD-001'},
)
print(f"  Book access granted to user")

# Create topics (Topic doesn't have a direct `book` FK — uses specialty.book)
topic, _ = Topic.objects.get_or_create(
    slug='heart-failure',
    specialty=spec,
    defaults={
        'title': 'Heart Failure',
        'display_order': 1,
    }
)
topic2, _ = Topic.objects.get_or_create(
    slug='atrial-fibrillation',
    specialty=spec,
    defaults={
        'title': 'Atrial Fibrillation',
        'display_order': 2,
        'is_board_basics': True,
    }
)
print(f"  Topics: {topic.title}, {topic2.title}")

# Create questions (field is question_text not stem; specialty required)
q1, _ = Question.objects.get_or_create(
    question_text='A 65-year-old male presents with dyspnea on exertion. Chest X-ray shows cardiomegaly. Which is the most likely diagnosis?',
    specialty=spec,
    defaults={
        'topic': topic,
        'option_a': 'Pneumonia',
        'option_b': 'Heart Failure',
        'option_c': 'Pulmonary Embolism',
        'option_d': 'COPD',
        'correct_answer': 'B',
        'explanation': 'Cardiomegaly with dyspnea on exertion points to heart failure.',
        'difficulty': 'medium',
        'is_active': True,
    }
)
q2, _ = Question.objects.get_or_create(
    question_text='What is the first-line treatment for rate control in atrial fibrillation?',
    specialty=spec,
    defaults={
        'topic': topic2,
        'option_a': 'Amiodarone',
        'option_b': 'Digoxin',
        'option_c': 'Beta-blockers',
        'option_d': 'Flecainide',
        'correct_answer': 'C',
        'explanation': 'Beta-blockers are first-line for rate control in AFib.',
        'difficulty': 'easy',
        'is_active': True,
    }
)
print(f"  Questions: {q1.id}, {q2.id}")

# Create flashcards (specialty is required FK)
fc1, _ = Flashcard.objects.get_or_create(
    front_text='What are the 4 stages of heart failure?',
    specialty=spec,
    defaults={
        'back_text': 'Stage A: At risk, B: Pre-HF, C: Symptomatic HF, D: Advanced HF',
        'book': book,
        'related_topic': topic,
        'display_order': 1,
    }
)
fc2, _ = Flashcard.objects.get_or_create(
    front_text='What is the CHADS2-VASc score used for?',
    specialty=spec,
    defaults={
        'back_text': 'Estimating stroke risk in patients with atrial fibrillation',
        'book': book,
        'related_topic': topic2,
        'display_order': 2,
    }
)
print(f"  Flashcards: {fc1.id}, {fc2.id}")

# Create CME Activity (field is 'credits' not 'credits_available', no 'passing_score')
cme_act, _ = CMEActivity.objects.get_or_create(
    title='Cardiology Quiz CME',
    defaults={
        'activity_type': CMEActivity.ActivityType.QUIZ,
        'credits': 0.5,
        'specialty': spec,
    }
)

# Create a CME credit for the user (field is 'status' not 'credit_status')
cme_credit, _ = UserCMECredit.objects.get_or_create(
    user=user,
    activity=cme_act,
    defaults={
        'credits_earned': 0.5,
        'status': UserCMECredit.Status.EARNED,
        'credit_year': 2026,
    }
)
print(f"  CME Activity & Credit created")

# Create Support Help Center Data
faq_cat, _ = FAQCategory.objects.get_or_create(
    name='Account & Access',
    display_order=1
)
FAQ.objects.get_or_create(
    category=faq_cat,
    question='How do I reset my password?',
    defaults={
        'answer': 'You can reset your password from the login page or profile settings.',
        'display_order': 1,
        'is_published': True
    }
)
ContactMethod.objects.get_or_create(
    title='support@medigest.com',
    defaults={
        'subtitle': 'Email Support',
        'icon_type': ContactMethod.IconType.EMAIL,
        'action_text': 'Get help from our support team ->',
        'action_url': 'mailto:support@medigest.com',
        'display_order': 1
    }
)
print(f"  Help Center data created")

# Create a recent activity
RecentActivity.objects.get_or_create(
    user=user,
    activity_type=RecentActivity.ActivityType.READING,
    title='Read Heart Failure',
    defaults={
        'description': 'Read Heart Failure topic for 15 min',
        'reference_id': topic.id,
    }
)
print(f"  Recent activity created")

print("\n  ✅ Seed data ready!\n")

# ═══════════════════════════════════════════════════════
# TEST 1: AUTHENTICATION
# ═══════════════════════════════════════════════════════
print("="*60)
print("  1. AUTHENTICATION")
print("="*60)

# Register
reg_resp = client.post('/api/v1/auth/register/', data=json.dumps({
    'email': 'newuser@medigest.com',
    'first_name': 'New',
    'last_name': 'User',
    'password': 'StrongPass789!',
    'password_confirm': 'StrongPass789!',
}), content_type='application/json')
test("Register new user", reg_resp, [201, 400])  # 400 if already exists

# Login
login_resp = client.post('/api/v1/auth/login/', data=json.dumps({
    'email': test_email,
    'password': test_password,
}), content_type='application/json')
ok = test("Login", login_resp, [200])

access_token = ''
refresh_token = ''
if ok:
    tokens = login_resp.json()
    access_token = tokens.get('access', '')
    refresh_token = tokens.get('refresh', '')
    print(f"    → Got access token: {access_token[:20]}...")

AUTH = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}

# Refresh token
ref_resp = client.post('/api/v1/auth/token/refresh/', data=json.dumps({
    'refresh': refresh_token,
}), content_type='application/json')
if test("Refresh token", ref_resp, [200]):
    new_token = ref_resp.json()
    access_token = new_token.get('access', access_token)
    AUTH = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}

# Get profile
test("Get profile", client.get('/api/v1/users/me/', **AUTH))

# Update profile
test("Update profile", client.patch('/api/v1/users/me/',
    data=json.dumps({'first_name': 'Updated', 'theme': 'dark'}),
    content_type='application/json', **AUTH))

# Password reset request
test("Password reset request", client.post('/api/v1/auth/password/reset/',
    data=json.dumps({'email': test_email}),
    content_type='application/json'))

# Change password
test("Change password", client.post('/api/v1/users/me/change-password/',
    data=json.dumps({
        'current_password': test_password,
        'new_password': 'NewStrongPass456!',
        'new_password_confirm': 'NewStrongPass456!',
    }), content_type='application/json', **AUTH))

# Re-login with new password
login_resp2 = client.post('/api/v1/auth/login/', data=json.dumps({
    'email': test_email,
    'password': 'NewStrongPass456!',
}), content_type='application/json')
if test("Re-login after password change", login_resp2, [200]):
    tokens2 = login_resp2.json()
    access_token = tokens2.get('access', '')
    refresh_token = tokens2.get('refresh', '')
    AUTH = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}

# Reset password back for future tests
user.set_password(test_password)
user.save()

# ═══════════════════════════════════════════════════════
# TEST 2: DASHBOARD
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  2. DASHBOARD")
print("="*60)

# Re-login (password was reset)
login_resp3 = client.post('/api/v1/auth/login/', data=json.dumps({
    'email': test_email,
    'password': test_password,
}), content_type='application/json')
if login_resp3.status_code == 200:
    tokens3 = login_resp3.json()
    access_token = tokens3.get('access', '')
    refresh_token = tokens3.get('refresh', '')
    AUTH = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}

resp = client.get('/api/v1/dashboard/', **AUTH)
if test("Get Dashboard", resp):
    data = resp.json()
    print(f"    → Stats keys: {list(data.get('stats', {}).keys())}")
    print(f"    → Quick actions: {len(data.get('quick_actions', []))}")
    print(f"    → Recent activity: {len(data.get('recent_activity', []))}")

# ═══════════════════════════════════════════════════════
# TEST 3: SYLLABUS & BOOKS
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  3. SYLLABUS & BOOKS")
print("="*60)

# My Books
resp = client.get('/api/v1/syllabus/my-books/', **AUTH)
if test("My Books", resp):
    data = resp.json()
    print(f"    → Books count: {len(data.get('books', []))}")

# Store
test("Store Books", client.get('/api/v1/syllabus/store/', **AUTH))

# Book detail
resp = client.get(f'/api/v1/syllabus/books/{book.slug}/', **AUTH)
if test("Book Detail", resp):
    data = resp.json()
    print(f"    → Book: {data.get('title', 'N/A')}")

# Topic detail
resp = client.get(f'/api/v1/syllabus/topics/{topic.slug}/', **AUTH)
if test("Topic Detail", resp):
    data = resp.json()
    print(f"    → Topic: {data.get('title', 'N/A')}")

# Update topic progress
test("Update Topic Progress", client.patch(
    f'/api/v1/syllabus/topics/{topic.slug}/progress/',
    data=json.dumps({
        'reading_time_seconds': 120,
        'last_read_section': 'section-2',
    }), content_type='application/json', **AUTH))

# Create bookmark
bm_resp = client.post('/api/v1/syllabus/bookmarks/',
    data=json.dumps({
        'topic': str(topic.id),
        'section_anchor': 'test-section-1',
        'label': 'Test Bookmark',
    }), content_type='application/json', **AUTH)
bookmark_id = None
if test("Create Bookmark", bm_resp, [201]):
    bookmark_id = bm_resp.json().get('id')

# List bookmarks
test("List Bookmarks", client.get('/api/v1/syllabus/bookmarks/', **AUTH))

# Create highlight
hl_resp = client.post('/api/v1/syllabus/highlights/',
    data=json.dumps({
        'topic': str(topic.id),
        'highlighted_text': 'Heart failure is a clinical syndrome',
        'start_offset': 0,
        'end_offset': 36,
        'color': 'yellow',
    }), content_type='application/json', **AUTH)
highlight_id = None
if test("Create Highlight", hl_resp, [201]):
    highlight_id = hl_resp.json().get('id')

# Create note
note_resp = client.post('/api/v1/syllabus/notes/',
    data=json.dumps({
        'topic': str(topic.id),
        'content': 'Remember the stages of HF',
        'position_offset': 50,
    }), content_type='application/json', **AUTH)
note_id = None
if test("Create Note", note_resp, [201]):
    note_id = note_resp.json().get('id')

# Update note
if note_id:
    test("Update Note", client.patch(
        f'/api/v1/syllabus/notes/{note_id}/',
        data=json.dumps({'content': 'Updated note content'}),
        content_type='application/json', **AUTH))

# Notes & Highlights list
test("Notes & Highlights", client.get('/api/v1/syllabus/notes-highlights/', **AUTH))

# Notes & Highlights by topic
test("Notes & Highlights by Topic",
    client.get(f'/api/v1/syllabus/notes-highlights/{topic.id}/', **AUTH))

# Delete operations (cleanup)
if note_id:
    test("Delete Note", client.delete(f'/api/v1/syllabus/notes/{note_id}/delete/', **AUTH), [204])
if highlight_id:
    test("Delete Highlight", client.delete(f'/api/v1/syllabus/highlights/{highlight_id}/', **AUTH), [204])
if bookmark_id:
    test("Delete Bookmark", client.delete(f'/api/v1/syllabus/bookmarks/{bookmark_id}/', **AUTH), [204])

# ═══════════════════════════════════════════════════════
# TEST 4: QUESTION BANK
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  4. QUESTION BANK")
print("="*60)

# Main page
resp = client.get('/api/v1/question-bank/', **AUTH)
if test("Question Bank Main", resp):
    data = resp.json()
    print(f"    → Question sets: {len(data.get('question_sets', []))}")

# Question set by book
test("Question Set by Book",
    client.get(f'/api/v1/question-bank/sets/{book.slug}/', **AUTH))

# Question detail
resp = client.get(f'/api/v1/question-bank/questions/{q1.id}/', **AUTH)
if test("Question Detail", resp):
    data = resp.json()
    print(f"    → Options count: {len(data.get('options', []))}")

# Submit answer
ans_resp = client.post(
    f'/api/v1/question-bank/questions/{q1.id}/answer/',
    data=json.dumps({'selected_answer': 'B'}),
    content_type='application/json', **AUTH)
if test("Submit Answer (correct)", ans_resp):
    data = ans_resp.json()
    print(f"    → Correct: {data.get('is_correct')}")

# Submit answer (wrong)
ans_resp2 = client.post(
    f'/api/v1/question-bank/questions/{q2.id}/answer/',
    data=json.dumps({'selected_answer': 'A'}),
    content_type='application/json', **AUTH)
if test("Submit Answer (incorrect)", ans_resp2):
    data = ans_resp2.json()
    print(f"    → Correct: {data.get('is_correct')}")

# Answered questions
test("Answered Questions", client.get('/api/v1/question-bank/answered/', **AUTH))

# Toggle save question
test("Toggle Save Question (save)",
    client.post(f'/api/v1/question-bank/questions/{q1.id}/toggle-save/', **AUTH))

# Saved questions
resp = client.get('/api/v1/question-bank/saved/', **AUTH)
if test("Saved Questions", resp):
    data = resp.json()
    print(f"    → Saved count: {len(data.get('results', data.get('questions', [])))}")

# Toggle save again (unsave)
test("Toggle Save Question (unsave)",
    client.post(f'/api/v1/question-bank/questions/{q1.id}/toggle-save/', **AUTH))

# Create custom quiz
quiz_resp = client.post('/api/v1/question-bank/custom-quizzes/create/',
    data=json.dumps({
        'template': 'build_your_own',
        'title': 'Test Quiz',
        'question_count': 5,
    }), content_type='application/json', **AUTH)
quiz_id = None
if test("Create Custom Quiz", quiz_resp, [201]):
    quiz_id = quiz_resp.json().get('id')

# List custom quizzes
resp = client.get('/api/v1/question-bank/custom-quizzes/', **AUTH)
if test("Custom Quizzes List", resp):
    data = resp.json()
    print(f"    → Quizzes: {len(data.get('quizzes', []))}")

# Delete custom quiz
if quiz_id:
    test("Delete Custom Quiz",
        client.delete(f'/api/v1/question-bank/custom-quizzes/{quiz_id}/', **AUTH), [204])

# Shuffle questions
resp = client.post('/api/v1/question-bank/shuffle/',
    data=json.dumps({'count': 2}), content_type='application/json', **AUTH)
if test("Shuffle Questions", resp):
    data = resp.json()
    print(f"    → Shuffled: {len(data.get('questions', []))}")

# ═══════════════════════════════════════════════════════
# TEST 5: FLASHCARDS
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  5. FLASHCARDS")
print("="*60)

# Flashcard decks
resp = client.get('/api/v1/flashcards/', **AUTH)
if test("Flashcard Decks", resp):
    data = resp.json()
    print(f"    → Decks: {len(data.get('decks', []))}")

# Flashcard by position
resp = client.get(f'/api/v1/flashcards/decks/{book.slug}/1/', **AUTH)
if test("Flashcard by Position", resp):
    data = resp.json()
    print(f"    → Card: {data.get('front_text', 'N/A')[:50]}")

# Review flashcard
test("Review Flashcard", client.post(
    f'/api/v1/flashcards/{fc1.id}/review/',
    data=json.dumps({'confidence': 3}),
    content_type='application/json', **AUTH))

# ═══════════════════════════════════════════════════════
# TEST 6: LEARNING PLAN
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  6. LEARNING PLAN")
print("="*60)

# Get learning plan
test("Get Learning Plan", client.get('/api/v1/learning-plan/', **AUTH))

# Available topics
resp = client.get('/api/v1/learning-plan/available-topics/', **AUTH)
if test("Available Topics", resp):
    data = resp.json()
    print(f"    → Available: {len(data.get('results', []))}")

# Add topic to plan
add_resp = client.post('/api/v1/learning-plan/topics/',
    data=json.dumps({'topic': str(topic.id)}),
    content_type='application/json', **AUTH)
plan_entry_id = None
if test("Add Topic to Plan", add_resp, [201]):
    plan_entry_id = add_resp.json().get('id')

# Get learning plan again
resp = client.get('/api/v1/learning-plan/', **AUTH)
if test("Learning Plan (after add)", resp):
    data = resp.json()
    print(f"    → Topics in plan: {data.get('count', 0)}")

# Remove topic from plan
if plan_entry_id:
    test("Remove Topic from Plan",
        client.delete(f'/api/v1/learning-plan/topics/{plan_entry_id}/', **AUTH), [204])

# ═══════════════════════════════════════════════════════
# TEST 7: CORE
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  7. CORE")
print("="*60)

# CORE dashboard
resp = client.get('/api/v1/core/', **AUTH)
if test("CORE Dashboard", resp):
    data = resp.json()
    print(f"    → Badges: {len(data.get('badges', []))}")

# CORE specialty detail
test("CORE Specialty Detail",
    client.get(f'/api/v1/core/{spec.slug}/', **AUTH))

# ═══════════════════════════════════════════════════════
# TEST 8: BOARD BASICS
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  8. BOARD BASICS")
print("="*60)

resp = client.get('/api/v1/board-basics/', **AUTH)
if test("Board Basics List", resp):
    data = resp.json()
    print(f"    → Specialties: {len(data.get('specialties', []))}")

# ═══════════════════════════════════════════════════════
# TEST 9: CME / MOC
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  9. CME / MOC")
print("="*60)

# CME Dashboard
resp = client.get('/api/v1/cme/', **AUTH)
if test("CME Dashboard", resp):
    data = resp.json()
    print(f"    → Earned credits: {data.get('earned_credits', 0)}")

# CME History
test("CME Credit History", client.get('/api/v1/cme/history/', **AUTH))

# Submit CME Credits
test("Submit CME Credits", client.post('/api/v1/cme/submit/',
    data=json.dumps({
        'accreditation_body': 'ama',
        'credit_ids': [str(cme_credit.id)],
        'notes': 'Test submission',
    }), content_type='application/json', **AUTH), [201])

# ═══════════════════════════════════════════════════════
# TEST 10: CERTIFICATES
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  10. CERTIFICATES")
print("="*60)

# List certificates
resp = client.get('/api/v1/certificates/', **AUTH)
if test("List Certificates", resp):
    data = resp.json()
    print(f"    → Certificates: {len(data.get('results', []))}")

# ═══════════════════════════════════════════════════════
# TEST 11: STUDY SESSIONS
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  11. STUDY SESSIONS")
print("="*60)

test("Record Study Session", client.post('/api/v1/users/me/study-sessions/',
    data=json.dumps({
        'session_type': 'reading',
        'duration_seconds': 1800,
        'started_at': '2026-03-01T09:00:00Z',
    }), content_type='application/json', **AUTH), [201])

# ═══════════════════════════════════════════════════════
# TEST 12: WEBHOOKS
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  12. WEBHOOKS")
print("="*60)

# Purchase webhook (no auth, but needs HMAC signature)
import hashlib, hmac as hmac_mod
webhook_secret = getattr(settings, 'WEBHOOK_SIGNING_SECRET', '')
webhook_body = json.dumps({
    'order_id': 'TEST-ORD-999',
    'customer_email': 'webhookbuyer@example.com',
    'customer_first_name': 'Webhook',
    'customer_last_name': 'Buyer',
    'product_ids': ['PROD-001'],
}).encode()
if webhook_secret:
    sig = hmac_mod.new(webhook_secret.encode(), webhook_body, hashlib.sha256).hexdigest()
else:
    sig = ''
test("Purchase Webhook", client.post('/api/v1/webhooks/purchase/',
    data=webhook_body, content_type='application/json',
    HTTP_X_WEBHOOK_SIGNATURE=sig))

# Verify webhook created user and granted access
wh_user = User.objects.filter(email='webhookbuyer@example.com').first()
if wh_user:
    wh_access = UserBookAccess.objects.filter(user=wh_user, book=book).exists()
    print(f"    → Webhook user created: True, Book access: {wh_access}")
else:
    print(f"    → Webhook user NOT created")

# ═══════════════════════════════════════════════════════
# TEST 13: HELP CENTER
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  13. HELP CENTER")
print("="*60)

resp = client.get('/api/v1/help/', **AUTH)
if test("Help Center", resp):
    data = resp.json()
    print(f"    → FAQ Categories: {len(data.get('faq_categories', []))}")
    print(f"    → Contact Methods: {len(data.get('contact_methods', []))}")

# ═══════════════════════════════════════════════════════
# TEST 14: LOGOUT
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  13. LOGOUT")
print("="*60)

# Need a fresh refresh token since rotating was on
login_resp4 = client.post('/api/v1/auth/login/', data=json.dumps({
    'email': test_email,
    'password': test_password,
}), content_type='application/json')
if login_resp4.status_code == 200:
    tokens4 = login_resp4.json()
    fresh_refresh = tokens4.get('refresh', '')
    fresh_access = tokens4.get('access', '')
    test("Logout", client.post('/api/v1/auth/logout/',
        data=json.dumps({'refresh': fresh_refresh}),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {fresh_access}'))

# ═══════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════
print("\n" + "="*60)
print("  RESULTS SUMMARY")
print("="*60)
total = results['pass'] + results['fail'] + results['skip']
print(f"\n  Total:  {total}")
print(f"  {PASS}:  {results['pass']}")
print(f"  {FAIL}:  {results['fail']}")
print(f"  {SKIP}:  {results['skip']}")
pct = round((results['pass'] / total) * 100) if total else 0
print(f"\n  Pass Rate: {pct}%")
if results['fail'] == 0:
    print(f"\n  🎉 ALL TESTS PASSED!")
else:
    print(f"\n  ⚠️  {results['fail']} test(s) need attention.")
print("="*60 + "\n")
