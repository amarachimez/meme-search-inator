import webapp2
import jinja2
import os
import time
import datetime
import json
from google.appengine.api import users
from google.appengine.ext import ndb
from models import Member
from models import Message
from seed_data import seed_data
from search import search

the_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class HomePage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    data = {}
    if user:
        data["logged_in"] = True
        data["signout_url"] = users.create_logout_url('/')
        user = users.get_current_user()
        member_query = Member.query(Member.email == user.nickname())
        member = member_query.get()
        if member is None:
            data["logged_in"] = False
            data["login_url"] = users.create_login_url('/')
            data["register_url"] = users.create_login_url('/Registration')
        else:
            data["name"] = member.display_name
    else:
        data["logged_in"] = False
        data["login_url"] = users.create_login_url('/')
        data["register_url"] = users.create_login_url('/Registration')

    home_template = the_jinja_env.get_template('templates/HomePage.html')
    self.response.write(home_template.render(data))  # the response

class ResultsPage(webapp2.RequestHandler):
    pass

class RegistrationPage(webapp2.RequestHandler):
    def get(self):
        registration_template = the_jinja_env.get_template('templates/RegistrationPage.html')
        self.response.write(registration_template.render())  # the response

    def post(self):
        user = users.get_current_user()
        # Create a new member.
        member = Member(
            display_name = self.request.get('display_name'),
            email = user.nickname())
        # Store that Entity in Datastore.
        member.put()
        time.sleep(1)
        return webapp2.redirect("/")

class LoginPage(webapp2.RequestHandler):
    def get(self):
        login_url = users.create_login_url('/')
        login_html_element = '<a href="%s">Sign in</a>' % login_url
        self.response.write('Please log in.<br>' + login_html_element)

class MessagesPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        data = {}
        if user:
            member_query = Member.query(Member.email == user.nickname())
            member = member_query.get()
            data["logged_in"] = True
            data["message_list"] = Message.query().order(Message.timestamp)
            data["signout_url"] = users.create_logout_url('/')
            data["name"] = member.display_name
        else:
            data["logged_in"] = False
            data["login_url"] = users.create_login_url('/')
            data["register_url"] = users.create_login_url('/Registration')
        messages_template = the_jinja_env.get_template('templates/MessagesPage.html')
        self.response.write(messages_template.render(data))  # the response

    def post(self):
        user = users.get_current_user()
        member_query = Member.query(Member.email == user.nickname())
        member = member_query.get()
        now = datetime.datetime.now()
        #Create a new message.
        message = Message(
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S"),
            message = self.request.get('message'),
            sender = member.display_name
        )
        # Store that Entity in Datastore.
        message.put()
        time.sleep(1)
        return webapp2.redirect("/Messages")

class BlogPage(webapp2.RequestHandler):
    def get(self):
        blog_template = the_jinja_env.get_template('templates/BlogPage.html')
        self.response.write(blog_template.render())  # the response

class MessagesJSON(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        query = Message.query().order(Message.timestamp)
        data = []
        for m in query:
            data.append({"timestamp" : m.timestamp, "sender": m.sender, "message": m.message})
        self.response.out.write(json.dumps(data))

class SeedData(webapp2.RequestHandler):
    def get(self):
        seed_data()
        self.response.write("test")

class qTest(webapp2.RequestHandler):
    def get(self):
        results = search('just eats monkey when your')
        out = ''
        for result in results:
            out += ("<img src="+result+">")
        self.response.write(out)

app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/Results', ResultsPage),
    ('/Registration', RegistrationPage),
    ('/Messages', MessagesPage),
    ('/Blog', BlogPage),
    ('/MessagesJSON', MessagesJSON),
    ('/SeedData', SeedData),
    ('/q', qTest)
    ], debug=True)
