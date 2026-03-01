# MEDIGEST Platform — Student API Endpoints Specification

> **Version:** 1.0  
> **Last Updated:** 2026-03-01  
> **Status:** 📝 Draft — Awaiting Review  
> **Based on:** Figma Parts 1-3 (33 screens) + Models Analysis  

---

## Table of Contents

1. [General Info](#1-general-info)
2. [Authentication](#2-authentication-endpoints)
3. [Dashboard](#3-dashboard-endpoints)
4. [Syllabus & Store](#4-syllabus--store-endpoints)
5. [Reading Interface](#5-reading-interface-endpoints)
6. [Question Bank](#6-question-bank-endpoints)
7. [Learning Plan](#7-learning-plan-endpoints)
8. [CORE Certification](#8-core-certification-endpoints)
9. [Board Basics](#9-board-basics-endpoints)
10. [Flashcards](#10-flashcard-endpoints)
11. [CME/MOC/CPD](#11-cmemoccpd-endpoints)
12. [User Profile & Preferences](#12-user-profile--preferences-endpoints)
13. [Changelog](#13-changelog)

---

## 1. General Info

### Base URL
```
https://online.medigesthealth.com/api/v1/
```

### Authentication
All endpoints (except Auth) require a Bearer token in the header:
```
Authorization: Bearer <access_token>
```

### Common Headers
```
Content-Type: application/json
Accept: application/json
```

### Standard Error Response
```json
{
  "error": "string",
  "detail": "string",
  "code": "ERROR_CODE"
}
```

### Pagination Format (used in all list endpoints)
```json
{
  "count": 195,
  "page": 1,
  "page_size": 6,
  "total_pages": 33,
  "next": "https://…/api/v1/…/?page=2",
  "previous": null,
  "results": []
}
```

---

## 2. Authentication Endpoints

> **Figma Screens:** 1 (Login), 2 (Reset Password Email), 3 (Create New Password), 4 (Check Your Email)

### 2.1 Register (Create Account)

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/auth/register/` |
| **Auth Required** | ❌ No |

**Request Body:**
```json
{
  "email": "user@example.com",
  "first_name": "Alex",
  "last_name": "Johnson",
  "password": "SecureP@ssw0rd!",
  "password_confirm": "SecureP@ssw0rd!"
}
```

**Success Response (201 Created):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "Alex",
  "last_name": "Johnson",
  "access": "eyJ…access_token…",
  "refresh": "eyJ…refresh_token…"
}
```

**Error Responses:**
| Code | Condition |
|------|-----------|
| 400 | Validation error (weak password, email exists, passwords don't match) |

---

### 2.2 Login

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/auth/login/` |
| **Auth Required** | ❌ No |

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd!",
  "remember_me": true
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJ…access_token…",
  "refresh": "eyJ…refresh_token…",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "Alex",
    "last_name": "Johnson",
    "profile_picture": "https://…/profiles/photo.jpg",
    "role": "student",
    "theme": "light",
    "font_size": "medium"
  }
}
```

**Error Responses:**
| Code | Condition |
|------|-----------|
| 401 | Invalid credentials |
| 400 | Missing fields |

---

### 2.3 Token Refresh

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/auth/token/refresh/` |
| **Auth Required** | ❌ No |

**Request Body:**
```json
{
  "refresh": "eyJ…refresh_token…"
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJ…new_access_token…"
}
```

---

### 2.4 Logout

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/auth/logout/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "refresh": "eyJ…refresh_token…"
}
```

**Success Response (200 OK):**
```json
{
  "detail": "Successfully logged out."
}
```

---

### 2.5 Request Password Reset

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/auth/password/reset/` |
| **Auth Required** | ❌ No |

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200 OK):**
```json
{
  "detail": "Password reset instructions sent to user@example.com"
}
```

> ⚠️ Always returns 200 even if email doesn't exist (security best practice).

---

### 2.6 Confirm Password Reset

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/auth/password/reset/confirm/` |
| **Auth Required** | ❌ No |

**Request Body:**
```json
{
  "uid": "base64_encoded_user_id",
  "token": "password_reset_token",
  "new_password": "NewSecureP@ss1!",
  "new_password_confirm": "NewSecureP@ss1!"
}
```

**Success Response (200 OK):**
```json
{
  "detail": "Password has been reset successfully."
}
```

---

## 3. Dashboard Endpoints

> **Figma Screens:** 5 (Dashboard Home)

### 3.1 Get Dashboard Data

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/dashboard/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "welcome": {
    "first_name": "Alex",
    "greeting": "Welcome back, Alex!"
  },
  "stats": {
    "overall_progress": {
      "percentage": 52,
      "detail": "450 / 870 pages"
    },
    "quiz_average": {
      "percentage": 85,
      "detail": "Last 10 quizzes"
    },
    "study_time": {
      "hours": 12.5,
      "detail": "This week"
    },
    "study_streak": {
      "days": 7,
      "detail": "Keep it up!"
    }
  },
  "continue_learning": [
    {
      "id": "uuid",
      "book_title": "Internal Medicine Essentials",
      "topic_title": "Heart Failure",
      "specialty_name": "Cardiovascular Disease",
      "progress_percentage": 45,
      "last_accessed": "2026-02-14T10:00:00Z"
    }
  ],
  "quick_actions": {
    "start_reading": {
      "label": "Start Reading",
      "has_history": true,
      "resume_url": "/syllabus/topics/heart-failure/",
      "resume_context": {
        "book_title": "Internal Medicine Essentials",
        "topic_title": "Heart Failure",
        "topic_slug": "heart-failure",
        "last_read_section": "pathophysiology",
        "progress_percentage": 60
      },
      "fallback_url": "/syllabus/"
    },
    "practice_questions": {
      "label": "Practice Questions",
      "has_history": true,
      "resume_url": "/question-bank/questions/uuid_of_next_unanswered/",
      "resume_context": {
        "book_title": "Internal Medicine Essentials",
        "quiz_session_id": "uuid_or_null",
        "next_question_id": "uuid",
        "questions_answered": 5,
        "total_questions": 215
      },
      "fallback_url": "/question-bank/"
    },
    "study_flashcards": {
      "label": "Study Flashcards",
      "has_history": true,
      "resume_url": "/flashcards/decks/internal-medicine-essentials/42/",
      "resume_context": {
        "book_title": "Internal Medicine Essentials",
        "book_slug": "internal-medicine-essentials",
        "last_position": 42,
        "total_in_deck": 215
      },
      "fallback_url": "/flashcards/"
    }
  },
  "todays_goals": {
    "reading_time": { "current": 45, "target": 60, "unit": "min" },
    "practice_questions": { "current": 15, "target": 20, "unit": "done" },
    "flashcards_review": { "current": 0, "target": 25, "unit": "done" }
  },
  "board_basics_preview": [
    {
      "id": "uuid",
      "book_title": "Internal Medicine Essentials",
      "topic_title": "Topic Name",
      "progress_percentage": 45
    }
  ],
  "core_preview": {
    "badges_earned": 4,
    "badges_total": 11,
    "next_badges": [
      {
        "number": 5,
        "name": "Hematology",
        "status": "in_progress",
        "progress_percentage": 45
      },
      {
        "number": 6,
        "name": "Infectious Disease",
        "status": "pending",
        "progress_percentage": 0
      }
    ]
  }
}
```

> **📌 Quick Actions — Resume Logic (Backend):**
>
> Each Quick Action is a **smart "continue where you left off" button**, not a static link. The backend resolves the student's last unfinished activity for each type:
>
> | Action | Resume Logic |
> |--------|-------------|
> | **Start Reading** | Find the most recently accessed topic that is NOT marked as completed (`is_completed=false`). Uses `UserTopicProgress.updated_at` ordered descending. If no history exists, `has_history=false` and frontend uses `fallback_url`. |
> | **Practice Questions** | Find the last active quiz session (`QuizSession.is_completed=false`) or the most recently answered question's book set. Returns the next unanswered question ID. If no history, falls back to `/question-bank/`. |
> | **Study Flashcards** | Find the last reviewed flashcard (`UserFlashcardProgress.last_reviewed_at` descending), return its deck (book) and the next position. If no history, falls back to `/flashcards/`. |
>
> The `resume_context` object gives the frontend enough info to show a subtitle like *"Continue: Heart Failure — Internal Medicine Essentials"* on the button.

---

## 4. Syllabus & Store Endpoints

> **Figma Screens:** 6 (My Books), 7 (Store), 8-9 (Bookmarks/Notes Empty), 11-13 (Bookmarks/Notes Populated)

### 4.1 Get My Books (Syllabus)

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/syllabus/my-books/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "stats": {
    "overall_progress": { "percentage": 52, "detail": "450 / 870 pages" },
    "bank_average_score": { "percentage": 85, "detail": "Last 10 quizzes" },
    "study_time": { "hours": 12.5, "detail": "This week" },
    "study_streak": { "days": 7, "detail": "Keep it up!" }
  },
  "books": [
    {
      "id": "uuid",
      "title": "Internal Medicine Essentials",
      "slug": "internal-medicine-essentials",
      "cover_image": "https://…/covers/ime.jpg",
      "last_topic_title": "Heart Failure",
      "last_specialty_name": "Cardiovascular Disease",
      "last_accessed": "2026-02-14T10:00:00Z",
      "progress_percentage": 45,
      "quick_links": {
        "flashcards": "/flashcards/?book=uuid",
        "board_basics": "/board-basics/?book=uuid",
        "question_bank": "/question-bank/?book=uuid"
      }
    }
  ]
}
```

---

### 4.2 Get Store Books

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/syllabus/store/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "books": [
    {
      "id": "uuid",
      "title": "Internal Medicine Essentials",
      "slug": "internal-medicine-essentials",
      "cover_image": "https://…/covers/ime.jpg",
      "price": "49.99",
      "topic_count": 15,
      "lesson_count": 15,
      "flashcard_count": 155,
      "status": "active",
      "purchase_url": "https://medigesthealth.com/products/internal-medicine"
    }
  ]
}
```

---

### 4.3 Get Book Detail (Specialties & Topics)

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/syllabus/books/{book_slug}/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "id": "uuid",
  "title": "Internal Medicine Essentials",
  "slug": "internal-medicine-essentials",
  "cover_image": "https://…",
  "progress_percentage": 45,
  "specialties": [
    {
      "id": "uuid",
      "name": "Cardiovascular Disease",
      "slug": "cardiovascular-disease",
      "icon": "https://…",
      "progress_percentage": 80,
      "topic_count": 5,
      "topics": [
        {
          "id": "uuid",
          "title": "Heart Failure",
          "slug": "heart-failure",
          "is_completed": false,
          "progress_percentage": 60
        }
      ]
    }
  ]
}
```

---

### 4.4 Get Bookmarks

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/syllabus/bookmarks/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "count": 4,
  "bookmarks": [
    {
      "id": "uuid",
      "topic_id": "uuid",
      "topic_title": "Abdominal and Pelvic Pain",
      "section_anchor": "epidemiology-risk-factors",
      "label": "Epidemiology and Risk Factors",
      "created_at": "2026-02-14T10:00:00Z"
    }
  ]
}
```

---

### 4.5 Create Bookmark

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/syllabus/bookmarks/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "topic_id": "uuid",
  "section_anchor": "epidemiology-risk-factors",
  "label": "Epidemiology and Risk Factors"
}
```

**Success Response (201 Created):**
```json
{
  "id": "uuid",
  "topic_id": "uuid",
  "topic_title": "Abdominal and Pelvic Pain",
  "section_anchor": "epidemiology-risk-factors",
  "label": "Epidemiology and Risk Factors",
  "created_at": "2026-02-14T10:00:00Z"
}
```

---

### 4.6 Delete Bookmark

| Detail | Value |
|--------|-------|
| **Method** | `DELETE` |
| **URL** | `/api/v1/syllabus/bookmarks/{bookmark_id}/` |
| **Auth Required** | ✅ Yes |

**Success Response (204 No Content)**

---

### 4.7 Get Notes & Highlights (List by Topic)

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/syllabus/notes-highlights/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "total_count": 24,
  "topics": [
    {
      "topic_id": "uuid",
      "topic_title": "Abdominal and Pelvic Pain",
      "notes_count": 3,
      "highlights_count": 5
    }
  ]
}
```

---

### 4.8 Get Notes & Highlights Detail (for a Topic)

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/syllabus/notes-highlights/{topic_id}/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "topic_id": "uuid",
  "topic_title": "Abdominal and Pelvic Pain",
  "highlights": [
    {
      "id": "uuid",
      "highlighted_text": "Important observations…",
      "section_label": "Epidemiology and Risk Factors",
      "color": "yellow",
      "start_offset": 120,
      "end_offset": 180,
      "created_at": "2026-02-14T10:00:00Z"
    }
  ],
  "notes": [
    {
      "id": "uuid",
      "content": "Important observations…",
      "section_label": "Epidemiology and Risk Factors",
      "position_offset": 150,
      "highlight_id": "uuid_or_null",
      "created_at": "2026-02-14T10:00:00Z"
    }
  ]
}
```

---

### 4.9 Create Highlight

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/syllabus/highlights/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "topic_id": "uuid",
  "highlighted_text": "Important observations for the medical textbook.",
  "start_offset": 120,
  "end_offset": 180,
  "color": "yellow"
}
```

**Success Response (201 Created):** Returns created highlight object.

---

### 4.10 Delete Highlight

| Detail | Value |
|--------|-------|
| **Method** | `DELETE` |
| **URL** | `/api/v1/syllabus/highlights/{highlight_id}/` |
| **Auth Required** | ✅ Yes |

**Success Response (204 No Content)**

---

### 4.11 Create Note

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/syllabus/notes/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "topic_id": "uuid",
  "content": "My note text here…",
  "position_offset": 150,
  "highlight_id": "uuid_or_null"
}
```

**Success Response (201 Created):** Returns created note object.

---

### 4.12 Update Note

| Detail | Value |
|--------|-------|
| **Method** | `PATCH` |
| **URL** | `/api/v1/syllabus/notes/{note_id}/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "content": "Updated note text…"
}
```

**Success Response (200 OK):** Returns updated note object.

---

### 4.13 Delete Note

| Detail | Value |
|--------|-------|
| **Method** | `DELETE` |
| **URL** | `/api/v1/syllabus/notes/{note_id}/` |
| **Auth Required** | ✅ Yes |

**Success Response (204 No Content)**

---

## 5. Reading Interface Endpoints

> **Figma Screens:** 10 (Topic Reader)

### 5.1 Get Topic Content

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/syllabus/topics/{topic_slug}/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "id": "uuid",
  "title": "Heart Failure",
  "slug": "heart-failure",
  "specialty": {
    "id": "uuid",
    "name": "Cardiovascular Disease",
    "slug": "cardiovascular-disease"
  },
  "book": {
    "id": "uuid",
    "title": "Internal Medicine Essentials",
    "slug": "internal-medicine-essentials"
  },
  "content": "<h1>Cardiovascular Disease</h1><h2>Introduction</h2><p>…</p>",
  "key_points": ["Point 1", "Point 2"],
  "is_completed": false,
  "is_bookmarked": true,
  "progress": {
    "last_read_section": "pathophysiology",
    "reading_time_seconds": 1200,
    "tasks_completed": 1,
    "estimated_tasks": 3
  },
  "test_your_knowledge": {
    "total_questions": 1,
    "answered_questions": 0
  },
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "previous_topic": { "slug": "coronary-artery-disease", "title": "Coronary Artery Disease" },
    "next_topic": { "slug": "arrhythmias", "title": "Arrhythmias" }
  }
}
```

---

### 5.2 Update Topic Progress

| Detail | Value |
|--------|-------|
| **Method** | `PATCH` |
| **URL** | `/api/v1/syllabus/topics/{topic_slug}/progress/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "is_completed": true,
  "last_read_section": "management",
  "reading_time_seconds": 300
}
```

**Success Response (200 OK):**
```json
{
  "is_completed": true,
  "last_read_section": "management",
  "reading_time_seconds": 1500,
  "tasks_completed": 2,
  "estimated_tasks": 3
}
```

---

## 6. Question Bank Endpoints

> **Figma Screens:** 14 (Main), 15-16 (Empty States), 17-22 (Quizzes), 23 (Question Interface)

### 6.1 Get Question Bank Main Page

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/question-bank/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "stats": {
    "completion": {
      "percentage": 1,
      "completed_questions": 5,
      "action_label": "Review →",
      "action_url": "/question-bank/answered/"
    },
    "average_score": {
      "percentage": 85,
      "detail": "Last 10 quizzes",
      "action_label": "Shuffle Questions →"
    },
    "custom_quizzes": {
      "completed": 0,
      "started": 1,
      "action_label": "Custom Quizzes →",
      "action_url": "/question-bank/custom-quizzes/"
    }
  },
  "question_sets": [
    {
      "id": "uuid",
      "book_title": "Internal Medicine Essentials",
      "book_slug": "internal-medicine-essentials",
      "total_questions": 215,
      "last_accessed": "2026-02-14T10:00:00Z",
      "progress_percentage": 45,
      "quick_links": {
        "flashcards": "/flashcards/?book=uuid",
        "board_basics": "/board-basics/?book=uuid"
      }
    }
  ]
}
```

---

### 6.2 Get Question Set Detail (by Book)

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/question-bank/sets/{book_slug}/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "book_title": "Internal Medicine Essentials",
  "total_questions": 136,
  "answered_questions": 3,
  "correct_percentage": 0,
  "incorrect_percentage": 0,
  "last_accessed": "2026-02-14T10:00:00Z",
  "progress_percentage": 45,
  "recently_answered": [
    {
      "id": "uuid",
      "educational_objective": "Treat critical limb ischemia.",
      "is_correct": true,
      "tags": {
        "specialty": "Cardiovascular Medicine",
        "care_type": "Ambulatory",
        "patient_demographic": "Age ≥65 y"
      },
      "is_saved": false
    }
  ]
}
```

---

### 6.3 Get Answered Questions

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/question-bank/answered/` |
| **Auth Required** | ✅ Yes |
| **Query Params** | `?page=1&specialty=uuid&status=correct|incorrect` |

**Success Response (200 OK):** Paginated list of answered question objects (same shape as `recently_answered` above).

---

### 6.4 Get Saved Questions

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/question-bank/saved/` |
| **Auth Required** | ✅ Yes |
| **Query Params** | `?page=1&specialty=uuid&status=correct|incorrect|unanswered&show_objectives=true` |

**Success Response (200 OK):** Paginated list of saved question objects with additional `answer_status` field (`correct`, `incorrect`, `unanswered`).

---

### 6.5 Toggle Save Question (Bookmark)

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/question-bank/questions/{question_id}/toggle-save/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "is_saved": true
}
```

---

### 6.6 Get Custom Quizzes

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/question-bank/custom-quizzes/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "count": 1,
  "quizzes": [
    {
      "id": "uuid",
      "title": "Quiz Name",
      "mode": "practice",
      "total_questions": 136,
      "correct_count": 0,
      "progress_percentage": 45,
      "last_accessed": "2026-02-14T10:00:00Z",
      "is_completed": false
    }
  ]
}
```

---

### 6.7 Create Custom Quiz

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/question-bank/custom-quizzes/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "title": "Cardio Review",
  "mode": "practice",
  "template": "build_your_own",
  "number_of_questions": 50,
  "content_areas": ["uuid_specialty_1", "uuid_specialty_2"],
  "answer_status": "incorrect",
  "include_saved": true,
  "advanced_filters": {
    "question_types": [],
    "care_type": [],
    "patient": []
  },
  "time_limit_per_question": null,
  "show_explanations": true
}
```

> **Template shortcuts:**
> - `"lka_practice"` → auto-sets: random questions, all specialties, 300s timer
> - `"exam_practice"` → auto-sets: 50 questions, all specialties, 90s/q timer, hide explanations
> - `"retry_incorrect"` → auto-sets: only incorrect questions, shuffled

**Success Response (201 Created):**
```json
{
  "id": "uuid",
  "title": "Cardio Review",
  "mode": "practice",
  "total_questions": 50,
  "first_question_id": "uuid"
}
```

---

### 6.8 Delete Custom Quiz

| Detail | Value |
|--------|-------|
| **Method** | `DELETE` |
| **URL** | `/api/v1/question-bank/custom-quizzes/{quiz_id}/` |
| **Auth Required** | ✅ Yes |

**Success Response (204 No Content)**

---

### 6.9 Get Question (Full Question View)

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/question-bank/questions/{question_id}/` |
| **Auth Required** | ✅ Yes |
| **Query Params** | `?quiz_session=uuid` (optional — context for quiz navigation) |

**Success Response (200 OK):**
```json
{
  "id": "uuid",
  "question_id_display": "cvqpp24023",
  "last_updated": "2025-02-01",
  "educational_objective": "Treat critical limb ischemia.",
  "tags": {
    "specialty": "Cardiovascular Medicine",
    "care_type": "Ambulatory",
    "patient_demographic": "Age ≥65 y"
  },
  "question_text": "<p>A 77-year-old man is evaluated for…</p>",
  "question_image": "https://…/images/clinical.jpg",
  "lab_values": [
    {
      "name": "Calcium",
      "value_today": "10.0 mg/dL (2.5 mmol/L)",
      "value_prior": "11.4 mg/dL (2.8 mmol/L)",
      "flag": "H",
      "ref_range": "8.5-10.5 mg/dL"
    }
  ],
  "options": [
    { "key": "A", "text": "Initiate aspirin and clopidogrel" },
    { "key": "B", "text": "Initiate vorapaxar" },
    { "key": "C", "text": "Perform invasive angiography" },
    { "key": "D", "text": "Perform magnetic resonance angiography" },
    { "key": "E", "text": "" }
  ],
  "is_saved": false,
  "timer_seconds": null,
  "user_attempt": null,
  "total_correct": 0,
  "total_incorrect": 3,
  "navigation": {
    "previous_question_id": "uuid_or_null",
    "next_question_id": "uuid_or_null",
    "current_position": 5,
    "total_in_set": 136
  }
}
```

---

### 6.10 Submit Answer

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/question-bank/questions/{question_id}/answer/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "selected_answer": "C",
  "time_spent_seconds": 21,
  "quiz_session_id": "uuid_or_null"
}
```

**Success Response (200 OK):**
```json
{
  "is_correct": false,
  "correct_answer": "B",
  "time_spent_seconds": 21,
  "peer_stats": {
    "A": 5,
    "B": 68,
    "C": 22,
    "D": 4,
    "E": 1
  },
  "explanation": "<p>Detailed explanation text with <b>Option A</b>, <b>Option B</b>…</p>",
  "key_point": "In patients with critical limb ischemia, immediate invasive angiography…",
  "references": [
    {
      "text": "Gornik HL, Aronow HD, Goodney PP, et al. 2024 ACC/AHA/AACVPR…",
      "pmid": "38743929",
      "doi": "10.1161/CIR.0000000000001251"
    }
  ],
  "related_syllabus": [
    {
      "topic_id": "uuid",
      "topic_title": "Peripheral Artery Disease",
      "section": "Interventional Therapy for Peripheral Artery Disease",
      "link": "/syllabus/topics/peripheral-artery-disease/"
    }
  ],
  "learning_plan_topic": {
    "topic_id": "uuid",
    "topic_title": "Calcium and Metabolic Bone Disorders",
    "includes": {
      "questions": 10,
      "syllabus_sections": 4,
      "learning_links": 2,
      "board_basics_topics": 7,
      "flashcards": 22
    },
    "is_in_plan": false
  },
  "total_correct": 0,
  "total_incorrect": 4
}
```

---

### 6.11 Shuffle Questions (Random Practice)

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/question-bank/shuffle/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "book_id": "uuid_or_null",
  "specialty_id": "uuid_or_null"
}
```

**Success Response (200 OK):**
```json
{
  "quiz_session_id": "uuid",
  "first_question_id": "uuid"
}
```

---

## 7. Learning Plan Endpoints

> **Figma Screens:** 24 (Empty), 25 (Topic Picker), 26 (Populated)

### 7.1 Get Learning Plan

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/learning-plan/` |
| **Auth Required** | ✅ Yes |
| **Query Params** | `?filter=specialty_slug` |

**Success Response (200 OK):**
```json
{
  "count": 4,
  "topics": [
    {
      "id": "uuid",
      "learning_plan_entry_id": "uuid",
      "title": "Abdominal and Pelvic Pain",
      "specialty_name": "Cardiovascular Medicine",
      "questions_completed": 0,
      "questions_total": 2,
      "tasks_completed": 0,
      "tasks_total": 3,
      "has_started": true,
      "added_at": "2026-02-14T10:00:00Z"
    }
  ]
}
```

---

### 7.2 Browse Available Topics (Topic Picker)

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/learning-plan/available-topics/` |
| **Auth Required** | ✅ Yes |
| **Query Params** | `?page=1&page_size=6&filter=specialty_slug` |

**Success Response (200 OK):** Paginated (33 pages × 6 topics = 195 topics):
```json
{
  "count": 195,
  "page": 1,
  "total_pages": 33,
  "results": [
    {
      "id": "uuid",
      "title": "Abdominal and Pelvic Pain",
      "specialty_name": "Cardiovascular Medicine",
      "questions_completed": 0,
      "questions_total": 2,
      "tasks_completed": 0,
      "tasks_total": 3,
      "is_in_plan": false
    }
  ]
}
```

---

### 7.3 Add Topic to Learning Plan

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/learning-plan/topics/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "topic_id": "uuid"
}
```

**Success Response (201 Created):**
```json
{
  "id": "uuid",
  "topic_id": "uuid",
  "topic_title": "Abdominal and Pelvic Pain",
  "added_at": "2026-03-01T08:00:00Z"
}
```

---

### 7.4 Remove Topic from Learning Plan

| Detail | Value |
|--------|-------|
| **Method** | `DELETE` |
| **URL** | `/api/v1/learning-plan/topics/{entry_id}/` |
| **Auth Required** | ✅ Yes |

**Success Response (204 No Content)**

---

## 8. CORE Certification Endpoints

> **Figma Screens:** 27 (Progress Page), 28 (Specialty Detail)

### 8.1 Get CORE Progress

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/core/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "badges_earned": 4,
  "badges_total": 11,
  "specialties": [
    {
      "id": "uuid",
      "number": 1,
      "name": "Cardiovascular Medicine",
      "slug": "cardiovascular-medicine",
      "badge_status": "completed",
      "progress_percentage": 100,
      "questions_answered": 136,
      "questions_correct": 120,
      "core_quiz_unlocked": true,
      "badge_earned_at": "2026-02-10T10:00:00Z"
    },
    {
      "id": "uuid",
      "number": 5,
      "name": "Hematology",
      "slug": "hematology",
      "badge_status": "in_progress",
      "progress_percentage": 45,
      "questions_answered": 61,
      "questions_correct": 40,
      "core_quiz_unlocked": false,
      "badge_earned_at": null
    }
  ]
}
```

---

### 8.2 Get CORE Specialty Detail

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/core/{specialty_slug}/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "specialty_name": "Cardiovascular Medicine",
  "total_questions": 136,
  "answered_questions": 3,
  "correct_percentage": 0,
  "incorrect_percentage": 0,
  "last_accessed": "2026-02-14T10:00:00Z",
  "progress_percentage": 45,
  "core_quiz_unlocked": false,
  "threshold_message": "Score 50% or higher on your last 30 questions to access the CORE Quiz.",
  "recently_answered": []
}
```

---

### 8.3 Start/Resume CORE Questions

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/core/{specialty_slug}/start/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "quiz_session_id": "uuid",
  "first_question_id": "uuid"
}
```

---

## 9. Board Basics Endpoints

> **Figma Screens:** 29 (Main Page)

### 9.1 Get Board Basics Main Page

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/board-basics/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "stats": {
    "overall_progress": { "percentage": 52, "detail": "450 / 870 pages" },
    "bank_average_score": { "percentage": 85, "detail": "Last 10 quizzes" },
    "study_time": { "hours": 12.5, "detail": "This week" },
    "study_streak": { "days": 7, "detail": "Keep it up!" }
  },
  "books": [
    {
      "id": "uuid",
      "title": "Internal Medicine Essentials",
      "last_topic_title": "Topic Name",
      "last_lesson_name": "Lesson Name",
      "last_accessed": "2026-02-14T10:00:00Z",
      "progress_percentage": 45,
      "quick_links": {
        "flashcards": "/flashcards/?book=uuid",
        "question_bank": "/question-bank/?book=uuid"
      }
    }
  ]
}
```

---

## 10. Flashcard Endpoints

> **Figma Screens:** 30 (Main), 31 (Question Side), 32 (Answer Side)

### 10.1 Get Flashcard Decks

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/flashcards/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "stats": {
    "overall_progress": { "percentage": 52, "detail": "450 / 870 flashcards" },
    "study_time": { "hours": 12.5, "detail": "This week" },
    "study_streak": { "days": 7, "detail": "Keep it up!" }
  },
  "decks": [
    {
      "id": "uuid",
      "book_title": "Internal Medicine Essentials",
      "book_slug": "internal-medicine-essentials",
      "total_flashcards": 215,
      "reviewed_flashcards": 100,
      "progress_percentage": 45,
      "last_accessed": "2026-02-14T10:00:00Z"
    }
  ]
}
```

---

### 10.2 Get Flashcard (by Position in Deck)

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/flashcards/decks/{book_slug}/{position}/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "id": "uuid",
  "position": 2,
  "total_in_deck": 215,
  "front_text": "Severe pulmonary hypertension with cardiac shunt reversal (right-to-left shunting)",
  "back_text": "Eisenmenger syndrome",
  "related_topic": {
    "id": "uuid",
    "title": "Pulmonary Hypertension",
    "slug": "pulmonary-hypertension",
    "link": "/syllabus/topics/pulmonary-hypertension/"
  },
  "is_reviewed": false,
  "navigation": {
    "previous_position": 1,
    "next_position": 3,
    "has_previous": true,
    "has_next": true
  }
}
```

