import json
import os
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from django.db import transaction

class Command(BaseCommand):
    help = "Seed database with Figma mockup dummy data directly from JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help="Path to the figma_data JSON file (optional).",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("\n🌱 Seeding Figma Demo Data...\n"))
        
        custom_file = options.get('file')
        if custom_file:
            json_path = os.path.abspath(custom_file)
        else:
            json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../figma_data.json')
            
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f"Could not find JSON file at {json_path}"))
            return

        with open(json_path, 'r') as f:
            data = json.load(f)

        # Wrap everything in a single transaction for speed on remote Postgres
        with transaction.atomic():
            student = self._create_student(data['user'])
            self._create_books_and_specialties(data['books'])
            self._create_questions()
            self._create_flashcards()
            self._grant_book_access(student)
            self._create_cme(student)
            self._create_student_activity(student)

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Figma demo data seeded successfully!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  Login:\n"
            f"  Email   : {student.email}\n"
            f"  Password: StudentPassword123!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        ))

    def _create_student(self, d):
        from accounts.models import User
        user, created = User.objects.get_or_create(
            email=d["email"],
            defaults={
                "first_name": d["first_name"],
                "last_name": d["last_name"],
                "role": d["role"],
                "theme": d["theme"],
                "font_size": d["font_size"],
                "current_study_streak": d["current_study_streak"],
                "longest_study_streak": d["longest_study_streak"],
                "daily_reading_goal_minutes": d["daily_reading_goal_minutes"],
                "daily_flashcard_goal": d["daily_flashcard_goal"],
                "daily_questions_goal": d["daily_questions_goal"],
                "last_study_date": timezone.now().date() - timedelta(days=1),
            }
        )
        if created:
            user.set_password(d["password"])
            user.save()
            self.stdout.write(f"  👤 Created student: {d['email']}")
        else:
            self.stdout.write(f"  ⏭️  Student exists: {d['email']}")
            user.first_name = d["first_name"]
            user.last_name = d["last_name"]
            user.current_study_streak = d["current_study_streak"]
            user.set_password(d["password"])
            user.save()
        return user

    def _create_books_and_specialties(self, books):
        from books.models import Book, Specialty, Topic
        for book_data in books:
            book, created = Book.objects.get_or_create(
                product_id=book_data["product_id"],
                defaults={
                    "title": book_data["title"],
                    "slug": slugify(book_data["title"]) + "-" + book_data["product_id"],
                    "price": book_data["price"],
                    "status": book_data["status"],
                    "display_order": book_data["display_order"],
                    "estimated_pages": book_data["estimated_pages"],
                    "description": book_data["description"],
                }
            )
            self.stdout.write(f"  📚 {'Created' if created else 'Exists'}: {book.title}")
            for j, sd in enumerate(book_data.get("specialties", [])):
                spec, _ = Specialty.objects.get_or_create(
                    book=book,
                    slug=slugify(sd["name"]),
                    defaults={
                        "name": sd["name"],
                        "display_order": j,
                        "is_core_specialty": sd.get("is_core", False),
                        "core_display_order": sd.get("core_order", 0),
                        "description": f"Topics related to {sd['name']}.",
                    }
                )
                for k, td in enumerate(sd.get("topics", [])):
                    Topic.objects.get_or_create(
                        specialty=spec,
                        slug=slugify(td["title"]) + "-" + str(spec.id),
                        defaults={
                            "title": td["title"],
                            "display_order": k,
                            "is_board_basics": td.get("board_basics", False),
                            "start_page": td.get("start_page", 1),
                            "end_page": td.get("end_page", 10),
                            "estimated_tasks": 3,
                        }
                    )
                    self.stdout.write(f"      📖 {td['title']}")

    def _create_questions(self):
        from books.models import Specialty
        from questions.models import Question
        specs = Specialty.objects.all()
        for spec in specs:
            if not spec.topics.exists():
                continue
            topic = spec.topics.first()
            existing = set(
                Question.objects.filter(specialty=spec)
                .values_list('question_text', flat=True)
            )
            new_questions = []
            for j in range(15):
                text = f"Question {j+1} for {spec.name}"
                if text not in existing:
                    new_questions.append(Question(
                        specialty=spec,
                        question_text=text,
                        educational_objective=f"Objective {j}",
                        topic=topic,
                        option_a="A",
                        option_b="B",
                        option_c="C",
                        option_d="D",
                        correct_answer="B",
                        difficulty="medium",
                        explanation=f"Explanation for Q{j}",
                    ))
            if new_questions:
                Question.objects.bulk_create(new_questions)
                self.stdout.write(f"  ❓ Created {len(new_questions)} questions for {spec.name}")

    def _create_flashcards(self):
        from books.models import Specialty
        from flashcards.models import Flashcard
        specs = Specialty.objects.all()
        for spec in specs:
            if not spec.topics.exists():
                continue
            existing = set(
                Flashcard.objects.filter(specialty=spec)
                .values_list('front_text', flat=True)
            )
            new_cards = []
            for i in range(10):
                front = f"Flashcard front {i+1} for {spec.name}"
                if front not in existing:
                    new_cards.append(Flashcard(
                        specialty=spec,
                        book=spec.book,
                        topic=spec.topics.first(),
                        front_text=front,
                        back_text=f"Flashcard back {i+1}",
                        display_order=i,
                    ))
            if new_cards:
                Flashcard.objects.bulk_create(new_cards)
                self.stdout.write(f"  🃏 Created {len(new_cards)} flashcards for {spec.name}")

    def _grant_book_access(self, student):
        from books.models import Book, UserBookAccess
        active_books = list(Book.objects.filter(status="active").order_by('display_order'))[:3]
        for book in active_books:
            UserBookAccess.objects.get_or_create(
                user=student,
                book=book,
                defaults={
                    "order_id": f"DEMO-{random.randint(10000, 99999)}",
                    "source": "manual_admin",
                }
            )

    def _create_cme(self, student):
        from books.models import Specialty
        from certificates.models import UserCOREProgress
        
        hematology = Specialty.objects.filter(name="Hematology").first()
        if hematology:
            UserCOREProgress.objects.get_or_create(
                user=student,
                specialty=hematology,
                defaults={
                    "badge_status": "in_progress",
                    "questions_answered": 100,
                    "questions_correct": 45,
                    "last_30_correct": 10,
                    "last_30_total": 20,
                    "core_quiz_unlocked": False
                }
            )
        
        infectious = Specialty.objects.filter(name="Infectious Disease").first()
        if infectious:
            UserCOREProgress.objects.get_or_create(
                user=student,
                specialty=infectious,
                defaults={
                    "badge_status": "pending",
                    "questions_answered": 0,
                    "questions_correct": 0,
                    "last_30_correct": 0,
                    "last_30_total": 0,
                    "core_quiz_unlocked": False
                }
            )

    def _create_student_activity(self, student):
        from books.models import Topic
        from learning.models import UserTopicProgress, UserStudySession
        from questions.models import QuizSession, UserQuestionAttempt, Question
        
        now = timezone.now()

        topics = list(Topic.objects.all())
        if topics:
            t = topics[0]
            t.title = "Evaluation of Lipid Levels"
            t.save()
            UserTopicProgress.objects.get_or_create(
                user=student, topic=t,
                defaults={
                    "is_completed": False,
                    "last_page_read": t.start_page + 44 if t.start_page else 45,
                    "reading_time_seconds": 1800,
                    "tasks_completed": 1,
                    "updated_at": now
                }
            )
            
            for t2 in topics[1:]:
                UserTopicProgress.objects.get_or_create(
                    user=student, topic=t2,
                    defaults={
                        "is_completed": True,
                        "last_page_read": t2.end_page,
                        "reading_time_seconds": 3600,
                        "tasks_completed": 3,
                        "updated_at": now - timedelta(days=2)
                    }
                )

        q_qs = list(Question.objects.all()[:10])
        if not q_qs:
            return

        for i in range(10):
            session, _ = QuizSession.objects.get_or_create(
                user=student,
                title=f"Quiz Session {i+1}",
                defaults={
                    "mode": "practice",
                    "total_questions": 10,
                    "correct_count": 8 if i < 5 else 9,
                    "total_time_seconds": 600,
                    "is_completed": True,
                    "completed_at": now - timedelta(days=i),
                }
            )
            existing_attempts = set(
                UserQuestionAttempt.objects.filter(user=student, quiz_session=session)
                .values_list('question_id', flat=True)
            )
            new_attempts = []
            for q_idx, q in enumerate(q_qs):
                if q.id not in existing_attempts:
                    new_attempts.append(UserQuestionAttempt(
                        user=student,
                        question=q,
                        quiz_session=session,
                        selected_answer="B",
                        is_correct=q_idx < (8 if i < 5 else 9),
                        time_spent_seconds=60,
                        attempted_at=now - timedelta(days=i),
                    ))
            if new_attempts:
                UserQuestionAttempt.objects.bulk_create(new_attempts)

        UserStudySession.objects.get_or_create(
            user=student,
            session_type="reading",
            started_at=now - timedelta(days=1),
            defaults={
                "duration_seconds": int(12.5 * 3600),
                "ended_at": now - timedelta(days=1) + timedelta(hours=12.5),
            }
        )
        
        daily_session, _ = QuizSession.objects.get_or_create(
            user=student,
            title="Today's Practice",
            defaults={
                "mode": "practice",
                "total_questions": 15,
                "correct_count": 15,
                "total_time_seconds": 900,
                "is_completed": True,
                "completed_at": now,
            }
        )
        existing_daily = set(
            UserQuestionAttempt.objects.filter(user=student, quiz_session=daily_session)
            .values_list('question_id', flat=True)
        )
        daily_attempts = []
        for q in q_qs[:15]:
            if q.id not in existing_daily:
                daily_attempts.append(UserQuestionAttempt(
                    user=student,
                    question=q,
                    quiz_session=daily_session,
                    selected_answer="B",
                    is_correct=True,
                    time_spent_seconds=60,
                    attempted_at=now,
                ))
        if daily_attempts:
            UserQuestionAttempt.objects.bulk_create(daily_attempts)
