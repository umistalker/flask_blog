import datetime

from flask import flash, url_for, request, current_app, render_template
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import redirect
from flask_babel import _, lazy_gettext as _l
from blog import db
from blog.main import bp
from blog.main.forms import PostForm, EditProfileForm, EmptyForm, EditPostForm, MessageForm
from blog.models import Post, User, Message


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            body=form.post.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post is posted')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POST_PER_PAGE'], False
    )
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home', posts=posts.items, form=form, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    form = EmptyForm()
    user = db.session.query(User).filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(Post).order_by(Post.date.desc()).paginate(
        page, current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    form = EmptyForm()
    user = db.session.query(User).filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user, form=form)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        db.session.commit()


@bp.route('/user/edit_profile', methods=['GET', "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(Post).order_by(Post.date.desc()).paginate(
        page, current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/delete/<username>/<int:id>')
@login_required
def delete(username, id):
    post = db.session.query(Post).filter_by(id=id).first_or_404()
    if post.author.username == username:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted')
    return redirect(url_for('main.index'))


@bp.route('/edit_post/<username>/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(username, id):
    form = EditPostForm()
    post = db.session.query(Post).filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        if post.author.username == username:
            post.body = form.post_text.data
            post.date = datetime.datetime.utcnow()
            db.session.commit()
            flash('Post edited')
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        form.post_text.data = post.body
    return render_template('edit_post.html', title='Edit Post', form=form)


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = db.session.query(User).filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(
            author=current_user,
            recipient=user,
            body=form.message.data
        )
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent')
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title='Send Message', form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    current_last_message_read_time = datetime.datetime.utcnow()
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.date.desc()).paginate(
        page, current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_message/<username>/<id>', methods=['GET', 'POST'])
@login_required
def edit_message(username, id):
    form = MessageForm()
    msg = db.session.query(Message).filter_by(author=username, id=id).first_or_404()
    if form.validate_on_submit():
        if current_user.username == username:
            msg.body = form.message.data
            msg.data = datetime.datetime.utcnow()
            db.session.commit()
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        form.message.data = msg.body
    return render_template('send_message.html', title='Send Message', form=form)
