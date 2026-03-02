# MEDIGEST Health Platform — API Documentation (Part 1)

This document provides a detailed description of the API endpoints available in the `postman_part1.json` collection. This documentation is intended for frontend developers to integrate these endpoints into the platform.

**Base URL:** `http://localhost:8000/api/v1`  
**Authentication:** JWT Bearer Token (Authorization: Header `Authorization: Bearer {{access_token}}`)

---

## 1. Authentication & Profile

These endpoints handle user sessions, profile management, and password security.

### 1.1 Login
*   **Endpoint:** `POST /auth/login/`
*   **Description:** Authenticate user credentials and receive JWT tokens.
*   **Request Body (`application/json`):**
    ```json
    {
      "email": "user@example.com",
      "password": "yourpassword"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "access": "eyJhbG...",
      "refresh": "eyJhbG...",
      "user": {
        "id": "31ea5dcb-656d-4c78-9a28-938cc470a896",
        "email": "user@example.com",
        "first_name": "Test",
        "last_name": "User",
        "profile_picture": null,
        "role": "student",
        "current_study_streak": 0,
        "longest_study_streak": 0,
        "last_study_date": null,
        "purchased_books_count": 0,
        "created_at": "2026-03-02T06:01:10Z"
      }
    }
    ```

### 1.2 Refresh Token
*   **Endpoint:** `POST /auth/token/refresh/`
*   **Description:** Obtain a new access token using a valid refresh token.
*   **Request Body (`application/json`):**
    ```json
    {
      "refresh": "eyJhbG..."
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "access": "eyJhbG..."
    }
    ```

### 1.3 Password Reset Request (OTP)
*   **Endpoint:** `POST /auth/password/reset/`
*   **Description:** Sends a 6-digit OTP code to the user's email address.
*   **Request Body (`application/json`):**
    ```json
    {
      "email": "user@example.com"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "detail": "Password reset code sent to user@example.com"
    }
    ```

### 1.4 Password Reset Confirm
*   **Endpoint:** `POST /auth/password/reset/confirm/`
*   **Description:** Finalize password reset using the emailed OTP code.
*   **Request Body (`application/json`):**
    ```json
    {
      "otp": "123456",
      "new_password": "NewSecurePass456!"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "detail": "Password has been reset successfully."
    }
    ```

### 1.5 Get Current Profile
*   **Endpoint:** `GET /users/me/`
*   **Description:** Retrieve the authenticated user's profile details.
*   **Response (200 OK):**
    ```json
    {
        "id": "31ea5dcb-656d-4c78-9a28-938cc470a896",
        "email": "user@example.com",
        "first_name": "Test",
        "last_name": "User",
        "profile_picture": "http://localhost:8000/media/profiles/user.jpg",
        "role": "student",
        "current_study_streak": 5,
        "longest_study_streak": 12,
        "last_study_date": "2026-03-02",
        "purchased_books_count": 3,
        "created_at": "..."
    }
    ```

### 1.6 Update Profile
*   **Endpoint:** `PATCH /users/me/`
*   **Description:** Update profile fields. **Supports `multipart/form-data` for profile picture upload.**
*   **Request Body (`multipart/form-data`):**
    *   `first_name` (string, optional)
    *   `last_name` (string, optional)
    *   `profile_picture` (file, optional)
*   **Response (200 OK):** Returns the updated user object (same schema as Get Profile).

### 1.7 Change Password
*   **Endpoint:** `POST /users/me/change-password/`
*   **Description:** Change password for an already authenticated session.
*   **Request Body (`application/json`):**
    ```json
    {
      "current_password": "OldPassword123!",
      "new_password": "NewSecurePass456!",
      "new_password_confirm": "NewSecurePass456!"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "detail": "Password changed successfully."
    }
    ```

---

## 2. Dashboard

