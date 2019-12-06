import copy
import re

from collections.abc import MutableMapping

from lite_forms.components import FormGroup, Link


def get_form_by_pk(form_pk, form_group: FormGroup):
    for form in form_group.forms:
        if str(form.pk) == str(form_pk):
            return copy.deepcopy(form)
    return


def get_previous_form(form_pk, form_group: FormGroup):
    for form in form_group.forms:
        # If the current form is the final form in the group
        if int(form.pk) == int(form_pk) - 1:
            return copy.deepcopy(form)
    return


def get_next_form(form_pk, form_group: FormGroup):
    next_one = False
    for form in form_group.forms:
        if next_one:
            return copy.deepcopy(form)
        if str(form.pk) == str(form_pk):
            next_one = True
    return


def remove_unused_errors(errors, form):
    """
    Removes all errors that don't belong to a form's fields
    :param errors: ['errors'] children
    :param form: Form object
    :return: Array of cleaned errors
    """
    cleaned_errors = {}

    if not errors:
        return {}

    for question in form.questions:
        if hasattr(question, "name") and errors.get(question.name):
            cleaned_errors[question.name] = errors.get(question.name)

    return cleaned_errors


def nest_data(sent_data):
    """
    Nests strings into dictionaries eg
    {
        'site.name': 'SITE1'
    }
    becomes
    {
        'site': {
            'name': 'SITE1'
        }
    }
    """

    def _create_keys(d, keys, value):
        keys = keys.split(".")
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    data = {}

    for q, v in sent_data.items():
        _create_keys(data, q, v)

    return data


def flatten_data(d, parent_key="", sep="."):
    """
    Flattens dictionaries eg
    {
        'site': {
            'name': 'SITE1'
        }
    }
    becomes
    {
        'site.name': 'SITE1'
    }
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_data(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def conditional(condition: bool, obj, else_obj=None):
    """
    Returns the object depending on a condition
    Optionally: returns else_obj if it is set
    """
    if condition:
        return obj

    return else_obj


def extract_links(text: str):
    """
    Takes a string and splits into a list of strings and links
    based on markdown conventions
    """
    markup_regex = "(.*?)(\[.*?\))([^\[]*)"  # noqa
    link_regex = "\[(.*)\]\((.*)\)"  # noqa

    return_value = []
    matches = re.findall(markup_regex, text)

    if not matches:
        return [text]

    for match in matches:
        for item in [x for x in match if x]:
            value = re.findall(link_regex, item)

            if len(value) == 0:
                return_value.append(item)
            else:
                return_value.append(Link(value[0][0], value[0][1]))

    return [x for x in return_value if x]
