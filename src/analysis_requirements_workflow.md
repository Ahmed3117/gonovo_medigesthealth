# MEDIGEST Platform — Complete Analysis, Requirements & Workflow

> **Project**: MEDIGEST Health — Online Medical Learning Platform  
> **Domain**: `medigesthealth.com` (E-Commerce Store) → `online.medigesthealth.com` (Web App)  
> **Reference App**: ACP MKSAP (`https://mksap.acponline.org/app`)  
> **Author**: Dr. Saad A. Hagras, MD  
> **Date**: 2026-02-18  

---

## Table of Contents

1. [Resource Analysis](#1-resource-analysis)
   - [A. Shopify Integration PDF](#a-shopify-integration-based-on-shopify-integrationpdf)
   - [B. MKSAP Reference Website Deep Dive](#b-mksap-reference-website-deep-dive)
   - [C. Figma Sitemap Analysis](#c-figma-sitemap-analysis)
   - [D. Live Store Analysis (medigesthealth.com)](#d-live-store-analysis-medigestshealthcom)
2. [Cross-Reference & Gap Analysis](#2-cross-reference--gap-analysis)
3. [Functional Requirements](#3-functional-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [Data Model Design](#5-data-model-design)
6. [Implementation Workflow](#6-implementation-workflow)
7. [Action Items & Open Questions](#7-action-items--open-questions)

---

## 1. Resource Analysis

### A. E-Commerce Integration (Based on `Shopify Integration.pdf`)

The PDF describes a three-part integration plan between the client's e-commerce store and our web application.

> ✅ **CLARIFIED**: The e-commerce platform (`medigesthealth.com`) is **not our concern**. We implement a **platform-agnostic webhook endpoint**. The client's developer will configure their store (regardless of platform — WooCommerce, Shopify, or other) to send us a POST request when a purchase is completed. We define the expected payload format and give them our endpoint URL.

#### Part 1 — Web App Access
| Detail | Value |
|--------|-------|
| E-Commerce Store Domain | `medigesthealth.com` |
| Web App Subdomain | `online.medigesthealth.com` |
| Access Method | Button on the storefront linking to the web app |
| Client Responsibility | Creating the button and hyperlink on their store |
| Our Responsibility | Providing the hosting IP address |
| Phase | Before Deployment to Production |

#### Part 2 — DNS Setup
| Detail | Value |
|--------|-------|
| DNS Records Needed | "A" record (and MX if needed) |
| Client Responsibility | Creating DNS records in the domain registrar |
| Our Responsibility | Providing the server IP address to point the subdomain to |
| Phase | Before Deployment to Production |

#### Part 3 — Webhook Integration (Development Phase)

**A) Webhook (Event-Based, One-Way)**

| Detail | Value |
|--------|-------|
| Trigger Event | `purchase completed` on `medigesthealth.com` |
| Direction | Client's store → Our endpoint (one-way POST) |
| Webhook Signing Secret | `8828edf31bf2349bde1141cc3e0d841b1560bebadd5bdab0adeb0bf214fc6094` |
| Payload Schema | We define it (see below). Client's developer adapts to match. |

**Recommended Webhook Payload Schema (JSON):**

Since the original `.json` schema file was not provided, we define the following recommended payload. The client's developer should send this structure, or we adjust after receiving theirs:

```json
{
  "event": "order.completed",
  "order_id": "ORD-20260218-001",
  "customer": {
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "items": [
    {
      "product_id": "prod_pulmonary",
      "product_name": "Pulmonary and Critical Care Medicine",
      "price": 60.00
    },
    {
      "product_id": "prod_cardiovascular",
      "product_name": "Cardiovascular Medicine",
      "price": 55.00
    }
  ],
  "total_amount": 115.00,
  "currency": "USD",
  "payment_status": "paid",
  "timestamp": "2026-02-18T17:30:00Z",
  "signature": "<HMAC-SHA256 hash>"
}
```

**Complete Integration Flow:**
```
┌─────────────────────────────┐      Webhook POST       ┌──────────────────────────────────┐
│   medigesthealth.com        │ ─────────────────────►   │   online.medigesthealth.com       │
│   (E-Commerce Store)        │                          │   (Our MEDIGEST Platform)         │
│                             │  POST /api/webhooks/     │                                   │
│  1. User browses books      │  purchase/               │  4. Verify HMAC signature         │
│  2. User adds to cart       │                          │  5. Parse order data              │
│  3. User pays & checkout    │  Payload:                │  6. Check if user exists by email │
│     ✅ Payment successful   │  {order_id, email,       │     ├─ NEW: Create account        │
│                             │   product_ids, ...}      │     │  → Generate password          │
│  Store developer configs    │                          │     │  → Grant book access          │
│  webhook to hit our URL     │                          │     │  → Send welcome email         │
│                             │                          │     └─ EXISTS: Grant book access   │
│                             │                          │        → Send notification email  │
│  User sees: "Access details │                          │  7. Save to UserBookAccess table  │
│  sent to your email"        │                          │  8. User logs in & reads books    │
└─────────────────────────────┘                          └──────────────────────────────────┘
```

**Webhook Business Logic (Step by Step):**
1. Receive `POST /api/webhooks/purchase/` request
2. Verify the HMAC-SHA256 signature using the signing secret
3. Parse the JSON payload and extract `customer.email` & `items[].product_id`
4. **IF user email does NOT exist in DB:**
   - Create a new user account (auto-generate secure password)
   - Grant access to purchased book(s) based on `product_id` values
   - Send **welcome email** with login credentials (email + generated password)
5. **IF user email already EXISTS in DB:**
   - Add the newly purchased book(s) to their access list
   - Send **notification email** informing them of new book access
6. Log the webhook event in `WebhookLogs` for debugging and audit
7. Return `HTTP 200 OK` to acknowledge receipt

**Our Responsibilities:**
- Define and document the webhook payload format
- Provide the client's developer with our webhook URL endpoint
- Handle all user provisioning and access management on our side

**Client's Developer Responsibilities:**
- Configure their store to send a POST request to our endpoint on successful payment
- Match the payload format we define (or we adapt to theirs)
- Include the HMAC signature for security verification

**B) Redeem Purchases (Manual Fail-Safe)**

This is a secondary mechanism to handle cases when the webhook fails to fire or data is lost.

| Detail | Description |
|--------|-------------|
| Mechanism | Admin manually grants access, or user contacts support |
| Data Required | User email + order confirmation from the store |
| Action | Admin verifies the purchase and manually grants book access |

**Required UI Elements:**
1. **User-facing page** — "Restore Access" / "Redeem Purchases" button inside the user's Profile page
2. **External link** — Client will also link to this page from their store website
3. **Admin Dashboard** — Section for admins to manually grant/restore book access for any user

---

### B. MKSAP Reference Website Deep Dive

**URL:** `https://mksap.acponline.org/app`  
**Purpose:** The client wants us to clone the feature set and UX of this application for medical education.

#### Layout & Navigation Architecture
- **Top Bar (fixed):** Logo (left), Global Search icon (right), Kebab menu (right) for Settings/Logout
- **Left Sidebar (fixed, dark theme):**
  - Navigation links: Home, Syllabus, Question Bank, Learning Plan, CORE, Board Basics®, Flashcards, CME/MOC/CPD, Help
  - User profile section at bottom (name + email + kebab menu for Account Profile / Logout)
  - Sidebar is collapsible for mobile — responsive design
- **Main Content Area:** Large light-themed workspace, dynamically changes based on sidebar selection
- **Breadcrumb Navigation:** Present at top of content area (e.g., `Syllabus > Cardiovascular Medicine > Epidemiology and Risk Factors`)

#### Feature 1 — Dashboard (Home)
- **Welcome banner:** Personalized greeting ("Welcome, [Name]") with a subtitle ("Your resource for continual learning in Internal Medicine")
- **Getting Started Video card:** Dismissible (×) card with "Watch Video" button
- **"Not sure where to begin?" card:** Dismissible card with "Find Your Approach →" button
- **Your Recent Activity section:**
  - Shows last-accessed items across ALL modules (Syllabus, Learning Plan, Question Bank)
  - Each card shows: Module icon, topic name, progress bar, "Resume Studying →" button
  - Progress indicator: "X of Y topics marked completed"

#### Feature 2 — Syllabus
- **Overview page:**
  - Header: "Syllabus — Comprehensive resource for Internal Medicine clinical knowledge"
  - Tutorial video link ("2 3-min video" button)
  - **Resume banner:** "Resume your progress in [Specialty]" with "Table of Contents →" button
  - **Specialty list:** Each row has:
    - Specialty icon/image (e.g., heart for Cardiovascular)
    - Specialty name
    - Topic count (e.g., "14 Topics")
    - Arrow navigation (→)
  - Specialties identified: Cardiovascular Medicine (14), Common Symptoms (18), Critical Care Medicine (3), Dermatology (18), Endocrinology and Metabolism (8), Foundations of Clinical Practice, and more

- **Specialty detail page (e.g., Cardiovascular Medicine):**
  - Resume banner: "Pick up where you left off in [Topic]" with "Resume →" button
  - **Topic listing:**
    - Each topic shows name + badges (e.g., "1 Highlight", "In Learning Plan")
    - Examples: Epidemiology and Risk Factors, Dyslipidemia, Diagnostic Testing in Cardiology, Coronary Artery Disease, Heart Failure, Arrhythmias, Valvular Heart Disease, Myocardial Disease

- **Reading Interface (Topic Reader):**
  - **Breadcrumb:** Full navigation path
  - **Header area:**
    - "Next Topic ▸" button (top right)
    - Topic title block with specialty name, topic name
    - "Topic Key Points ↗" expandable button
    - "Mark this topic completed" checkbox
  - **Content body:**
    - Long-form medical text with nested sections (Overview, sub-sections, Bibliography)
    - **Key Points box:** Highlighted bordered box at the top of each section with bullet points
    - Rich text: Headers, paragraphs, bold terms, clinical images, CT scans, tables
  - **Right sidebar (dual-tab):**
    - **"In this topic" tab:** Table of Contents for the current topic
      - Lists: Topic Key Points, Overview, Risk Factors for Cardiovascular Disease, Calculating Cardiovascular Risk, Specific Risk Groups, Bibliography, Learning Plan Topic
      - Each section has a circle icon (checked if completed)
    - **"Notes" tab:** User can type personal notes attached to this specific topic
  - **Interactive features observed:**
    - Text highlighting capability
    - Note-taking per topic
    - Mark as completed
    - Navigate to next/previous topic
    - Cross-links to related content and Learning Plan

#### Feature 3 — Question Bank
- **Overview page:**
  - Header: "Question Bank — Multiple-choice questions based on single-best-answer clinical scenarios"
  - Tutorial video link ("3-min video" button)
  - **Progress dashboard:**
    - Circular gauge: "< 1% Complete"
    - Horizontal bars: "X Completed Questions" → "Y% correct" (green) + "Z% incorrect" (red)
    - "Review ▸" link to review completed questions
  - **Two action cards:**
    - **Shuffle Questions** — "Answer randomized questions from across the Question Bank" → "Answer Questions ⊠" button
    - **Custom Quizzes** — "Select questions to create custom quizzes based on your learning needs" → "New Custom Quiz +" button
  - **Question Sets section:**
    - "Saved Questions" (bookmark icon) — 0 saved questions
    - Per-specialty breakdown: e.g., "Cardiovascular Medicine" with progress

- **New Custom Quiz page:**
  - **Quiz Templates:**
    1. **Build your own** — "Make selections to create a custom quiz from the question bank"
    2. **Longitudinal Knowledge Assessment (LKA) Practice** — "Random questions from across all content areas with 5-minute countdown timer"
    3. **Exam Practice** — "60 random questions from across all content areas with a two-hour time limit"
    4. **Retry incorrect questions** — "Shuffle your incorrectly answered questions"
  - **Next step:** "Choose your questions" (specialty/topic selection)
  - **Final step:** "Create Your Quiz" button with question count summary

- **Question Interface (during quiz):**
  - Question text (may include clinical images, diagrams, CT scans)
  - Multiple choice options (A, B, C, D, E) — single best answer
  - **Strikethrough feature:** Visually eliminate wrong answers
  - "Submit" button to lock in answer
  - **After submission — Feedback area:**
    - Correct/Incorrect indicator
    - **Peer Statistics:** Bar graph showing percentage of users who selected each option
    - **Answer and Critique:** Detailed medical explanation
    - **Educational Objective:** Summary learning point
    - Links to related Syllabus topics

#### Feature 4 — Learning Plan
- Personalized study tool
- Users can target specific topics for focused study
- Tracks: Tasks completed, MCQs answered per topic
- Topics tagged with "In Learning Plan" badge in Syllabus

#### Feature 5 — CORE (Confirmation of Relevant Education)
- Achievement-oriented system
- Users earn badges/certificates by demonstrating mastery
- Work towards certification in specific content areas

#### Feature 6 — Board Basics®
- Same specialty-based structure as Syllabus
- Content is condensed, "digest-style" for exam prep
- Features: "Don't Forget!" boxes, study tables, summarized facts
- Uses the SAME reading interface (TOC sidebar, Notes tab) as the regular Syllabus
- Separate progress tracking from main Syllabus

#### Feature 7 — Flashcards
- **Overview page:**
  - Header: "Flashcards — Learn through repeated exposure to quick-study concepts"
  - Global progress: "X of Y Flashcards Reviewed"
  - Performance: "X% Correct | Y% Incorrect"
  - "Answer Flashcards ⊠" button for global shuffle
  - **Flashcard Decks:** One per specialty, each showing:
    - Specialty icon
    - Specialty name
    - Card count (e.g., "183 Flashcards")
    - Individual progress bar
  - Decks include: Cardiovascular Medicine (183), Common Symptoms (99), Critical Care Medicine (50), Dermatology (70), Endocrinology and Metabolism, etc.
- **Study Interface:**
  - **Front of card:** Clinical question/prompt
  - **"Reveal Answer" button** flips the card
  - **Back of card:** Answer text + "Related Text" button (links to Syllabus)
  - **Confidence Rating:** User rates as "Correct", "Unsure", or "Incorrect" → drives spaced repetition algorithm
  - Card counter: "Card X of Y"

#### Feature 8 — CME/MOC/CPD
- Dashboard showing total credits earned vs. available
- Credits are auto-unlocked ("ready to claim") when user maintains ≥50% correct score in Question Bank
- Portal for managing certificates
- ABIM (American Board of Internal Medicine) submission integration

#### Feature 9 — Global Search
- Accessible from magnifying glass icon in top bar
- Full-text search across ALL content types
- **Search results page:**
  - Result count: "Showing X results"
  - **Filters button** — narrows by section or specialty
  - "Use this exact word or phrase" checkbox
  - Each result card shows:
    - Source label (e.g., "Syllabus - Rheumatology")
    - Title (clickable link)
    - Text snippet with **highlighted/bolded** matching keywords
    - Cross-module results (Syllabus, Board Basics, Flashcards all in one search)

#### Feature 10 — User Settings & Profile
- **Account Profile:** ACP ID, email, name
- **Display Settings:**
  - Theme toggle: **Light, Dark, System** modes
  - Text size: **Small, Medium, Large**
- **Data Management:** Reset progress for entire app or specific sections
- **Help:** External link

---

### C. Figma Sitemap Analysis

The UI/UX designer's sitemap defines the specific information architecture for MEDIGEST. Below is a complete node-by-node breakdown:

```
Start: User Arrives
    ├── Login Page ─────────────────────────┐
    ├── Sign Up / Registration              │
    └── Password Recovery                   │
                                            ▼
                               Main Application Dashboard
                                            │
            ┌───────────────────────────────┼──────────────────────────┐
            ▼                               ▼                          ▼
    Core Learning Module          Physician/CME Dashboard      User Management
            │                               │                          │
            ├─ Syllabus Reader              ├─ CORE Certification      ├─ Edit Profile
            │   ├─ Table of Contents        │   ├─ Certification Reg.  ├─ Subscription & Billing
            │   ├─ Reading Interface        │   ├─ Submit Exam Scores  ├─ App Preferences
            │   │   ├─ Highlight Text       │   └─ Download Certificate│   ├─ Dark Mode Toggle
            │   │   ├─ Create Flashcard     │                          │   └─ Adjust Font Size
            │   │   └─ Add Notes            ├─ CME/MOC/CPD Credits     ├─ Notification Settings
            │   ├─ Topic List by Specialty  │   ├─ Credit Dashboard    ├─ Help & Support
            │   └─ Digest Reader View       │   ├─ Activity Log        └─ Manage Profile
            │                               │   └─ Submit to Medical Board
            ├─ Board Basics                 │
            │                               │
            ├─ Flashcards System            │
            │   ├─ My Custom Deck           │
            │   │   ├─ Active Study Mode    │
            │   │   ├─ Spaced Repetition    │
            │   │   ├─ All Notes            │
            │   │   ├─ All Highlights       │
            │   │   └─ Export as PDF        │
            │   └─ Professor's Deck         │
            │                               │
            ├─ Library / Store              │
            │   ├─ My Purchased Books       │
            │   └─ Locked Books             │
            │       ├─ Book Preview Modal   │
            │       ├─ Purchase Flow        │
            │       └─ Payment & Checkout   │
            │                               │
            ├─ Question Bank                │
            │   ├─ Quiz Builder             │
            │   ├─ Take Quiz                │
            │   ├─ Review & Explanations    │
            │   └─ Performance Analytics    │
            │                               │
            └─ Learning Plan                │
                ├─ Progress Dashboard       │
                ├─ Performance Analytics    │
                └─ Study Schedule           │
                                            │
            Global Search ──── Available Everywhere
```

**Figma-Specific Items NOT in MKSAP (Unique to MEDIGEST):**
1. **Library / Store** — Full e-commerce flow within the app (My Purchased Books, Locked Books, Book Preview Modal, Purchase Flow, Payment & Checkout)
2. **"Create Flashcard" from Reading Interface** — Users can create custom flashcards directly while reading
3. **"Export as PDF"** — Flashcard export capability
4. **"Professor's Deck"** — Pre-made flashcard deck (separate from user custom decks)
5. **"Digest Reader View"** — Alternate reading layout
6. **Subscription & Billing** — User-facing billing management
7. **Notification Settings** — In user preferences
8. **Adjust Font Size** — Accessibility setting in user preferences

---

### D. Live Store Analysis (medigesthealth.com)

**URL:** `https://medigesthealth.com`  
**Purpose:** This is the client's live e-commerce store where medical books are sold. Our web app will integrate with it.

#### ℹ️ Store Platform Note

The live store is currently built on **WordPress + WooCommerce + Elementor**. However, this **does not affect our implementation** — we expose a platform-agnostic webhook endpoint. The client's developer will configure their store to send order data to our URL regardless of their underlying platform.

#### Store Branding & Design Language
| Element | Details |
|---------|---------|
| **Logo** | Shield emblem with book icon + "MEDIGESTHEALTH" text |
| **Primary Colors** | Navy Blue (#1B3F74), Teal/Aqua (#00B5AD), White backgrounds |
| **Typography** | Serif fonts for headings, Sans-serif for body text |
| **Visual Style** | High-quality 3D book renders, clean medical aesthetic |
| **Tone** | Professional, authoritative, academic medical authority |

#### Store Navigation Structure
```
Header:
├── Home
├── About Author
├── Books
├── Contact Us
├── Blog
├── 👤 User Account (/my-account/)
└── 🛒 Shopping Cart (/cart/)
```

#### Complete Product Catalog

**Author:** Dr. Saad A. Hagras, MD — Specialist in Hospital Medicine and ICU Management

| # | Product | Price | Chapters | Status | Product URL | Online Access URL | Preview PDF |
|---|---------|-------|----------|--------|-------------|-------------------|-------------|
| 1 | **Pulmonary and Critical Care Medicine** | $60 | 30+ chapters, 204 pages | ✅ Available | `/product/pulmonary-and-critical-care-medicine/` | `/books/pulmonary/` | `PUL-SAMPLE.pdf` |
| 2 | **Cardiovascular Medicine** | $55 | 25+ chapters | ✅ Available | `/product/cardiovasicular-medicine/` *(note: typo in URL)* | `/books/cardiovasicular/` | `CVD-SAMPLE.pdf` |
| 3 | **Infectious Diseases** | $50 | 20+ chapters | ✅ Available | `/product/infectious-diseases/` | `/books/infectious-disease/` | `ID-SAMPLE.pdf` |
| 4 | **Nephrology** | $50 | Multiple chapters | ✅ Available | `/product/nephrology/` | `/books/nephrology/` | `NEPH-SAMPLE.pdf` |
| 5 | **Hematology and Oncology** | $60 | Multiple chapters | ✅ Available | `/product/hematology-and-oncology/` | TBD | TBD |
| 6 | **Gastroenterology and Hepatology** | — | 20+ chapters | 🔒 Coming Soon | — | — | — |
| 7 | **Endocrinology** | — | 15+ chapters | 🔒 Coming Soon | — | — | — |
| 8 | **Neurology** | — | 20+ chapters | 🔒 Coming Soon | — | — | — |
| 9 | **Rheumatology** | — | 15+ chapters | 🔒 Coming Soon | — | — | — |
| 10 | **General Internal Medicine** | — | 20+ chapters | 🔒 Coming Soon | — | — | — |

**Bundle:**
| Bundle | Price | Original | Discount | Contents |
|--------|-------|----------|----------|----------|
| **Pack 1 (5 books)** | $250 | $275 | $25 off | First 5 available books |

**Total Available Products:** 5 individual books + 1 bundle = 6 purchasable items  
**Total Planned Products:** 10 individual books (5 more coming soon)

#### Existing "Online Access" System (Current — To Be Replaced)

The store currently has a **manual, password-protected** digital access system:
- Each book has an "Online Access" button linking to `medigesthealth.com/books/{specialty}/`
- These pages are **password-protected** (WordPress password protection feature)
- Users must enter a password (provided after purchase) to view the book content online
- Content is **read-only** — no downloads or copying allowed
- Described as: "Easy-to-navigate digital format — Access from any device with login credentials"

**This is the system our MEDIGEST platform (`online.medigesthealth.com`) will replace** with a proper authenticated digital reading experience.

#### Each Product Page Contains:
- 3D book cover image
- Product title and price
- Detailed description of topics covered
- **"Preview Book" link** → Opens a free PDF sample of the book (important: we may want to replicate this as the "Book Preview Modal" from Figma)
- **"Online Access" link** → Links to the current password-protected reading page
- **"Buy Now" button** → WooCommerce add-to-cart flow
- **"Books that might interest you"** section → Upsell/cross-sell
- **Customer Reviews** with star ratings (5-star system)
- Reviews show reviewer name, date, written review text, and helpfulness voting

#### FAQ Insights (From Books Page)
Key answers that inform our requirements:
| Question | Answer | Implication for our platform |
|----------|--------|------------------------------|
| What formats are available? | Paperback and digital (online access only) | No downloadable PDF/eBook — read-only web viewer |
| How to access digital version? | "After purchasing, you'll receive login details to access the book online via our website" | Confirms the webhook → auto-provision → email credentials flow |
| Can I download or copy? | "No, the online version is for reading only. You cannot copy or download it." | Must implement DRM-like restrictions (no text selection copy, no right-click save, no print) |
| Will the book be updated? | "Yes, includes latest guidelines for 2025 & 2026, future editions will be updated" | Need a content versioning system |
| Who do I contact for issues? | Via contact form on website | Need "Help & Support" in our app too |

#### Social Media & Contact
| Channel | URL |
|---------|-----|
| YouTube | `youtube.com/@MEDIGEST2025` |
| Facebook | `facebook.com/profile.php?id=61572303403407` |
| Admin Email | `admin@medigesthealth.com` |

#### Legal Pages
- Refund and Returns Policy (`/refund-returns/`)
- Privacy Policy (`/privacy-policy/`)
- Terms and Conditions (`/terms-and-conditions/`)

#### Key Store Observations for Our Platform
1. **Product-to-Specialty Mapping:** Each book = one medical specialty. Our Syllabus specialties should map 1:1 to the Shopify/WooCommerce `productIds`
2. **Content Protection is Essential:** "No downloads or copying" — must implement robust content protection in the web reader
3. **Book Previews Exist:** Free PDF samples are already available — consider integrating these into the "Book Preview Modal" in our Library/Store
4. **Reviews System:** The store has real customer reviews — consider whether to mirror these in our app
5. **Gradual Content Release:** 5 of 10 books are "Coming Soon" — our platform must gracefully handle products that exist in the store but don't have content yet
6. **URL Typo:** "cardiovasicular" (missing 'l') is baked into product URLs — note for data mapping

---

### E. Figma UI/UX Design Analysis (Part 1 — `part1.pdf`)

> **Source file:** `part1.pdf` (11 pages)  
> **Screens covered:** Authentication (Login, Password Reset), Dashboard (Home), Syllabus (My Books, Store, Bookmarks, Notes & Highlights, Reading Interface)  
> **Figma parts remaining:** Part 2+ (Question Bank, Learning Plan, CORE, Board Basics, Flashcards, CME/MOC/CPD, Help Center, Settings, etc.)

#### Design System & Global Layout

**Branding (from Figma):**
| Element | Details |
|---------|---------|
| **Logo** | MEDIGEST shield-book icon (green/teal gradient) with "MEDIGEST" text |
| **Tagline** | "Where Medical Knowledge Grows" |
| **Primary Color** | Dark Navy (#1B2A4A approx.) for sidebar and brand areas |
| **Accent Color** | Teal/Green (#2ECC71 / #00B894 approx.) for CTAs, active states, progress bars |
| **Background** | White/Light Gray (#F8F9FA) for main content area |
| **Typography** | Clean sans-serif (likely Inter or similar) |
| **Dark Mode Toggle** | Moon icon (🌙) visible in top-right bar on ALL screens (auth + app) |
| **Copyright** | "Copyright © 2026 **MEDIGEST** - All Rights Reserved" |

**Authenticated App Shell (Consistent across all logged-in screens):**

```
┌───────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────┐  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │ MEDIGEST 📋 │  │ 👤 Alex Sam      │  │ 🔍 Search books, chapters,  │ │
│  │  (logo)     │  │    Student        │  │    questions...              │ │
│  └─────────────┘  └──────────────────┘  └──────────────────────────────┘ │
│                                                          🌙   🔔        │
├──────────────────┬────────────────────────────────────────────────────────┤
│                  │                                                        │
│  🏠  Home        │                                                        │
│  📖  Syllabus    │              MAIN CONTENT AREA                        │
│  🎯  Question    │                                                        │
│      Bank        │     (Changes dynamically based on                      │
│  📋  Learning    │      sidebar selection)                                │
│      Plan        │                                                        │
│  📝  CORE        │                                                        │
│  📚  Board       │                                                        │
│      Basics      │                                                        │
│  🗂️  Flashcards  │                                                        │
│  🔄  CME/MOC/CPD │                                                        │
│  ─────────────── │                                                        │
│  💬  Help Center │                                                        │
│  ─────────────── │                                                        │
│  ⚙️  Settings    │                                                        │
│                  │                                                        │
│                  │                                                        │
│  🚪 Log out     │                                                        │
│                  │                                                        │
└──────────────────┴────────────────────────────────────────────────────────┘
```

**Top Bar Components:**
| Position | Element | Details |
|----------|---------|---------|
| Far Left | MEDIGEST Logo + 📋 icon | Logo with small clipboard/sidebar toggle icon |
| Left-Center | User Avatar + Name + Role | Profile photo thumbnail, "Alex Sam", "Student" |
| Center-Right | Global Search Bar | Placeholder: "Search books, chapters, questions..." |
| Far Right | Dark Mode Toggle (🌙) | Moon icon — toggles theme |
| Far Right | Notification Bell (🔔) | Bell icon — likely notification center |

**Left Sidebar Navigation Items (in order):**
1. 🏠 Home
2. 📖 Syllabus *(highlighted/active state = dark background fill)*
3. 🎯 Question Bank
4. 📋 Learning Plan
5. 📝 CORE
6. 📚 Board Basics
7. 🗂️ Flashcards
8. 🔄 CME/MOC/CPD
9. ── *(separator line)*
10. 💬 Help Center
11. ── *(separator line)*
12. ⚙️ Settings
13. *(spacer — pushed to bottom)*
14. 🚪 Log out *(red/teal text at very bottom)*

> **Key Design Observation:** The sidebar navigation differs slightly from the original MKSAP reference and the initial Figma sitemap:
> - "Help Center" replaces "Help & Support" (renamed)
> - "Log out" is at the very bottom of the sidebar (not in a kebab menu)
> - User info (name + role + avatar) is in the **top bar** (not at the bottom of the sidebar as in MKSAP)
> - A **Notification Bell icon (🔔)** is present — confirms notification system is needed

---

#### Screen 1: Login Page

**Layout:** Split-screen design
| Section | Content |
|---------|---------|
| **Left Panel (Dark Navy)** | MEDIGEST logo, tagline ("Where Medical Knowledge Grows") |
| **Left Panel — Heading** | "**Welcome Back!**" |
| **Left Panel — Subtitle** | "Continue your medical education journey" |
| **Left Panel — Feature List** | Checkmarks (✅ green) for: "Access comprehensive medical textbooks", "Practice with 1,700+ MKSAP-style questions", "Create and study custom flashcards", "Track your learning progress", "Earn CME/MOC credits (physicians)" |
| **Left Panel — Footer** | "Copyright © 2026 **MEDIGEST** - All Rights Reserved" |
| **Right Panel (White)** | Login form |
| **Top-Right** | 🌙 Dark mode toggle |

**Login Form Fields:**
1. **Email address*** — Input with placeholder "example@example.com"
2. **Password*** — Input with placeholder "Please enter your account password" + 👁️ show/hide toggle
3. ☑️ **Remember me** checkbox (checked by default in design)
4. **Forgot your password?** link (right-aligned, inline with Remember me)
5. **[Log in]** button — Full-width, dark/navy filled button
6. "or" divider line
7. "Don't have an account? **Create an account**" — link text
8. "Help & Support" — link text (centered below)

**Design Notes:**
- No social login (Google, Apple, etc.) — Email/Password only as shown
- "Remember me" is present (persist session)
- The 1,700+ question count is a specific marketing number to replicate in the platform's messaging
- "Help & Support" link on auth pages — links to external help page

---

#### Screen 2: Reset Password — Email Input

**Layout:** Same split-screen as Login

| Section | Content |
|---------|---------|
| **Left Panel** | Same branding as Login |
| **Left Panel — Heading** | "**Reset your password**" |
| **Left Panel — Subtitle** | "Enter your email address and we'll send you instructions to reset your password" |
| **Right Panel** | Reset form |

**Form Fields:**
1. **Email address*** — Input with placeholder "example@example.com"
2. **[Send Reset Instructions]** button — Full-width, dark/navy filled
3. "**Return to log in**" — link (teal/green color)
4. "or" divider line
5. "Don't have an account? **Create an account**" — link
6. "Help & Support" — centered link

---

#### Screen 3: Create New Password

**Layout:** Same split-screen as Login

| Section | Content |
|---------|---------|
| **Left Panel** | Same branding |
| **Left Panel — Heading** | "**Create a new password**" |
| **Left Panel — Subtitle** | "For your security, please reset your password to access your medical records." |
| **Right Panel** | New password form |

**Form Fields:**
1. **New Password*** — Input with placeholder "Please enter your new account password" + 👁️ toggle
   - **Password rules displayed below field:**
     - "Use a long password: the longer the password, the harder it is to crack."
     - "Use a mix of characters (uppercase and lowercase), numbers, and symbols."
     - "Do not use personal information (your name, birthday, etc.)"
     - "Do not use the same password for multiple sites."
     - "Do not share your password with others."
2. **Password Confirmation*** — Input with placeholder "Please reenter your new account password" + 👁️ toggle
3. **[Reset password]** button — Full-width, dark/navy
4. "Help & Support" — centered link

**Design Note:** The password requirements are displayed as a visible helper text list (not hidden validation messages). This is useful UX and should be implemented as inline helper text beneath the password field.

---

#### Screen 4: Check Your Email (Confirmation)

**Layout:** Same split-screen

| Section | Content |
|---------|---------|
| **Left Panel** | Same branding as Reset Password |
| **Right Panel** | Confirmation state |

**Right Panel Content:**
1. **Email illustration** — Envelope with checkmark icon (3D-style illustration)
2. **"Check your email"** heading
3. "We've sent password reset instructions to **example@example.com**"
4. **[Back to Sign In]** button — Full-width, dark/navy
5. "Didn't receive the email? Check your spam folder or **try again**" — "try again" is a link
6. "Help & Support" — centered link

**Design Note:** This is a dedicated confirmation screen (not a toast/notification) — full-page state change after submitting the reset email form. The "try again" link should resend the reset email.

---

#### Screen 5: Dashboard (Home)

**Layout:** Full authenticated app shell (sidebar + top bar + main content)

**Main Content Structure (top to bottom):**

**1. Welcome Banner:**
- "**Welcome back, Alex!**"
- Subtitle: "A Place Where Medical Knowledge Thrives and Continues to Grow"

**2. Stats Summary Bar (4 cards in a row):**
| Stat | Value | Subtext | Icon |
|------|-------|---------|------|
| **Overall Progress** | 52% | 450 / 870 pages | 📈 trend arrow |
| **Quiz Average** | 85% | Last 10 quizzes | 🎯 target icon |
| **Study Time** | 12.5h | This week | ⏱️ clock icon |
| **Study Streak** | 7 days | Keep it up! | 🔥 flame/calendar icon |

**3. Continue Learning Section:**
- Header: "**Continue Learning**" with "View All →" link on the right
- **Card list** (vertical, scrollable):
  - Each card shows:
    - Book icon (📖, dark teal square)
    - **"Internal Medicine Essentials"** (book/specialty name)
    - "Topic Name - Lesson Name" (subtitle)
    - Progress bar (green/teal) with **"45%"** label
    - **[Continue]** button (outlined, teal border)
  - Multiple cards shown (at least 4 visible)

**4. Quick Actions Section (Right sidebar widget):**
- **"Quick Actions"** heading
- Three buttons stacked vertically:
  1. **[📖 Start Reading]** — filled green/teal button (primary)
  2. **[🎯 Practice Questions]** — outlined button
  3. **[🗂️ Study Flashcards]** — outlined button

**5. Today's Goals Section (Right sidebar widget, below Quick Actions):**
- **"Today's Goals"** heading
- Three progress items:
  | Goal | Progress |
  |------|----------|
  | Reading Time | 45 / 60 min (with progress bar) |
  | Practice Questions | 15 / 20 done (with progress bar) |
  | Flashcards Review | 0 / 25 done (with progress bar) |

**6. Board Basics Section:**
- Header: "**Board Basics**" with "View All →" link
- Same card format as Continue Learning:
  - Book icon + "Internal Medicine Essentials" + "Topic Name - Lesson Name"
  - Progress bar (45%) + **[Continue]** button
  - Two cards shown

**7. Confirmation of Relevant Education (CORE) Section:**
- Header: "**Confirmation of Relevant Education (CORE)**" with badge count "4/11 Badges Earned"
- "View Progress →" link
- **Badge cards:**
  - Badge 5: **Hematology** — Progress bar at 45%, "In Progress" badge (green), "Continue →"
  - Badge 6: **Infectious Disease** — Progress bar at 0%, "Pending" badge (gray), "Start Now →"

> **Key Dashboard Differences from MKSAP:**
> - **Stats Summary Bar** — MKSAP doesn't have this prominent 4-stat quick-view. This is a MEDIGEST-specific design.
> - **Quick Actions widget** — Not in MKSAP. Dedicated shortcut buttons.
> - **Today's Goals widget** — Not in MKSAP. Daily goal tracking with progress bars.
> - **Board Basics preview on Dashboard** — MKSAP separates Board Basics entirely. MEDIGEST shows it on the dashboard.
> - **CORE progress on Dashboard** — MKSAP doesn't show CORE badges on the home page.
> - **No "Getting Started" video card** — MKSAP has a dismissible getting started video. Not present in the Figma design for MEDIGEST.
> - **No "Not sure where to begin?" card** — MKSAP has this. Not present in the Figma design.

---

#### Screen 6: Syllabus — My Books Tab

**Layout:** Authenticated app shell

**Page Header:**
- "**Syllabus**"
- Subtitle: "Comprehensive resource for Internal Medicine clinical knowledge"

**Tab Navigation (pill-style toggle):**
- **[My Books (3)]** — active (filled dark/navy), shows count
- **[Store (2)]** — inactive (outlined), shows count

**Stats Summary Bar (same 4 stats as Dashboard):**
| Stat | Value | Subtext |
|------|-------|---------|
| Overall Progress | 52% | 450 / 870 pages |
| Bank Average Score | 85% | Last 10 quizzes |
| Study Time | 12.5h | This week |
| Study Streak | 7 days | Keep it up! |

**Sub-navigation (right-aligned):**
- **[📝 Notes & Highlights]** button
- **[📑 Bookmarks]** button

**My Books Grid (2 columns):**
- Header: "**My Books (3)**"
- Each book card contains:
  - Book icon (📖, dark teal square with book graphic)
  - **"Internal Medicine Essentials"** (book title, bold)
  - "Topic Name - Lesson Name - Last accessed: 2/14/2026" (subtitle with date)
  - Progress bar (green/teal) with **"45%"** label
  - **Quick navigation links:** "Flashcards →" | "Board Basics →" | "Question Bank →"
  - **[Continue]** button — full-width bar at bottom of card
- 4 cards shown (2×2 grid), all similar format

> **Key Syllabus Design Observations:**
> - **"My Books" and "Store" are tabs within Syllabus** — not a separate "Library/Store" page! This is different from the original sitemap which showed Library/Store as a separate navigation item.
> - **Each book card has quick-link shortcuts** to its Flashcards, Board Basics, and Question Bank — cross-module navigation directly from the book card.
> - **The stats bar appears on both Dashboard and Syllabus** — it's a reusable component.
> - **"Notes & Highlights" and "Bookmarks" buttons** are accessible from the Syllabus page header — not just from within the reader.

---

#### Screen 7: Syllabus — Store Tab

**Layout:** Same as Syllabus page, but "Store" tab is active

**Tab Navigation:**
- **[My Books (3)]** — inactive
- **[Store (2)]** — active (filled green/teal)

**Store Content:**
- Header: "**Store (2)**"
- Each store item is a card (list format, not grid):
  - Book icon (📖, dark teal square)
  - **"Internal Medicine Essentials"** (book title, bold)
  - "15 Topic - 15 Lesson - 155 Flash Card" (content preview summary)
  - **"$49.99"** — price in green text
  - **"Learn More! →"** link (right side)
  - **[Purchase Now!]** button (outlined, dark border)
- Two items shown

> **Key Store Design Observations:**
> - **Store is a tab within Syllabus**, not a standalone page. This simplifies navigation — the user sees their owned books and available-for-purchase books in the same context.
> - **Each store item shows content metrics** (topic count, lesson count, flashcard count) — this helps the user understand what they're buying.
> - **"Learn More!"** link — likely opens a modal or detail page with book preview/description.
> - **"Purchase Now!"** button — triggers the purchase flow. Need to clarify: does this redirect to the external e-commerce store, or is there an in-app checkout?
> - **Price display** — $49.99 shown in green (accent color).

---

#### Screen 8: Syllabus — Bookmarks (Empty State)

**Layout:** Authenticated app shell with breadcrumb

**Breadcrumb:** `📖 Syllabus > Bookmarks`

**Page Content:**
- "**Bookmarks**"
- Subtitle: "Save topics to review later"

**Empty State Card:**
- "**No saved Bookmarks yet**"
- "To bookmark a page, chapter, or question, just click the bookmark icon. Come back here anytime to quickly jump to the content you've marked as important."
- "Your bookmarks sync across all your devices, so you can pick up right where you left off—on any device, anytime."

> **Design Note:** Empty states include helpful instructional text explaining how to use the feature. This is good UX — implement similar empty states for other sections.

---

#### Screen 9: Syllabus — Notes & Highlights (Empty State)

**Layout:** Same structure as Bookmarks empty state

**Breadcrumb:** `📖 Syllabus > Notes & Highlights`

**Page Content:**
- "**Notes & Highlights**"
- Subtitle: "Your personal study guide, built as you learn"

**Empty State Card:**
- "**No saved Notes & Highlights yet**"
- "To create a note or highlight, simply select any text while reading. Choose to highlight it, add your thoughts, or turn it into a flashcard."
- "Your notes sync across all your devices, so you can study anytime, anywhere. They're your personal study guide—and they grow with you"

> **Design Note:** The empty state mentions turning text into a flashcard — confirms the "Create Flashcard from Reading Interface" feature is required.

---

#### Screen 10: Syllabus — Reading Interface (Topic Reader)

**Layout:** Three-column layout within the app shell

**Breadcrumb:** `📖 Syllabus > Internal Medicine Essentials`

**Left Panel — Topic Sidebar (Table of Contents):**
- **Specialty sections** listed vertically (collapsible accordion):
  - **Cardiovascular Disease** — expanded with ">" arrow, progress bar at 80%
    - Heart Failure (sub-topic)
    - Coronary Artery Disease (sub-topic)
    - Arrhythmias (sub-topic)
  - **Pulmonary Medicine** — collapsed with ">" arrow, progress bar at 60%
  - **Gastroenterology** — collapsed, progress at 30%
  - **Endocrinology** — collapsed, progress at 0%
- Each specialty shows its progress bar and percentage underneath

**Content Area — Top Toolbar:**

| Element | Details |
|---------|---------|
| **Font Size** | "Font Size: A- A A+" — three size options (decrease, default, increase) |
| **Bookmark** | 📑 Bookmark icon with label |
| **Highlight** | ✏️ Highlight icon with label |
| **Note** | 📝 Note icon with label |

**Content Area — Topic Header:**
- ☑️ **"Mark this topic completed"** checkbox (checked in design)

**Content Area — Reading Body:**
- Long-form medical content with markdown-style formatting visible:
  - `# Cardiovascular Disease` (H1 heading)
  - `## Introduction` (H2 heading)
  - Paragraph text with medical content about cardiovascular system
  - `## Pathophysiology` section
  - `### Classification` subsection
  - Bold terms (`**HFrEF**`, `**HFmrEF**`, `**HFpEF**`)
  - `## Clinical Presentation` section
  - Numbered lists (1. Dyspnea, 2. Orthopnea, 3. PND, 4. Peripheral edema, 5. Fatigue)
  - `### Physical Examination Findings` subsection
  - `## Diagnostic Evaluation` section
  - `### Laboratory Studies` subsection
  - `### Imaging` subsection
  - `## Management` section
  - `### Pharmacologic Therapy` subsection

**Content Area — "Test Your Knowledge" Widget:**
- Dark/navy card embedded in the reading content:
  - "**Test your knowledge**"
  - "0 answered of 1 question"
  - **[Show Question]** button (outlined, white border)

**Content Area — Bottom Navigation (Pagination):**
- **[← Previous]** button (left)
- Page indicators: ● ○ ○ ○ ○ (dots showing current page position, can be for multi-page topics)
- **[Next →]** button (right)

> **Key Reading Interface Differences from MKSAP:**
> - **Left sidebar shows ALL specialties** (not just current book's TOC) — this is an accordion-style topic browser where you can switch between specialties directly from the reader.
> - **Progress bars per specialty** in the left sidebar — users can see their progress across all specialties while reading.
> - **Font Size controls** (A-, A, A+) — inline in the content toolbar. MKSAP has this in Settings. MEDIGEST puts it in the reader for quick access.
> - **"Test your knowledge" widget** — Embedded quiz prompt INSIDE the reading content. Not present in MKSAP's reader. This is a unique MEDIGEST feature that links the reading experience to the Question Bank.
> - **Pagination (Previous/Next with dots)** — Topics may be paginated into multiple pages (rather than a single long scroll). This differs from MKSAP which uses a single scrolling page.
> - **No right-side "In this topic" TOC panel** — MKSAP has a right-side panel with TOC + Notes tabs. MEDIGEST moves the TOC to the left sidebar and puts the toolbar (bookmark, highlight, note) inline at the top.
> - **No "Next Topic" / "Previous Topic" in MKSAP style** — Instead, there's pagination within a topic (Previous/Next page) and the left sidebar for topic navigation.

---

#### Screen 11: Syllabus — Bookmarks (Populated State)

**Layout:** Same as bookmarks empty state, but with content

**Breadcrumb:** `📖 Syllabus > Bookmarks`

**Page Content:**
- "**Bookmarks**"
- Subtitle: "Save topics to review later"

**Bookmarks Grid (2 columns):**
- Header: "**Bookmarks (4)**"
- Each bookmark card:
  - 📑 Bookmark icon (dark navy)
  - **"Abdominal and Pelvic Pain"** (topic title, bold)
  - "Epidemiology and Risk Factors" (section/subtitle)
  - 🗑️ Delete icon (red/dark, right side — for removing bookmark)
- 4 bookmarks shown in a 2×2 grid

> **Design Note:** Bookmarks are topic-level (not paragraph/section level). Each bookmark links to a specific topic within a specialty. The delete icon allows quick removal.

---

#### Screen 12: Syllabus — Notes & Highlights List (Populated State)

**Layout:** Authenticated app shell

**Breadcrumb:** `📖 Syllabus > Notes & Highlights`

**Page Content:**
- "**Notes & Highlights**"
- Subtitle: "Your personal study guide, built as you learn"

**Notes & Highlights Grid (2 columns):**
- Header: "**Notes & Highlights (24)**"
- Each item card:
  - 📖 Book icon (dark teal square)
  - **"Abdominal and Pelvic Pain"** (topic title, bold)
  - "3 Notes - 5 Highlights" (count summary)
  - → Arrow icon (navigate to detail view)
- 4 items shown in 2×2 grid (with scrolling for more)

> **Design Note:** This is a topic-level grouping — notes and highlights are organized BY TOPIC. Clicking a topic card opens the detail view showing all highlights and notes for that specific topic.

---

#### Screen 13: Syllabus — Notes & Highlights Detail View

**Layout:** Authenticated app shell

**Breadcrumb:** `📖 Syllabus > Notes & Highlights`

**Page Content:**
- "**Notes & Highlights**"
- Subtitle: "Your personal study guide, built as you learn"

**Two sections on this page:**

**Section 1: Highlights (4)**
- Header: "**Highlights (4)**"
- Grid layout (2 columns), each highlight card:
  - 📑 Bookmark/highlight icon (dark navy)
  - **"Abdominal and Pelvic Pain"** (topic title, bold)
  - "Epidemiology and Risk Factors" (specialty/section tag, in a badge/pill)
  - "Important observations for the medical textbook." (highlight text preview)
  - **⋯** (three dots — kebab menu, likely for: Edit, Delete, Create Flashcard)
- 4 highlight cards shown (2×2)

**Section 2: Notes (4)**
- Header: "**Notes (4)**"
- Same grid layout (2 columns), each note card:
  - 📝 Note icon (dark teal/green)
  - **"Abdominal and Pelvic Pain"** (topic title, bold)
  - "Epidemiology and Risk Factors" (specialty/section tag, in a badge/pill)
  - "Important observations for the medical textbook." (note text preview)
  - **⋯** (kebab menu)
- 4 note cards shown (2×2)

> **Key Notes & Highlights Design Observations:**
> - **Two-level navigation:** List page (grouped by topic) → Detail page (shows individual highlights + notes for that topic)
> - **Separated sections:** Highlights and Notes are shown in separate sections on the detail page (not interleaved)
> - **Kebab menu** (⋯) on each item — likely supports Edit, Delete, and potentially "Create Flashcard from Highlight"
> - **Badge/pill** for the section name (e.g., "Epidemiology and Risk Factors") — visual tag showing where in the reading the highlight/note was made

---

#### Summary of New/Updated Requirements from Part 1 Figma Designs

| # | Requirement | Source | Impact on Existing Requirements |
|---|-------------|--------|--------------------------------|
| 1 | **Split-screen auth layout** (left branding + right form) | Figma Part 1 | Updates FR-1.1, FR-1.2, FR-1.3 — specific UI layout now defined |
| 2 | **Password reset flow is 4 screens** (Request → Email Sent Confirmation → New Password → Success) | Figma Part 1 | Updates FR-1.3 — adds explicit screen flow |
| 3 | **Password rules visible as helper text** | Figma Part 1 | New UX detail for FR-1.2 |
| 4 | **Dashboard stats bar** (Overall Progress, Quiz Average, Study Time, Study Streak) | Figma Part 1 | New — updates FR-9 with specific stat widgets |
| 5 | **Quick Actions widget** (Start Reading, Practice Questions, Study Flashcards) | Figma Part 1 | New — adds FR-9.5 |
| 6 | **Today's Goals widget** (Reading Time, Practice Questions, Flashcards Review) | Figma Part 1 | New — adds FR-9.6 (daily goal tracking) |
| 7 | **Board Basics preview on Dashboard** | Figma Part 1 | New — Board Basics shown on home page |
| 8 | **CORE badge progress on Dashboard** | Figma Part 1 | New — CORE progress shown on home page |
| 9 | **Syllabus = My Books + Store tabs** (not separate Library page) | Figma Part 1 | **Major change** — FR-8 (Library/Store) is merged into FR-2 (Syllabus). No separate Library page. |
| 10 | **Book cards with cross-module quick links** (Flashcards, Board Basics, Question Bank) | Figma Part 1 | New UX pattern for book cards |
| 11 | **Store items show content metrics** (topic count, lesson count, flashcard count) | Figma Part 1 | New detail for store/purchase cards |
| 12 | **Reading interface with embedded "Test your knowledge" quiz widget** | Figma Part 1 | New — inline quiz in reader (not in MKSAP or original requirements) |
| 13 | **Topic pagination** (Previous/Next with page dots) instead of single long scroll | Figma Part 1 | Updates FR-2.9 — changes navigation model |
| 14 | **Left sidebar = specialty accordion with progress** (not right-side TOC) | Figma Part 1 | Updates FR-2.4 — TOC moved to left sidebar |
| 15 | **Font size controls in reader toolbar** (not in Settings) | Figma Part 1 | Updates FR-12.2 — inline control, not settings-only |
| 16 | **Notes & Highlights two-level navigation** (list by topic → detail view) | Figma Part 1 | New UX pattern — updates FR-2.5, FR-2.6 |
| 17 | **Bookmarks are topic-level** with dedicated page | Figma Part 1 | Updates FR-4.11 scope and adds new bookmark model |
| 18 | **Notification bell icon** in top bar | Figma Part 1 | Confirms notification system is needed (FR-12.3) |
| 19 | **"Remember me" on login** | Figma Part 1 | New detail for FR-1.1 |
| 20 | **No "Getting Started" video on dashboard** | Figma Part 1 | Removes FR-9.2 (or makes it lower priority) |

---

### F. Figma UI/UX Design Analysis (Part 2 — `part2.pdf`)

> **Source file:** `part2.pdf` (12 pages, page 11 is blank)  
> **Screens covered:** Question Bank (Main Page, Answered Questions, Saved Questions, Custom Quizzes, Custom Quiz Builder, Question-Taking Interface)  
> **Figma parts remaining:** Part 3+ (Learning Plan, CORE, Board Basics, Flashcards, CME/MOC/CPD, Help Center, Settings, etc.)

---

#### Screen 14: Question Bank — Main Page

**Layout:** Authenticated app shell (sidebar + top bar)

**Breadcrumb:** *(none — top-level page)*

**Page Header:**
- "**Question Bank**"
- Subtitle: "Multiple-choice questions based on single-best-answer clinical scenarios"

**Stats Summary Bar (3 cards in a row):**
| Stat | Value | Subtext | Action Link |
|------|-------|---------|-------------|
| **< 1% Complete** | 20% (progress bar) | 5 Completed Questions | **Review →** |
| **85%** Bank Average Score | *(icon)* | Last 10 quizzes | **Shuffle Questions →** |
| **0 Completed** Custom Quizzes | *(icon)* | 1 quiz started | **Custom Quizzes →** |

**Main Content:**

**Header Row:**
- "**Question Sets (4)**" — left
- **[🔖 Saved Questions]** — right-aligned button

**Question Sets Grid (2 columns):**
- Each question set card contains:
  - 📋 Question Bank icon (dark navy square with grid/stack graphic)
  - **"Internal Medicine Essentials"** (book/specialty name, bold)
  - "215 Questions - Last accessed: 2/14/2026" (metadata)
  - Progress bar (green/teal) with **"45%"** label
  - **Quick navigation links:** "Flashcards →" | "Board Basics →"
  - **[Continue]** button — full-width bar at bottom of card
- 4 cards shown in 2×2 grid

> **Key Question Bank Main Page Observations:**
> - **Stats bar has 3 stats** (not 4 like Dashboard/Syllabus) — completion %, average score, custom quizzes
> - **Each stat has an action link** (Review, Shuffle Questions, Custom Quizzes) — interactive stats, not just display
> - **"Shuffle Questions"** is a prominent action — randomized question practice mode
> - **"Saved Questions"** button in the header — quick access to bookmarked questions
> - **Question set cards mirror the book card pattern** from Syllabus — same visual component with different content
> - **Quick links on cards** include only "Flashcards" and "Board Basics" (no "Question Bank" link since you're already in it)

---

#### Screen 15: Question Bank — Answered Questions (Empty State)

**Layout:** Authenticated app shell

**Breadcrumb:** `🎯 Question Bank > Answered Questions`

**Page Content:**
- "**Answered Questions**"
- Subtitle: "Answered Questions from the Question Bank"

**Empty State Card:**
- "**No answered questions yet**"
- "Dive into your first quiz and discover just how much knowledge you possess! Each question you tackle not only enhances your understanding but also contributes to your growing performance history. Embrace the challenge and watch your skills flourish!"
- **[Take a Quiz →]** button (outlined, dark border)

---

#### Screen 16: Question Bank — Saved Questions (Empty State)

**Layout:** Authenticated app shell

**Breadcrumb:** `🎯 Question Bank > Saved Questions`

**Page Content:**
- "**Saved Questions**"
- Subtitle: "Saved Questions from the Question Bank"

**Empty State Card:**
- "**No saved questions yet**"
- "To save a question, just click the bookmark icon while viewing a question anywhere within **MEDIGEST**. Once you've bookmarked a few, come back here to create a quiz, review what you've saved, or filter for what's most relevant to you now."
- "Want to un-save a question? Just toggle the bookmark off. And remember, your saved questions sync across all your devices, so you can access them anytime, anywhere."

> **Design Note:** Confirms the "Saved Questions" feature (which was marked as "Not yet in Part 1" in the cross-reference). Saved Questions sync across devices and can be used to create targeted quizzes.

---

#### Screen 17: Question Bank — Custom Quizzes (Empty State)

**Layout:** Authenticated app shell

**Breadcrumb:** `🎯 Question Bank > Custom Quizzes`

**Page Content:**
- "**Custom Quizzes**"
- Subtitle: "You can create a new custom quiz using questions from our question bank."
- **[+ Create New Quiz]** button (top-right, dark filled button)

**Empty State Card:**
- "**No custom quizzes yet**"
- "Click the Create New Quiz button above to fill out a quick and easy form to build your own quizzes. Once you've made a few quizzes, revisit this page to review them and filter based on your learning needs. You can create and take as many quizzes as you'd like."
- "Need to tweak or trash a quiz? No problem — tools to edit and delete quizzes are right at your fingertips."
- "Quizzes sync across all your devices, so you can advance your learning anytime, anywhere and celebrate your progress."

---

#### Screen 18: Question Bank — Question Set Detail (Book-Level)

**Layout:** Authenticated app shell

**Breadcrumb:** `🎯 Question Bank > Internal Medicine Essentials`

**Page Content:**
- "**Internal Medicine Essentials**"
- Subtitle: "Internal Medicine Essentials from the Question Bank"

**Progress Card:**
- "**3 of 136 Questions Answered**"
- "0% Correct · 0% Incorrect · Last accessed: 2/14/2026"
- Progress bar (green/teal) at **45%**
- **[Resume Answer Questions]** button — full-width, dark/navy filled

**Section Below:**
- "**Your Recently Answered Questions**"
- *(Same empty state text as Saved Questions page — placeholder for when user has recently answered questions)*
- "To save a question, just click the bookmark icon while viewing a question anywhere within **MEDIGEST**. Once you've bookmarked a few, come back here to create a quiz, review what you've saved, or filter for what's most relevant to you now."
- "Want to un-save a question? Just toggle the bookmark off. And remember, your saved questions sync across all your devices, so you can access them anytime, anywhere."

> **Key Observation:** This is a **book-level question set detail page** — shows questions specific to one book/specialty. The "Resume Answer Questions" action continues the user's progress through that book's question bank.

---

#### Screen 19: Question Bank — Answered Questions (Populated State)

**Layout:** Authenticated app shell

**Breadcrumb:** `🎯 Question Bank > Answered Questions`

**Page Content:**
- "**Answered Questions**"
- Subtitle: "Answered Questions from the Question Bank"

**Section: "Your Recently Answered Questions"**
- Question list (vertical), each item:
  - **Status icon:** ✅ Green checkmark (correct) or ❌ Red X (incorrect)
  - **Question title:** "Treat critical limb ischemia." (educational objective, bold)
  - **Tag pills:** "Cardiovascular Medicine" | "Care type: Ambulatory" | "Patient: Age ≥65 y"
  - **Bookmark icon** (right side) — 📑 outline (not saved) or 📑 filled green (saved)
- 2 items shown

> **Key Answered Questions Design Observations:**
> - **Correct/Incorrect visual indicators** — Green ✅ and Red ❌ icons for quick scanning
> - **Question metadata tags** (pills) — Specialty, Care Type, Patient demographics
> - **Bookmark toggle** — Each answered question can be saved/unsaved from this list
> - **Question title is the educational objective** ("Treat critical limb ischemia.") — not the full question stem

---

#### Screen 20: Question Bank — Saved Questions (Populated State)

**Layout:** Authenticated app shell

**Breadcrumb:** `🎯 Question Bank > Saved Questions`

**Page Content:**
- "**Saved Questions**"
- Subtitle: "Saved Questions from the Question Bank"

**Action Banner:**
- "You can create a customized quiz from your saved questions for focused review and refine it using filters."
- **[+ Create New Quiz]** button (right side, dark filled)

**Section Header:**
- "**Saved Question (3)**"
- ☑️ **"Show educational objectives and tags for unanswered questions"** checkbox (checked)
- **[🔽 Filter]** button (right side)

**Question list (vertical), each item:**
- **Status icon:** ✅ Green checkmark (correct), ❌ Red X (incorrect), or ↩️ Gray arrow (unanswered/skipped)
- **Question title:** "Treat critical limb ischemia." (educational objective)
- **Tag pills:** "Cardiovascular Medicine" | "Care type: Ambulatory" | "Patient: Age ≥65 y"
- **Bookmark icon** (right side) — filled bookmark (saved state, removable)
- 3 items shown with all 3 status variants (correct, incorrect, unanswered)

> **Key Saved Questions Design Observations:**
> - **"Create New Quiz" from saved questions** — Users can create a focused quiz from their bookmarked questions
> - **Filter capability** — Filter saved questions (likely by specialty, status, tags)
> - **Toggle checkbox** to show/hide educational objectives and tags for unanswered questions — provides partial spoiler protection
> - **Three status states:** Correct (✅), Incorrect (❌), Unanswered (↩️/gray)
> - **Saved Questions ARE the "Saved Questions bookmark feature"** from MKSAP — ✅ NOW CONFIRMED

---

#### Screen 21: Question Bank — Custom Quiz Builder (New Custom Quiz)

**Layout:** Authenticated app shell (long scrollable form)

**Breadcrumb:** `🎯 Question Bank > Custom Quizzes > New Custom Quiz`

**Page Content:**
- "**New Custom Quiz**"
- Subtitle: "Custom Quizzes"

**Section 1: "Start with a template or build your own quiz"**
- Radio button options (4 templates):

| Template | Description |
|----------|-------------|
| ○ **Build your own** | "Make selections to create a custom quiz from the question bank." |
| ○ **Longitudinal Knowledge Assessment (LKA) Practice** | "Random questions from across all content areas with 5-minute countdown timer." |
| ○ **Exam Practice** | "50 random questions from across all content areas with a two-hour time limit." |
| ○ **Retry incorrect questions** | "Shuffle your incorrectly answered questions." |

**Section 2: "Quiz questions"**
| Field | Type | Details |
|-------|------|---------|
| **Number of Questions*** | Range slider | Min–Max scale, current value: **50** (shown in a tooltip bubble above the slider thumb) |
| **Content areas*** | Dropdown | "All Selected" — multi-select dropdown for specialties/content areas |
| **Answer status*** | Dropdown | "Incorrect" — filter by answer status (Correct, Incorrect, Unanswered) |
| ☑️ **Include saved questions (1)** | Checkbox | Include bookmarked questions in the quiz |

**Section 2b: "Advanced Filter Options (Optional)"** — expandable accordion (expanded in design)
| Field | Type | Default |
|-------|------|---------|
| **Question types** | Dropdown | "All Selected" |
| **Care type** | Dropdown | "All Selected" |
| **Patient** | Dropdown | "All Selected" |

**Section 3: "Quiz options"**
| Field | Type | Options |
|-------|------|---------|
| **Quiz Name*** | Text input | Placeholder: "Please enter name for your quiz" |
| **Quiz timing*** | Radio group (3 options) | ○ **Untimed** ("Relaxed review") · ○ **Standard Board Pace** ("(90 seconds / question)") · ○ **Fast Pace** ("(60 seconds / question)") |
| **Answer and critique visibility*** | Radio group (2 options) | ○ **Show** · ○ **Hide** |

**Submit Button:**
- **[Save Your Quiz]** — full-width, dark/navy filled button

> **Key Custom Quiz Builder Design Observations:**
> - **4 quiz templates** — "Build your own" (custom), LKA Practice, Exam Practice, Retry incorrect. This is more structured than MKSAP which only has "Build your own."
> - **LKA Practice template** — Specific ABIM exam practice mode with 5-minute countdown timer
> - **Exam Practice template** — 50 questions, 2-hour time limit — simulates real board exam conditions
> - **"Retry incorrect" template** — Dedicated mode to reshuffie failed questions — excellent study feature
> - **Question count slider** — Visual slider (not a number input) for selecting question count
> - **Answer status filter** — Can filter by Correct, Incorrect, or Unanswered — allows targeted review
> - **Include saved questions checkbox** — Option to include bookmarked questions in the quiz
> - **Advanced filters** (Question types, Care type, Patient) — Match the tag system visible on question cards
> - **Quiz timing options** — Untimed, 90s/question (Standard Board Pace), 60s/question (Fast Pace)
> - **Answer visibility toggle** — Show or Hide critique after each answer — "Hide" mode simulates exam conditions

---

#### Screen 22: Question Bank — Custom Quizzes (Populated State)

**Layout:** Authenticated app shell

**Breadcrumb:** `🎯 Question Bank > Custom Quizzes`

**Page Content:**
- "**Custom Quizzes**"
- Subtitle: "You can create a new custom quiz using questions from our question bank."
- **[+ Create New Quiz]** button (top-right)

**Quiz List:**
- "**1 Quiz**"
- Quiz card:
  - **"Quiz Name"** (user-given name, bold)
  - "136 Questions · 0% Correct · 0% Incorrect · Last accessed: 2/14/2026"
  - Progress bar at **45%**
  - **[Resume Answer Questions]** button — full-width, dark/navy filled

> **Design Note:** Custom quiz cards show the same progress/stats format as the book-level question set detail page. The user can resume a quiz from where they left off.

---

#### Screen 23: Question Bank — Question-Taking Interface (Full Question View)

**Layout:** Authenticated app shell (long scrollable page — most complex screen in the entire app)

**Breadcrumb:** `🎯 Question Bank > Endocrinology and Metabolism > Shuffle Endocrinology and Metabolism Questions`

**Page Header:**
- "**Question**"
- Educational Objective: "Treat critical limb ischemia."
- **Timer:** "MM:SS" (top-right, teal text — countdown timer when quiz is timed)
- **Tag pills:** "Cardiovascular Medicine" | "Care type: Ambulatory" | "Patient: Age ≥65 y"
- **Icons (top-right):** 📋 Copy/Report icon | 📑 Bookmark icon

**Section 1: Clinical Vignette (Question Stem)**
- Long-form clinical scenario text:
  - "A 77-year-old man is evaluated for 4 weeks of progressive left foot pain and calf pain that worsens with ambulation. Medical history is significant for hypertension and dyslipidemia. Medications are amlodipine and rosuvastatin."
  - Physical examination findings
  - "The ankle-brachial index is 0.62 on the right and unobtainable on the left."

**Section 2: Laboratory Studies Table**
| Lab Value | Today | On hospitalization | Flag |
|-----------|-------|--------------------|------|
| Calcium ⓘ | 10.0 mg/dL (2.5 mmol/L) | 11.4 mg/dL (2.8 mmol/L) | **H** (High) |
| Creatinine ⓘ | — | 0.9 mg/dL (79.6 μmol/L) | — |
| Parathyroid hormone ⓘ | — | <10 pg/mL (10 ng/L) | **L** (Low) |
| Thyroid-stimulating hormone ⓘ | — | 0.5 μIU/mL (0.5 mIU/L) | — |
| 1,25-Dihydroxyvitamin D ⓘ | — | 70 pg/mL (168 pmol/L) | **H** (High) |
| 25-Hydroxyvitamin D ⓘ | — | 30 ng/mL (75 nmol/L) | **L** (Low) |

> **Lab Table Design Notes:**
> - **ⓘ info icons** next to each lab name — tooltips/popovers with reference ranges
> - **H/L flags** — High/Low indicators in small badges (green for normal, red for abnormal? — appears as small lettered badges)
> - **Two-column comparison** (Today vs. On hospitalization) — common MKSAP question format

**Section 3: Question Prompt**
- "**Which of the following is the most appropriate next step in management**"

**Section 4: Answer Choices**
- Multiple-choice single-best-answer format:

| Icon | Answer | Peer Stats | Status |
|------|--------|------------|--------|
| ⚪ | Initiate aspirin and clopidogrel | 5% of peers chose Option A | — |
| ✅ ⭕ | **Initiate vorapaxar** | **68% of peers chose Option B** | "You answered **Option B** in 21 seconds" — highlighted green |
| ❌ ⭕ | **Perform invasive angiography** | **22% of peers chose Option C** | "You answered **Option C** in 21 seconds" — highlighted red |
| ⚪ | Perform magnetic resonance angiography | 4% of peers chose Option D | — |

**Answer State Indicators:**
- ✅ Green circle + highlight = **Correct answer** (Option B)
- ❌ Red circle + highlight = **User's incorrect selection** (Option C)
- ⚪ Gray = **Not selected, not correct**
- **Peer statistics** shown for ALL options ("X% of peers chose Option Y")
- **Time tracking** — "You answered Option X in 21 seconds" — response time recorded per question

**[Submit]** button — Full-width, dark/navy filled

**Section 5: Answer and Critique**
- Long-form explanation text (multiple paragraphs):
  - Opens with the correct explanation for the clinical scenario
  - **Bold option references:** "(**Option A**)", "(**Option B**)", "(**Option D**)" — each option explained inline
  - Vorapaxar (Option B) explanation with clinical trial reference (TRA 2°P-TIMI 50 trial)
  - "Noninvasive imaging studies such as magnetic resonance angiography **(Option D)** would result in treatment delays..."

**Section 6: Key Point**
- Gray/light card:
  - "**Key Point**"
  - Bullet point: "In patients with critical limb ischemia, immediate invasive angiography with endovascular revascularization is often the most effective strategy to preserve tissue viability."

**Section 7: Reference**
- Gray/light card:
  - "**Reference**"
  - Full citation: "Gornik HL, Aronow HD, Goodney PP, et al. 2024 ACC/AHA/AACVPR/APMA/ABC/SCAI/SVM/SVN/SVS/SIR/VESS guideline for the management of lower extremity peripheral artery disease..."
  - **PMID link:** "PMID: 38743929" (clickable link)
  - DOI: "doi:10.1161/CIR.0000000000001251"

**Section 8: Related Syllabus Content**
- Gray/light card:
  - "**Related Syllabus Content:**"
  - "Peripheral Artery Disease"
  - Bullet: "Interventional Therapy for Peripheral Artery Disease" — **"Read Now! →"** link (teal/green)

**Section 9: Learning Plan Topic**
- Gray/light card:
  - "📋 Learning Plan Topic:"
  - "**Calcium and Metabolic Bone Disorders**"
  - "**This topic includes:**"
    - 10 multiple-choice questions
    - 4 syllabus sections
    - 2 Learning Links
    - 7 Board Basics topics
    - 22 flashcards
  - **[+ Add Topic]** button (outlined, dark)
  - **"View Learning Plan Topic →"** link (right side, teal/green)

**Section 10: Bottom Navigation**
- **[← Previous]** button (left)
- **[Next →]** button (right, filled green/teal)

**Section 11: Question Footer Stats**
- "Question ID cvqpp24023 was last updated in February 2025."
- **[✅ Total 0 Correct]** — green outlined badge
- **[❌ Total 3 Incorrect]** — red filled badge
- "Review recently answered questions →" link

> **Key Question Interface Design Observations (MAJOR FINDINGS):**
> 
> 1. **Peer Answer Statistics ARE in the design** — "X% of peers chose Option Y" shown for all options. This was previously marked as "Not in Figma" — ✅ NOW CONFIRMED.
> 
> 2. **Response Time Tracking** — "You answered Option X in 21 seconds" — per-question timing is tracked and displayed. This was NOT in MKSAP analysis or original requirements. NEW FEATURE.
> 
> 3. **Lab Values Table** — Structured table with ⓘ info tooltips and H/L abnormal flags. Complex medical data display component needed.
> 
> 4. **Answer and Critique** — Long-form explanation with inline option references (**Option A**, **Option B**, etc. in bold). Rich text rendering required.
> 
> 5. **Key Point section** — Separate from Answer and Critique. Summarized takeaway for quick review.
> 
> 6. **Reference with PMID link** — Full academic citation with clickable PubMed link. Must support external links.
> 
> 7. **Related Syllabus Content** — Cross-links from question to relevant syllabus topics with "Read Now!" action. This confirms deep cross-module navigation.
> 
> 8. **Learning Plan Topic** — Each question can be linked to a Learning Plan topic, showing its complete content breakdown (questions, sections, links, flashcards). The "+ Add Topic" button lets users add it to their Learning Plan.
> 
> 9. **Question ID + Last Updated date** — Unique question identifier shown to users (useful for reporting issues). Content versioning date shown.
> 
> 10. **Total Correct/Incorrect per question** — Cumulative score display (user has attempted this question 3 times total, 0 correct, 3 incorrect).
> 
> 11. **"Review recently answered questions"** link — Quick navigation to Answered Questions page.
> 
> 12. **No strikethrough/elimination UI** — Still not visible in the answer choices. Feature may not be implemented.
> 
> 13. **Timer (MM:SS)** — Countdown timer in top-right for timed quiz modes (Standard Board Pace, Fast Pace).
> 
> 14. **Copy/Report icon** — Next to bookmark icon — likely for reporting incorrect questions or copying question ID.

---

#### Summary of New/Updated Requirements from Part 2 Figma Designs

| # | Requirement | Source | Impact on Existing Requirements |
|---|-------------|--------|--------------------------------|
| 21 | **Question Bank main page with 3-stat summary** (Completion, Average Score, Custom Quizzes) | Figma Part 2 | Updates FR-4 — specific stat widgets for Question Bank defined |
| 22 | **Question Sets grid** mirrors book card pattern with Flashcards/Board Basics quick links | Figma Part 2 | New UX pattern — consistent card design across modules |
| 23 | **"Shuffle Questions"** as a prominent action from stats bar | Figma Part 2 | New — adds randomized question mode (FR-4.3) |
| 24 | **Saved Questions page** with filtering and "Create New Quiz" action | Figma Part 2 | ✅ Confirms FR-4.11 — Saved Questions feature now fully designed |
| 25 | **Custom Quiz Builder** with 4 templates (Build own, LKA, Exam, Retry incorrect) | Figma Part 2 | **Major enhancement** — updates FR-4.6 with specific templates and configuration options |
| 26 | **LKA Practice mode** (random questions, 5-min countdown) | Figma Part 2 | New — adds specific ABIM exam prep template |
| 27 | **Exam Practice mode** (50 questions, 2-hour limit) | Figma Part 2 | New — adds board exam simulation template |
| 28 | **"Retry incorrect" quiz template** | Figma Part 2 | New — dedicated incorrect-question reshuffling mode |
| 29 | **Quiz timing options** (Untimed, 90s/question, 60s/question) | Figma Part 2 | New detail — updates FR-4.6 with specific timing configs |
| 30 | **Answer and critique visibility toggle** (Show/Hide) | Figma Part 2 | New — exam simulation mode hides explanations |
| 31 | **Advanced question filters** (Question types, Care type, Patient) | Figma Part 2 | New — adds multi-faceted filtering to quiz builder |
| 32 | **Peer answer statistics** on question interface ("X% chose Option Y") | Figma Part 2 | ✅ Confirms previously missing feature — adds FR-4.9 |
| 33 | **Response time tracking** per question ("answered in 21 seconds") | Figma Part 2 | **New feature** — not in MKSAP or original requirements |
| 34 | **Lab values table** with info tooltips and H/L abnormal flags | Figma Part 2 | New UI component — structured medical data display |
| 35 | **Key Point section** (separate from Answer and Critique) | Figma Part 2 | New — adds standalone key takeaway section to questions |
| 36 | **Reference section** with PMID links | Figma Part 2 | Confirms FR-4.7 — academic citations with external PubMed links |
| 37 | **Related Syllabus Content** cross-links in question view | Figma Part 2 | New — deep cross-module navigation from questions to syllabus |
| 38 | **Learning Plan Topic** card in question view with content breakdown | Figma Part 2 | New — cross-module link to Learning Plan with "+ Add Topic" action |
| 39 | **Question ID + Last Updated date** visible to users | Figma Part 2 | New — content versioning transparency |
| 40 | **Cumulative correct/incorrect count** per question | Figma Part 2 | New — tracks repeat attempts |
| 41 | **Timer (MM:SS)** for timed quiz modes | Figma Part 2 | Confirms timed quiz implementation needed |
| 42 | **Educational Objective** as question title/identifier | Figma Part 2 | New — questions identified by objective, not by number |
| 43 | **Tag system** (Specialty, Care type, Patient demographics) on questions | Figma Part 2 | New — multi-dimensional tagging for questions |
| 44 | **"Show educational objectives for unanswered"** toggle | Figma Part 2 | New — spoiler protection for saved unanswered questions |

---

### G. Figma UI/UX Design Analysis (Part 3 — `part3.pdf`)

> **Source:** `part3.pdf` (10 pages)
> **Modules Covered:** Learning Plan, CORE (Confirmation of Relevant Education), Board Basics, Flashcards, CME/MOC/CPD
> **Screens Documented:** 10 (Screens 24–33)

---

#### Screen 24: Learning Plan — Empty State

**Layout:** Authenticated app shell (sidebar + header)

**Page Header:**
- "**Learning Plan**"
- Subtitle: "Your personalized path to medical mastery"
- **[+ Add New Topic]** button (dark filled, top-right)

**Empty State Card:**
- "**Ready to start your journey?**"
- "Click the Add Topics button to choose syllabus topics you want to study. Your Learning Plan is a customized selection of topics for you to focus on, with trackable activities for each topic."
- "Once you're satisfied with your progress on a topic, you can remove it from your plan. You'll find opportunities to add topics throughout **MEDIGEST**."

> **Key Observations:**
> - **Learning Plan is a user-curated selection** — not auto-generated, users add topics manually
> - **Topics can be removed** — the plan is fully user-managed
> - **Topics can be added throughout the app** — confirms the "+ Add Topic" action seen in Question Bank (Part 2, Screen 23)
> - **No progress stats in the empty state** — stats bar only appears when topics are added (contrast with Question Bank)

---

#### Screen 25: Learning Plan — Add New Topic (Topic Picker)

**Layout:** Authenticated app shell

**Breadcrumb:** `🎓 Learning Plan > Add New Topic`

**Page Header:**
- "**Add Topics**"
- Subtitle: "Add new topics to your learning plan"

**Topic Listing:**
- "**195 Topics**" — total topic count displayed
- **[🔽 Filter]** button (top-right)
- **2-column grid of topic cards:**
  - Each card shows:
    - 📖 Book icon
    - **Topic Name** (e.g., "Abdominal and Pelvic Pain")
    - **Specialty tag** (e.g., "Cardiovascular Medicine")
    - Progress: "0/2 questions completed · 0/3 tasks completed"
    - **[+]** icon button to add topic (left column cards)
    - **[🗑️ red square]** icon button to remove topic (right column cards — already added)
- **Pagination:** `← 1 2 3 4 5 ... 33 →` — numbered pagination with 33 total pages

> **Key Observations:**
> - **195 topics available** — confirms scale of content library
> - **Topic cards show dual progress** — questions completed AND tasks completed
> - **Add/Remove toggle** — left column shows + to add, right column shows red icon for already-added topics
> - **Pagination with 33 pages** — ~6 topics per page × 33 pages = ~195 topics
> - **Filter capability** — topics can be filtered (likely by specialty)
> - **"Tasks"** — introduces a new concept: tasks associated with topics (beyond just questions)

---

#### Screen 26: Learning Plan — Populated State

**Layout:** Authenticated app shell

**Page Header:**
- "**Learning Plan**"
- Subtitle: "Your personalized path to medical mastery"
- **[+ Add New Topic]** button (dark filled, top-right)

**Topic Listing:**
- "**Included Topics (4)**" — count of topics in plan
- **[🔽 Filter]** button (top-right of list)
- **2-column grid of topic cards** (same card pattern as Add Topics):
  - Each card shows:
    - 📖 Book icon
    - **Topic Name** (e.g., "Abdominal and Pelvic Pain")
    - **Specialty tag** (e.g., "Cardiovascular Medicine")
    - **[🗑️ red square]** icon button (remove from plan)
    - Progress: "0/2 questions completed · 0/3 tasks completed"
    - **[Continue]** button (green filled) — for in-progress topics
    - **[Start]** button (green filled) — for not-yet-started topics

> **Key Observations:**
> - **Two CTA states:** "Continue" for in-progress topics, "Start" for not-started topics
> - **Remove button (🗑️)** on each card — confirms topics can be removed from plan
> - **Same card component** used in both Add Topics and Learning Plan pages — reusable component
> - **Filter available on the populated plan** — can filter included topics
> - **No overall progress stats bar** — unlike Question Bank or Dashboard, Learning Plan has no summary stats

---

#### Screen 27: CORE — Confirmation of Relevant Education (Progress Page)

**Layout:** Authenticated app shell

**Page Header:**
- "**Confirmation of Relevant Education (CORE)**" with badge count "4/11 Badges Earned"
- Subtitle: "Earn your Confirmation of Relevant Education certificate and celebrate lifelong learning"

**CORE Progress Section:**
- "**CORE Progress**"
- Explanation: "Monitor your progress in CORE areas to unlock quizzes, earn badges, and get your CORE certificate. Score 50% or higher on your last 30 questions to access the CORE Quiz."

**Badge Progress List (11 items):**
Each badge row showing:
- **Badge number** (1-11) in a colored square (green for completed, teal for in-progress, gray for pending)
- **Badge name** (medical specialty)
- **Status action button** (right-aligned):
  - "Review →" — for completed badges
  - "Continue →" — for in-progress badges
  - "Start Now →" — for pending badges
- **Progress bar** with percentage (100%, 45%, 00%)
- **Status label** (Completed / In Progress / Pending)

**Badge List (in order):**
1. Cardiovascular Medicine — ✅ Completed (100%) — Review →
2. Endocrinology and Metabolism — ✅ Completed (100%) — Review →
3. Foundations of Clinical Practice and Common Symptoms — ✅ Completed (100%) — Review →
4. Gastroenterology and Hepatology — ✅ Completed (100%) — Review →
5. Hematology — 🔄 In Progress (45%) — Continue →
6. Infectious Disease — ⏳ Pending (00%) — Start Now →
7. Interdisciplinary Medicine and Dermatology — ⏳ Pending (00%) — Start Now →
8. Nephrology — ⏳ Pending (00%) — Start Now →
9. Oncology — ⏳ Pending (00%) — Start Now →
10. Pulmonary and Critical Care Medicine — ⏳ Pending (00%) — Start Now →
11. Rheumatology — ⏳ Pending (00%) — Start Now →

> **Key Observations:**
> - **CORE is a certification system** — users earn a "Confirmation of Relevant Education certificate"
> - **11 medical specialty badges** — one per specialty area
> - **50% threshold rule** — must score 50%+ on the last 30 questions to access the CORE Quiz
> - **3 badge states**: Completed, In Progress, Pending — with distinct colors and actions
> - **Badge count in header** — "4/11 Badges Earned" shows overall progress
> - **Linear vertical list** — NOT a grid, uses a stacked progress bar layout
> - **This is a gamification/certification layer** on top of the Question Bank
> - **Reveals the 11 core specialties** of the MEDIGEST platform

---

#### Screen 28: CORE — Specialty Detail (Cardiovascular Medicine)

**Layout:** Authenticated app shell

**Breadcrumb:** `☑️ CORE > Cardiovascular Medicine`

**Page Header:**
- "**Cardiovascular Medicine**"
- Subtitle: "Score 50% or higher on your last 30 questions to access the CORE Quiz."

**Progress Card:**
- "**3 of 136 Questions Answered**"
- Stats: "0% Correct · 0% Incorrect · Last accessed: 2/14/2026"
- **Progress bar:** 45%
- **[Resume Answer Questions]** button (green filled, full-width)

**Recently Answered Questions Section:**
- "**Your Recently Answered Questions**"
- Question rows (same pattern as Question Bank Answered Questions — Screen 19):
  - ✅ Green checkmark or ❌ Red X icon
  - Educational objective: "Treat critical limb ischemia."
  - Tags: "Cardiovascular Medicine" | "Care type: Ambulatory" | "Patient: Age ≥65 y"
  - Bookmark icon (right side)

> **Key Observations:**
> - **CORE detail page reuses the Question Bank question set detail pattern** — same layout as Screen 18
> - **136 questions per CORE specialty** — substantial question pool
> - **Same question row component** — reusable across Question Bank and CORE modules
> - **50% threshold reminder** — repeated from CORE main page
> - **Last accessed date** and correct/incorrect percentages maintained per specialty

---

#### Screen 29: Board Basics — Main Page

**Layout:** Authenticated app shell

**Page Header:**
- "**Board Basics**"
- Subtitle: "A succinct, digest-style review to help you pass your Boards"

**Stats Bar (4 stats):**
| Stat | Value | Detail |
|------|-------|--------|
| 📈 Overall Progress | **52%** | 450 / 870 pages |
| 🎯 Bank Average Score | **85%** | Last 10 quizzes |
| ⏱️ Study Time | **12.5h** | This week |
| 🔥 Study Streak | **7 days** | Keep it up! |

**Books Grid:**
- "**My Books (3)**" with **[📝 Notes & Highlights]** action button (top-right)
- **2-column grid of book cards:**
  - Each card shows:
    - 📖 Book icon
    - **Book title:** "Internal Medicine Essentials"
    - **Metadata:** "Topic Name · Lesson Name · Last accessed: 2/14/2026"
    - **Progress bar:** 45%
    - **Quick links:** "Flashcards →" | "Question Bank →"
    - **[Continue]** button (outlined)

> **Key Observations:**
> - **Board Basics has its own dedicated module** — separate from the main Syllabus
> - **4-stat summary bar** — same pattern as Dashboard but with Board-specific stats
> - **New stat: "Study Time"** (12.5h this week) — **first appearance of time tracking in a stats bar**
> - **New stat: "Study Streak"** (7 days) — **gamification feature, first appearance**
> - **"Notes & Highlights"** action button — confirms note-taking/highlighting feature with a dedicated overview page
> - **Book cards identical to Syllabus** — same component reuse pattern
> - **Quick links include "Flashcards" and "Question Bank"** — cross-module navigation from Board Basics
> - **870 total pages** — confirms substantial Board Basics content library
> - **Board Basics is essentially a parallel Syllabus** — same structure but focused on board prep content

---

#### Screen 30: Flashcards — Main Page

**Layout:** Authenticated app shell

**Page Header:**
- "**Flashcards**"
- Subtitle: "Learn through repeated exposure to quick-study concepts"

**Stats Bar (3 stats):**
| Stat | Value | Detail |
|------|-------|--------|
| 📈 Overall Progress | **52%** | 450 / 870 pages |
| ⏱️ Study Time | **12.5h** | This week |
| 🔥 Study Streak | **7 days** | Keep it up! |

**Flashcard Decks Grid:**
- "**Flashcard Decks (4)**"
- **2-column grid of deck cards:**
  - Each card shows:
    - 📖 Book icon
    - **Deck title:** "Internal Medicine Essentials"
    - **Metadata:** "215 Flashcards · Last accessed: 2/14/2026"
    - **Progress bar:** 45%
    - **[Answer Flashcards]** button (outlined)

> **Key Observations:**
> - **Flashcards are grouped into "Decks"** — organized by book/specialty
> - **215 flashcards per deck** — significant volume
> - **3-stat bar** (no "Bank Average Score" — makes sense since flashcards aren't scored)
> - **Study Time and Study Streak** reappear here — consistent gamification across modules
> - **"Answer Flashcards"** as CTA — confirms flashcards have a question/answer interaction pattern
> - **Same card component** used but with "Answer Flashcards" instead of "Continue"

---

#### Screen 31: Flashcard — Question Side

**Layout:** Authenticated app shell

**Breadcrumb:** `🎴 Flashcards > Internal Medicine Essentials`

**Flashcard Display:**
- **Dark gradient card** (dark teal/green to dark, full-width)
  - Label: "Question"
  - **Question text:** "Severe pulmonary hypertension with cardiac shunt reversal (right-to-left shunting)"
  - **[Click to reveal answer]** link (centered, light text)

**Navigation Controls:**
- **[← Previous]** button (left, outlined)
- **Position indicator:** "2/215 Flashcards" (center)
- **[Next →]** button (right, filled dark teal)

> **Key Observations:**
> - **Simple, clean flashcard UI** — single card with question on dark gradient background
> - **"Click to reveal answer"** — standard flashcard tap-to-flip mechanic
> - **Position counter** — "2/215 Flashcards" shows current position in deck
> - **Previous/Next navigation** — linear progression through deck
> - **No self-rating system** (e.g., "Easy/Hard/Again") — simpler than Anki-style flashcards
> - **Questions are medical terms/conditions** — not full clinical vignettes like Question Bank

---

#### Screen 32: Flashcard — Answer Side

**Layout:** Authenticated app shell

**Breadcrumb:** `🎴 Flashcards > Internal Medicine Essentials`

**Flashcard Display:**
- **Dark gradient card** (green-teal to dark, full-width — same style but slightly different gradient hue)
  - Label: "Answer"
  - **Answer text:** "Eisenmenger syndrome"
  - **[Related Text →]** link (centered, navigates to syllabus content)
  - **[Click to hide answer]** link (centered, light text)

**Navigation Controls:**
- Same as Question side: **← Previous** | "2/215 Flashcards" | **Next →**

> **Key Observations:**
> - **"Related Text →"** link — **NEW: cross-links flashcard answers to related Syllabus text**
> - **Answer is concise** — short medical term answers (not long explanations)
> - **"Click to hide answer"** — can toggle back to question state
> - **Same card component** — reuses the gradient card but changes label from "Question" to "Answer"
> - **Cross-module navigation (Flashcard → Syllabus)** — deep linking throughout platform

---

#### Screen 33: CME/MOC/CPD — Main Page

**Layout:** Authenticated app shell

**Page Header:**
- "**CME/MOC/CPD**"
- Subtitle: "Submissions for continuing education credits"

**Credit Summary Card:**
- "**0 credits claimed** · 0.5 credits ready to claim"
- **[Claim 0.5 Credits Now!]** button (teal filled, right-aligned)
- Details:
  - "Up to a maximum of 300 credits available from December 31 – December 30, 2026"
  - "CME availability will renew on a calendar-year basis."
  - "Earn up to 0.25 AMA PRA Category 1 Credits™ and 0.25 MOC points for each question answered as long as you maintain a score of 50% correct."

**CME/MOC Submissions:**
- "**CME/MOC Submissions**"
- Empty state: "No submission history yet"
- "When you claim Continuing Medical Education (CME) credits and/or American Board of Internal Medicine (ABIM) Maintenance of Certification (MOC) points, they will appear here. You can view or print your submission history by year."

**ACP MKSAP CME, MOC, and CPD Information for Physicians:**
- Detailed information section with multiple subsections:

  **1. ACP/AMA CME Credits:**
  - Accredited by ACCME (Accreditation Council for Continuing Medical Education)
  - Maximum of 300 AMA PRA Category 1 Credits™
  - 0.25 credits per question (earning ≥50% correct)
  - MOC points equivalent to CME credits claimed
  - Credits available December 31, 2025 – December 30, 2026
  - Calendar-year basis, resets January 1
  - Credits must be submitted before 11:59 PM EST on December 31

  **2. How to Submit for CME/MOC:**
  - Earn credit by answering ≥1 of 2 questions correctly (≥50%)
  - Each question qualifies for 0.25 AMA PRA Category 1 Credits™ or ABIM MOC point
  - Access through Questions Bank tab
  - "Claim Credit Now" button to submit
  - Track progress on CME/MOC/CPD page

  **3. Royal College of Physicians & Surgeons of Canada: MOC Credits:**
  - Section 3 Accredited Self-Assessment Program
  - Maximum 300 hours (auto-calculated)
  - Can convert to AMA credits at www.ama-assn.org/go/internationalcme
  - Qatar Council arrangement for QCHP CME/CPD — Section 3 credits

  **4. How Royal College Fellows can earn MOC credits:**
  - Email confirmation of completion
  - Royal College MyMOC site to input hours
  - ACP MKSAP activity number: 00017040

  **5. Royal Australasian College of Physicians: CPD Credits:**
  - RACP Continuing Professional Development (CPD) hours
  - MyCPD Category 1 – Educational Activities
  - Links to MyCPD framework and MyCPD interactive Handbook

> **Key Observations:**
> - **This is a DENSE content page** — mostly text/information about credit earning policies
> - **"Claim Credits Now"** is the primary CTA — users manually submit credit claims
> - **0.25 credits per question** at ≥50% correct threshold
> - **300 credits maximum per year** — calendar-year renewal cycle
> - **Multi-country support:**
>   - 🇺🇸 AMA PRA Category 1 Credits™ (US physicians)
>   - 🇺🇸 ABIM MOC points (US board certification)
>   - 🇨🇦 Royal College of Physicians & Surgeons of Canada MOC
>   - 🇶🇦 Qatar Council QCHP CME/CPD
>   - 🇦🇺 Royal Australasian College RACP CPD
> - **Submission history by year** — annual tracking needed
> - **External links** to international medical organizations
> - **Calendar-year credit window** (Dec 31 – Dec 30) — important business logic
> - **The 50% score threshold ties into both CORE and CME** — shared business rule

---

#### Part 3 Summary — New/Updated Requirements

| # | Requirement | Source | Notes |
|---|-------------|--------|-------|
| 45 | **Learning Plan module** — user-curated topic selection with trackable activities | Figma Part 3 | New — confirms FR-6 with full UI specification |
| 46 | **"Add New Topic" picker** — 195 topics, paginated, with add/remove toggle | Figma Part 3 | New — topic browsing with 33-page pagination |
| 47 | **Topic cards with dual progress** — questions completed + tasks completed | Figma Part 3 | New — "tasks" concept introduced alongside questions |
| 48 | **Learning Plan topic cards** have Start/Continue CTAs | Figma Part 3 | New — progressive CTA based on user progress |
| 49 | **CORE (Confirmation of Relevant Education)** — 11-badge certification system | Figma Part 3 | New — gamification/certification layer on Question Bank |
| 50 | **CORE 50% threshold rule** — score ≥50% on last 30 questions to access CORE Quiz | Figma Part 3 | New — important business logic for badge earning |
| 51 | **CORE badge states** — Completed/In Progress/Pending with Review/Continue/Start Now actions | Figma Part 3 | New — 3-state progress tracking per specialty |
| 52 | **11 core medical specialties** defined for CORE | Figma Part 3 | New — defines the platform's specialty taxonomy |
| 53 | **Board Basics module** — separate digest-style review module | Figma Part 3 | New — parallel to Syllabus but for board prep |
| 54 | **Study Time tracking** — weekly hours displayed in stats bar (12.5h) | Figma Part 3 | **New feature** — session time tracking needed |
| 55 | **Study Streak** — consecutive day count gamification (7 days) | Figma Part 3 | **New gamification feature** — daily engagement tracking |
| 56 | **Notes & Highlights** overview page accessible from Board Basics | Figma Part 3 | Confirms note-taking feature with a dedicated summary view |
| 57 | **Flashcard module** — decks organized by book/specialty, 215+ cards per deck | Figma Part 3 | New — confirms FR-5 with full UI specification |
| 58 | **Flashcard interaction** — question/answer flip card with Previous/Next navigation | Figma Part 3 | New — simple tap-to-reveal, no self-rating system |
| 59 | **Flashcard → Syllabus "Related Text" link** | Figma Part 3 | New — cross-module deep linking from flashcard answers |
| 60 | **CME/MOC/CPD module** — credit claiming, submission tracking, multi-country support | Figma Part 3 | New — confirms FR-7 with full specification |
| 61 | **Credit earning rule:** 0.25 credits per question at ≥50% correct | Figma Part 3 | New — important business logic for credit calculation |
| 62 | **300 credits max per calendar year** — December 31 to December 30 cycle | Figma Part 3 | New — annual credit cap and renewal logic |
| 63 | **Multi-country CME support** — AMA, ABIM MOC, Canadian Royal College, Qatar QCHP, Australian RACP | Figma Part 3 | New — 5 international accreditation bodies supported |
| 64 | **"Claim Credits Now"** manual submission action | Figma Part 3 | New — user-initiated credit claiming workflow |
| 65 | **Submission history by year** — annual credit tracking and print capability | Figma Part 3 | New — historical credit record keeping |
| 66 | **MKSAP activity number** (00017040) for Royal College MOC reporting | Figma Part 3 | New — platform identifier for external credit submission |

---

## 2. Cross-Reference & Gap Analysis

### Items in Shopify PDF NOT yet in Figma (Parts 1-3):
| Item | Status | Action Required |
|------|--------|-----------------|
| Webhook URL endpoint | Not shown in Figma (backend-only) | ✅ Expected — backend architecture, no UI needed |
| "Redeem Purchases" page (user profile) | ❌ **NOT in any Figma Part (1-3)** | ⚠️ Must clarify with designer — may be handled via Settings page |
| Admin Dashboard for purchase restoration | Not shown in Figma (admin-only) | ✅ Expected — Django Admin handles this |
| Email notifications (welcome + access) | ❌ **NOT in any Figma Part (1-3)** | ⚠️ Email templates needed — must be designed separately |

### Items in MKSAP NOT in Figma (Parts 1-3):
| Item | Status | Action Required |
|------|--------|-----------------|
| "Saved Questions" bookmark feature | ✅ **CONFIRMED in Figma Part 2** — dedicated Saved Questions page with filtering, quiz creation | ✅ Resolved |
| Strikethrough answer elimination | ❌ **NOT in any Figma Part (1-3)** | Likely not included — confirm with designer |
| Peer answer statistics on Q&A | ✅ **CONFIRMED in Figma Part 2** — "X% of peers chose Option Y" shown for all answers | ✅ Resolved |
| "Mark topic as completed" checkbox | ✅ **CONFIRMED in Figma Part 1** — present in Reading Interface | ✅ Resolved |
| "Getting Started" video / onboarding | ❌ **NOT in any Figma Part (1-3)** | Likely removed — confirm with designer |
| Help (external link in sidebar) | ✅ **Present as "Help Center" in sidebar** (all Parts) | ✅ Resolved |
| Reset progress functionality | ❌ **NOT in any Figma Part (1-3)** | ⚠️ May be handled backend-only or via Settings — clarify with designer |
| Right-side "In this topic" TOC panel | ❌ **Replaced by left-side specialty accordion** | Design change — adapt implementation |
| Right-side "Notes" tab in reader | ❌ **Replaced by top toolbar "Note" button** | Design change — adapt implementation |

### Items Newly Confirmed by Figma Part 1:
| Item | Status | Details |
|------|--------|---------|
| **Library/Store merged into Syllabus** | ✅ CONFIRMED | "My Books" + "Store" are tabs within the Syllabus page |
| **Dark mode toggle present everywhere** | ✅ CONFIRMED | Moon icon in top-right of all screens (auth + app) |
| **Notification bell** | ✅ CONFIRMED | Bell icon in top bar — notification system needed |
| **"Test your knowledge" in reader** | ✅ NEW FEATURE | Embedded quiz widget inside reading content |
| **Topic pagination** | ✅ NEW DESIGN | Previous/Next with dot indicators instead of long scroll |
| **Today's Goals** | ✅ NEW FEATURE | Daily goal tracking on Dashboard |
| **Quick Actions** | ✅ NEW FEATURE | Shortcut buttons on Dashboard |
| **Stats bar** | ✅ NEW COMPONENT | Reusable 4-stat summary on Dashboard and Syllabus |
| **Font controls in reader** | ✅ CONFIRMED | Inline A-/A/A+ controls in reading toolbar |
| **Bookmark page** | ✅ CONFIRMED | Dedicated bookmarks page under Syllabus |
| **Notes & Highlights pages** | ✅ CONFIRMED | Two-level: list → detail (highlights + notes separated) |

### Items Newly Confirmed by Figma Part 2:
| Item | Status | Details |
|------|--------|---------|
| **Saved Questions** | ✅ CONFIRMED | Dedicated page with filtering + "Create Quiz from Saved" action |
| **Peer answer statistics** | ✅ CONFIRMED | "X% of peers chose Option Y" shown for all answer choices |
| **Custom Quiz Builder** | ✅ CONFIRMED | Full form with 4 templates, question config, timing, visibility toggle |
| **LKA Practice template** | ✅ NEW FEATURE | Random questions with 5-minute countdown (ABIM-specific) |
| **Exam Practice template** | ✅ NEW FEATURE | 50 questions, 2-hour time limit (board exam simulation) |
| **Retry incorrect template** | ✅ NEW FEATURE | Reshuffles incorrectly answered questions |
| **Response time tracking** | ✅ NEW FEATURE | Per-question timing ("answered in 21 seconds") |
| **Lab values table component** | ✅ NEW COMPONENT | Structured table with ⓘ tooltips and H/L abnormal flags |
| **Key Point section** | ✅ NEW COMPONENT | Standalone summary card separate from Answer & Critique |
| **Reference with PMID** | ✅ CONFIRMED | Academic citations with clickable PubMed links |
| **Related Syllabus Content** | ✅ NEW FEATURE | Cross-links from question to relevant syllabus topics |
| **Learning Plan Topic card** | ✅ NEW FEATURE | Question-level link to Learning Plan with "+ Add Topic" |
| **Question tagging** (specialty, care type, patient) | ✅ CONFIRMED | Multi-dimensional tag system on all questions |
| **Answer & critique visibility** | ✅ NEW FEATURE | Show/Hide toggle for exam simulation mode |

### Items Newly Confirmed by Figma Part 3:
| Item | Status | Details |
|------|--------|---------|
| **Learning Plan module** | ✅ CONFIRMED | Full UI: empty state, topic picker (195 topics, paginated), populated state with Start/Continue CTAs |
| **"Tasks" per topic** | ✅ NEW CONCEPT | Topics have both questions AND tasks with separate completion tracking |
| **CORE certification system** | ✅ NEW MODULE | 11 medical specialty badges, 50% threshold to access CORE Quiz, certificate earning |
| **11 core medical specialties** | ✅ CONFIRMED | Cardio, Endocrinology, Foundations, Gastro, Hematology, Infectious Disease, Interdisciplinary, Nephrology, Oncology, Pulmonary, Rheumatology |
| **Board Basics module** | ✅ NEW MODULE | Separate digest-style review, parallel to Syllabus with book cards and cross-module links |
| **Study Time tracking** | ✅ NEW FEATURE | Weekly hours tracked and displayed in stats bars (Board Basics, Flashcards) |
| **Study Streak gamification** | ✅ NEW FEATURE | Consecutive day tracking displayed in stats bars |
| **Notes & Highlights overview** | ✅ CONFIRMED | Accessible from Board Basics as a dedicated action |
| **Flashcard module** | ✅ CONFIRMED | Full UI: deck listing, question/answer flip cards with Previous/Next navigation, "Related Text" cross-links |
| **Flashcard → Syllabus deep linking** | ✅ NEW FEATURE | "Related Text →" on answer cards links to syllabus content |
| **CME/MOC/CPD module** | ✅ CONFIRMED | Full UI: credit summary, claim action, submission history, multi-country accreditation info |
| **Credit earning business logic** | ✅ NEW DETAIL | 0.25 credits/question at ≥50% correct, 300 max/year, calendar-year cycle |
| **Multi-country accreditation** | ✅ NEW DETAIL | US (AMA/ABIM), Canada (Royal College), Qatar (QCHP), Australia (RACP) |
| **MKSAP activity number** | ✅ NEW DETAIL | ID 00017040 for external credit submission |

### Missing Artifact:
| Item | Details |
|------|---------| 
| **Webhook JSON Schema** | The PDF references an attached `.json` file with the webhook payload schema. **This file was NOT provided in the project directory.** Must be requested from the client. |

### Items from Live Store NOT yet reflected in Figma or Requirements:
| Item | Status | Action Required |
|------|--------|-----------------|
| "Coming Soon" books (5 titles) | Not visible in Part 1 Store tab | Platform must handle unavailable content gracefully — may show as locked items |
| Book Preview PDFs (free samples) | Partially covered by "Learn More!" link in Store tab | Confirm: does "Learn More!" open a preview modal? |
| Customer Reviews on product pages | Not in Figma Part 1 | Decide if reviews should appear in our Store tab |
| Content Protection / DRM | Not explicitly in Figma | Must implement: no copy, no download, no print, no right-click |
| Content Versioning / Updates | Not in Figma | FAQ states books will be updated — need versioning strategy |
| "Books that might interest you" (cross-sell) | Not in Figma Part 1 | Consider adding to Store tab |
| Legal pages (Privacy, Terms, Refund) | Not in Figma Part 1 | ⏳ May appear in Part 2+ (Settings/Footer) |

---

### 🎨 ACTION REQUIRED — UI DESIGNER: Missing Figma Screens

> **📌 The following items are NOT yet designed in any Figma Part (1-3). Please design these screens and share them for analysis before development can proceed on these features.**

#### 🔴 High Priority — Core User Flows Missing:
| # | Screen/Feature Needed | Context | Notes for Designer |
|---|----------------------|---------|-------------------|
| 1 | **Settings / Profile Page** | Users need to manage their account, preferences, and theme settings. Sidebar shows "Settings" nav item but no screen is designed. | Should include: profile edit, password change, theme toggle, notification preferences, font size. |
| 2 | **"Redeem Purchases" Page** | After purchasing a book via the e-commerce store, users need a way to redeem/verify their purchase inside the platform. Referenced in Shopify integration flow. | Could be a section within Settings or a standalone page. Needs: purchase code input, order verification, access status display. |
| 3 | **Email Notification Templates** | Welcome email (after registration) and Access Granted email (after purchase). Referenced in Shopify PDF requirements. | Need designs for: welcome email, purchase confirmation email, access granted email. |
| 4 | **Reset Progress Functionality** | Users should be able to reset their reading/quiz progress to start fresh. Referenced in MKSAP as a standard feature. | Could be a button within Settings, or within individual book/specialty detail pages. |

#### 🟡 Medium Priority — Nice-to-Have Features:
| # | Screen/Feature Needed | Context | Notes for Designer |
|---|----------------------|---------|-------------------|
| 5 | **"Getting Started" Onboarding** | First-time user onboarding experience. MKSAP has a "Getting Started" video/tour. | Could be a modal walkthrough, a video intro, or a first-login tutorial overlay. |
| 6 | **Strikethrough Answer Elimination** | In Question Bank, users can visually cross out answer options they want to eliminate before selecting. Common in exam prep tools. | Add a strikethrough toggle/button on each answer option in the question-taking interface (Screen 23). |
| 7 | **Help Center Page** | Sidebar shows "Help Center" link but no actual Help Center page is designed. | Could be: FAQ accordion page, contact form, or link to external support (clarify intent). |
| 8 | **Notification Center** | Bell icon exists in top bar but no notification dropdown/page is designed. | Design: notification dropdown panel and/or full notifications page. |

#### 🟢 Low Priority — Can Be Deferred:
| # | Screen/Feature Needed | Context | Notes for Designer |
|---|----------------------|---------|-------------------|
| 9 | **"Coming Soon" Book State** | Store has 5 "Coming Soon" books. Need a visual treatment for unavailable content. | Locked/grayed card with "Coming Soon" badge and optional "Notify Me" button. |
| 10 | **Book Preview Modal** | Store tab has "Learn More!" links but no preview modal/page is designed. | Modal with book description, sample content, table of contents, and "Buy Now" CTA. |
| 11 | **Customer Reviews Section** | E-commerce store has customer reviews but they don't appear in Figma. | Optional: review stars + count on book cards in the Store tab. |
| 12 | **Legal Pages** (Privacy Policy, Terms, Refund Policy) | Standard legal pages needed for any platform. | Could be simple text pages or link to external URLs. |


---

## 3. Functional Requirements

### FR-1: Authentication & User Management
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-1.1 | Email/Password login with secure hashing | High | Figma |
| FR-1.2 | User registration form (name, email, password) | High | Figma |
| FR-1.3 | Password recovery via email link | High | Figma |
| FR-1.4 | Auto-account creation via purchase webhook | High | PDF |
| FR-1.5 | Welcome email with credentials on first purchase | High | PDF |
| FR-1.6 | Edit Profile page (name, email, profile picture) | Medium | Figma |
| FR-1.7 | Subscription & Billing management page | Medium | Figma |

### FR-2: Syllabus / Content Reader
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-2.1 | Display specialties list with topic counts and progress | High | MKSAP |
| FR-2.2 | Topic listing per specialty with "resume where you left off" | High | MKSAP |
| FR-2.3 | Rich text reading interface with headers, images, tables, clinical photos | High | MKSAP |
| FR-2.4 | "In this topic" sidebar — Table of Contents with section anchors | High | MKSAP |
| FR-2.5 | "Notes" tab — per-topic personal note-taking | High | MKSAP + Figma |
| FR-2.6 | Text highlighting functionality | High | MKSAP + Figma |
| FR-2.7 | "Key Points" summary box per section | Medium | MKSAP |
| FR-2.8 | "Mark this topic completed" checkbox | Medium | MKSAP |
| FR-2.9 | "Next Topic" / "Previous Topic" navigation | Medium | MKSAP |
| FR-2.10 | "Create Flashcard" from within reading interface | Medium | Figma |
| FR-2.11 | Breadcrumb navigation | Low | MKSAP |
| FR-2.12 | Digest Reader View (alternate layout) | Low | Figma |

### FR-3: Board Basics
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-3.1 | Separate content area with condensed exam-prep material | High | MKSAP + Figma |
| FR-3.2 | Same reading interface as Syllabus (TOC, Notes, Highlights) | High | MKSAP |
| FR-3.3 | "Don't Forget!" callout boxes and study tables | Medium | MKSAP |
| FR-3.4 | Independent progress tracking from main Syllabus | Medium | MKSAP |

### FR-4: Question Bank
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-4.1 | Global question progress dashboard (% complete, % correct/incorrect) | High | MKSAP |
| FR-4.2 | "Shuffle Questions" — random questions across all topics | High | MKSAP |
| FR-4.3 | "Custom Quizzes" — filter by specialty, topic, question status | High | MKSAP + Figma |
| FR-4.4 | Quiz Builder with templates (Build your own, Exam Practice, Retry Incorrect) | High | MKSAP |
| FR-4.5 | Question interface: text + optional image + 5 MCQ options (A–E) | High | MKSAP |
| FR-4.6 | Strikethrough feature to eliminate wrong answers visually | Medium | MKSAP |
| FR-4.7 | Post-answer feedback: Correct/Incorrect + detailed explanation | High | MKSAP + Figma |
| FR-4.8 | Educational Objective summary per question | Medium | MKSAP |
| FR-4.9 | Peer statistics (% of users who chose each option) | Low | MKSAP |
| FR-4.10 | Cross-link from explanation to related Syllabus topic | Medium | MKSAP |
| FR-4.11 | Saved/Bookmarked Questions | Medium | MKSAP |
| FR-4.12 | Performance Analytics page | High | Figma |
| FR-4.13 | Review & Explanations — review past quiz answers | High | Figma |
| FR-4.14 | Timed quiz modes (5-min LKA, 2-hour Exam Practice) | Medium | MKSAP |

### FR-5: Flashcards
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-5.1 | Flashcard Decks organized by specialty with per-deck card count + progress | High | MKSAP + Figma |
| FR-5.2 | Study interface: Front (question) → "Reveal Answer" → Back (answer) | High | MKSAP |
| FR-5.3 | Confidence rating: Correct / Unsure / Incorrect (drives spaced repetition) | High | MKSAP + Figma |
| FR-5.4 | "Related Text" link from flashcard back to Syllabus | Medium | MKSAP |
| FR-5.5 | Global shuffle mode: "Answer Flashcards" across all decks | Medium | MKSAP |
| FR-5.6 | My Custom Deck — user-created flashcards | High | Figma |
| FR-5.7 | Professor's Deck — pre-built flashcard deck | Medium | Figma |
| FR-5.8 | Active Study Mode with Spaced Repetition algorithm | High | Figma |
| FR-5.9 | View All Notes and All Highlights from flashcards | Medium | Figma |
| FR-5.10 | Export flashcards as PDF | Low | Figma |

### FR-6: Learning Plan
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-6.1 | Personalized study plan — add topics to "Learning Plan" | High | MKSAP + Figma |
| FR-6.2 | Progress Dashboard — tasks completed, MCQs answered per topic | High | MKSAP + Figma |
| FR-6.3 | Performance Analytics within Learning Plan | Medium | Figma |
| FR-6.4 | Study Schedule feature | Medium | Figma |

### FR-7: CORE Certification & CME/MOC/CPD
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-7.1 | CORE Certification Registration | Medium | Figma |
| FR-7.2 | Submit Exam Scores | Medium | Figma |
| FR-7.3 | Download Certificate (PDF generation) | Medium | Figma |
| FR-7.4 | CME Credit Dashboard — credits earned vs. available | Medium | MKSAP + Figma |
| FR-7.5 | Activity Log for CME activities | Medium | Figma |
| FR-7.6 | Submit to Medical Board | Low | Figma |

### FR-8: Library / Store (E-Commerce within App)
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-8.1 | "My Purchased Books" — list of accessible content | High | Figma |
| FR-8.2 | "Locked Books" — content requiring purchase | High | Figma |
| FR-8.3 | Book Preview Modal — sample content before purchase | Medium | Figma |
| FR-8.4 | Purchase Flow — add to cart / buy now | High | Figma |
| FR-8.5 | Payment & Checkout integration | High | Figma |
| FR-8.6 | Content access tied to `productIds` from Shopify | High | PDF |

### FR-9: Dashboard (Home)
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-9.1 | Welcome banner with personalized greeting | Medium | MKSAP |
| FR-9.2 | "Getting Started" onboarding video/card (dismissible) | Low | MKSAP |
| FR-9.3 | "Your Recent Activity" — last-accessed items across all modules | High | MKSAP |
| FR-9.4 | "Resume Studying →" deep links back to exact position | High | MKSAP |

### FR-10: Global Search
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-10.1 | Full-text search across Syllabus, Board Basics, Flashcards | High | MKSAP + Figma |
| FR-10.2 | Results categorized by source module | High | MKSAP |
| FR-10.3 | Search result snippets with highlighted matching keywords | Medium | MKSAP |
| FR-10.4 | Filters by section/specialty | Medium | MKSAP |
| FR-10.5 | "Use exact word or phrase" toggle | Low | MKSAP |

### FR-11: Shopify Integration (Backend)
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-11.1 | Webhook endpoint (`POST /api/webhooks/shopify/purchase`) | Critical | PDF |
| FR-11.2 | HMAC-SHA256 webhook signature verification | Critical | PDF |
| FR-11.3 | Auto user provisioning + access granting on purchase | Critical | PDF |
| FR-11.4 | Email sending: Welcome email with credentials | High | PDF |
| FR-11.5 | Email sending: Access notification for existing users | High | PDF |
| FR-11.6 | "Redeem Purchases" — User-facing page (Profile section) | High | PDF |
| FR-11.7 | "Redeem Purchases" — Admin Dashboard section | High | PDF |
| FR-11.8 | Poll Shopify API to retrieve purchases by email | High | PDF |

### FR-12: User Settings & Preferences
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-12.1 | Dark Mode / Light Mode / System theme toggle | Medium | MKSAP + Figma |
| FR-12.2 | Font Size adjustment (Small / Medium / Large) | Medium | MKSAP + Figma |
| FR-12.3 | Notification Settings | Low | Figma |
| FR-12.4 | Reset Progress (full or per-section) | Low | MKSAP |

### FR-13: Admin Panel (Django Admin as CMS)

> ✅ **CONFIRMED**: The admin (Dr. Hagras) will use **Django Admin** to manage all book content. The content structure mirrors the MKSAP website hierarchy.

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-13.1 | Admin Dashboard for managing users (list, search, activate/deactivate) | High | Implied |
| FR-13.2 | Admin section to manually grant/restore book access for any user | High | PDF |
| FR-13.3 | **Book Management** — CRUD for Books (title, description, cover image, product_id mapping, price, status: active/coming_soon) | High | Confirmed |
| FR-13.4 | **Specialty Management** — CRUD for Specialties within each Book (name, icon, display order) | High | Confirmed |
| FR-13.5 | **Topic Management** — CRUD for Topics within each Specialty (title, rich HTML content, key points, display order) | High | Confirmed |
| FR-13.6 | **Topic Content Editor** — Rich text editor (django-ckeditor or django-tinymce) supporting headers, bold, images, tables, clinical photos, "Key Points" boxes | High | Confirmed |
| FR-13.7 | **Question Management** — CRUD for MCQ questions (question text, image, 5 options with correct answer, explanation, educational objective, specialty/topic link) | High | Confirmed |
| FR-13.8 | **Flashcard Management** — CRUD for Flashcards (front text, back text, specialty, related topic link) | High | Confirmed |
| FR-13.9 | **Board Basics Management** — CRUD for Board Basics content (same topic structure but separate content pool) | Medium | Confirmed |
| FR-13.10 | User access management (view user's purchased books, grant/revoke access manually) | High | Implied |
| FR-13.11 | Webhook logs viewer (view incoming webhook events, status, errors) | Medium | Implied |
| FR-13.12 | Inline editing — Ability to add Topics directly from the Specialty admin page | Medium | UX |
| FR-13.13 | Bulk import — CSV/JSON import for questions and flashcards (optional, nice-to-have) | Low | Implied |

**Django Admin Content Hierarchy (mirrors MKSAP structure):**
```
Django Admin Sidebar:
├── 📚 Books
│   └── Each Book has:
│       ├── Title, Description, Cover Image, Price, Status (Active/Coming Soon)
│       ├── Product ID (maps to e-commerce store product)
│       └── Inline: Specialties belonging to this Book
│
├── 🎯 Specialties
│   └── Each Specialty has:
│       ├── Name, Icon, Display Order, Parent Book
│       └── Inline: Topics belonging to this Specialty
│
├── 📖 Topics (Syllabus Chapters)
│   └── Each Topic has:
│       ├── Title, Display Order, Parent Specialty
│       ├── Content (Rich HTML via CKEditor/TinyMCE)
│       ├── Key Points (list of bullet points)
│       └── Is Board Basics (boolean flag for dual-purpose content)
│
├── ❓ Questions (MCQ)
│   └── Each Question has:
│       ├── Question Text, Optional Image
│       ├── 5 Options (A-E) with correct answer marked
│       ├── Explanation, Educational Objective
│       └── Linked Specialty + Topic
│
├── ⚡ Flashcards
│   └── Each Flashcard has:
│       ├── Front Text (question/prompt)
│       ├── Back Text (answer)
│       └── Linked Specialty + Topic
│
├── 👥 Users & Access
│   ├── User list (with search/filter)
│   ├── UserBookAccess (grant/revoke per user)
│   └── Webhook Logs (incoming events)
│
└── 📊 Reports (optional)
    ├── Total users, Active users
    ├── Books sold (from webhook data)
    └── Content statistics (topics count, questions count)
```

---

## 4. Non-Functional Requirements

| ID | Requirement | Details |
|----|-------------|---------|
| NFR-1 | **Responsive Design** | Must work on Desktop, Tablet, Mobile. Collapsible sidebar on smaller screens. |
| NFR-2 | **Performance** | Lazy loading for reading content. Image optimization. Target < 3s page load. |
| NFR-3 | **Accessibility** | Font size options, Dark Mode, proper contrast ratios, keyboard navigation. |
| NFR-4 | **Security** | HTTPS, secure password hashing, HMAC webhook verification, CORS configuration, SQL injection prevention. |
| NFR-5 | **Email Deliverability** | Use a transactional email service (SendGrid/AWS SES) with proper SPF/DKIM records. |
| NFR-6 | **SEO** | Not critical for the learning app itself (requires login), but landing pages should be optimized. |
| NFR-7 | **Browser Support** | Chrome, Firefox, Safari, Edge (latest 2 versions). |
| NFR-8 | **Data Backup** | Regular automated DB backups. |

---

## 5. Data Model Design

### Core Tables

```
Users
├── id (PK)
├── email (unique)
├── password_hash
├── first_name
├── last_name
├── role (student / admin)
├── preferences_json (theme, font_size, notifications)
├── created_at
└── updated_at

Books / Products
├── id (PK)
├── product_id (unique, maps to e-commerce store product ID from webhook)
├── title
├── description (rich text)
├── cover_image (ImageField)
├── price (DecimalField)
├── status (active / coming_soon / archived)
├── display_order
├── created_at
└── updated_at

UserBookAccess
├── id (PK)
├── user_id (FK → Users)
├── book_id (FK → Books)
├── order_id (from webhook payload)
├── granted_at
└── source (webhook / manual_admin)

Specialties
├── id (PK)
├── book_id (FK → Books)
├── name
├── icon_url
├── display_order
└── topic_count

Topics (Syllabus Chapters) — Admin adds via Django Admin with rich text editor
├── id (PK)
├── specialty_id (FK → Specialties)
├── title
├── content_html (RichTextField via CKEditor/TinyMCE — supports headers, images, tables, clinical photos)
├── key_points_json (list of bullet-point strings)
├── display_order
├── is_board_basics (boolean — if true, appears in Board Basics section too)
├── created_at
└── updated_at

UserTopicProgress
├── id (PK)
├── user_id (FK → Users)
├── topic_id (FK → Topics)
├── is_completed (boolean)
├── last_read_section
├── reading_time_seconds
└── updated_at

UserHighlights
├── id (PK)
├── user_id (FK → Users)
├── topic_id (FK → Topics)
├── highlighted_text
├── start_offset
├── end_offset
├── color
└── created_at

UserNotes
├── id (PK)
├── user_id (FK → Users)
├── topic_id (FK → Topics)
├── section_anchor
├── note_text
└── created_at

Questions
├── id (PK)
├── specialty_id (FK → Specialties)
├── topic_id (FK → Topics, nullable)
├── question_text
├── question_image_url (nullable)
├── options_json (array of {label, text, is_correct})
├── explanation_text
├── educational_objective
├── difficulty_level
└── created_at

UserQuizSessions
├── id (PK)
├── user_id (FK → Users)
├── quiz_type (shuffle / custom / exam_practice / retry_incorrect)
├── specialty_filter (nullable)
├── started_at
├── completed_at
├── total_questions
├── correct_count
└── time_limit_seconds (nullable)

UserQuestionAnswers
├── id (PK)
├── user_id (FK → Users)
├── question_id (FK → Questions)
├── quiz_session_id (FK → UserQuizSessions)
├── selected_option
├── is_correct
├── is_bookmarked
├── time_spent_seconds
└── answered_at

FlashcardDecks
├── id (PK)
├── specialty_id (FK → Specialties, nullable)
├── deck_type (professor / custom)
├── user_id (FK → Users, nullable — only for custom decks)
├── title
└── card_count

Flashcards
├── id (PK)
├── deck_id (FK → FlashcardDecks)
├── front_text
├── back_text
├── related_topic_id (FK → Topics, nullable)
├── created_by_user_id (FK → Users, nullable)
└── created_at

UserFlashcardProgress
├── id (PK)
├── user_id (FK → Users)
├── flashcard_id (FK → Flashcards)
├── confidence_rating (correct / unsure / incorrect)
├── review_count
├── next_review_at (for spaced repetition)
├── ease_factor
└── last_reviewed_at

LearningPlanItems
├── id (PK)
├── user_id (FK → Users)
├── topic_id (FK → Topics)
├── target_date (nullable)
├── is_completed
└── added_at

CMECredits
├── id (PK)
├── user_id (FK → Users)
├── activity_type
├── credits_earned
├── description
├── evidence_url (nullable)
├── logged_at
└── submitted_to_board (boolean)

Certificates
├── id (PK)
├── user_id (FK → Users)
├── certificate_type (core / cme)
├── issued_at
├── pdf_url
└── status (active / expired)

WebhookLogs
├── id (PK)
├── order_id (from webhook payload)
├── payload_json
├── signature_valid (boolean)
├── processing_status (received / processed / failed)
├── error_message (nullable)
├── received_at
└── processed_at
```

---

## 6. Implementation Workflow

### Phase 1: Foundation & Infrastructure (Weeks 1–2)
1. **Project Setup**
   - Initialize Django project with Django REST Framework
   - Configure PostgreSQL database
   - Setup authentication (JWT or session-based)
   - Configure email service integration (SendGrid/AWS SES)
2. **Database Schema**
   - Implement all core models (Users, Books, Specialties, Topics, Questions, Flashcards)
   - Create migrations
   - Seed initial data structure
3. **Django Admin as CMS**
   - Customize Django Admin for content management
   - Install and configure rich text editor (django-ckeditor or django-tinymce)
   - **Book Admin:** CRUD with cover image upload, product_id mapping, status field
   - **Specialty Admin:** Inline within Book, with icon upload and display order
   - **Topic Admin:** Rich HTML editor for content body, key points field, "is_board_basics" flag
   - **Question Admin:** Question text + image upload, 5 option fields with correct answer marker, explanation, educational objective, specialty/topic selector
   - **Flashcard Admin:** Front/back text fields, specialty/topic selector
   - **User Admin:** User list with search, access management, manual access granting
   - **Webhook Logs:** Read-only log viewer for incoming webhook events
   - Admin filters and search on all models for easy content management

### Phase 2: Webhook Integration (Week 3)
1. **Webhook Endpoint**
   - Create `POST /api/webhooks/purchase/`
   - Implement HMAC-SHA256 signature verification
   - Implement business logic: parse payload → user lookup by email → create/update → grant book access → send email
   - Add `WebhookLogs` for debugging and audit trail
2. **Manual Access Restoration**
   - Admin can manually grant book access via Django Admin
   - User-facing "Redeem Purchases" page for support cases
3. **Email Templates**
   - Welcome email with login credentials (new user from webhook)
   - New book access notification (existing user from webhook)

### Phase 3: Authentication & Layout (Week 4)
1. **Frontend Setup**
   - Initialize React/Next.js frontend
   - Implement design system (colors, typography, spacing)
2. **Auth Pages**
   - Login page
   - Registration page
   - Password recovery flow
3. **App Shell**
   - Fixed left sidebar with all navigation items
   - Top bar with logo + search icon + settings menu
   - Responsive layout: sidebar collapse on mobile
   - User profile section at bottom of sidebar

### Phase 4: Core Learning — Syllabus & Board Basics (Weeks 5–6)
1. **Syllabus Overview**
   - Specialty list with icons, topic counts, and progress bars
   - "Resume your progress" banner
2. **Topic Listing**
   - Per-specialty topic list with badges ("1 Highlight", "In Learning Plan")
3. **Reading Interface**
   - Rich HTML content renderer
   - "In this topic" sidebar TOC with section anchors
   - "Notes" tab with per-topic note CRUD
   - Text highlighting with color support
   - "Mark topic completed" checkbox
   - "Key Points" collapsible box
   - "Next Topic" / "Previous Topic" navigation
   - "Create Flashcard" action from selected text
   - Breadcrumb navigation
4. **Board Basics**
   - Same reading interface, separate content pool
   - Independent progress tracking

### Phase 5: Question Bank (Weeks 7–8)
1. **Question Bank Overview**
   - Progress circle (% complete)
   - Correct/Incorrect stats bars
   - "Shuffle Questions" and "Custom Quizzes" cards
   - Per-specialty question sets
2. **Quiz Builder**
   - Template selection (Build your own, Exam Practice, Retry Incorrect)
   - Specialty and topic filter
   - Question count summary
3. **Quiz Interface**
   - Question display (text + optional image)
   - MCQ options with strikethrough elimination
   - Submit button
   - Feedback: Correct/Incorrect, Explanation, Educational Objective
   - Peer statistics bars
   - "Related Syllabus Topic" links
4. **Saved Questions** — Bookmark functionality

### Phase 6: Flashcards System (Week 9)
1. **Deck Overview**
   - Specialty-based decks with card counts + progress
   - Global shuffle mode
2. **Study Interface**
   - Front → Reveal → Back card flip
   - Confidence rating (Correct/Unsure/Incorrect)
   - Spaced repetition scheduling
   - "Related Text" link to Syllabus
3. **Custom Deck Creation**
   - From reading interface
   - Manual flashcard creation
4. **Professor's Deck** — pre-built content
5. **View All Notes & Highlights**
6. **Export as PDF**

### Phase 7: Learning Plan (Week 10)
1. **Plan Items** — Add/remove topics
2. **Progress Dashboard** — Visualize completion
3. **Performance Analytics** — Quiz performance per topic
4. **Study Schedule** — Calendar-based planning

### Phase 8: Library/Store & Dashboard (Week 11)
1. **Library**
   - "My Purchased Books" — list of accessible books
   - "Locked Books" — books requiring purchase
   - Book Preview Modal
2. **Purchase Flow**
   - Integration with payment gateway (Stripe or Shopify Checkout)
   - Access granted on successful payment
3. **Dashboard (Home)**
   - Welcome banner
   - Recent Activity cards with "Resume" deep links
   - Onboarding card (dismissible)

### Phase 9: CME/CORE, Search & Settings (Week 12)
1. **CORE Certification**
   - Registration, Exam Score submission, Certificate PDF generation
2. **CME Dashboard**
   - Credit tracking, Activity Log
3. **Global Search**
   - Full-text index across Syllabus + Board Basics + Flashcards
   - Result categorization, keyword highlighting, filters
4. **User Preferences**
   - Dark/Light/System theme
   - Font Size (S/M/L)
   - Notification settings

### Phase 10: Polish, Testing & Deployment (Weeks 13–14)
1. **Testing**
   - Webhook testing with Shopify test orders
   - Content access control verification
   - Quiz scoring accuracy
   - Responsive design across devices
   - Cross-browser testing
2. **Performance Optimization**
   - Lazy loading for reading content
   - Image optimization
   - Database query optimization
3. **Deployment**
   - Deploy backend (DigitalOcean/AWS/Heroku)
   - Deploy frontend (Vercel/Netlify)
   - Configure DNS: A record for `online.medigesthealth.com`
   - SSL certificate setup
   - Provide webhook URL to client for Shopify dashboard configuration
4. **Handoff**
   - Admin training documentation
   - Content upload guide

---

## 7. Action Items & Open Questions

### 🔴 Critical — Must Resolve Before Development
| # | Item | Owner | Status |
|---|------|-------|--------|
| ~~1~~ | ~~Clarify E-Commerce Platform~~ | Client | ✅ **RESOLVED** — Platform-agnostic webhook. We define the payload, client's dev adapts. |
| ~~2~~ | ~~Obtain Webhook JSON Schema~~ | Us | ✅ **RESOLVED** — We designed our own recommended schema (see Section A, Part 3). Client's dev will match it or we adjust. |
| 3 | **Confirm Authentication Mode** — Email/Password vs. Magic Link vs. Social Auth | Us + Client | ⏳ Pending |
| 4 | **Hosting Decision** — Provider + IP address for DNS setup | Us | ⏳ Pending |

### 🟡 Important — Confirm Before Relevant Phase
| # | Item | Owner | Status |
|---|------|-------|--------|
| ~~7~~ | ~~Content Format~~ | Us + Client | ✅ **RESOLVED** — Admin adds HTML content via Django Admin with rich text editor (CKEditor/TinyMCE). |
| 8 | **Content Protection / DRM** — Store FAQ explicitly states "no downloads or copying allowed". Must implement robust content protection (disable copy, right-click, print, screenshots). | Us | ⏳ Pending |
| 9 | **Content Versioning** — Store FAQ says "future editions will continue to be updated". Need a strategy for updating book content. | Us + Client | ⏳ Pending |
| ~~10~~ | ~~Admin Panel Scope~~ | Us + Client | ✅ **RESOLVED** — Django Admin is the CMS. Admin adds all content (Books, Specialties, Topics, Questions, Flashcards) through customized Django Admin interface. |
| 11 | **Medical Board Submission** — Is actual ABIM API integration needed or just a placeholder? | Client | ⏳ Pending |
| 12 | **Email Service** — SendGrid, AWS SES, or other? | Us | ⏳ Pending |
| 13 | **"Digest Reader View"** — What exactly is different from the standard reader? | Designer | ⏳ Pending |
| 14 | **Product URL typo** — "cardiovasicular" in store URLs. How should we map this in our DB? | Us | ⏳ Pending |

### 🟢 Nice to Have — Confirm During Development
| # | Item | Owner | Status |
|---|------|-------|--------|
| 15 | Peer statistics on questions — aggregate data needed across users | Us | ⏳ Pending |
| 16 | "Getting Started" onboarding video — will client provide this? | Client | ⏳ Pending |
| 17 | Specialty icons/images — need assets from designer (store has 3D book renders that could be reused) | Designer | ⏳ Pending |
| 18 | PDF certificate template design | Designer | ⏳ Pending |
| 19 | Customer reviews — should reviews from the store appear in our Library/Store? | Client | ⏳ Pending |
| 20 | "Coming Soon" books — how to handle in our Library (show as locked? hide entirely?) | Client | ⏳ Pending |
| 21 | Book preview PDFs — integrate existing PDF samples into the "Book Preview Modal"? | Client | ⏳ Pending |