---

### 10.3 Mark Flashcard as Reviewed

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/flashcards/{flashcard_id}/review/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "confidence": 1
}
```

> **Confidence values:** `0` = Not Reviewed, `1` = Viewed, `2` = Somewhat, `3` = Confident, `4` = Very Confident  
> Figma only shows reveal/next pattern, so `1` (Viewed) is the primary value.

**Success Response (200 OK):**
```json
{
  "flashcard_id": "uuid",
  "confidence": 1,
  "times_reviewed": 3,
  "last_reviewed_at": "2026-03-01T08:00:00Z"
}
```

---

## 11. CME/MOC/CPD Endpoints

> **Figma Screens:** 33 (Main Page)

### 11.1 Get CME Dashboard

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/cme/` |
| **Auth Required** | ✅ Yes |
| **Query Params** | `?year=2026` |

**Success Response (200 OK):**
```json
{
  "current_year": 2026,
  "credits_claimed": 0,
  "credits_ready_to_claim": 0.5,
  "credits_max_per_year": 300,
  "credit_window": "December 31, 2025 – December 30, 2026",
  "earning_rule": "0.25 AMA PRA Category 1 Credits™ per question at ≥50% correct",
  "activity_number": "00017040",
  "submissions": [],
  "accreditation_info": {
    "ama": { "name": "AMA PRA Category 1 Credits™", "max": 300 },
    "abim_moc": { "name": "ABIM Maintenance of Certification", "equivalent": true },
    "canada_rc": { "name": "Royal College of Physicians & Surgeons of Canada", "max_hours": 300 },
    "qatar_qchp": { "name": "Qatar Council for Healthcare Practitioners", "section": 3 },
    "australia_racp": { "name": "Royal Australasian College of Physicians", "category": "MyCPD Category 1" }
  }
}
```

