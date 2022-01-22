from datetime import datetime, timedelta
import unittest
import config
from blog import models, db, create_app
from blog.models import User, Post


class Test(unittest.TestCase):
    def setUp(self):
        db.create_all()
        db.session.add(User(username='mark', email='umistalker@gmail.com'))
        db.session.add(User(username='mark1', email='test@test.com'))
        db.session.add(Post(body='Some text'))
        db.session.commit()

    def tearDown(self) -> None:
        db.drop_all()

    def test_user(self):
        user = db.session.query(User).filter(User.email == 'test@test.com').first()
        user.set_password('my_password')
        self.assertEqual(user.role, 0)
        self.assertEqual(user.username, 'mark1')
        self.assertTrue(user.check_password('my_password'))
        self.assertFalse(user.check_password('not_my_password'))

    def test_post(self):
        post = db.session.query(Post).filter_by(body='Some text').first()
        self.assertEqual(post.body, 'Some text')

    def test_avatar(self):
        user = db.session.query(User).filter_by(username='mark').first()
        self.assertEqual(user.grav(128),
                         ('https://www.gravatar.com/avatar/ab06ef7164fb4bdff66a1c9c0e20343a?size=128&default=retro'))

    def test_follow(self):
        user = db.session.query(User).filter_by(username='mark').first()
        user2 = db.session.query(User).filter_by(username='mark1').first()
        self.assertEqual(user.followed.all(), [])
        self.assertEqual(user2.followed.all(), [])
        user.follow(user2)
        db.session.commit()
        self.assertTrue(user.is_following(user2))
        self.assertEqual(user.followed.count(), 1)
        self.assertEqual(user.followed.first().username, 'mark1')
        self.assertEqual(user2.followers.count(), 1)
        self.assertEqual(user2.followers.first().username, 'mark')

        user.unfollow(user2)
        db.session.commit()
        self.assertFalse(user.is_following(user2))
        self.assertEqual(user.followed.count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                  date=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                  date=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3,
                  date=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  date=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


class TestConfig(config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.blog = create_app(TestConfig)
        self.blog_context = self.blog.app_context()
        self.blog_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.blog_context.pop()

if __name__ == '__main__':
    unittest.main()