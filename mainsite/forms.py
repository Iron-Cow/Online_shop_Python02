from django.forms import Form, CharField, EmailField, Textarea


class FeedbackForm(Form):
    email = EmailField()
    text = CharField(widget=Textarea)