---

### 11.2 Claim Credits

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/cme/claim/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "accreditation_body": "ama",
  "credit_year": 2026
}
```

**Success Response (201 Created):**
```json
{
  "id": "uuid",
  "credits_claimed": 0.5,
  "accreditation_body": "ama",
  "accreditation_body_display": "AMA PRA Category 1 Credits™",
  "credit_year": 2026,
  "status": "pending",
  "submitted_at": "2026-03-01T08:00:00Z"
}
```

---

### 11.3 Get Submission History

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/cme/submissions/` |
| **Auth Required** | ✅ Yes |
| **Query Params** | `?year=2026` |

**Success Response (200 OK):**
```json
{
  "count": 2,
  "submissions": [
    {
      "id": "uuid",
      "credits_claimed": 0.5,
      "accreditation_body": "ama",
      "accreditation_body_display": "AMA PRA Category 1 Credits™",
      "credit_year": 2026,
      "status": "confirmed",
      "submitted_at": "2026-02-15T10:00:00Z"
    }
  ]
}
```

---

## 12. User Profile & Preferences Endpoints

> ⚠️ **Note:** Settings/Profile page is NOT yet designed in Figma. These endpoints are inferred from the models and header UI elements.

### 12.1 Get Current User Profile

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/users/me/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "Alex",
  "last_name": "Johnson",
  "profile_picture": "https://…/profiles/photo.jpg",
  "role": "student",
  "theme": "light",
  "font_size": "medium",
  "email_notifications": true,
  "current_study_streak": 7,
  "longest_study_streak": 14,
  "last_study_date": "2026-03-01",
  "purchased_books_count": 3,
  "created_at": "2026-01-15T10:00:00Z"
}
```

---

### 12.2 Update User Profile

| Detail | Value |
|--------|-------|
| **Method** | `PATCH` |
| **URL** | `/api/v1/users/me/` |
| **Auth Required** | ✅ Yes |

**Request Body (all fields optional):**
```json
{
  "first_name": "Alex",
  "last_name": "Johnson",
  "theme": "dark",
  "font_size": "large",
  "email_notifications": false
}
```

**Success Response (200 OK):** Returns updated user profile object.

---

### 12.3 Change Password

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/users/me/change-password/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "current_password": "OldP@ssw0rd!",
  "new_password": "NewP@ssw0rd!",
  "new_password_confirm": "NewP@ssw0rd!"
}
```

