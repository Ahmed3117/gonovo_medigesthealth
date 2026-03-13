# MEDIGEST Platform — Student API Endpoints Specification

> **Version:** 2.0  
> **Last Updated:** 2026-03-11  
> **Status:** ✅ Verified — All endpoints tested  
> **Based on:** Figma Designs (37 screens) + Shopify Integration PDF + V2 Workflow  

---

## Table of Contents

1. [General Info](#1-general-info)
2. [Authentication](#2-authentication-endpoints)
3. [Dashboard](#3-dashboard-endpoints)
4. [Syllabus & Store](#4-syllabus--store-endpoints)
5. [Reading Interface (PDF-Based)](#5-reading-interface-endpoints)
6. [Question Bank](#6-question-bank-endpoints)
7. [Learning Plan](#7-learning-plan-endpoints)
8. [CORE Certification](#8-core-certification-endpoints)
9. [Board Basics](#9-board-basics-endpoints)
10. [Flashcards](#10-flashcard-endpoints)
11. [CME/MOC/CPD](#11-cmemoccpd-endpoints)
12. [Certificates](#12-certificate-endpoints)
13. [User Profile & Preferences](#13-user-profile--preferences-endpoints)
14. [Webhooks](#14-webhook-endpoints)
15. [Changelog](#15-changelog)

---

## 1. General Info

### Base URL
```
https://online.medigesthealth.com/api/v1/
```

### Authentication
All endpoints (except Auth and Webhooks) require a Bearer token in the header:
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
  "detail": "Error description string"
}
```

### Pagination Format (used in list endpoints)
```json
{
  "count": 195,
  "next": "https://…/api/v1/…/?page=2",
  "previous": null,
  "results": []
}
```

---

## 2. Authentication Endpoints

> **Figma Screens:** 1 (Login), 2 (Forgot Password), 3 (Reset Confirmation)

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
  "password": "SecureP@ssw0rd!"
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

### 2.5 Request Password Reset (OTP)

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
  "detail": "If user@example.com is registered, a password reset code has been sent."
}
```

> ⚠️ Always returns 200 even if email doesn't exist (security best practice). Sends a 6-digit OTP code via email.

---

### 2.6 Confirm Password Reset (OTP)

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/auth/password/reset/confirm/` |
| **Auth Required** | ❌ No |

**Request Body:**
```json
{
  "otp": "123456",
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

> **Figma Screens:** 4-5 (Dashboard Home)

### 3.1 Get Dashboard Data

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/dashboard/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
  "user": {
    "first_name": "Alex",
    "last_name": "Sam"
  },
  "stats": {
    "overall_progress": {
      "percentage": 33,
      "detail": "100 / 300 pages"
    },
    "bank_average_score": {
      "percentage": 88,
      "detail": "Last 10 quizzes"
    },
    "study_time": {
      "hours": 2.7,
      "detail": "This week"
    },
    "study_streak": {
      "days": 7,
      "detail": "Keep it up!"
    }
  },
  "continue_learning": [
    {
      "topic_slug": "evaluation-of-lipid-levels",
      "topic_title": "Evaluation of Lipid Levels",
      "book_title": "Internal Medicine Essentials",
      "progress_percentage": 45,
      "url": "/syllabus/topics/evaluation-of-lipid-levels/"
    }
  ],
  "quick_actions": [
    {
      "label": "Continue Reading",
      "type": "reading",
      "url": "/syllabus/topics/evaluation-of-lipid-levels/",
      "resume": {
        "topic_slug": "evaluation-of-lipid-levels",
        "topic_title": "Evaluation of Lipid Levels",
        "section": "introduction",
        "last_page_read": 15
      }
    },
    {
      "label": "Practice Questions",
      "type": "quiz",
      "url": "/question-bank/",
      "resume": null
    },
    {
      "label": "Review Flashcards",
      "type": "flashcard",
      "url": "/flashcards/decks/hematology-and-oncology/1/",
      "resume": {
        "book_slug": "hematology-and-oncology",
        "book_title": "Hematology and Oncology"
      }
    }
  ],
  "todays_goals": {
    "reading": {
      "target_minutes": 60,
      "completed_minutes": 25
    },
    "flashcards": {
      "target": 60,
      "completed": 12
    },
    "questions": {
      "target": 20,
      "completed": 8
    }
  },
  "recent_activity": [
    {
      "id": "uuid",
      "type": "reading",
      "title": "Completed Heart Failure topic",
      "description": "Internal Medicine Essentials",
      "reference_id": "uuid_or_null",
      "created_at": "2026-03-10T10:00:00Z"
    }
  ]
}
```

> **📌 Key design notes:**
> - `stats.overall_progress.detail` shows **pages** (e.g., "100 / 300 pages") when books have PDF page data. Falls back to "X / Y topics" if no page data exists.
> - `todays_goals` targets are read from the user's **Settings > Preferences** (`daily_reading_goal_minutes`, `daily_flashcard_goal`, `daily_questions_goal`).
> - `quick_actions[].resume.last_page_read` tells the frontend which PDF page to open when resuming reading.

---

## 4. Syllabus & Store Endpoints

> **Figma Screens:** 6 (My Books), 7-8 (Book Cards), 11 (Store)

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
    "overall_progress": { "percentage": 33, "detail": "100 / 300 pages" },
    "bank_average_score": { "percentage": 88, "detail": "Last 10 quizzes" },
    "study_time": { "hours": 2.7, "detail": "This week" },
    "study_streak": { "days": 7, "detail": "Keep it up!" }
  },
  "books": [
    {
      "id": "uuid",
      "title": "Cardiovascular Medicine",
      "slug": "cardiovascular-medicine",
      "cover_image": "https://…/covers/cv.jpg",
      "has_pdf": true,
      "total_pages": 300,
      "estimated_pages": 300,
      "progress_percentage": 45,
      "specialty_count": 3,
      "topic_count": 8,
      "last_accessed": "2026-03-10T10:00:00Z"
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

**Success Response (200 OK):** Paginated list:
```json
[
  {
    "id": "uuid",
    "title": "Nephrology",
    "slug": "nephrology",
    "cover_image": "https://…/covers/neph.jpg",
    "description": "Comprehensive nephrology review…",
    "price": "49.99",
    "status": "active",
    "estimated_pages": 250,
    "purchase_url": "https://medigesthealth.com/products/nephrology"
  }
]
```

---

### 4.3 Get Book Detail (Specialties & Topics with Page Ranges)

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/syllabus/books/{book_slug}/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "id": "uuid",
  "title": "Cardiovascular Medicine",
  "slug": "cardiovascular-medicine",
  "cover_image": "https://…/covers/cv.jpg",
  "has_pdf": true,
  "total_pages": 300,
  "estimated_pages": 300,
  "specialties": [
    {
      "id": "uuid",
      "name": "Dyslipidemia",
      "slug": "dyslipidemia",
      "icon": "https://…/icons/lipid.png",
      "start_page": 1,
      "end_page": 100,
      "page_count": 100,
      "progress_percentage": 60,
      "topics": [
        {
          "id": "uuid",
          "title": "Evaluation of Lipid Levels",
          "slug": "evaluation-of-lipid-levels",
          "start_page": 1,
          "end_page": 33,
          "page_count": 33,
          "is_completed": false,
          "progress_percentage": 45
        },
        {
          "id": "uuid",
          "title": "Management of Dyslipidemias",
          "slug": "management-of-dyslipidemias",
          "start_page": 34,
          "end_page": 66,
          "page_count": 33,
          "is_completed": false,
          "progress_percentage": 0
        }
      ]
    }
  ]
}
```

> **📌 PDF Architecture:** Each Specialty and Topic has `start_page` / `end_page` defining its range within the book PDF. The frontend PDF viewer should render only the pages in the selected topic's range.

---

### 4.3b Secure PDF Serving

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/syllabus/books/{book_slug}/pdf/` |
| **Auth Required** | ✅ Yes (must own book) |

Streams the book PDF through an authenticated endpoint. The raw PDF file URL is never exposed to the frontend.

**Success Response (200 OK):** Returns the PDF file as `application/pdf` with `Content-Disposition: inline`.

**Error Responses:**
| Code | Condition |
|------|-----------|
| 401 | Not authenticated |
| 403 | User does not own this book |
| 404 | Book not found or no PDF file uploaded |

> **Content Protection Headers:**
> ```
> Cache-Control: no-store, no-cache, must-revalidate, max-age=0
> Pragma: no-cache
> ```

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
      "topic": "uuid",
      "topic_title": "Evaluation of Lipid Levels",
      "page_number": 12,
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
  "topic": "uuid",
  "page_number": 12,
  "section_anchor": "epidemiology-risk-factors",
  "label": "Epidemiology and Risk Factors"
}
```

**Success Response (201 Created):** Returns created bookmark object.

---

### 4.6 Delete Bookmark

| Detail | Value |
|--------|-------|
| **Method** | `DELETE` |
| **URL** | `/api/v1/syllabus/bookmarks/{bookmark_id}/` |
| **Auth Required** | ✅ Yes |

**Success Response (204 No Content)**

---

### 4.7 Get Notes & Highlights (Grouped by Topic)

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
      "topic_title": "Evaluation of Lipid Levels",
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
  "topic_title": "Evaluation of Lipid Levels",
  "highlights": [
    {
      "id": "uuid",
      "highlighted_text": "Important observations…",
      "color": "yellow",
      "page_number": 5,
      "start_offset": 120,
      "end_offset": 180,
      "created_at": "2026-02-14T10:00:00Z"
    }
  ],
  "notes": [
    {
      "id": "uuid",
      "content": "My note text…",
      "page_number": 5,
      "position_offset": 150,
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
  "topic": "uuid",
  "highlighted_text": "Important observations for the medical textbook.",
  "page_number": 5,
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
  "topic": "uuid",
  "content": "My note text here…",
  "page_number": 8,
  "position_offset": 150
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
| **URL** | `/api/v1/syllabus/notes/{note_id}/delete/` |
| **Auth Required** | ✅ Yes |

**Success Response (204 No Content)**

---

## 5. Reading Interface Endpoints

> **Figma Screens:** 9-10 (Reading Interface, PDF Viewer)
> **Key Change:** Content is now PDF-based. `start_page` / `end_page` define the page range to render in the React PDF Viewer.

### 5.1 Get Topic Detail (PDF Page Range)

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/syllabus/topics/{topic_slug}/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "id": "uuid",
  "title": "Evaluation of Lipid Levels",
  "slug": "evaluation-of-lipid-levels",
  "start_page": 1,
  "end_page": 33,
  "page_count": 33,
  "specialty": {
    "id": "uuid",
    "name": "Dyslipidemia",
    "slug": "dyslipidemia"
  },
  "book": {
    "id": "uuid",
    "title": "Cardiovascular Medicine",
    "slug": "cardiovascular-medicine",
    "has_pdf": true,
    "total_pages": 300
  },
  "content": "<h1>…</h1><p>…</p>",
  "key_points": ["Point 1", "Point 2"],
  "is_completed": false,
  "is_bookmarked": true,
  "progress": {
    "last_read_section": "introduction",
    "last_page_read": 15,
    "reading_time_seconds": 1472,
    "tasks_completed": 1,
    "estimated_tasks": 3
  },
  "test_your_knowledge": {
    "total_questions": 5,
    "answered_questions": 2
  },
  "pagination": {
    "current_position": 1,
    "total_topics": 3,
    "previous_topic": null,
    "next_topic": {
      "slug": "management-of-dyslipidemias",
      "title": "Management of Dyslipidemias"
    }
  }
}
```

> **📌 PDF Rendering:**
> - Use `start_page` and `end_page` to restrict the React PDF viewer to this topic's pages.
> - Use `progress.last_page_read` to scroll to the user's last position.
> - The `content` field (CKEditor HTML) is **deprecated** — PDF pages are the primary content.

---

### 5.2 Update Topic Progress

| Detail | Value |
|--------|-------|
| **Method** | `PATCH` |
| **URL** | `/api/v1/syllabus/topics/{topic_slug}/progress/` |
| **Auth Required** | ✅ Yes |

**Request Body (all fields optional):**
```json
{
  "is_completed": false,
  "last_read_section": "management",
  "last_page_read": 15,
  "reading_time_seconds": 300
}
```

> **Note:** `reading_time_seconds` is **additive** — the value sent is added to the existing total.

**Success Response (200 OK):**
```json
{
  "is_completed": false,
  "last_read_section": "management",
  "last_page_read": 15,
  "reading_time_seconds": 1772,
  "tasks_completed": 1,
  "estimated_tasks": 3
}
```

---

## 6. Question Bank Endpoints

> **Figma Screens:** 13-23 (Question Bank pages)

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
      "percentage": 5,
      "completed_questions": 12
    },
    "average_score": {
      "percentage": 88,
      "detail": "Last 10 quizzes"
    },
    "custom_quizzes": {
      "completed": 2,
      "started": 1
    }
  },
  "question_sets": [
    {
      "id": "uuid",
      "book_title": "Cardiovascular Medicine",
      "book_slug": "cardiovascular-medicine",
      "total_questions": 215,
      "progress_percentage": 5
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
  "book_title": "Cardiovascular Medicine",
  "total_questions": 136,
  "answered_questions": 3,
  "correct_percentage": 67,
  "incorrect_percentage": 33,
  "progress_percentage": 2,
  "recently_answered": [
    {
      "id": "uuid",
      "educational_objective": "Treat critical limb ischemia.",
      "is_correct": true,
      "is_saved": false,
      "tags": {
        "specialty": "Cardiovascular Medicine",
        "care_type": "Ambulatory",
        "patient_demographic": "Age ≥65 y"
      }
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
| **Query Params** | `?specialty=uuid&status=correct|incorrect` |

**Success Response (200 OK):** Paginated list of question row objects (same shape as `recently_answered` above).

---

### 6.4 Get Saved Questions

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/question-bank/saved/` |
| **Auth Required** | ✅ Yes |
| **Query Params** | `?specialty=uuid` |

**Success Response (200 OK):** Paginated list of saved question row objects.

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

**Success Response (200 OK):** Paginated list:
```json
[
  {
    "id": "uuid",
    "title": "Cardio Review",
    "mode": "practice",
    "total_questions": 50,
    "correct_count": 15,
    "progress_percentage": 60,
    "last_accessed": "2026-03-10T10:00:00Z",
    "is_completed": false
  }
]
```

---

### 6.7 Create Custom Quiz

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/question-bank/custom-quizzes/create/` |
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
  "time_limit_per_question": null,
  "show_explanations": true
}
```

> **Template shortcuts:**
> - `"lka_practice"` → random questions, 300s/question timer
> - `"exam_practice"` → 50 questions, 90s/question, hide explanations
> - `"retry_incorrect"` → only previously incorrect questions, shuffled

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

### 6.9 Get Question (Full Detail)

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/question-bank/questions/{question_id}/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "id": "uuid",
  "educational_objective": "Treat critical limb ischemia.",
  "tags": {
    "specialty": "Cardiovascular Medicine",
    "care_type": "Ambulatory",
    "patient_demographic": "Age ≥65 y"
  },
  "question_text": "<p>A 77-year-old man is evaluated for…</p>",
  "question_image": "https://…/images/clinical.jpg",
  "lab_values": "Relevant lab values text…",
  "options": [
    { "key": "A", "text": "Initiate aspirin and clopidogrel" },
    { "key": "B", "text": "Initiate vorapaxar" },
    { "key": "C", "text": "Perform invasive angiography" },
    { "key": "D", "text": "Perform magnetic resonance angiography" }
  ],
  "is_saved": false,
  "user_attempt": null,
  "total_correct": 45,
  "total_incorrect": 12,
  "updated_at": "2026-02-01T00:00:00Z"
}
```

> When `user_attempt` is not null:
> ```json
> "user_attempt": {
>   "selected_answer": "C",
>   "is_correct": false,
>   "time_spent_seconds": 21,
>   "attempted_at": "2026-03-10T10:00:00Z"
> }
> ```

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
  "explanation": "<p>Detailed explanation…</p>",
  "key_point": "In patients with critical limb ischemia…",
  "references": ["Reference 1 text", "Reference 2 text"],
  "related_syllabus": [
    {
      "topic_id": "uuid",
      "topic_title": "Peripheral Artery Disease",
      "link": "/syllabus/topics/peripheral-artery-disease/"
    }
  ],
  "total_correct": 45,
  "total_incorrect": 13
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

> **Figma Screens:** 24-26 (Learning Plan pages)

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
      "topic": "uuid",
      "topic_title": "Heart Failure",
      "specialty_name": "Cardiovascular Medicine",
      "questions_completed": 1,
      "questions_total": 5,
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
| **Query Params** | `?filter=specialty_slug` |

**Success Response (200 OK):** Paginated list:
```json
[
  {
    "id": "uuid",
    "title": "Heart Failure",
    "specialty_name": "Cardiovascular Medicine",
    "is_in_plan": false
  }
]
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
  "topic": "uuid"
}
```

**Success Response (201 Created):** Returns the created learning plan entry.

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

> **Figma Screens:** 27-28 (CORE pages)

### 8.1 Get CORE Dashboard

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/core/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "overall_progress": {
    "completed_badges": 4,
    "total_badges": 11,
    "percentage": 36
  },
  "badges": [
    {
      "id": "uuid",
      "specialty_name": "Cardiovascular Medicine",
      "specialty_icon": "https://…/icons/cv.png",
      "specialty_slug": "cardiovascular-medicine",
      "badge_status": "completed",
      "questions_answered": 136,
      "questions_correct": 120,
      "progress_percentage": 100,
      "correct_percentage": 88,
      "core_quiz_unlocked": true
    },
    {
      "id": "uuid",
      "specialty_name": "Hematology",
      "specialty_icon": null,
      "specialty_slug": "hematology",
      "badge_status": "in_progress",
      "questions_answered": 61,
      "questions_correct": 40,
      "progress_percentage": 45,
      "correct_percentage": 66,
      "core_quiz_unlocked": false
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
  "specialty": {
    "id": "uuid",
    "name": "Cardiovascular Medicine",
    "icon": "https://…/icons/cv.png"
  },
  "badge_status": "in_progress",
  "questions_answered": 61,
  "questions_correct": 40,
  "last_30_correct": 18,
  "last_30_total": 30,
  "core_quiz_unlocked": false,
  "progress_percentage": 45,
  "correct_percentage": 66,
  "recently_answered": [
    {
      "id": "uuid",
      "educational_objective": "Treat critical limb ischemia.",
      "is_correct": true,
      "is_saved": false,
      "tags": {
        "specialty": "Cardiovascular Medicine",
        "care_type": "Ambulatory",
        "patient_demographic": "Age ≥65 y"
      },
      "attempted_at": "2026-03-10T10:00:00Z"
    }
  ]
}
```

> **📌 Note:** `recently_answered` mirrors the same format as Question Bank Set Detail, showing the user's most recent 10 answered questions for this CORE specialty.

---

## 9. Board Basics Endpoints

> **Figma Screen:** 29

### 9.1 Get Board Basics Main Page

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/board-basics/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "overall_progress": {
    "completed": 5,
    "total": 12,
    "percentage": 42
  },
  "specialties": [
    {
      "id": "uuid",
      "name": "Cardiovascular Medicine",
      "topics": [
        {
          "id": "uuid",
          "title": "Heart Failure",
          "slug": "heart-failure",
          "is_completed": false
        }
      ]
    }
  ]
}
```

> **Note:** Board Basics shows only topics where `is_board_basics=True`.

---

## 10. Flashcard Endpoints

> **Figma Screens:** 30-31 (Flashcard pages)

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
    "overall_progress": { "percentage": 15, "detail": "30 / 200 flashcards" },
    "bank_average_score": { "percentage": 88, "detail": "Last 10 quizzes" },
    "study_time": { "hours": 2.7, "detail": "This week" },
    "study_streak": { "days": 7, "detail": "Keep it up!" }
  },
  "decks": [
    {
      "id": "uuid",
      "book_title": "Cardiovascular Medicine",
      "book_slug": "cardiovascular-medicine",
      "total_flashcards": 215,
      "reviewed_flashcards": 100,
      "progress_percentage": 47,
      "last_accessed": "2026-03-10T10:00:00Z"
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
  "display_order": 2,
  "front_text": "Severe pulmonary hypertension with cardiac shunt reversal",
  "back_text": "Eisenmenger syndrome",
  "related_topic": {
    "id": "uuid",
    "title": "Pulmonary Hypertension",
    "slug": "pulmonary-hypertension",
    "link": "/syllabus/topics/pulmonary-hypertension/"
  },
  "is_reviewed": false,
  "total_in_deck": 215,
  "position": 2,
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

**Success Response (200 OK):**
```json
{
  "flashcard_id": "uuid",
  "confidence": 1,
  "times_reviewed": 3,
  "last_reviewed_at": "2026-03-10T10:00:00Z"
}
```

---

## 11. CME/MOC/CPD Endpoints

> **Figma Screens:** 32-33 (CME pages)

### 11.1 Get CME Dashboard

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/cme/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):**
```json
{
  "earned_credits": 2.5,
  "yearly_cap": 300,
  "credit_year": 2026,
  "credits_by_type": {
    "self_assessment": 1.5,
    "quiz_completion": 1.0
  },
  "recent_credits": [
    {
      "id": "uuid",
      "activity_title": "Cardiovascular Self-Assessment",
      "activity_type": "self_assessment",
      "credits_earned": "0.25",
      "status": "earned",
      "credit_year": 2026,
      "earned_at": "2026-03-10T10:00:00Z"
    }
  ]
}
```

---

### 11.2 Get CME Credit History

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/cme/history/` |
| **Auth Required** | ✅ Yes |
| **Query Params** | `?year=2026&type=self_assessment` |

**Success Response (200 OK):** Paginated list of credit objects (same shape as `recent_credits` above).

---

### 11.3 Submit CME Credits

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/cme/submit/` |
| **Auth Required** | ✅ Yes |

**Request Body:**
```json
{
  "accreditation_body": "ama",
  "credit_ids": ["uuid_1", "uuid_2"]
}
```

**Success Response (201 Created):**
```json
{
  "id": "uuid",
  "accreditation_body": "ama",
  "credits_claimed": "2.50",
  "credit_year": 2026,
  "status": "pending",
  "submitted_at": "2026-03-10T10:00:00Z"
}
```

---

## 12. Certificate Endpoints

### 12.1 Get Certificates

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/certificates/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):** Paginated list:
```json
[
  {
    "id": "uuid",
    "certificate_type": "cme_completion",
    "title": "CME Completion Certificate — 2026",
    "description": "Awarded for completing 10 CME credits",
    "pdf_file": "https://…/certificates/cert.pdf",
    "credit_year": 2026,
    "issued_at": "2026-03-10T10:00:00Z"
  }
]
```

---

### 12.2 Download Certificate PDF

| Detail | Value |
|--------|-------|
| **Method** | `GET` |
| **URL** | `/api/v1/certificates/{cert_id}/download/` |
| **Auth Required** | ✅ Yes |

**Success Response (200 OK):** Returns the PDF file as `application/pdf` attachment.

---

## 13. User Profile & Preferences Endpoints

> **Figma Screens:** 35-37 (Settings — Profile, Security, Preferences tabs)

### 13.1 Get Current User Profile

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
  "push_notifications": true,
  "weekly_reports": true,
  "study_reminders": true,
  "daily_reading_goal_minutes": 60,
  "daily_flashcard_goal": 60,
  "daily_questions_goal": 20,
  "current_study_streak": 7,
  "longest_study_streak": 14,
  "last_study_date": "2026-03-10",
  "purchased_books_count": 3,
  "created_at": "2026-01-15T10:00:00Z"
}
```

---

### 13.2 Update User Profile & Preferences

| Detail | Value |
|--------|-------|
| **Method** | `PATCH` |
| **URL** | `/api/v1/users/me/` |
| **Auth Required** | ✅ Yes |
| **Content-Type** | `multipart/form-data` (for photo upload) or `application/json` |

**Request Body (all fields optional):**
```json
{
  "first_name": "Alex",
  "last_name": "Johnson",
  "profile_picture": "(file upload)",
  "theme": "dark",
  "font_size": "large",
  "email_notifications": true,
  "push_notifications": false,
  "weekly_reports": true,
  "study_reminders": false,
  "daily_reading_goal_minutes": 45,
  "daily_flashcard_goal": 30,
  "daily_questions_goal": 15
}
```

> **Figma mapping:**
> - **Profile tab**: `first_name`, `last_name`, `profile_picture`, notification toggles
> - **Preferences tab**: `daily_reading_goal_minutes`, `daily_flashcard_goal`, `daily_questions_goal`, `font_size`, `theme`

**Success Response (200 OK):** Returns the full updated user profile object.

---

### 13.3 Change Password

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/users/me/change-password/` |
| **Auth Required** | ✅ Yes |

> **Figma:** Settings > Security tab

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

### 13.4 Delete Account

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/users/me/delete-account/` |
| **Auth Required** | ✅ Yes |

> **Figma:** Settings > Danger Zone

**Request Body:**
```json
{
  "password": "CurrentP@ssw0rd!"
}
```

**Success Response (200 OK):**
```json
{
  "detail": "Your account has been permanently deleted."
}
```

**Error Responses:**
| Code | Condition |
|------|-----------|
| 400 | Password not provided or incorrect |

> **Note:** The account is soft-deleted (`is_active = False`) for GDPR data retention. The user is immediately logged out and cannot re-authenticate.

---

### 13.5 Record Study Session

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
  "book": "uuid_or_null",
  "specialty": "uuid_or_null",
  "topic": "uuid_or_null",
  "started_at": "2026-03-10T08:00:00Z",
  "ended_at": "2026-03-10T08:30:00Z"
}
```

> **Session types:** `reading`, `quiz`, `flashcard`, `board_basics`, `core`

**Success Response (201 Created):**
```json
{
  "id": "uuid",
  "session_type": "reading",
  "duration_seconds": 1800,
  "book": "uuid",
  "specialty": null,
  "topic": null,
  "started_at": "2026-03-10T08:00:00Z",
  "ended_at": "2026-03-10T08:30:00Z"
}
```

---

## 14. Webhook Endpoints

### 14.1 Purchase Webhook (Shopify)

| Detail | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `/api/v1/webhooks/purchase/` |
| **Auth Required** | ❌ No (HMAC signature verified) |

**Request Headers:**
```
X-Webhook-Signature: <HMAC-SHA256 hex digest>
```

**Request Body (from Shopify):**
```json
{
  "order_id": "shopify_order_12345",
  "customer_email": "buyer@example.com",
  "customer_first_name": "John",
  "customer_last_name": "Doe",
  "product_ids": ["product_001", "product_002"]
}
```

**Success Response (200 OK):**
```json
{
  "status": "processed",
  "user_created": true,
  "books_granted": 2
}
```

> **Backend Logic:**
> 1. Verify HMAC-SHA256 signature
> 2. Create user if email doesn't exist
> 3. Grant book access for each `product_id` mapped to a Book
> 4. Log the webhook event

---

## 15. Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-03-01 | 1.0 | Initial draft — 33 Figma screens covered |
| 2026-03-11 | 2.0 | **Major update:** PDF-based book architecture (start_page/end_page on specialties & topics), new user preference fields (push_notifications, weekly_reports, study_reminders, daily goals), page_number on bookmarks/highlights/notes, last_page_read tracking, dashboard goals read from user preferences + flashcard goal added, pages-based overall progress, OTP-based password reset, webhook endpoint documented, certificates endpoint documented |

---

## Endpoint Summary Table

| # | Module | Method | Endpoint | Figma Screen |
|---|--------|--------|----------|--------------|
| 1 | Auth | POST | `/auth/register/` | 1 |
| 2 | Auth | POST | `/auth/login/` | 1 |
| 3 | Auth | POST | `/auth/token/refresh/` | — |
| 4 | Auth | POST | `/auth/logout/` | — |
| 5 | Auth | POST | `/auth/password/reset/` | 2 |
| 6 | Auth | POST | `/auth/password/reset/confirm/` | 3 |
| 7 | Dashboard | GET | `/dashboard/` | 4, 5 |
| 8 | Syllabus | GET | `/syllabus/my-books/` | 6 |
| 9 | Syllabus | GET | `/syllabus/store/` | 8, 11 |
| 10 | Syllabus | GET | `/syllabus/books/{slug}/` | 7 |
| 11 | Syllabus | GET | `/syllabus/books/{slug}/pdf/` | 10 |
| 12 | Syllabus | GET | `/syllabus/bookmarks/` | 9 |
| 13 | Syllabus | POST | `/syllabus/bookmarks/` | 10 |
| 14 | Syllabus | DELETE | `/syllabus/bookmarks/{id}/` | — |
| 15 | Syllabus | GET | `/syllabus/notes-highlights/` | 9 |
| 16 | Syllabus | GET | `/syllabus/notes-highlights/{topic_id}/` | 9 |
| 17 | Syllabus | POST | `/syllabus/highlights/` | 10 |
| 18 | Syllabus | DELETE | `/syllabus/highlights/{id}/` | — |
| 19 | Syllabus | POST | `/syllabus/notes/` | 10 |
| 20 | Syllabus | PATCH | `/syllabus/notes/{id}/` | — |
| 21 | Syllabus | DELETE | `/syllabus/notes/{id}/delete/` | — |
| 22 | Reading | GET | `/syllabus/topics/{slug}/` | 9, 10 |
| 23 | Reading | PATCH | `/syllabus/topics/{slug}/progress/` | 10 |
| 24 | Q-Bank | GET | `/question-bank/` | 13 |
| 25 | Q-Bank | GET | `/question-bank/sets/{slug}/` | 17, 21, 22 |
| 26 | Q-Bank | GET | `/question-bank/answered/` | 14, 18 |
| 27 | Q-Bank | GET | `/question-bank/saved/` | 15, 19 |
| 28 | Q-Bank | POST | `/question-bank/questions/{id}/toggle-save/` | 19 |
| 29 | Q-Bank | GET | `/question-bank/custom-quizzes/` | 16, 23 |
| 30 | Q-Bank | POST | `/question-bank/custom-quizzes/create/` | 20 |
| 31 | Q-Bank | DELETE | `/question-bank/custom-quizzes/{id}/` | 23 |
| 32 | Q-Bank | GET | `/question-bank/questions/{id}/` | — |
| 33 | Q-Bank | POST | `/question-bank/questions/{id}/answer/` | — |
| 34 | Q-Bank | POST | `/question-bank/shuffle/` | 13 |
| 35 | L-Plan | GET | `/learning-plan/` | 24, 26 |
| 36 | L-Plan | GET | `/learning-plan/available-topics/` | 25 |
| 37 | L-Plan | POST | `/learning-plan/topics/` | 25 |
| 38 | L-Plan | DELETE | `/learning-plan/topics/{id}/` | 26 |
| 39 | CORE | GET | `/core/` | 27 |
| 40 | CORE | GET | `/core/{slug}/` | 28 |
| 41 | Board | GET | `/board-basics/` | 29 |
| 42 | Flash | GET | `/flashcards/` | 30 |
| 43 | Flash | GET | `/flashcards/decks/{slug}/{pos}/` | 30, 31 |
| 44 | Flash | POST | `/flashcards/{id}/review/` | 31 |
| 45 | CME | GET | `/cme/` | 32, 33 |
| 46 | CME | GET | `/cme/history/` | 33 |
| 47 | CME | POST | `/cme/submit/` | 33 |
| 48 | Certs | GET | `/certificates/` | — |
| 49 | Certs | GET | `/certificates/{id}/download/` | — |
| 50 | Profile | GET | `/users/me/` | 35 |
| 51 | Profile | PATCH | `/users/me/` | 35, 37 |
| 52 | Profile | POST | `/users/me/change-password/` | 36 |
| 53 | Profile | POST | `/users/me/delete-account/` | 36 |
| 54 | Profile | POST | `/users/me/study-sessions/` | — |
| 55 | Webhook | POST | `/webhooks/purchase/` | — |

**Total: 55 endpoints**
