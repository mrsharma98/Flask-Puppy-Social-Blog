# users/views.py
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from puppycompanyblog import db
from puppycompanyblog.models import User, BlogPost
from puppycompanyblog.users.forms import RegistrationForm, LoginForm, UpdateUserForm
from puppycompanyblog.users.picture_handler import add_profile_pic

# register user
# login user
# logout
# to show account (update UserForm)
# user's list of blog post

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        # about pass_confirm, the form in the form.py itself taking care of it.
        db.session.add(user)
        db.session.commit()

        flash('Thanks for registering! Now you can login!')
        return redirect(url_for('users.login'))

    return render_template('register.html', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user.check_password(form.password.data) and user is not None:
            #Log in the user

            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0]=='/':
                next = url_for('core.index')

            return redirect(next)

    return render_template('login.html', form=form)



@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():

    form = UpdateUserForm()

    if form.validate_on_submit():

        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data, username)
            # pic will have name of the pic i.e. username.png or .jpg
            current_user.profile_image = pic
            # assigned pic name to profile_image of the user in the model

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('User Account Updated!')

        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    # just to show the profile image on the account page, grabbing it using path
    profile_image = url_for('static', filename='profile_pics/'+current_user.profile_image)

    return render_template('account.html', profile_image=profile_image, form=form)



@users.route('/<username>')
def user_posts(username):
    page = request.args.get('page',1, type=int)
    # if the user has 150 posts then we are not gonna see all of
    # them at once, instead we see the above variable page in template
    # to distribute those posts on no. of pages
    # basically we are requesting for a page

    user = User.query.filter_by(username=username).first_or_404()
    #if user manually types in url bar and that username doesn't exist
    # then the above query will return 404 error
    # either grab the first user or return 404 error
    blog_posts = BlogPost.query.filter_by(author=user).order_by(BlogPost.date.desc()).paginate(page=page, per_page=5)
    # author is our backref, which we can use here

    return render_template('user_blog_posts.html', blog_posts=blog_posts, user=user)
