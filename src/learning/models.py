import uuid
from django.db import models
from django.conf import settings


class UserTopicProgress(models.Model):
    """
    Tracks a user's reading progress for each topic.
    Includes completion status, reading time, and last read position.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='topic_progress'
    )
    topic = models.ForeignKey(
        'books.Topic', on_delete=models.CASCADE, related_name='user_progress'
    )
    is_completed = models.BooleanField(
        default=False,
        help_text='User marked this topic as completed.'
    )
    last_read_section = models.CharField(
        max_length=255, blank=True,
        help_text='ID/anchor of the last section the user was reading.'
    )
    reading_time_seconds = models.PositiveIntegerField(
        default=0, help_text='Total cumulative reading time.'
    )

    # ── Figma Part 3: Learning Plan shows "0/3 tasks completed" ─────
    tasks_completed = models.PositiveIntegerField(
        default=0,
        help_text='Number of tasks completed for this topic (for Learning Plan progress).'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Topic Progress'
        verbose_name_plural = 'Topic Progress'
        unique_together = ['user', 'topic']
        ordering = ['-updated_at']

    def __str__(self):
        status = '✓' if self.is_completed else '○'
        return f'{status} {self.user.email} — {self.topic.title}'


class UserHighlight(models.Model):
    """
    A text highlight made by a user in a topic.
    Supports multiple colors for different highlight purposes.
    """

    class Color(models.TextChoices):
        YELLOW = 'yellow', 'Yellow'
        GREEN = 'green', 'Green'
        BLUE = 'blue', 'Blue'
        PINK = 'pink', 'Pink'
        ORANGE = 'orange', 'Orange'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='highlights'
    )
    topic = models.ForeignKey(
        'books.Topic', on_delete=models.CASCADE, related_name='highlights'
    )
    highlighted_text = models.TextField(help_text='The selected text.')
    start_offset = models.PositiveIntegerField(
        help_text='Character offset of highlight start.'
    )
    end_offset = models.PositiveIntegerField(
        help_text='Character offset of highlight end.'
    )
    color = models.CharField(
        max_length=10, choices=Color.choices, default=Color.YELLOW
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Highlight'
        verbose_name_plural = 'Highlights'
        ordering = ['topic', 'start_offset']

    def __str__(self):
        return f'{self.user.email}: "{self.highlighted_text[:50]}"'


class UserNote(models.Model):
    """
    A note added by a user to a specific position in a topic.
    Can be attached to a highlight or standalone.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notes'
    )
    topic = models.ForeignKey(
        'books.Topic', on_delete=models.CASCADE, related_name='notes'
    )
    highlight = models.OneToOneField(
        UserHighlight, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='note',
        help_text='Optional: link to a highlight this note is attached to.'
    )
    content = models.TextField(help_text='The note text.')
    position_offset = models.PositiveIntegerField(
        default=0, help_text='Character offset where this note is placed.'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['topic', 'position_offset']

    def __str__(self):
        return f'{self.user.email}: "{self.content[:50]}"'


class UserBookmark(models.Model):
    """
    A page/section bookmark in the Syllabus reader.
    Figma Part 1 (Screen 12) shows a dedicated Bookmarks page under Syllabus.
    Users can bookmark specific pages/sections while reading.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    topic = models.ForeignKey(
        'books.Topic', on_delete=models.CASCADE, related_name='bookmarks'
    )
    section_anchor = models.CharField(
        max_length=255, blank=True,
        help_text='Section/anchor ID within the topic content.'
    )
    label = models.CharField(
        max_length=500, blank=True,
        help_text='Auto-generated or user-given label for the bookmark.'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'
        unique_together = ['user', 'topic', 'section_anchor']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email}: {self.topic.title} — {self.label or self.section_anchor}'


class UserLearningPlanTopic(models.Model):
    """
    Tracks which topics a user has added to their personal Learning Plan.
    Figma Part 3 (Screens 24-26): Users curate a list of topics to focus on.
    Topics can be added/removed. Progress is tracked per topic.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='learning_plan_topics'
    )
    topic = models.ForeignKey(
        'books.Topic', on_delete=models.CASCADE, related_name='learning_plan_entries'
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Learning Plan Topic'
        verbose_name_plural = 'Learning Plan Topics'
        unique_together = ['user', 'topic']
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.user.email} → {self.topic.title}'


class UserStudySession(models.Model):
    """
    Records individual study sessions for time tracking.
    Figma Part 3 (Board Basics & Flashcards) shows "12.5h this week" study time.
    Each record represents a continuous study period.
    """

    class SessionType(models.TextChoices):
        READING = 'reading', 'Syllabus Reading'
        QUIZ = 'quiz', 'Question Bank / Quiz'
        FLASHCARD = 'flashcard', 'Flashcard Review'
        BOARD_BASICS = 'board_basics', 'Board Basics'
        CORE = 'core', 'CORE Practice'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='study_sessions'
    )
    session_type = models.CharField(
        max_length=15, choices=SessionType.choices
    )
    duration_seconds = models.PositiveIntegerField(
        default=0,
        help_text='Duration of this study session in seconds.'
    )

    # Optional context: what was the user studying?
    book = models.ForeignKey(
        'books.Book', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='study_sessions'
    )
    specialty = models.ForeignKey(
        'books.Specialty', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='study_sessions'
    )
    topic = models.ForeignKey(
        'books.Topic', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='study_sessions'
    )

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Study Session'
        verbose_name_plural = 'Study Sessions'
        ordering = ['-started_at']

    def __str__(self):
        hours = self.duration_seconds / 3600
        return f'{self.user.email} — {self.session_type} ({hours:.1f}h)'


class RecentActivity(models.Model):
    """
    Tracks recent user activity for the Dashboard's "Recent Activity" section.
    Shows what the user last interacted with (topic, quiz, flashcard).
    """

    class ActivityType(models.TextChoices):
        READING = 'reading', 'Reading'
        QUIZ = 'quiz', 'Quiz'
        FLASHCARD = 'flashcard', 'Flashcard'
        BOARD_BASICS = 'board_basics', 'Board Basics'
        CORE = 'core', 'CORE'
        LEARNING_PLAN = 'learning_plan', 'Learning Plan'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='recent_activities'
    )
    activity_type = models.CharField(
        max_length=15, choices=ActivityType.choices
    )
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=500, blank=True)

    # Generic reference to the related object
    reference_id = models.UUIDField(
        null=True, blank=True,
        help_text='UUID of the related topic/quiz/flashcard.'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Recent Activity'
        verbose_name_plural = 'Recent Activities'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.activity_type}: {self.title}'
