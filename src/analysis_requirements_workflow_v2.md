# MEDIGEST Health Platform — Analysis & Requirements (V2)

> **Source of Truth** — derived exclusively from the **Figma designs (37 screens)** and the **Shopify Integration PDF**.
> Last updated: 2026-03-10

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [Shopify Integration](#2-shopify-integration)
3. [Global App Shell & Navigation](#3-global-app-shell--navigation)
4. [Module Breakdown (Screen-by-Screen)](#4-module-breakdown)
   - 4.1 Authentication
   - 4.2 Dashboard (Home)
   - 4.3 Syllabus & PDF-Based Reading
   - 4.4 Notes & Highlights
   - 4.5 Question Bank
   - 4.6 Learning Plan
   - 4.7 CORE Certification
   - 4.8 Board Basics
   - 4.9 Flashcards
   - 4.10 CME/MOC/CPD
   - 4.11 Help Center
   - 4.12 Settings
5. [PDF Book Architecture (Key Design Decision)](#5-pdf-book-architecture)
6. [Data Model](#6-data-model)
7. [Functional Requirements](#7-functional-requirements)
8. [Non-Functional Requirements](#8-non-functional-requirements)
9. [Cross-Module Links & Navigation Map](#9-cross-module-links)
10. [Identified Gaps & Clarifications Needed](#10-identified-gaps)

---

## 1. Platform Overview

**MEDIGEST** ("Where Medical Knowledge Grows") is an online medical education platform for physicians and students. Users purchase books through the Shopify e-commerce store (`medigesthealth.com`), then access content on the web app (`online.medigesthealth.com`).

**Core value proposition:**
- PDF-based medical textbooks organized by Specialty → Topic with page-range navigation
- Question Bank with clinical-scenario MCQs, peer statistics, and CME credit earning
- Flashcards with spaced repetition
- CORE Certification with 11 specialty badges
- Board Basics digest-style review module
- CME/MOC/CPD credit tracking with multi-country accreditation
- Personalized Learning Plan

---

## 2. Shopify Integration

### 2.1 Web App Access
- E-commerce store: `medigesthealth.com` (Shopify)
- Web app: `online.medigesthealth.com` (subdomain)
- A button on the Shopify store links to the web app
- DNS: Client provides IP for A-record pointing

### 2.2 Webhook Integration (Event-Based)

| Field | Detail |
|-------|--------|
| **Trigger** | `purchase completed` event from Shopify |
| **Signing Secret** | `8828edf31bf2349bde1141cc3e0d841b1560bebadd5bdab0adeb0bf214fc6094` |
| **Signature Method** | HMAC-SHA256 |
| **Payload Fields** | `order_id`, `customer.email`, `items[].product_id` |

**Backend Logic on Webhook Receipt:**
1. Verify HMAC-SHA256 signature
2. Check if `customer.email` exists in database
   - **New user** → Create account, grant book access, send welcome email with credentials
   - **Existing user** → Grant book access, send notification email
3. Log the webhook event for auditing

### 2.3 Redeem Purchases (Fail-Safe Polling)
- **Purpose**: Backup method if webhook fails
- **Mechanism**: Poll Shopify API with user email to retrieve `product_id` list
- **User-facing**: "Redeem Purchases" section in user profile/settings
- **Admin-facing**: Admin dashboard section to manually restore purchases
- Shopify store will also link to the redeem page

### 2.4 Responsibilities
| Task | Owner |
|------|-------|
| Webhook URL endpoint | Backend Dev |
| Shopify webhook config & button | Client (Shopify admin) |
| DNS A/MX records | Client |
| IP address for DNS | Backend Dev |
| Shopify API polling research | Client |

---

## 3. Global App Shell & Navigation

### 3.1 Top Bar (All Pages)
- User avatar + name + role badge ("Student")
- Global search: "Search books, chapters, questions…"
- Dark mode toggle (moon icon)
- Notification bell icon

### 3.2 Left Sidebar Navigation
Collapsible, dark navy background. Items in order:

| # | Label | Icon |
|---|-------|------|
| 1 | Home | 🏠 |
| 2 | Syllabus | 📚 |
| 3 | Question Bank | ❓ |
| 4 | Learning Plan | 📋 |
| 5 | CORE | ✅ |
| 6 | Board Basics | 📄 |
| 7 | Flashcards | 🃏 |
| 8 | CME/MOC/CPD | 🏆 |
| 9 | Help Center | ❤️ |
| — | *(separator)* | — |
| 10 | Settings | ⚙️ |
| 11 | Log out | 🚪 |

- Active item: highlighted background with left accent bar
- Sidebar shows MEDIGEST logo at top with tagline

---

## 4. Module Breakdown

### 4.1 Authentication

**Figma screens:** Pasted image.png, Pasted image (2).png, Pasted image (3).png

#### Login Page
- **Layout**: Split-screen — left side dark navy with MEDIGEST branding, right side white form
- **Left panel**: Logo, tagline "Where Medical Knowledge Grows", decorative medical illustration
- **Right panel form fields**:
  - Email Address (text input)
  - Password (password input with show/hide toggle)
  - "Remember me" checkbox
  - "Forgot Password?" link
  - **"Sign In"** button (full-width, dark)
- No sign-up option visible (accounts created via webhook or admin)

#### Forgot Password Flow
- Email input → "Send Reset Link" button
- Success state: confirmation message, "Back to Login" link

---

### 4.2 Dashboard (Home)

**Figma screens:** Pasted image (4).png, Pasted image (5).png

#### Welcome Banner
- "Welcome Back, [First Name]!" heading
- Motivational subtitle

#### 4-Stat Summary Bar
Consistent pattern used across multiple modules:

| Stat | Example | Subtext |
|------|---------|---------|
| Overall Progress | 52% | "450 / 870 pages" |
| Bank Average Score | 85% | "Last 10 quizzes" |
| Study Time | 12.5h | "This week" |
| Study Streak | 7 days | "Keep it up!" |

#### Quick Actions Section
Cards/buttons for fast navigation to key features

#### Today's Goals
- Daily reading time goal (e.g., 60 min)
- Daily flashcard review goal (e.g., 60 cards)
- Daily practice questions goal (e.g., 20 questions)
- Progress bars for each goal

#### Module Previews
- Board Basics preview card
- CORE progress preview card

---

### 4.3 Syllabus & PDF-Based Reading

**Figma screens:** Pasted image (6).png through Pasted image (12).png

#### 4.3.1 Syllabus Landing Page

**Two tabs:**

##### "My Books" Tab
- Grid of book cards (2 per row) for purchased books
- Each card shows:
  - Book cover image (3D render)
  - Book title (e.g., "Internal Medicine Essentials")
  - Topic count + Last accessed date
  - Progress bar with percentage
  - **Quick links**: "Flashcards →", "Board Basics →" (cross-module navigation)
  - **"Continue"** button

##### "Store" Tab
- Same grid layout for books not yet purchased
- Cards show: cover, title, description
- **"Buy Now"** button → redirects to Shopify store
- Price displayed on card

#### 4.3.2 PDF Book Architecture (NEW — Key Design Decision)

> **Critical Update**: Instead of CKEditor HTML content, books are uploaded as **whole PDF files**. The admin defines page ranges for specialties and topics.

**Hierarchy:**
```
Book (PDF file)
├── Specialty 1 (pages 1-50)
│   ├── Topic A (pages 1-15)
│   ├── Topic B (pages 16-30)
│   └── Topic C (pages 31-50)
├── Specialty 2 (pages 51-120)
│   ├── Topic D (pages 51-75)
│   └── Topic E (pages 76-120)
└── ...
```

**Admin workflow:**
1. Upload the full book PDF
2. Create specialties, assign page ranges (start_page, end_page)
3. Create topics under each specialty, assign page ranges within the specialty's range

**Frontend rendering:**
- Use a **React PDF Viewer** library (e.g., `react-pdf`, `@react-pdf-viewer/core`)
- When user clicks a topic, render only the pages in that topic's range
- Prevent full-document download (content protection)

#### 4.3.3 Reading Interface

**Left Sidebar — Specialty Accordion:**
- Collapsible specialty sections
- Each specialty shows: name, progress bar, percentage
- Under each specialty: list of topic links
- Clicking a topic loads its page range in the PDF viewer

**Main Content Area — PDF Viewer:**
- Displays the PDF pages for the selected topic's range
- **Inline toolbar** (floating or fixed):
  - Font size controls (A-, A, A+)
  - Bookmark toggle
  - Highlight tool
  - Note/annotation tool
- **Embedded quiz widget**: Inline MCQ appears within reading flow
- **Topic pagination**: "← Previous Topic" / "Next Topic →" navigation at bottom

**No right-side panel** — Notes/Highlights are accessed via dedicated page

---

### 4.4 Notes & Highlights

**Figma screens:** Pasted image (9).png (related views)

#### Two-Level Navigation
1. **Level 1**: Select a book from "My Books"
2. **Level 2**: View notes/highlights organized by specialty → topic

#### Features
- View all saved notes and highlights per topic
- Notes show: text snippet, user annotation, date created
- Highlights show: highlighted text, color, page reference
- Filter by specialty or topic
- Access from: Syllabus card "Notes & Highlights" quick link, Board Basics "Notes & Highlights" button

---

### 4.5 Question Bank

**Figma screens:** Pasted image (13).png through Pasted image (23).png

#### 4.5.1 Question Bank Landing Page

**3-Stat Summary Bar:**

| Stat | Example | Action Link |
|------|---------|-------------|
| Completion | <1% Complete (20%) | "Review →" |
| Bank Average Score | 85% | "Shuffle Questions →" |
| Custom Quizzes | 0 Completed | "Custom Quizzes →" |

**Question Sets Grid:**
- Cards per book (2 per row)
- Each card: Book title, question count, last accessed date, progress bar, percentage
- Quick links: "Flashcards →", "Board Basics →"
- "Continue" button
- **"Saved Questions"** button (top-right) → dedicated page

#### 4.5.2 Book Question Set Detail Page
- Breadcrumb: Question Bank > [Book Name]
- Progress: "3 of 136 Questions Answered"
- Stats: "0% Correct · 0% Incorrect · Last accessed: [date]"
- Progress bar with percentage
- **"Resume Answer Questions"** button
- **"Your Recently Answered Questions"** section:
  - List of questions with: ✅/❌ icon, question title, tags (Specialty, Care type, Patient age), bookmark toggle

#### 4.5.3 Answered Questions Page
- Breadcrumb: Question Bank > Answered Questions
- **Empty state**: "No answered questions yet" with motivational text + "Take a Quiz →" button
- **Populated state**: List of answered questions with same card format + bookmark icons

#### 4.5.4 Saved Questions Page
- Breadcrumb: Question Bank > Saved Questions
- **Empty state**: "No saved questions yet" with instructions on how to save
- **Populated state**:
  - Banner: "You can create a customized quiz from your saved questions" + "Create New Quiz" button
  - "Saved Question (N)" count with Filter button
  - Checkbox: "Show educational objectives and tags for unanswered questions"
  - Question cards: ✅/❌/unanswered icon, title, tags, bookmark toggle
  - Three question states: Correct (green ✅), Incorrect (red ❌), Unanswered (gray arrow)

#### 4.5.5 Custom Quizzes Page
- Breadcrumb: Question Bank > Custom Quizzes
- **Empty state**: "No custom quizzes yet" with instructions
- **Populated state**: Quiz cards with name, question count, stats, progress bar, "Resume" button
- **"+ Create New Quiz"** button

#### 4.5.6 New Custom Quiz Builder
- Breadcrumb: Question Bank > Custom Quizzes > New Custom Quiz

**Section 1 — Quiz Template:**
| Template | Description |
|----------|-------------|
| Build your own | Custom selection from question bank |
| LKA Practice | Random questions, 5-min countdown |
| Exam Practice | 60 random questions, 2-hour limit |
| Retry incorrect | Shuffle previously incorrect answers |

**Section 2 — Quiz Questions:**
- Number of Questions: slider (1-100+), default 50
- Content areas: multi-select dropdown ("All Selected")
- Answer status: dropdown (Incorrect, Correct, Unanswered, All)
- ☑ "Include saved questions (N)" checkbox
- **Advanced Filter Options** (collapsible):
  - Question types: multi-select
  - Care type: multi-select
  - Patient: multi-select

**Section 3 — Quiz Options:**
- Quiz Name: text input (required)
- Quiz timing: radio — Untimed / Standard Board Pace (90s) / Fast Pace (60s)
- Answer and critique visibility: radio — Show / Hide
- **"Save Your Quiz"** button

---

### 4.6 Learning Plan

**Figma screens:** Pasted image (24).png through Pasted image (26).png

#### 4.6.1 Learning Plan Landing Page
- Title: "Learning Plan — Your personalized path to medical mastery"
- **"+ Add New Topic"** button (top-right)
- **Empty state**: "Ready to start your journey?" with instructions
- **Populated state**:
  - "Included Topics (N)" with Filter button
  - Topic cards (2 per row):
    - Book icon, Topic name, Specialty tag badge
    - Dual progress: "0/2 questions completed · 0/3 tasks completed"
    - ❌ remove button (top-right of card)
    - "Continue" or "Start" button

#### 4.6.2 Add New Topic Page
- Breadcrumb: Learning Plan > Add New Topic
- Title: "Add Topics"
- "N Topics" count with Filter button
- Topic cards (2 per row):
  - Book icon, Topic name, Specialty tag badge
  - Progress: "0/2 questions completed · 0/3 tasks completed"
  - ➕ add button (topics not yet in plan)
  - ❌ remove button (topics already in plan)
- **Pagination**: 1, 2, 3, 4, 5 … 33 with ← → arrows

---

### 4.7 CORE Certification

**Figma screens:** Pasted image (27).png, Pasted image (28).png

#### 4.7.1 CORE Landing Page
- Title: "Confirmation of Relevant Education (CORE)" + "4/11 Badges Earned"
- Subtitle: "Earn your CORE certificate and celebrate lifelong learning"

**CORE Progress Section:**
- Instructions: "Score 50% or higher on your last 30 questions to access the CORE Quiz"
- **11 Specialty Badge Cards** (vertical list):

| Badge # | Specialty | Status | Progress |
|---------|-----------|--------|----------|
| 1 | Cardiovascular Medicine | Completed ✅ | 100% |
| 2 | Endocrinology and Metabolism | Completed ✅ | 100% |
| 3 | Foundations of Clinical Practice | Completed ✅ | 100% |
| 4 | Gastroenterology and Hepatology | Completed ✅ | 100% |
| 5 | Hematology | In Progress 🔵 | 45% |
| 6 | Infectious Disease | Pending ⬜ | 0% |
| 7 | Interdisciplinary Medicine and Dermatology | Pending ⬜ | 0% |
| 8 | Nephrology | Pending ⬜ | 0% |
| 9 | Oncology | Pending ⬜ | 0% |
| 10 | Pulmonary and Critical Care Medicine | Pending ⬜ | 0% |
| 11 | Rheumatology | Pending ⬜ | 0% |

- Action buttons: "Review →" (completed), "Continue →" (in progress), "Start Now →" (pending)

#### 4.7.2 CORE Specialty Detail Page
- Breadcrumb: CORE > [Specialty Name]
- Instruction: "Score 50% or higher on your last 30 questions"
- Progress: "3 of 136 Questions Answered"
- Stats: "0% Correct · 0% Incorrect · Last accessed: [date]"
- Progress bar + percentage
- **"Resume Answer Questions"** button
- **"Your Recently Answered Questions"** section (same format as Question Bank)

---

### 4.8 Board Basics

**Figma screen:** Pasted image (29).png

#### Board Basics Landing Page
- Title: "Board Basics — A succinct, digest-style review to help you pass your Boards"

**4-Stat Summary Bar:**
| Stat | Value | Subtext |
|------|-------|---------|
| Overall Progress | 52% | "450 / 870 pages" |
| Bank Average Score | 85% | "Last 10 quizzes" |
| Study Time | 12.5h | "This week" |
| Study Streak | 7 days | "Keep it up!" |

**"My Books (N)"** section with **"Notes & Highlights"** button
- Book cards (2 per row): same format as Syllabus
- Each card: cover, title, "Topic Name · Lesson Name", last accessed, progress bar
- Quick links: "Flashcards →", "Question Bank →"
- "Continue" button

> **Note**: Board Basics shows the same books but filtered to topics marked `is_board_basics = True`

---

### 4.9 Flashcards

**Figma screens:** Pasted image (30).png, Pasted image (31).png

#### 4.9.1 Flashcards Landing Page
- Decks organized by book (same card grid as other modules)
- Each card: book cover, title, flashcard count, last accessed, progress bar
- "Continue" button

#### 4.9.2 Flashcard Study Interface
- Breadcrumb: Flashcards > [Book Name]
- **Large flip card** (gradient dark background):
  - **Question side**: "Question" label, question text, "Click to reveal answer"
  - **Answer side**: "Answer" label, answer text, **"Related Text →"** link, "Click to hide answer"
- **Navigation bar below card**: "← Previous" | "2/215 Flashcards" | "Next →"

> **"Related Text →"** link navigates to the relevant topic in the Syllabus reader

---

### 4.10 CME/MOC/CPD

**Figma screens:** Pasted image (32).png, Pasted image (33).png

#### CME/MOC/CPD Page
- Title: "CME/MOC/CPD — Submissions for continuing education credits"

**Credit Summary Banner:**
- "0 credits claimed" (bold) + "0.5 credits ready to claim"
- "Up to a maximum of 300 credits available from December 31 – December 30, 2026"
- "CME availability will renew on a calendar-year basis"
- Credit rate: "0.25 AMA PRA Category 1 credits™ and 0.25 MOC points per question answered (50% correct threshold)"
- **"Claim X Credits Now!"** button (teal, right-aligned)

**CME/MOC Submissions Section:**
- "No submission history yet" (empty state)
- When populated: submission history table by year

**Information Sections** (static content blocks):
1. **ACP MEDIGEST CME, MOC, and CPD Information for Physicians**
   - ACCME accreditation details, 300 AMA PRA Category 1 max
   - Calendar-year reset (Jan 1), submission deadline (Dec 31, 11:59 PM EST)
   - Non-US physicians eligible for AMA PRA Category 1

2. **How to Submit for CME/MOC** (boxed section)
   - Step-by-step instructions for claiming credits
   - Minimum: 1 of 2 questions correct (50%) per self-assessment
   - Each assessment = 0.25 AMA PRA Category 1 + 0.25 ABIM MOC point

3. **Royal College of Physicians & Surgeons of Canada: MOC Credits** (boxed)
   - Section 3 Self-Assessment, max 300 hours
   - Cross-conversion to AMA credits via ama-assn.org
   - QCHP CME/CPD Category 3 credits (Qatar)

4. **How Royal College Fellows can earn MOC credits** (boxed)
   - Email with certificate after CME submission
   - Royal College MyMOC site, ACP MEDIGEST activity #00017040

5. **Royal Australasian College of Physicians: CPD Credits** (boxed)
   - MyCPD Category 1 – Educational Activities
   - Links to MyCPD framework and handbook

---

### 4.11 Help Center

**Figma screen:** Pasted image (34).png

#### Help Center Page
- Title: "Help Center — Search our knowledge base or contact our support team"

**FAQ Section:**
- Category filter tabs: All | Reading & Textbooks | Practice Questions | Flashcards & Spaced Repetition | CME/MOC Credits | Account & …
- Accordion-style Q&A items:
  - "How do I track my CME credits?" (expanded example with answer)
  - "Can I study offline?"
  - "How does the spaced repetition algorithm work?"
  - "What's the difference between student and physician accounts?"
  - "How do I reset my password?"
  - "Can I change my study goals?"
  - "How are my quiz scores calculated?"
  - "Is my data secure?"

**Contact Support Section:**
- Email: support@medigest.com — "Get help from our support team →"
- Phone: 1-800-MEDIGEST — "Speak with a specialist →"

---

### 4.12 Settings

**Figma screens:** Pasted image (35).png, Pasted image (36).png, Pasted image (37).png

#### Settings Page — 3 Tabs

##### Tab 1: Profile
- Avatar with initials, name, "Student Account" badge
- "Change Photo" button
- **Form fields**: Full Name, Email Address
- **"Save Changes"** button
- **Notification Preferences:**
  - Email Notifications (toggle, default ON)
  - Push Notifications (toggle, default ON)
  - Weekly Progress Reports (toggle, default ON)
  - Study Reminders (toggle, default ON)
- **"Save Preferences"** button
- **Danger Zone** (red border):
  - "Permanently delete your account and all associated data"
  - "Delete Account" button (outlined, red)

##### Tab 2: Security
- **Password & Security:**
  - Current Password input
  - New Password input (with show/hide toggle)
  - **"Change Password"** button

##### Tab 3: Preferences
- **Learning Preferences:**
  - Daily Reading Time Goal (minutes): default 60
  - Daily Flashcards Review Goal: default 60
  - Daily Practice Questions Goal: default 20
  - **"Save Preferences"** button
- **Display Settings:**
  - Font Size: A- / A / A+ buttons
  - Dark Mode: toggle (default OFF)

---

## 5. PDF Book Architecture (Key Design Decision)

### 5.1 Concept

The content delivery model has shifted from **CKEditor HTML content** to **PDF-based books**. Each book is a single PDF file. The admin defines a hierarchical structure of **Specialties** and **Topics** mapped to **page ranges** within the PDF.

### 5.2 Admin Workflow

```
1. Upload full book PDF file to Book model
2. Create Specialty records:
   - Name, slug, display_order
   - start_page, end_page (within the book PDF)
3. Create Topic records under each Specialty:
   - Name, slug, display_order
   - start_page, end_page (within the specialty's page range)
4. System validates: topic ranges must fall within parent specialty range
```

### 5.3 Frontend PDF Viewer

**Library recommendation:** `@react-pdf-viewer/core` or `react-pdf`

**Behavior:**
- Load the full PDF document once (cached)
- When user selects a topic, scroll/navigate to `start_page` and restrict viewing to `start_page..end_page`
- Sidebar accordion shows specialty → topic tree with progress indicators
- Previous/Next topic navigation respects the defined ordering

### 5.4 Content Protection

- Disable right-click context menu on PDF viewer
- Disable print functionality via viewer config
- Disable text selection/copy (where library supports it)
- Do not expose raw PDF URL to frontend (serve via authenticated API endpoint)
- Consider watermarking with user email (future enhancement)

### 5.5 Model Changes Required

The existing `Book`, `Specialty`, and `Topic` models need updates:

**Book model — add:**
- `pdf_file` (FileField) — the uploaded PDF
- `total_pages` (PositiveIntegerField) — auto-detected or admin-set

**Specialty model — add:**
- `start_page` (PositiveIntegerField)
- `end_page` (PositiveIntegerField)

**Topic model — modify:**
- `content` (CKEditor5Field) → keep for backward compat but mark as deprecated
- Add `start_page` (PositiveIntegerField)
- Add `end_page` (PositiveIntegerField)
- The PDF page range becomes the primary content delivery mechanism

---

## 6. Data Model

### 6.1 Core Content Models

#### Book
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK, auto |
| product_id | CharField(100) | Maps to Shopify product ID |
| title | CharField(255) | |
| slug | SlugField(255) | Unique |
| description | CKEditor5Field | Rich text for Store display |
| cover_image | ImageField | 3D render preferred |
| **pdf_file** | **FileField** | **NEW: Full book PDF** |
| **total_pages** | **PositiveIntegerField** | **NEW: Page count** |
| price | DecimalField(8,2) | |
| status | CharField (active/coming_soon/archived) | |
| display_order | PositiveIntegerField | |
| estimated_pages | PositiveIntegerField | For progress display |
| created_at | DateTimeField | Auto |
| updated_at | DateTimeField | Auto |

#### Specialty
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| book | FK → Book | CASCADE |
| name | CharField(255) | |
| slug | SlugField(255) | Unique per book |
| icon | ImageField | |
| description | TextField | |
| display_order | PositiveIntegerField | |
| **start_page** | **PositiveIntegerField** | **NEW: PDF start page** |
| **end_page** | **PositiveIntegerField** | **NEW: PDF end page** |
| is_core_specialty | BooleanField | For CORE module |
| core_display_order | PositiveIntegerField | 1-11 |
| created_at / updated_at | DateTimeField | Auto |

#### Topic
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| specialty | FK → Specialty | CASCADE |
| title | CharField(500) | |
| slug | SlugField(500) | Unique per specialty |
| content | CKEditor5Field | **DEPRECATED: kept for compat** |
| **start_page** | **PositiveIntegerField** | **NEW: PDF start page** |
| **end_page** | **PositiveIntegerField** | **NEW: PDF end page** |
| key_points | JSONField | List of strings |
| display_order | PositiveIntegerField | |
| is_board_basics | BooleanField | Appears in Board Basics |
| created_at / updated_at | DateTimeField | Auto |

#### UserBookAccess
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | CASCADE |
| book | FK → Book | CASCADE |
| order_id | CharField(100) | From webhook |
| source | CharField (webhook/manual_admin) | |
| granted_at | DateTimeField | Auto |

### 6.2 Question Bank Models

#### Question
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| book | FK → Book | CASCADE |
| specialty | FK → Specialty | CASCADE |
| topic | FK → Topic | Nullable, CASCADE |
| vignette | TextField | Clinical scenario text |
| question_text | TextField | The actual question |
| explanation | CKEditor5Field | Critique/explanation |
| key_point | TextField | "Key Point" summary |
| reference_text | TextField | References with PMIDs |
| related_topic | FK → Topic | "Related Syllabus Content" link |
| question_type | CharField | MCQ type classification |
| care_type | CharField | Ambulatory/Hospital/etc. |
| patient_category | CharField | Age/gender filters |
| display_order | PositiveIntegerField | |
| created_at / updated_at | DateTimeField | Auto |

#### AnswerChoice
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| question | FK → Question | CASCADE |
| label | CharField(1) | A, B, C, D, E |
| text | TextField | Answer text |
| is_correct | BooleanField | |
| peer_selection_pct | DecimalField | % of users who chose this |

#### UserQuestionAttempt
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | |
| question | FK → Question | |
| selected_answer | FK → AnswerChoice | |
| is_correct | BooleanField | |
| response_time_seconds | PositiveIntegerField | Tracks speed |
| attempted_at | DateTimeField | |

#### CustomQuiz
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | |
| name | CharField(255) | |
| template_type | CharField | build_own/lka/exam/retry |
| question_count | PositiveIntegerField | |
| timing_mode | CharField | untimed/standard_90s/fast_60s |
| show_answers | BooleanField | |
| content_areas | JSONField | Selected specialties |
| answer_status_filter | CharField | incorrect/correct/unanswered/all |
| advanced_filters | JSONField | question_type, care_type, patient |
| include_saved | BooleanField | |
| created_at | DateTimeField | |

#### SavedQuestion
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | |
| question | FK → Question | |
| saved_at | DateTimeField | |

### 6.3 Flashcard Models

#### Flashcard
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| book | FK → Book | CASCADE |
| specialty | FK → Specialty | Nullable |
| topic | FK → Topic | Nullable |
| question_text | TextField | Front of card |
| answer_text | TextField | Back of card |
| related_topic | FK → Topic | "Related Text →" link |
| display_order | PositiveIntegerField | |

#### UserFlashcardProgress
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | |
| flashcard | FK → Flashcard | |
| last_reviewed | DateTimeField | |
| confidence_level | IntegerField | For spaced repetition |
| next_review_date | DateTimeField | Calculated |

### 6.4 Learning Plan Models

#### LearningPlanTopic
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | |
| topic | FK → Topic | |
| questions_completed | PositiveIntegerField | "0/2 questions" |
| questions_total | PositiveIntegerField | |
| tasks_completed | PositiveIntegerField | "0/3 tasks" |
| tasks_total | PositiveIntegerField | |
| added_at | DateTimeField | |

### 6.5 CORE Models

#### CoreBadgeProgress
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | |
| specialty | FK → Specialty | Must have is_core_specialty=True |
| questions_answered | PositiveIntegerField | |
| questions_total | PositiveIntegerField | |
| correct_count | PositiveIntegerField | |
| incorrect_count | PositiveIntegerField | |
| status | CharField | pending/in_progress/completed |
| last_accessed | DateTimeField | |
| badge_earned_at | DateTimeField | Nullable |

### 6.6 CME/MOC/CPD Models

#### CMEActivity
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | |
| credits_earned | DecimalField | 0.25 per qualifying answer |
| moc_points_earned | DecimalField | 0.25 per qualifying answer |
| activity_type | CharField | self_assessment/quiz |
| year | PositiveIntegerField | Calendar year |
| claimed_at | DateTimeField | Nullable |

#### CMESubmission
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | |
| credits_claimed | DecimalField | |
| moc_points_claimed | DecimalField | |
| submission_year | PositiveIntegerField | |
| submitted_at | DateTimeField | |
| certificate_url | URLField | Generated PDF certificate |

### 6.7 Study Tracking Models

#### ReadingProgress
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | |
| topic | FK → Topic | |
| last_page_read | PositiveIntegerField | Within topic's range |
| completed | BooleanField | |
| time_spent_minutes | PositiveIntegerField | |
| last_read_at | DateTimeField | |

#### UserNote
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | |
| topic | FK → Topic | |
| page_number | PositiveIntegerField | PDF page reference |
| note_text | TextField | User's annotation |
| highlighted_text | TextField | Selected text (if highlight) |
| note_type | CharField | note/highlight |
| color | CharField | Highlight color |
| created_at | DateTimeField | |

#### UserBookmark
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | |
| topic | FK → Topic | |
| page_number | PositiveIntegerField | |
| created_at | DateTimeField | |

#### StudyStreak
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | FK → User | |
| date | DateField | |
| reading_minutes | PositiveIntegerField | |
| questions_answered | PositiveIntegerField | |
| flashcards_reviewed | PositiveIntegerField | |

### 6.8 User Preferences Model

#### UserPreferences
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| user | OneToOne → User | |
| daily_topics_goal | PositiveIntegerField | Default 60 |
| daily_flashcard_goal | PositiveIntegerField | Default 60 |
| daily_questions_goal | PositiveIntegerField | Default 20 |
| font_size | CharField | small/medium/large |
| dark_mode | BooleanField | Default False |
| email_notifications | BooleanField | Default True |
| push_notifications | BooleanField | Default True |
| weekly_reports | BooleanField | Default True |
| study_reminders | BooleanField | Default True |

### 6.9 Integration Models

#### WebhookLog
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| order_id | CharField(100) | |
| customer_email | EmailField | |
| payload | JSONField | Raw webhook JSON |
| signature_valid | BooleanField | |
| processed | BooleanField | |
| error_message | TextField | If processing failed |
| received_at | DateTimeField | |
| processed_at | DateTimeField | Nullable |

#### FAQ
| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| category | CharField | reading/questions/flashcards/cme/account |
| question | TextField | |
| answer | TextField | |
| display_order | PositiveIntegerField | |

---

## 7. Functional Requirements

### FR-01: Authentication & Authorization
- FR-01.1: Split-screen login with email/password
- FR-01.2: "Remember me" persistent session
- FR-01.3: Forgot password → email reset link flow
- FR-01.4: No self-registration (accounts via webhook or admin only)
- FR-01.5: Role-based access (Student, Physician, Admin)

### FR-02: Shopify Integration
- FR-02.1: Webhook endpoint accepts POST from Shopify on purchase
- FR-02.2: Verify HMAC-SHA256 signature on every webhook
- FR-02.3: Auto-create user if email not in database
- FR-02.4: Auto-grant book access based on product_id mapping
- FR-02.5: Send welcome email (new user) or notification email (existing user)
- FR-02.6: Log all webhook events (payload, status, errors)
- FR-02.7: "Redeem Purchases" user-facing page (polls Shopify API)
- FR-02.8: Admin dashboard section for manual purchase restoration

### FR-03: Dashboard
- FR-03.1: Welcome banner with user's first name
- FR-03.2: 4-stat summary bar (progress, score, study time, streak)
- FR-03.3: Today's Goals section with progress bars (configurable goals)
- FR-03.4: Quick Actions for module navigation
- FR-03.5: Board Basics and CORE preview cards

### FR-04: Syllabus & PDF Reader
- FR-04.1: "My Books" tab showing purchased books with progress
- FR-04.2: "Store" tab showing available books with "Buy Now" → Shopify
- FR-04.3: Book card cross-links (Flashcards, Board Basics, Question Bank)
- FR-04.4: Upload full PDF per book (admin)
- FR-04.5: Define specialty page ranges within PDF (admin)
- FR-04.6: Define topic page ranges within specialty ranges (admin)
- FR-04.7: Validate topic ranges fall within parent specialty range
- FR-04.8: React PDF viewer renders only selected topic's pages
- FR-04.9: Left sidebar specialty accordion with progress bars
- FR-04.10: Topic pagination (Previous/Next)
- FR-04.11: Inline toolbar: font size, bookmark, highlight, note
- FR-04.12: Embedded quiz widget in reading flow
- FR-04.13: Content protection (no download, no copy, no print)
- FR-04.14: Track reading progress per topic (last page, time spent)

### FR-05: Notes & Highlights
- FR-05.1: Save notes with text annotation per page
- FR-05.2: Save highlights with color selection per page
- FR-05.3: Two-level navigation (book → specialty/topic)
- FR-05.4: Filter by specialty or topic
- FR-05.5: Access from Syllabus and Board Basics modules

### FR-06: Question Bank
- FR-06.1: 3-stat summary bar (completion, average, custom quizzes)
- FR-06.2: Question sets grouped by book with progress
- FR-06.3: Question detail with vignette, choices, peer stats, timer
- FR-06.4: Critique/explanation after answering
- FR-06.5: Key Point and Reference sections per question
- FR-06.6: "Related Syllabus Content" cross-link
- FR-06.7: "Add to Learning Plan" button per question
- FR-06.8: Bookmark/save questions
- FR-06.9: Answered Questions page with correct/incorrect icons
- FR-06.10: Saved Questions page with filter and "Create Quiz" option
- FR-06.11: Custom Quiz Builder with templates (Build own, LKA, Exam, Retry)
- FR-06.12: Quiz builder advanced filters (question type, care type, patient)
- FR-06.13: Quiz timing modes (untimed, 90s standard, 60s fast)
- FR-06.14: Answer/critique visibility toggle
- FR-06.15: Track response time per question

### FR-07: Learning Plan
- FR-07.1: Empty state with onboarding instructions
- FR-07.2: Add topics from paginated topic picker
- FR-07.3: Remove topics from plan
- FR-07.4: Filter topics by specialty
- FR-07.5: Dual progress tracking (questions + tasks) per topic
- FR-07.6: "Continue" / "Start" buttons per topic card

### FR-08: CORE Certification
- FR-08.1: Display 11 specialty badges with status (Pending/In Progress/Completed)
- FR-08.2: Badge earned when 50%+ correct on last 30 questions in specialty
- FR-08.3: Overall badge count ("4/11 Badges Earned")
- FR-08.4: Specialty detail page with question progress and recent answers
- FR-08.5: "Resume Answer Questions" button per specialty

### FR-09: Board Basics
- FR-09.1: 4-stat summary bar (same pattern as Dashboard)
- FR-09.2: Show books filtered to `is_board_basics=True` topics
- FR-09.3: "Notes & Highlights" button
- FR-09.4: Cross-links to Flashcards and Question Bank

### FR-10: Flashcards
- FR-10.1: Decks organized by book
- FR-10.2: Flip card interaction (question → answer)
- FR-10.3: "Related Text →" link to syllabus topic
- FR-10.4: Previous/Next navigation with count ("2/215")
- FR-10.5: Spaced repetition algorithm for review scheduling

### FR-11: CME/MOC/CPD
- FR-11.1: Credit summary with ready-to-claim count
- FR-11.2: "Claim Credits Now" button
- FR-11.3: Automatic credit calculation (0.25 per qualifying answer)
- FR-11.4: Calendar-year credit limits (300 max)
- FR-11.5: Submission history table by year
- FR-11.6: Static information pages for ACP, Royal College Canada, RACP
- FR-11.7: Certificate generation per submission

### FR-12: Help Center
- FR-12.1: FAQ with category filter tabs
- FR-12.2: Accordion-style expandable answers
- FR-12.3: Contact support: email + phone
- FR-12.4: Admin-manageable FAQ entries

### FR-13: Settings
- FR-13.1: Profile update (name, email, photo)
- FR-13.2: Notification preferences (4 toggles)
- FR-13.3: Password change (current + new)
- FR-13.4: Learning preferences (3 daily goals)
- FR-13.5: Display settings (font size, dark mode)
- FR-13.6: Account deletion (Danger Zone)

### FR-14: Global Features
- FR-14.1: Global search across books, chapters, questions
- FR-14.2: Dark mode toggle (persisted in preferences)
- FR-14.3: Notification bell with dropdown
- FR-14.4: Responsive sidebar navigation
- FR-14.5: Breadcrumb navigation on all subpages

---

## 8. Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-01 | HTTPS everywhere (TLS 1.2+) | Critical |
| NFR-02 | HMAC-SHA256 webhook verification | Critical |
| NFR-03 | Secure password hashing (bcrypt/Argon2) | Critical |
| NFR-04 | PDF content protection (no download/copy/print) | High |
| NFR-05 | Page load time < 3 seconds | High |
| NFR-06 | PDF viewer lazy-loading (only requested pages) | High |
| NFR-07 | Responsive design (desktop-first, tablet support) | Medium |
| NFR-08 | Dark mode support across all components | Medium |
| NFR-09 | Accessibility (WCAG 2.1 AA) | Medium |
| NFR-10 | Webhook idempotency (duplicate detection) | High |
| NFR-11 | Database query optimization (N+1 prevention) | Medium |
| NFR-12 | Transactional email reliability (SendGrid/SES) | High |
| NFR-13 | PDF caching (CDN or browser cache) | Medium |
| NFR-14 | Audit trail for all access grants | Medium |
| NFR-15 | GDPR compliance (account deletion) | Medium |

---

## 9. Cross-Module Links & Navigation Map

The Figma designs emphasize aggressive cross-module linking. Here's the complete map:

```
Syllabus Book Card
├── "Flashcards →"        → Flashcards deck for this book
├── "Board Basics →"      → Board Basics filtered to this book
└── "Continue"            → Reading interface (last read topic)

Question Bank Book Card
├── "Flashcards →"        → Flashcards deck for this book
├── "Board Basics →"      → Board Basics filtered to this book
└── "Continue"            → Resume quiz for this book

Question Detail
├── "Related Syllabus Content →" → Topic in reading interface
└── "Add to Learning Plan"       → Add topic to Learning Plan

Flashcard (Answer Side)
└── "Related Text →"      → Topic in reading interface

Board Basics Book Card
├── "Flashcards →"        → Flashcards deck
├── "Question Bank →"     → Question Bank for this book
└── "Notes & Highlights"  → Notes page filtered to this book

Dashboard
├── Board Basics preview  → Board Basics module
├── CORE preview          → CORE module
└── Quick Actions         → Various modules

CORE Specialty Detail
└── Same UI as Question Bank (shared question-taking component)

Saved Questions
└── "Create New Quiz"     → Custom Quiz Builder (pre-filtered)
```

---

## 10. Identified Gaps & Clarifications Needed

### 10.1 Design Gaps (Missing Figma Screens)

| Gap | Description | Impact |
|-----|-------------|--------|
| Question-Taking UI | No Figma screen for the actual question-answering interface (vignette → choices → critique flow) | High — core feature |
| Email Templates | No design for welcome/notification email templates | Medium |
| Notification Dropdown | Bell icon visible but no dropdown/panel design | Low |
| "Coming Soon" Book State | No visual design for books with `status=coming_soon` | Low |
| Book Preview Modal | Store tab shows cards but no preview/detail modal | Low |
| "Redeem Purchases" Page | Referenced in Shopify PDF but no Figma screen | Medium |
| Embedded Quiz in Reader | Referenced but no specific design for inline quiz widget | Medium |
| Lab Values Table | Referenced in MKSAP analysis but not in current Figma | Medium |

### 10.2 Business Logic Clarifications

| Question | Context |
|----------|---------|
| How is reading progress calculated for PDF topics? | Page-by-page tracking? Time-based? Scroll-based? |
| What triggers a "task completed" in Learning Plan? | Read topic? Answer questions? Review flashcards? |
| How are CORE questions different from Question Bank? | Same pool filtered by specialty? Separate set? |
| What is the spaced repetition algorithm for flashcards? | SM-2? Leitner? Custom? |
| Can users re-take custom quizzes? | Reset and restart? Or view past results? |
| How are peer statistics calculated? | Real-time? Batch? Minimum sample size? |
| Content versioning when PDF is updated? | Reset progress? Maintain markers? |
| What happens to notes/highlights if PDF changes? | Page numbers might shift |

### 10.3 Technical Decisions Needed

| Decision | Options |
|----------|---------|
| React PDF Viewer library | `@react-pdf-viewer/core` (feature-rich) vs `react-pdf` (lightweight) |
| PDF serving strategy | Direct file URL vs authenticated streaming API |
| Search implementation | Full-text search library? Algolia? Database search? |
| Real-time notifications | WebSocket? Polling? Push notifications service? |
| Email service provider | SendGrid? AWS SES? Mailgun? |
| Certificate PDF generation | ReportLab? WeasyPrint? HTML-to-PDF service? |

### 10.4 Existing Model Migrations Required

The current Django models need these changes for PDF support:

```python
# Book model — ADD:
pdf_file = models.FileField(upload_to='books/pdfs/', blank=True, null=True)
total_pages = models.PositiveIntegerField(default=0)

# Specialty model — ADD:
start_page = models.PositiveIntegerField(default=0)
end_page = models.PositiveIntegerField(default=0)

# Topic model — ADD:
start_page = models.PositiveIntegerField(default=0)
end_page = models.PositiveIntegerField(default=0)
# Mark 'content' field as deprecated (keep for migration period)
```

---

## Appendix: Figma Screen Index

| # | Filename | Module | Content |
|---|----------|--------|---------|
| 1 | Pasted image.png | Auth | Login page (split-screen) |
| 2 | Pasted image (2).png | Auth | Login variant / Forgot password |
| 3 | Pasted image (3).png | Auth | Password reset flow |
| 4 | Pasted image (4).png | Dashboard | Home page (top half) |
| 5 | Pasted image (5).png | Dashboard | Home page (bottom half) |
| 6 | Pasted image (6).png | Syllabus | My Books tab |
| 7 | Pasted image (7).png | Syllabus | Book card details |
| 8 | Pasted image (8).png | Syllabus | Store tab |
| 9 | Pasted image (9).png | Syllabus | Reading interface / Notes |
| 10 | Pasted image (10).png | Syllabus | Reading interface variant |
| 11 | Pasted image (11).png | Syllabus | Store card variant |
| 12 | Pasted image (12).png | Syllabus | Book preview |
| 13 | Pasted image (13).png | QBank | Question Bank landing |
| 14 | Pasted image (14).png | QBank | Answered Questions (empty) |
| 15 | Pasted image (15).png | QBank | Saved Questions (empty) |
| 16 | Pasted image (16).png | QBank | Custom Quizzes (empty) |
| 17 | Pasted image (17).png | QBank | Book detail (empty recent) |
| 18 | Pasted image (18).png | QBank | Answered Questions (populated) |
| 19 | Pasted image (19).png | QBank | Saved Questions (populated) |
| 20 | Pasted image (20).png | QBank | Custom Quiz Builder |
| 21 | Pasted image (21).png | QBank | Book detail (populated) |
| 22 | Pasted image (22).png | QBank | Book detail variant |
| 23 | Pasted image (23).png | QBank | Custom Quizzes (populated) |
| 24 | Pasted image (24).png | Learning | Learning Plan (empty) |
| 25 | Pasted image (25).png | Learning | Add Topics picker |
| 26 | Pasted image (26).png | Learning | Learning Plan (populated) |
| 27 | Pasted image (27).png | CORE | CORE badges list |
| 28 | Pasted image (28).png | CORE | Specialty detail |
| 29 | Pasted image (29).png | Board | Board Basics landing |
| 30 | Pasted image (30).png | Flash | Flashcard (question side) |
| 31 | Pasted image (31).png | Flash | Flashcard (answer side) |
| 32 | Pasted image (32).png | CME | CME/MOC/CPD page (top) |
| 33 | Pasted image (33).png | CME | CME/MOC/CPD page (full) |
| 34 | Pasted image (34).png | Help | Help Center |
| 35 | Pasted image (35).png | Settings | Profile tab |
| 36 | Pasted image (36).png | Settings | Security tab |
| 37 | Pasted image (37).png | Settings | Preferences tab |
