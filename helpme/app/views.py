from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator

from app import models
from app import utils


def index(request: HttpRequest):
    page = utils.paginate(models.Question.objects.get_new_questions(), request)
    context = {
        'questions': page['object_list'], 
        'page': page,
        'is_auth': False,
        'if_empty': {
            'title': 'So far, there are no questions.',
            'description': 'But you can ask your question!'
        },
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }

    return render(request, 'index.html', context)

def hot(request: HttpRequest):
    page = utils.paginate(models.Question.objects.get_top_questions(), request)
    context = {
        'questions': page['object_list'], 
        'page': page,
        'is_auth': False,
        'if_empty': {
            'title': 'So far there are no questions.',
            'description': 'But you can ask your question!'
        },
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }

    return render(request, 'hot.html', context)

def question(request: HttpRequest, question_id: int):
    context = {
        'is_auth': True,
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }
    question_item = models.Question.objects.get_question(question_id)

    if not question_item:
        return render(request, 'not_found.html', context, status=404)

    page = utils.paginate(models.Answer.objects.get_answers_for_question(question_id), request)
    context.update({
        "question": question_item,
        "answers": page['object_list'],
        'page': page,
        'if_empty': {
            'title': 'So far, there are no answers.',
            'description': 'But you can answer this question first!'
        },
    })

    return render(request, 'question.html', context)

def login(request: HttpRequest):
    context = {
        'is_auth': False,
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }
    return render(request, 'login.html', context)

def signup(request: HttpRequest):
    context = {
        'is_auth': False,
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }
    return render(request, 'signup.html', context)

def ask(request: HttpRequest):
    context = {
        'is_auth': True, 
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }
    return render(request, 'ask.html', context)

def tag(request: HttpRequest, tag_name: str):
    page = utils.paginate(models.Question.objects.get_questions_by_tag(tag_name), request)
    context = {
        'tag_name': tag_name, 
        'questions': page['object_list'], 
        'page': page,
        'is_auth': False,
        'if_empty': {
            'title': 'So far, there are no questions with such a tag.',
            'description': 'But you can ask your question!'
        },
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }
    return render(request, 'tag.html', context)

def settings(request: HttpRequest):
    context = {
        'is_auth': True,
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }
    return render(request, 'settings.html', context)

def profile(request: HttpRequest, user_id: int):
    context = {
        'is_auth': True,
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }
    user = models.Profile.objects.get_user_by_id(user_id)

    if not user:
        return render(request, 'not_found.html', context, status=404)
    
    page = utils.paginate(models.Question.objects.get_question_by_user(user_id), request)
    context = {
        'questions': page['object_list'], 
        'page': page,
        'is_auth': False,
        'if_empty': {
            'title': 'So far, this user has not asked any questions yet.'
        },
        'profile': user,
        'top_users': models.Profile.objects.get_top_users(),
        'top_tags': models.Tag.objects.get_top_tags(count=7)
    }

    return render(request, 'profile.html', context)