**Success Response (200 OK):**
```json
{
  "detail": "Password changed successfully."
}
```

---

### 12.4 Record Study Session

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/users/me/study-sessions/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "session_type": "reading",
  "duration_seconds": 1800,
  "book_id": "uuid_or_null",
  "specialty_id": "uuid_or_null",
  "topic_id": "uuid_or_null",
  "started_at": "2026-03-01T08:00:00Z",
  "ended_at": "2026-03-01T08:30:00Z"
}
```

> **Session types:** `reading`, `quiz`, `flashcard`, `board_basics`, `core`

**Success Response (201 Created):**
```json
{
  "id": "uuid",
  "session_type": "reading",
  "duration_seconds": 1800,
  "started_at": "2026-03-01T08:00:00Z"
}
```

---

## 13. Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-03-01 | 1.0 | Initial draft — all 33 Figma screens covered |

---

## Endpoint Summary Table

| # | Module | Method | Endpoint | Figma Screen |
|---|--------|--------|----------|--------------|
| 1 | Auth | POST | `/auth/register/` | 1 |
| 2 | Auth | POST | `/auth/login/` | 1 |
| 3 | Auth | POST | `/auth/token/refresh/` | — |
| 4 | Auth | POST | `/auth/logout/` | — |
| 5 | Auth | POST | `/auth/password/reset/` | 2 |
| 6 | Auth | POST | `/auth/password/reset/confirm/` | 3, 4 |
| 7 | Dashboard | GET | `/dashboard/` | 5 |
| 8 | Syllabus | GET | `/syllabus/my-books/` | 6 |
| 9 | Syllabus | GET | `/syllabus/store/` | 7 |
| 10 | Syllabus | GET | `/syllabus/books/{slug}/` | 6 |
| 11 | Syllabus | GET | `/syllabus/bookmarks/` | 8, 11 |
| 12 | Syllabus | POST | `/syllabus/bookmarks/` | 10 |
| 13 | Syllabus | DELETE | `/syllabus/bookmarks/{id}/` | 11 |
| 14 | Syllabus | GET | `/syllabus/notes-highlights/` | 9, 12 |
| 15 | Syllabus | GET | `/syllabus/notes-highlights/{topic_id}/` | 13 |
| 16 | Syllabus | POST | `/syllabus/highlights/` | 10 |
| 17 | Syllabus | DELETE | `/syllabus/highlights/{id}/` | 13 |
| 18 | Syllabus | POST | `/syllabus/notes/` | 10 |
| 19 | Syllabus | PATCH | `/syllabus/notes/{id}/` | 13 |
| 20 | Syllabus | DELETE | `/syllabus/notes/{id}/` | 13 |
| 21 | Reading | GET | `/syllabus/topics/{slug}/` | 10 |
| 22 | Reading | PATCH | `/syllabus/topics/{slug}/progress/` | 10 |
| 23 | Q-Bank | GET | `/question-bank/` | 14 |
| 24 | Q-Bank | GET | `/question-bank/sets/{slug}/` | 18 |
| 25 | Q-Bank | GET | `/question-bank/answered/` | 15, 19 |
| 26 | Q-Bank | GET | `/question-bank/saved/` | 16, 20 |
| 27 | Q-Bank | POST | `/question-bank/questions/{id}/toggle-save/` | 19, 20, 23 |
| 28 | Q-Bank | GET | `/question-bank/custom-quizzes/` | 17, 22 |
| 29 | Q-Bank | POST | `/question-bank/custom-quizzes/` | 21 |
| 30 | Q-Bank | DELETE | `/question-bank/custom-quizzes/{id}/` | 22 |
| 31 | Q-Bank | GET | `/question-bank/questions/{id}/` | 23 |
| 32 | Q-Bank | POST | `/question-bank/questions/{id}/answer/` | 23 |
| 33 | Q-Bank | POST | `/question-bank/shuffle/` | 14 |
| 34 | L-Plan | GET | `/learning-plan/` | 24, 26 |
| 35 | L-Plan | GET | `/learning-plan/available-topics/` | 25 |
| 36 | L-Plan | POST | `/learning-plan/topics/` | 25 |
| 37 | L-Plan | DELETE | `/learning-plan/topics/{id}/` | 26 |
| 38 | CORE | GET | `/core/` | 27 |
| 39 | CORE | GET | `/core/{slug}/` | 28 |
| 40 | CORE | POST | `/core/{slug}/start/` | 28 |
| 41 | Board | GET | `/board-basics/` | 29 |
| 42 | Flash | GET | `/flashcards/` | 30 |
| 43 | Flash | GET | `/flashcards/decks/{slug}/{pos}/` | 31, 32 |
| 44 | Flash | POST | `/flashcards/{id}/review/` | 31, 32 |
| 45 | CME | GET | `/cme/` | 33 |
| 46 | CME | POST | `/cme/claim/` | 33 |
| 47 | CME | GET | `/cme/submissions/` | 33 |
| 48 | Profile | GET | `/users/me/` | — |
| 49 | Profile | PATCH | `/users/me/` | — |
| 50 | Profile | POST | `/users/me/change-password/` | — |
| 51 | Profile | POST | `/users/me/study-sessions/` | — |

**Total: 51 endpoints**
