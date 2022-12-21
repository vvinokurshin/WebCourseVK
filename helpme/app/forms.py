from django import forms
from app import models 


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'mb-3'}), min_length=4)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'mb-3'}), min_length=8)


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'mb-3'}), min_length=8, help_text='The minimum length is 8 characters')
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'mb-3'}), min_length=8)

    class Meta:
        model = models.User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']

        widgets = {
            'email': forms.TextInput(attrs={'class': 'mb-3'}),
            'username': forms.TextInput(attrs={'class': 'mb-3'}),
            'first_name': forms.TextInput(attrs={'class': 'mb-3'}),
            'last_name': forms.TextInput(attrs={'class': 'mb-3'})
        }

        help_texts = {
            'email': ('It will be needed to restore the password'),
            'username': ('Will be used as your nickname on the site')
        }

    def clean(self):
        for field in ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm']:
            if field not in self.cleaned_data.keys():
                return self.cleaned_data

        if self.cleaned_data['password'] != self.cleaned_data['password_confirm']:
            self.add_error('password_confirm', "Passwords don't match")
        
        email_count = models.User.objects.filter(email=self.cleaned_data['email']).count()

        if email_count:
            self.add_error('email', 'A user with such an email has already been registered')

        if len(self.cleaned_data['username']) < 4:
            self.add_error('username', 'The minimum length of the username is 4')

        username_count = models.User.objects.filter(username=self.cleaned_data['username']).count()

        if username_count:
            self.add_error('username', 'A user with such an username has already been registered')

        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.save()

        self.cleaned_data.pop('password_confirm')
        profile = models.Profile.objects.create(user=user)

        if commit:
            profile.save()

        return profile


class AvatarForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ['avatar']
        labels = {
            'avatar': 'Avatar'
        }

    def save(self, profile):
        profile.avatar = self.data['avatar'] 
        profile.save()
        return profile


class SettingsForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['email', 'username', 'first_name', 'last_name']

        widgets = {
            'email': forms.TextInput(attrs={'class': 'mb-3', 'disabled': 'True'}),
            'username': forms.TextInput(attrs={'class': 'mb-3'}),
            'first_name': forms.TextInput(attrs={'class': 'mb-3'}),
            'last_name': forms.TextInput(attrs={'class': 'mb-3'})
        }

        help_texts = {
            'username': ('This is used as your nickname on the site')
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user.id
        self.fields['email'].widget.attrs['placeholder'] = user.email
        self.fields['username'].widget.attrs['value'] = user.username
        self.fields['first_name'].widget.attrs['value'] = user.first_name
        self.fields['last_name'].widget.attrs['value'] = user.last_name

    def clean(self):
        last_data = models.User.objects.get(id=self.user_id)

        try:
            existed_username_user = models.User.objects.get(username=self.cleaned_data['username'])

            if existed_username_user != last_data:
                self.add_error('username', 'A user with such an username has already been registered')
        except models.User.DoesNotExist:
            pass

        if len(self.cleaned_data['username']) < 4:
            self.add_error('username', 'The minimum length of the username is 4')

        return self.cleaned_data

    def save(self):
        user = models.User.objects.get(id=self.user_id)
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'mb-3'}), help_text='There may be several tags, list them separated by a space')

    class Meta:
        model = models.Question
        fields = ['title', 'text']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'mb-3'}),
            'text': forms.Textarea(attrs={'class': 'mb-3'}),
        }

        help_texts = {
            'title': ('Enter a title that briefly describes your problem. The length of the title should be from 10 to 80 characters.'),
            'text': ('Describe your problem in the most detail'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'How to create a question?'
        self.fields['title'].required = False
        self.fields['text'].widget.attrs['placeholder'] = ''
        self.fields['text'].required = False
        self.fields['tags'].widget.attrs['placeholder'] = 'Python PostgreSQL'
        self.fields['tags'].required = False

    def clean(self):
        if 'title' not in self.cleaned_data.keys() or len(self.cleaned_data['title']) < 3:
            self.add_error('title', 'The minimum length of the title is 3')

        if 'text' not in self.cleaned_data.keys() or len(self.cleaned_data['text']) < 5:
            self.add_error('text', 'The minimum length of the text of the question text is 5')

    def save(self, profile):
        question = super().save(commit=False)
        question.user = profile
        question.save()
        tags = self.cleaned_data['tags'].split()

        for tag in tags:
            new = models.Tag.objects.get_or_create(name=tag)
            question.tags.add(new[0].id)
        question.save()

        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = ['text']

        widgets = {
            'text': forms.Textarea(attrs={'class': 'mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = 'Write your answer'
        self.fields['text'].required = False

    def clean(self):
       if 'text' not in self.cleaned_data.keys() or len(self.cleaned_data['text']) < 5:
                self.add_error('text', 'The minimum length of the text of the question text is 5')

    def save(self, profile, question):
        answer = super().save(commit=False)
        answer.user = profile
        answer.question = question
        answer.save()

        return answer
