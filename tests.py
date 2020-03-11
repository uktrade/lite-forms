from http import HTTPStatus
from unittest import TestCase

from django.test.client import RequestFactory

from lite_forms.components import (
    Form,
    DetailComponent,
    TextInput,
    FormGroup,
    _Component,
    Label,
    HelpSection,
    Option,
    DateInput,
    ControlListEntryInput,
    BackLink,
    HiddenField,
    NumberInput,
    RadioButtons,
)
from lite_forms.helpers import (
    nest_data,
    flatten_data,
    remove_unused_errors,
    get_form_by_pk,
    get_next_form,
    get_previous_form,
    convert_form_to_summary_list_instance,
    get_all_form_components,
    insert_hidden_fields,
)
from lite_forms.submitters import submit_paged_form
from lite_forms.templatetags import custom_tags
from lite_forms.templatetags.custom_tags import prefix_dots


class FormTests(TestCase):
    def test_get_form_by_pk(self):
        forms = FormGroup([Form(questions=[]), Form(questions=[]), Form(questions=[])])

        self.assertEqual(get_form_by_pk(1, forms).pk, 1)

    def test_get_previous_form_by_pk(self):
        forms = FormGroup([Form(questions=[]), Form(questions=[]), Form(questions=[])])

        self.assertEqual(get_previous_form(2, forms).pk, 1)

    def test_get_next_form_by_pk(self):
        forms = FormGroup([Form(questions=[]), Form(questions=[]), Form(questions=[])])

        self.assertEqual(get_next_form(1, forms).pk, 2)

    def test_classname(self):
        expected_value = "type"
        actual_value = custom_tags.classname(TestCase)

        self.assertEqual(actual_value, expected_value)

    def test_remove_unused_errors(self):
        form = Form(questions=[TextInput("name"), TextInput("age"), TextInput("password"), DetailComponent("", ""),])

        errors = {
            "name": "This field must not be empty",
            "email": "This field must not be empty",
            "age": "This field must not be empty",
            "password": "This field must not be empty",
        }

        cleaned_errors = {
            "name": "This field must not be empty",
            "age": "This field must not be empty",
            "password": "This field must not be empty",
        }

        self.assertEqual(cleaned_errors, remove_unused_errors(errors, form))

    def test_nest_data(self):
        value = {
            "reference": "conversation_16",
            "organisation.name": "Live on coffee and flowers inc.",
            "organisation.site.address.city": "London",
            "organisation.site.name": "Lemonworld",
            "user.first_name": "Matthew",
        }

        data = nest_data(value)

        self.assertEqual(
            data,
            {
                "reference": "conversation_16",
                "organisation": {
                    "name": "Live on coffee and flowers inc.",
                    "site": {"address": {"city": "London",}, "name": "Lemonworld",},
                },
                "user": {"first_name": "Matthew",},
            },
        )

    def test_flatten_data(self):
        value = {
            "reference": "conversation_16",
            "organisation": {
                "name": "Live on coffee and flowers inc.",
                "site": {"address": {"city": "London",}, "name": "Lemonworld",},
            },
            "user": {"first_name": "Matthew",},
        }

        data = flatten_data(value)

        self.assertEqual(
            data,
            {
                "reference": "conversation_16",
                "organisation.name": "Live on coffee and flowers inc.",
                "organisation.site.address.city": "London",
                "organisation.site.name": "Lemonworld",
                "user.first_name": "Matthew",
            },
        )

    def test_convert_form_to_summary_list_instance(self):
        form = Form(title="I Am Easy to Find", caption="The National", default_button_name="Rylan")
        form = convert_form_to_summary_list_instance(form)
        self.assertEqual(form.caption, "")
        self.assertEqual(form.buttons[0].value, "Save and return")
        self.assertEqual(form.buttons[0].action, "return")

    def test_get_all_form_components(self):
        form = Form(
            title="I Am Easy to Find",
            questions=[
                RadioButtons(
                    name="hello",
                    options=[
                        Option("key", "value", components=[TextInput("text")]),
                        Option("key2", "value", components=[TextInput("text2")]),
                    ],
                )
            ],
        )
        components = get_all_form_components(form)
        self.assertEqual(len(components), 3)

    def test_insert_hidden_fields(self):
        form = Form(title="I Am Easy to Find", questions=[],)
        insert_hidden_fields({"matt": "berninger"}, form)
        self.assertEqual(len(form.questions), 1)


class TestSubmitPagedFormTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_expect_many_values(self):
        """
        Ensure submit_paged_form handles a field which expects many values.
        """
        request = self.request_factory.post(
            "/thing",
            (
                "key_a=a&key_a=b&key_a=c&"
                "key_b=d&key_b=e&key_b=f&"
                "key_c=g&"
                "key_d=h&"
                "form_pk=0&"
                "csrfmiddlewaretoken=bar"
            ),
            content_type="application/x-www-form-urlencoded",
        )
        forms = FormGroup([Form(questions=[]), Form(questions=[]), Form(questions=[]),])

        def handle_post(request, data):
            return data, HTTPStatus.OK

        form, data = submit_paged_form(request, forms, handle_post, expect_many_values=["key_a", "key_c", "key_e"])

        self.assertEqual(
            data, {"key_a": ["a", "b", "c"], "key_b": "f", "key_c": ["g"], "key_d": "h", "key_e": None,},
        )


class TemplateTagsTestCase(TestCase):
    def test_prefix_dots(self):
        self.assertEqual("nodots", prefix_dots("nodots"))
        self.assertEqual(r"\\.startdot", prefix_dots(".startdot"))
        self.assertEqual(r"enddot\\.", prefix_dots("enddot."))
        self.assertEqual(r"mid\\.dot", prefix_dots("mid.dot"))
        self.assertEqual(r"\\.all\\.the\\.dots\\.", prefix_dots(".all.the.dots."))


class MarkdownTest(TestCase):
    def setUp(self):
        super().setUp()
        self.markdown_description = "Please **Click** this [link](https://www.gov.uk/)"
        self.html_description = (
            "Please <strong>Click</strong> this <a class='govuk-link' href=\"https://www.gov.uk/\">link</a>"
        )

    def test_generic_component(self):
        component = _Component(name="a", description=self.markdown_description)
        self.assertEqual(component.description, self.html_description)

    def test_label(self):
        label = Label(self.markdown_description)
        self.assertEqual(label.text, self.html_description)

    def test_form(self):
        form = Form(description=self.markdown_description)
        self.assertEqual(form.description, self.html_description)

    def test_detail_component(self):
        detail = DetailComponent(title="abc", description=self.markdown_description)
        self.assertEqual(detail.description, self.html_description)

    def test_help_section(self):
        detail = HelpSection(title="abc", description=self.markdown_description)
        self.assertEqual(detail.description, self.html_description)

    def test_option(self):
        option = Option(key="a", value="A", description=self.markdown_description)
        self.assertEqual(option.description, self.html_description)

    def test_date_input(self):
        date = DateInput(prefix="Date", description=self.markdown_description)
        self.assertEqual(date.description, self.html_description)

    def test_control_list_entry_input(self):
        clc = ControlListEntryInput(name="abc", options=[], description=self.markdown_description)
        self.assertEqual(clc.description, self.html_description)


class SingleQuestionFormAccessibilityTest(TestCase):
    def test_no_questions_no_title_label(self):
        form = Form()
        self.assertIsNone(form.single_form_element)

    def test_no_user_inputs_no_title_label(self):
        form = Form(questions=[BackLink(), Label("abc"), HiddenField("abc", "123"),])
        self.assertIsNone(form.single_form_element)

    def test_single_user_input_with_other_questions_has_title_label(self):
        name = "Test"
        form = Form(questions=[BackLink(), Label("abc"), TextInput(name), HiddenField("abc", "123"),])
        self.assertEqual(form.single_form_element.name, name)

    def test_single_user_input_alone_has_title_label(self):
        name = "Test"
        form = Form(questions=[TextInput(name),])
        self.assertEqual(form.single_form_element.name, name)

    def test_multiple_user_inputs_no_title_label(self):
        form = Form(questions=[TextInput("abc"), NumberInput("def"),])
        self.assertIsNone(form.single_form_element)
