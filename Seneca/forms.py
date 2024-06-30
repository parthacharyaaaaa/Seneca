from flask_wtf import FlaskForm, RecaptchaField, RecaptchaWidget
from wtforms import StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Length, EqualTo, NumberRange, ValidationError, AnyOf, Regexp

import re

#Custom Validators
class EmailCheck:
    def __init__(self, regexStandard = None, message=None):
        self.regexStandard = regexStandard or r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        self.message = message or "Invalid Email Address Provided"
    
    def __call__(self, form, field):
        email = field.data
        print("Field Data: ", email)
        if re.match(self.regexStandard, email) == None:
            print("Forms: Incorrect Email Format")
            raise ValidationError(self.message)

class PassCheck:
    def __init__(self, regexStandard = None, message = None):

        self.regexStandard = regexStandard or r"^[a-zA-Z0-9!@#$%^&*()-=_+`~[\]\\{}|;:'\",.<>/?]+$"

        self.message = message or "Password fields must contain alphabets, numbers and special characters ( ()[]{},.;:'? )"

    def __call__(self, form, field):
        password = field.data
        if re.match(self.regexStandard, password) == None:
            raise ValidationError(self.message)

class PhoneCheck:
    def __init__(self, regexStandard = None, message = None):
        self.message = message or "Invalid phone number provided"

        self.regexStandard = regexStandard or r'^(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}$'

    def __call__(self, form, field):
        phoneNumber = field.data
        if re.match(self.regexStandard, phoneNumber) == None:
            raise ValidationError(self.message)

class IdentityCheck:
    def __init__(self, message=None, emailRegex = None, phoneRegex = None):
        self.message = message or "Invalid syntax for email address or phone number provided"


        self.emailRegex = emailRegex or r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        self.phoneRegex = phoneRegex or r'^(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}$'
    
    def __call__(self, form, field):
        identity = field.data
        if re.match(self.emailRegex, identity) == None and re.match(self.phoneRegex, identity) == None:
            print("pp")
            raise ValidationError(self.message)

class lengthCheck:
    def __init__(self, min=-1, max=0, message = None):
        self.min = min
        self.max = max

        assert self.max >= self.min,  "Maximum length must be greater than or equal to minimum length"
        self.message =  message or "Input Length must be between {} and {}".format(self.min, self.max)

    def __call__(self, form, field):
        data = (field.data).strip()
        length = len(data)
        print("Data: ", data, length)
        if length < self.min or length > self.max:
            print("pp")
            raise ValidationError(self.message)

class BillingCheck:
    def __init__(self, flag, billingEmail, shippingAddress, confirmShippingAddress):
        self.flag = flag
        self.billingEmail = billingEmail
        self.shippingAddress = shippingAddress
        self.confirmShippingAddress = confirmShippingAddress

    def __call__(self) -> bool:
        print("BillingCheck called")

        if self.flag not in ['download', 'mail']:
            print("Invalid Flag")
            return False
        
        # if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.billingEmail) == None:
        #     return False

        if self.flag == "mail":
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.shippingAddress) == None:
                return False
            
            if self.shippingAddress in (None, 'undefined', '') or len((self.shippingAddress).strip()) < 6:
                return False

            if self.confirmShippingAddress != self.shippingAddress:
                return False
    
        print("Valid")
        return True
            
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
    first_name = customStringField(validators=[lengthCheck(min=1, max=30, message="First Name length must be between 1 and 30 letters")], description="Enter First Name")

    last_name = customStringField(validators=[lengthCheck(min=1, max=30, message="Last Name length must be between 1 and 30 letters")], description="Enter Last Name")

    age = customIntegerField(validators=[NumberRange(min=12, max=100, message="Age must be between 12 and 100")], description="Age")
    phone_number = customStringField(validators=[lengthCheck(min=10, max=15), PhoneCheck()], description="Enter Phone Number")

    email_id = customStringField(validators=[EmailCheck(), lengthCheck(5, 256)], description="Enter Email Address", render_kw={"type" : "email"})

    password = customStringField(validators=[lengthCheck(min=8, max=32, message="Password length must fall betweem 8 and 32 characters"), PassCheck()] , description="Set Password", render_kw={"type" : "password"})

    confirm_password = customStringField(validators=[EqualTo('password', message="Password fields do not match")],description="Confirm Password", render_kw={"type" : "password"})

    recaptcha = RecaptchaField()

class LoginForm(FlaskForm):
    emailPhone = customStringField(validators=[IdentityCheck(), lengthCheck(5, 256)], description="Enter Email Address/Phone Number")

    password = customStringField(validators=[Length(min=8, max=32, message="Passwords are between 8 and 32 characters")], render_kw = {'type' : 'password'}, description="Enter password")
    recaptcha = RecaptchaField()

class FeedbackForm(FlaskForm):
    email = customStringField(validators=[EmailCheck()], description="Enter Email Address")
    title = customStringField(validators=[lengthCheck(min=6, max=32, message="Title length must be between 6 and 32 characters")], description="Add Title")
    flag = SelectField('Flag', choices=[
        ('support', 'Support'),
        ('bug', 'Bug'),
        ('query', 'Query'),
        ('order', 'Orders'),
        ('legal', 'Legal'),
        ('api', 'APIs')
    ], validators=[AnyOf(["support", "bug", "query", "order", "legal", "api"])])
    query = TextAreaField(validators=[lengthCheck(min=6, max=1024, message="Your query details must be between 6 and 1024 characters long"), InputRequired("Query is a required field")], render_kw={'placeholder' : "Add details"})

class ReviewForm(FlaskForm):
    review_title = customStringField(validators=[lengthCheck(min=6, max=32, message="Review title should be between 6 and 32 characters"), Regexp(r'^[a-zA-Z0-9 .,!?;:\'\"-]+$', message="Unsupported character found in review title")], description="Review Title", render_kw={'id' : 'review-title'}, name="review-title")

    review_body = customStringField(validators=[lengthCheck(min=16, max=1024, message="Review body must be between 18 and 1024 characters long"), Regexp(r'^[a-zA-Z0-9 .,!?;:\'\"-]+$', message="Unsupported character found in review body")], description="Review Description", render_kw={"class" : "review-body"}, name="review-body")