from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Length, EqualTo, NumberRange, ValidationError, Optional, ReadOnly

import re

#Custom Validators
class EmailCheck:
    def __init__(self, regexStandard = None, message=None):
        if not regexStandard:
            self.regexStandard = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not message:
            self.message = "Invalid Email Address Provided"
    
    def __call__(self, form, field):
        email = field.data
        if re.match(self.regexStandard, email) == None:
            raise ValidationError(self.message)

class PassCheck:
    def __init__(self, regexStandard = None, message = None):
        if not regexStandard:
            self.regexStandard = r"^[a-zA-Z0-9!@#$%^&*()-=_+`~[\]\\{}|;:'\",.<>/?]+$"
        if not message:
            self.message = "Password fields must contain alphabets, numbers and special characters ( ()[]{},.;:'? )"

    def __call__(self, form, field):
        password = field.data
        if re.match(self.regexStandard, password) == None:
            raise ValidationError(self.message)

class PhoneCheck:
    def __init__(self, regexStandard = None, message = None):
        if not message:
            self.message = "Invalid phone number provided"
        if not regexStandard:
            self.regexStandard = r'^(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}$'

    def __call__(self, form, field):
        phoneNumber = field.data
        if re.match(self.regexStandard, phoneNumber) == None:
            raise ValidationError(self.message)

class IdentityCheck:
    def __init__(self, message=None, **kwargs):
        if not message:
            self.message = "Invalid syntax for email address or phone number provided"
        if not kwargs:
            self.emailRegex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            self.phoneRegex = r'^(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}$'
    
    def __call__(self, form, field):
        identity = field.data
        if re.match(self.emailRegex, identity) == None and re.match(self.phoneRegex, identity) == None:
            print("pp")
            raise ValidationError(self.message)

#Custom Form Fields
class customStringField(StringField):
    def __init__(self, label='', validators=None, **kwargs):
        super().__init__(label=label, validators=validators, **kwargs)
        self.render_kw = {}
        self.render_kw.update({"class" : "form-field", "required" : True, "placeholder" : self.description if self.description else label})
        self.render_kw.update(kwargs.get('render_kw')) if kwargs.get('render_kw') else None

        validators = [InputRequired("{} is a mandatory field".format(self.description))].append(validators)

class customIntegerField(IntegerField):
    def __init__(self, label='', validators=None, **kwargs):
        super().__init__(label=label, validators=validators, **kwargs)
        self.render_kw = {}
        self.render_kw.update({"class" : "form-field", "required" : True, "placeholder" : self.description if self.description else label})
        self.render_kw.update(kwargs.get('render_kw')) if kwargs.get('render_kw') else None

        validators = [InputRequired("{} is a mandatory field".format(self.description))].append(validators)

#Form Classes
class SignupForm(FlaskForm):
    first_name = customStringField(validators=[Length(min=1, max=30, message="First Name length must be between 1 and 30 letters")],description="Enter First Name")

    last_name = customStringField(validators=[Length(min=1, max=30, message="Last Name length must be between 1 and 30 letters")], description="Enter Last Name")

    age = customIntegerField(validators=[NumberRange(min=12, max=100, message="Age must be between 12 and 100")], description="Age")
    phone_number = customStringField(validators=[Length(min=10, max=10, message="Phone Number must have ten digits only")], description="Enter Phone Number")

    email_id = customStringField(validators=[EmailCheck()], description="Enter Email Address", render_kw={"type" : "email"})

    password = customStringField(validators=[Length(min=8, max=32, message="Password length must fall betweem 8 and 32 characters"), PassCheck()] , description="Set Password", render_kw={"type" : "password"})

    confirm_password = customStringField(validators=[EqualTo('password', message="Password fields do not match")],description="Confirm Password", render_kw={"type" : "password"})


class LoginForm(FlaskForm):
    emailPhone = customStringField(validators=[IdentityCheck()], description="Enter Email Address/Phone Number")

    password = customStringField(validators=[Length(min=8, max=32, message="Passwords are between 8 and 32 characters")], render_kw = {'type' : 'password'}, description="Enter password")

class FeedbackForm(FlaskForm):
    email = customStringField(validators=[EmailCheck()], description="Enter Email Address")
    title = customStringField(validators=[Length(min=6, max=32, message="Title length must be between 6 and 32 characters")], description="Add Title")
    flag = SelectField('Flag', choices=[
        ('support', 'Support'),
        ('bug', 'Bug'),
        ('query', 'Query'),
        ('order', 'Orders'),
        ('legal', 'Legal'),
        ('api', 'APIs')
    ])
    query = TextAreaField(validators=[Length(min=6, max=1024, message="Your query details must be between 6 and 1024 characters long"), InputRequired("Query is a required field")], render_kw={'placeholder' : "Add details"})


class ReviewForm(FlaskForm):
    review_title = customStringField(validators=[Length(min=6, max=32, message="Review title should be between 6 and 32 characters")], description="Review Title", render_kw={'id' : 'review-title'}, name="review-title")

    review_body = customStringField(validators=[Length(min=16, max=1024, message="Review body must be between 18 and 1024 characters long")], description="Review Description", render_kw={"class" : "review-body"}, name="review-body")

class BillingForm(FlaskForm):
    billingEmail = customStringField(validators=[EmailCheck()], name = "billing-email", description="Billing Address (Required)", render_kw={'class' : 'bg-field'})

    email = customStringField(validators=[EmailCheck()], name = "mail-id", description="Enter Billing Email Address", render_kw={"type" : "email", "id" : "mail-id", "class" : "mail-field"})

    confirmEmail = customStringField(validators=[EmailCheck(), EqualTo(email, message="Please ensure that the email addresses match before mailing your order")], description="Enter Billing Email Address", render_kw={"type" : "email", "id" : "confirm-mail-id", "class" : "mail-field"}, name="confirm-mail-id")

    message = TextAreaField(validators=[Optional(strip_whitespace=True)], name="gift-message", render_kw={"class" : "bg-field", "placeholder" : "Optionally, Enter a message to send alongside your purchase :D"})