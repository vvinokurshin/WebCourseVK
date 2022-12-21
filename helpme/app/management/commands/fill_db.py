from django.core.management.base import BaseCommand

from faker import Faker
from app.models import *
import random as r

from django.db.models import Min, Q

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def add_arguments(self, parser):
        parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        self.count = options['poll_ids'][0]

        # User.objects.filter(~Q(username='valeriy')).delete()
        # Tag.objects.all().delete()

        self.create_users()
        self.create_tags()
        self.create_questions()
        self.create_answers()
        self.mark_correct_answers()
        self.create_likes()

    def create_user(self):
        return User(
            email=self.fake.unique.email(),
            password=self.fake.password(),
            username=self.fake.unique.user_name(),
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name()
        )  

    def create_users(self):
        users = []
        profiles = []

        for i in range(self.count):
            if (self.count / 10):
                print(f"PROGRESS {i / self.count * 100}%")

            cur_user = self.create_user()
            users.append(cur_user)
            profiles.append(Profile(user=cur_user, avatar=f'static/uploads/avatar{r.randint(1, 8)}.jpg'))

        User.objects.bulk_create(users)
        Profile.objects.bulk_create(profiles)

        self.start_id_profile = Profile.objects.all().aggregate(Min('id'))['id__min']
        self.end_id_profile = self.start_id_profile + Profile.objects.all().count() - 1
        print("Users Done")

    def create_tag(self):
        try:
            symbols = list(self.fake.unique.word())
            r.shuffle(symbols)
            tag = Tag(name=''.join(symbols))
        except:
            self.fake.unique.clear()
            symbols = list(self.fake.unique.word())
            r.shuffle(symbols)
            tag = Tag(name=''.join(symbols))
        
        return tag

    def create_tags(self):
        tags = []

        for i in range(self.count):
            if (i % (self.count / 10) == 0):
                print(f"PROGRESS {i / self.count}%")

            tags.append(self.create_tag())

        Tag.objects.bulk_create(tags)

        self.start_id_tag = Tag.objects.all().aggregate(Min('id'))['id__min']
        self.end_id_tag = self.start_id_tag + Tag.objects.all().count() - 1
        print("Tags Done")

    def create_question(self):
        return Question(
            title=f'{self.fake.paragraph(2)[:80][:-1]}?',
            text=self.fake.paragraph(r.randint(10, 30))[:2000],
            user_id=self.get_random_profile_id()
        )

    def add_tags_to_question(self, question):
        tags = []
        tags_count = r.randint(2, 4)

        for _ in range(tags_count):
            tags.append(Tag.objects.get(id=self.get_random_tag_id()))

        question.tags.add(*tags)

    def create_questions(self):
        questions = []

        for i in range(self.count * 10):
            if (i % self.count == 0):
                print(f"PROGRESS {i / self.count * 10}%")

            questions.append(self.create_question())

        print("Questions Done")

        questions = Question.objects.bulk_create(questions)
        self.start_id_question = Question.objects.all().aggregate(Min('id'))['id__min']
        self.end_id_question = self.start_id_question + Question.objects.all().count() - 1

        for i in range(self.count * 10):
            if (i % self.count == 0):
                print(f"PROGRESS {i / self.count * 10}%")

            self.add_tags_to_question(questions[i])

        print("Tags to questions Done")

    def create_answer(self):
        return Answer(
            text=self.fake.paragraph(r.randint(10, 30))[:1000],
            user_id=self.get_random_profile_id(),
            question_id=self.get_random_question_id()
        )

    def create_answers(self):
        answers = []

        for i in range(self.count * 100):
            if (i % (10 * self.count) == 0):
                print(f"PROGRESS {i / self.count}%")
            answers.append(self.create_answer())

            if ((i + 1) % (10000) == 0):
                Answer.objects.bulk_create(answers)
                answers = []

        if len(answers):
            Answer.objects.bulk_create(answers)
        self.start_id_answer = Answer.objects.all().aggregate(Min('id'))['id__min']
        self.end_id_answer = self.start_id_answer + Answer.objects.all().count() - 1
        print("Answers Done")

    def mark_correct_answers(self):
        for id in range(self.start_id_question, self.end_id_question + 1):
            answers = Answer.objects.filter(question_id=id)

            if len(answers):
                answers[0].is_correct = True
                answers[0].save()

    def create_likes_questions(self):
        likes = []

        for i in range(self.count * 30):
            if (i % (3 * self.count) == 0):
                print(f"PROGRESS {i / (self.count * 30) * 100}%")

            while True:
                profile_id = self.get_random_profile_id()
                question_id = self.get_random_question_id()
                this_question_from_this_user = Question.objects.filter(id=question_id, user_id=profile_id).exists()
                liked_by_this_user = LikeQuestion.objects.filter(question_id=question_id, from_user_id=profile_id).exists()

                if not this_question_from_this_user and not liked_by_this_user:
                    likes.append(LikeQuestion(question_id=question_id, from_user_id=profile_id))
                    break

            if ((i + 1) % (10000) == 0):
                LikeQuestion.objects.bulk_create(likes)
                likes = []

        if len(likes):
            LikeQuestion.objects.bulk_create(likes)
        print("Likes Q Done")

    def create_dislikes_questions(self):
        dislikes = []

        for i in range(self.count * 70):
            if i % (7 * self.count) == 0:
                print(f"PROGRESS {i / (self.count * 70) * 100}%")

            while True:
                profile_id = self.get_random_profile_id()
                question_id = self.get_random_question_id()
                this_question_from_this_user = Question.objects.filter(id=question_id, user_id=profile_id).exists()
                liked_by_this_user = LikeQuestion.objects.filter(question_id=question_id, from_user_id=profile_id).exists()
                disliked_by_this_user = DislikeQuestion.objects.filter(question_id=question_id, from_user_id=profile_id).exists()

                if not this_question_from_this_user and not liked_by_this_user and not disliked_by_this_user:
                    dislikes.append(DislikeQuestion(question_id=question_id, from_user_id=profile_id))
                    break

            if ((i + 1) % (10000) == 0):
                DislikeQuestion.objects.bulk_create(dislikes)
                dislikes = []

        if len(dislikes):
            DislikeQuestion.objects.bulk_create(dislikes)

        # DislikeQuestion.objects.bulk_create(dislikes)
        print("Dislikes Q Done")


    def create_likes_answers(self):
        likes = []

        for i in range(self.count * 30):
            if i % (3 * self.count) == 0:
                print(f"PROGRESS {i / (self.count * 30) * 100}%")

            while True:
                profile_id = self.get_random_profile_id()
                answer_id = self.get_random_answer_id()
                this_answer_from_this_user = Answer.objects.filter(id=answer_id, user_id=profile_id).exists()
                liked_by_this_user = LikeAnswer.objects.filter(answer_id=answer_id, from_user_id=profile_id).exists()

                if not this_answer_from_this_user and not liked_by_this_user:
                    likes.append(LikeAnswer(answer_id=answer_id, from_user_id=profile_id))
                    break

            if ((i + 1) % (10000) == 0):
                LikeAnswer.objects.bulk_create(likes)
                likes = []

        if len(likes):
            LikeAnswer.objects.bulk_create(likes)

        # LikeAnswer.objects.bulk_create(likes)
        print("Likes A Done")

    def create_dislikes_answers(self):
        dislikes = []

        for i in range(self.count * 70):
            if i % (7 * self.count) == 0:
                print(f"PROGRESS {i / (self.count * 70) * 100}%")

            while True:
                profile_id = self.get_random_profile_id()
                answer_id = self.get_random_answer_id()
                this_answer_from_this_user = Answer.objects.filter(id=answer_id, user_id=profile_id).exists()
                liked_by_this_user = LikeAnswer.objects.filter(answer_id=answer_id, from_user_id=profile_id).exists()
                disliked_by_this_user = DislikeAnswer.objects.filter(answer_id=answer_id, from_user_id=profile_id).exists()

                if not this_answer_from_this_user and not liked_by_this_user and not disliked_by_this_user:
                    dislikes.append(DislikeAnswer(answer_id=answer_id, from_user_id=profile_id))
                    break

            if ((i + 1) % (10000) == 0):
                DislikeAnswer.objects.bulk_create(dislikes)
                dislikes = []

        if len(dislikes):
            DislikeAnswer.objects.bulk_create(dislikes)

        # DislikeAnswer.objects.bulk_create(dislikes)
        print("Dislikes A Done")

    def create_likes(self):
        self.create_likes_questions()
        self.create_dislikes_questions()
        self.create_likes_answers()
        self.create_dislikes_answers()

    def get_random_profile_id(self):
        return r.randint(self.start_id_profile, self.end_id_profile)

    def get_random_tag_id(self):
        return r.randint(self.start_id_tag, self.end_id_tag)

    def get_random_question_id(self):
        return r.randint(self.start_id_question, self.end_id_question)

    def get_random_answer_id(self):
        return r.randint(self.start_id_answer, self.end_id_answer)