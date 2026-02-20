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

## 2. Cross-Reference & Gap Analysis

### Items in Shopify PDF NOT yet in Figma:
| Item | Status | Action Required |
|------|--------|-----------------|
| Webhook URL endpoint | Not shown in Figma | Add to backend architecture |
| "Redeem Purchases" page (user profile) | Partially covered by "Subscription & Billing" | Confirm if merged or separate |
| Admin Dashboard for purchase restoration | Not shown in Figma | Confirm with designer — need Admin panel |
| Email notifications (welcome + access) | Not shown in Figma | Add email template designs |

### Items in MKSAP NOT in Figma:
| Item | Status | Action Required |
|------|--------|-----------------|
| "Saved Questions" bookmark feature | Not in Figma | Confirm with client if needed |
| Strikethrough answer elimination | Not in Figma | Confirm with client — nice UX feature |
| Peer answer statistics on Q&A | Not in Figma | Confirm with client |
| "Mark topic as completed" checkbox | Not in Figma | Likely implied — confirm |
| "Getting Started" video / onboarding | Not in Figma | Confirm with client |
| Help (external link in sidebar) | Present in Figma as "Help & Support" | ✅ Covered |
| Reset progress functionality | Not in Figma | Confirm if needed |

### Missing Artifact:
| Item | Details |
|------|---------|
| **Webhook JSON Schema** | The PDF references an attached `.json` file with the webhook payload schema. **This file was NOT provided in the project directory.** Must be requested from the client. |

### Items from Live Store NOT yet reflected in Figma or Requirements:
| Item | Status | Action Required |
|------|--------|-----------------|
| "Coming Soon" books (5 titles) | Not in Figma | Platform must handle unavailable content gracefully |
| Book Preview PDFs (free samples) | Partially covered by "Book Preview Modal" in Figma | Confirm: show PDF sample or custom preview page? |
| Customer Reviews on product pages | Not in Figma | Decide if reviews should appear in our Library/Store |
| Content Protection / DRM | Not explicitly in Figma | Must implement: no copy, no download, no print, no right-click |
| Content Versioning / Updates | Not in Figma | FAQ states books will be updated — need versioning strategy |
| "Books that might interest you" (cross-sell) | Not in Figma | Consider adding to Library/Store section |
| Legal pages (Privacy, Terms, Refund) | Not in Figma | Need links in footer or settings |

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

