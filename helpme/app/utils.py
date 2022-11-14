from django.core.paginator import Paginator
from app.models import *

def paginate(objects_list, request, per_page=10):
    p = Paginator(objects_list, per_page)
    num_page = request.GET.get('page')
    page = p.get_page(num_page) 

    return gen_page_for_paginator(page)

def gen_page_for_paginator(page):
    count_pages = len(page.paginator.page_range)
    cur_page = {'first_page': None, 'last_page': None}

    if 3 < page.number <= count_pages - 3:
        cur_page['first_page'], cur_page['last_page'] = 1, count_pages
        cur_page['range'] = range(page.number - 1, page.number + 2)
    elif page.number > 3:
        cur_page['first_page'] = 1
        cur_page['range'] = range(page.number - 1, count_pages + 1)
    elif page.number <= count_pages - 3:
        cur_page['last_page'] = count_pages
        cur_page['range'] = range(1, page.number + 2)
    else:
        cur_page['range'] = range(1, count_pages + 1)

    cur_page['object_list'] = page.object_list
    cur_page['previous'] = page.previous_page_number() if page.has_previous() else None
    cur_page['next'] = page.next_page_number() if page.has_next() else None
    cur_page['number'] = page.number

    return cur_page

def get_questions_by_tag(all_questions, tag):
    questions = []

    for question in all_questions:
        if tag in question['tags']:
            questions.append(question)

    return questions

def sort_questions(questions, reverse=True):
    return sorted(questions, key=lambda x: x['likes'], reverse=reverse)

def add_info_about_question(questions):
    for question in questions:
        question_item = question
        question_item['count_answers'] = Answer.objects.get_count_answers_for_question(question.id)
        question_item['image'] = Question.objects.get_user_avatar(question.id)
        question_item['tags'] = Question.objects.get_tags(question.id)