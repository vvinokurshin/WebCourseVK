from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count


class ProfileManager(models.Manager):
    def get_top_users(self, count=5):
        return self.annotate(answer_count=Count('answer')).order_by('-answer_count')[:count]

    def get_profile_by_id(self, id):
        try:
            return self.annotate(question_count=Count('question', distinct=True), answer_count=Count('answer', distinct=True)).get(id=id)
        except Profile.DoesNotExist:
            return None

    def get_prof_by_user_id(self, id):
        try:
            return self.get(user_id=id)
        except Profile.DoesNotExist:
            return None


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    avatar = models.ImageField(null=True, blank=True, upload_to='static/uploads/')
    objects = ProfileManager()

    def __str__(self):
        return str(self.user.username)


class TagManager(models.Manager):
    def get_top_tags(self, count=7):
        return self.annotate(q_count=Count('question')).order_by('-q_count')[:count]


class Tag(models.Model):
    name = models.CharField(max_length=20)
    objects = TagManager()

    def __str__(self):
        return str(self.name)


class QuestionManager(models.Manager):
    def get_info_questions(self):
        return self.annotate(count_answers=Count('answer', distinct=True), 
                      raiting=Count('likequestion', distinct=True) - Count('dislikequestion', distinct=True))

    def get_new_questions(self):
        return self.get_info_questions().order_by('-publish_date')

    def get_top_questions(self):
        return self.get_info_questions().order_by('-raiting')
    
    def get_questions_by_tag(self, tag_name):
        return self.get_info_questions().filter(tags__name=tag_name).order_by('-publish_date')

    def get_question(self, id):
        try:
            return self.get_info_questions().get(id=id)
        except Question.DoesNotExist:
            return None

    def get_questions_by_user(self, user_id):
        return self.get_info_questions().filter(user_id=user_id).order_by('-publish_date')


class Question(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=80)
    text = models.CharField(max_length=2000)
    tags = models.ManyToManyField(Tag)
    publish_date = models.DateTimeField(auto_now_add=True)
    objects = QuestionManager()

    def __str__(self):
        return str(self.title)


class AnswerManages(models.Manager):
    def get_info_answers(self):
        return self.annotate(raiting=Count('likeanswer', distinct=True) - Count('dislikeanswer', distinct=True))
    
    def get_answers_for_question(self, id):
        return self.get_info_answers().filter(question_id=id).order_by('-is_correct', 'publish_date')


class Answer(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    publish_date = models.DateTimeField(auto_now_add=True)
    objects = AnswerManages()

    def __str__(self):
        return f"{str(self.text)[:80]}..."
    

class LikeQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    from_user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    
class DislikeQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    from_user = models.ForeignKey(Profile, on_delete=models.CASCADE)


class LikeAnswer(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    from_user = models.ForeignKey(Profile, on_delete=models.CASCADE)


class DislikeAnswer(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    from_user = models.ForeignKey(Profile, on_delete=models.CASCADE)
