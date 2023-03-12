# Google forms
Instalation:
```console
$ git clone https://github.com/piotr-ginal/google-forms.git
$ cd google-forms
$ python -m pip install -e .
```

## Spammers
scripts that will automatically send responses to a given form
### threaded_spammer_1.py
Usage:
```console
$ python threaded_spammer_1.py
```
You will be asked for the id of your form. You will then be asked to answer each question on the form. At the end, you will have to specify the number of replies you want to send (eg. 500).

For now, only these types of questions are supported:
- short answer question
- paragraph question
- dropdown question
- multiple choice question

If your form contains an unsupported question the script will stop.