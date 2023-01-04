from django.http import HttpRequest#, HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import auth
from django.urls import reverse
from django.core.cache import cache
from django.contrib.auth.decorators import login_required


from app import models
from app import utils
from app import forms


def index(request: HttpRequest):
    page = utils.paginate(models.Question.objects.get_new_questions(), request)
    context = {
        'questions': page['object_list'], 
        'page': page,
        'if_empty': {
            'title': 'So far, there are no questions.',
            'description': 'But you can ask your question!'
        },
        'auth_user': models.Profile.objects.get_prof_by_user_id(request.user.id),
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }

    return render(request, 'index.html', context)


def hot(request: HttpRequest):
    page = utils.paginate(models.Question.objects.get_top_questions(), request)
    context = {
        'questions': page['object_list'], 
        'page': page,
        'if_empty': {
            'title': 'So far there are no questions.',
            'description': 'But you can ask your question!'
        },
        'auth_user': models.Profile.objects.get_prof_by_user_id(request.user.id),
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }

    return render(request, 'hot.html', context)


def question(request: HttpRequest, question_id: int):
    context = {
        'auth_user': models.Profile.objects.get_prof_by_user_id(request.user.id),
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }
    question_item = models.Question.objects.get_question(question_id)

    if not question_item:
        return render(request, 'not_found.html', context, status=404)

    if request.method == 'GET':
        answer_form = forms.AnswerForm()
    elif request.method == 'POST':
        if str(request.user) == 'AnonymousUser':
            return redirect(f'/login/?continue={request.path}')
    
        answer_form = forms.AnswerForm(request.POST)

        if answer_form.is_valid():
            profile = models.Profile.objects.get_prof_by_user_id(request.user.id)
            answer = answer_form.save(profile, question_item)
            answers = Paginator(models.Answer.objects.get_answers_for_question(question_id), 10)

            return redirect(f'{request.path}?page={answers.num_pages}#{answer.id}')

    page = utils.paginate(models.Answer.objects.get_answers_for_question(question_id), request)
    context.update({
        "question": question_item,
        "answers": page['object_list'],
        'page': page,
        'if_empty': {
            'title': 'So far, there are no answers.',
            'description': 'But you can answer this question first!'
        },
        'form': answer_form
    })

    return render(request, 'question.html', context)


def login(request: HttpRequest):
    _continue = request.GET.get("continue")
    if not _continue:
        _continue = "index"

    if request.user.is_authenticated:
        return redirect(_continue)

    if request.method == 'GET':
        user_form = forms.LoginForm()
        cache.set("continue", _continue)
    elif request.method == 'POST':
        user_form = forms.LoginForm(request.POST)

        if user_form.is_valid():
            user = auth.authenticate(request=request, **user_form.cleaned_data)

            if user:
                auth.login(request, user)
                _continue_url = cache.get('continue')

                if not _continue_url:
                    _continue_url = 'index'

                cache.delete('continue')
                return redirect(_continue_url)
            
            user_form.add_error(field=None, error="Wrong username or password")

    context = {
        'auth_user': models.Profile.objects.get_prof_by_user_id(request.user.id),
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7),
        'form': user_form
    }

    return render(request, 'login.html', context)


def signup(request: HttpRequest):
    if request.method == 'GET':
        user_form = forms.RegistrationForm()
    elif request.method == 'POST':
        user_form = forms.RegistrationForm(request.POST)

        if user_form.is_valid():
            profile = user_form.save()
            auth.login(request, profile.user)
            return redirect(reverse('index'))
                        
    context = {
        'auth_user': models.Profile.objects.get_prof_by_user_id(request.user.id),
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7),
        'form': user_form
    }
    return render(request, 'signup.html', context)

   
@login_required(login_url="login", redirect_field_name="continue")
def ask(request: HttpRequest):
    if request.method == 'GET':
        question_form = forms.QuestionForm()
    elif request.method == 'POST':
        question_form = forms.QuestionForm(request.POST)

        if question_form.is_valid():
            question = question_form.save(models.Profile.objects.get_prof_by_user_id(request.user.id))
            return redirect(reverse('question', args=[question.id]))
        
    context = {
        'auth_user': models.Profile.objects.get_prof_by_user_id(request.user.id),
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7),
        'form': question_form
    }
    return render(request, 'ask.html', context)


def tag(request: HttpRequest, tag_name: str):
    page = utils.paginate(models.Question.objects.get_questions_by_tag(tag_name), request)
    context = {
        'tag_name': tag_name, 
        'questions': page['object_list'], 
        'page': page,
        'if_empty': {
            'title': 'So far, there are no questions with such a tag.',
            'description': 'But you can ask your question!'
        },
        'auth_user': models.Profile.objects.get_prof_by_user_id(request.user.id),
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }
    return render(request, 'tag.html', context)


@login_required(login_url="login", redirect_field_name="continue")
def settings(request: HttpRequest):
    if request.method == 'GET':
        settings_form = forms.SettingsForm(user=request.user)
        avatar_form = forms.AvatarForm()
    elif request.method == 'POST':
        settings_form = forms.SettingsForm(request.user, request.POST)
        avatar_form = forms.AvatarForm(request.FILES)

        if settings_form.is_valid() and avatar_form.is_valid():
            settings_form.save()

            if request.FILES:
                avatar_form.save(models.Profile.objects.get_prof_by_user_id(request.user.id))
            return redirect(reverse('settings'))

        settings_form.add_error(field=None, error="First fill in all the fields correctly")

    context = {
        'auth_user': models.Profile.objects.get_prof_by_user_id(request.user.id),
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7),
        'settings_form': settings_form,
        'avatar_form': avatar_form
    }
    return render(request, 'settings.html', context)


def profile(request: HttpRequest, user_id: int):
    context = {
        'auth_user': models.Profile.objects.get_prof_by_user_id(request.user.id),
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }
    user = models.Profile.objects.get_profile_by_id(user_id)

    if not user:
        return render(request, 'not_found.html', context, status=404)
    
    page = utils.paginate(models.Question.objects.get_questions_by_user(user_id), request)
    context = {
        'questions': page['object_list'], 
        'page': page,
        'if_empty': {
            'title': 'So far, this user has not asked any questions yet.'
        },
        'profile': user,
        'auth_user': models.Profile.objects.get_prof_by_user_id(request.user.id),
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }

    return render(request, 'profile.html', context)


@login_required(login_url="login", redirect_field_name="continue")
def logout(request: HttpRequest):
    auth.logout(request)
    return redirect(request.META.get('HTTP_REFERER'))