### 2.1 Get Dashboard
*   **Endpoint:** `GET /dashboard/`
*   **Description:** Aggregated data for the main landing page.
*   **Response (200 OK):**
    ```json
    {
      "stats": {
        "overall_progress": { "percentage": 45, "detail": "45 / 100 topics" },
        "bank_average_score": { "percentage": 82, "detail": "Last 10 quizzes" },
        "study_time": { "hours": 4.5, "detail": "This week" },
        "study_streak": { "days": 5, "detail": "Keep going!" }
      },
      "quick_actions": [
        {
          "label": "Continue Reading",
          "type": "reading",
          "url": "/syllabus/topics/heart-failure/",
          "resume": { "topic_slug": "heart-failure", "topic_title": "Heart Failure", "section": "section-2" }
        }
      ],
      "todays_goals": {
        "reading": { "target_minutes": 30, "completed_minutes": 15 },
        "questions": { "target": 10, "completed": 4 }
      },
      "recent_activity": [
          {
              "id": "...",
              "type": "quiz",
              "title": "Completed Cardio Quiz",
              "description": "Scored 80% on 20 questions",
              "created_at": "2026-03-02T08:00:00Z"
          }
      ]
    }
    ```

---

## 3. Syllabus & Books (Reading Interface)

### 3.1 List My Books
*   **Endpoint:** `GET /syllabus/my-books/`
*   **Description:** List books owned/purchased by the user.

### 3.2 Browse Store Books
*   **Endpoint:** `GET /syllabus/store/`
*   **Description:** List books available for purchase (excluding owned ones).

### 3.3 Book Details
*   **Endpoint:** `GET /syllabus/books/{book_slug}/`
*   **Description:** Detailed info, table of contents (specialties & topics).

### 3.4 Topic Details (Reading View)
*   **Endpoint:** `GET /syllabus/topics/{topic_slug}/`
*   **Description:** Full HTML content, sections, and key points for a specific topic.

### 3.5 Update Reading Progress
*   **Endpoint:** `PATCH /syllabus/topics/{topic_slug}/progress/`
*   **Description:** Sync reading progress to the backend.
*   **Request Body:**
    ```json
    {
      "reading_time_seconds": 120,
      "last_read_section": "section-id-anchor",
      "is_completed": false
    }
    ```

### 3.6 Bookmarks
*   **List:** `GET /syllabus/bookmarks/`
*   **Create:** `POST /syllabus/bookmarks/` (Body: `{"topic": "topic-uuid", "section_anchor": "sec-1", "label": "Save for later"}`)
*   **Delete:** `DELETE /syllabus/bookmarks/{id}/`

### 3.7 Notes & Highlights
*   **List All:** `GET /syllabus/notes-highlights/`
*   **Topic Specific:** `GET /syllabus/notes-highlights/{topic_id}/`
*   **Create Highlight:** `POST /syllabus/highlights/`
    *   Body: `{"topic": "uuid", "highlighted_text": "text", "start_offset": 100, "end_offset": 130, "color": "yellow"}`
*   **Create Note:** `POST /syllabus/notes/`
    *   Body: `{"topic": "uuid", "content": "note text", "position_offset": 150}`
*   **Update Note:** `PATCH /syllabus/notes/{id}/` (Body: `{"content": "new text"}`)
*   **Delete Note:** `DELETE /syllabus/notes/{id}/delete/`

---

## 4. Learning Plan

### 4.1 Get My Plan
*   **Endpoint:** `GET /learning-plan/`
*   **Description:** Current topics added to the user's custom study plan.

### 4.2 Available Topics
*   **Endpoint:** `GET /learning-plan/available-topics/`
*   **Description:** Filtered list of topics that can be added to the plan.

### 4.3 Add/Remove Topic
*   **Add:** `POST /learning-plan/topics/` (Body: `{"topic": "topic-uuid"}`)
*   **Remove:** `DELETE /learning-plan/topics/{plan_entry_id}/`

---

## 5. CORE Certification (Badges)

### 5.1 CORE Dashboard
*   **Endpoint:** `GET /core/`
*   **Description:** Overall CORE status and list of specialties with their `specialty_slug`.
*   **Response Example (badges array):**
    ```json
    {
        "specialty_name": "Gastroenterology",
        "specialty_slug": "gastroenterology",
        "specialty_icon": "http://...",
        "badge_status": "locked",
        "progress_percentage": 0,
        "questions_answered": 0,
        "questions_correct": 0,
        "core_quiz_unlocked": false
    }
    ```

### 5.2 CORE Specialty Details
*   **Endpoint:** `GET /core/{specialty_slug}/`
*   **Description:** In-depth metrics for a specific CORE badge.

---

## 6. Board Basics

### 6.1 Browse Board Basics
*   **Endpoint:** `GET /board-basics/`
*   **Description:** List all Board Basics specialties and their topics, grouped hierarchically.
