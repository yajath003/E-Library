# External Modules
from flask import Blueprint, render_template, redirect, session, request, url_for, flash, abort
from flask_restful import Resource, Api
from flask_restful import fields, marshal_with, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
from datetime import datetime

# Internal Modules
from application import db
from user.models import user_login, requests
from section.models import sections
from librarian.models import lib_login, accept
from book.models import books
from api.decorators import auth_required
from api.validation import BusinessValidationError, NotFoundError
from blog.views import _save_tags

api_app = Blueprint('api_app', __name__)


# Used the following parser to create new registration as part of POST
create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('user_full_name', help="The name is required.", required=True)
create_user_parser.add_argument('user_email', help="The email is required.", required=True)
create_user_parser.add_argument('user_password', help="The password is required.", required=True)

# Used the following parser to update author as part of PUT
update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument('user_aboutme')

# Used the following parser to create new post as part of POST
create_post_parser = reqparse.RequestParser()
create_post_parser.add_argument('post_title', help="Post Title is required.", required=True)
create_post_parser.add_argument('post_body', help="Post body is required.", required=True)
create_post_parser.add_argument('post_category', type=int, help="Post category is required.", required=True)
create_post_parser.add_argument('post_author', type=int, help="Post author is required.", required=True)
create_post_parser.add_argument('post_tags')

# Used the following parser to update post as part of PUT
update_post_parser = reqparse.RequestParser()
update_post_parser.add_argument('post_title')
update_post_parser.add_argument('post_body')
update_post_parser.add_argument('post_category')
update_post_parser.add_argument('post_tags')

# Used the following parser to create new comment as part of POST
create_comment_parser = reqparse.RequestParser()
create_comment_parser.add_argument('comment_text', help="Comment text is required.", required=True)
create_comment_parser.add_argument('comment_author', help="Author is required.", required=True)
create_comment_parser.add_argument('comment_postid', help="Post id is required.", required=True)

# Used the following parser to update comment as part of PUT
update_comment_parser = reqparse.RequestParser()
update_comment_parser.add_argument('comment_text')

user_resource_fields = {
    'id':   fields.Integer,
    'full_name' : fields.String,
    'email':    fields.String,
    'aboutme': fields.String
}

post_resource_fields = {
    'id':   fields.Integer,
    'user_id': fields.Integer,
    'category_id': fields.Integer,
    'title': fields.String, 
    'body':  fields.String
}

comment_resource_fields = {
    'id':   fields.Integer,
    'name': fields.String,
    'text': fields.String,
}

class UserAPI(Resource):
    @marshal_with(user_resource_fields)
    @auth_required
    def get(self):
        users = user_login.query.all()
        if users != None:
            return users, 200
        else:
            raise NotFoundError(status_code=404)

    @marshal_with(user_resource_fields)
    @auth_required
    def put(self, email=None):
        print(email)
        args = update_user_parser.parse_args()
        user_aboutme = args.get("user_aboutme", "Blog Member updated")        
        if email is None:
            raise BusinessValidationError(status_code=400, error_code="AUTHOR04", error_message="email is required input")

        author = user_login.query.filter(user_login.email == email).first()
        print(author)
        if author is None:
            raise BusinessValidationError(status_code=400, error_code="AUTHOR03", error_message="Author not found")            

        user_login.aboutme=user_aboutme
        db.session.commit()
        return author, 200                

    @marshal_with(user_resource_fields)
    @auth_required
    def post(self):
        args = create_user_parser.parse_args()
        user_full_name = args.get("user_full_name", None)
        user_email = args.get("user_email", None)
        user_password = generate_password_hash(args.get("user_password", None)) 
        if user_full_name is None or user_email is None or user_password is None:
            raise BusinessValidationError(status_code=400, error_code="AUTHOR01", error_message="Name, email and password are required inputs")
        
        author = user_login.query.filter(user_login.email == user_email).first()
        if author:
            raise BusinessValidationError(status_code=409, error_code="AUTHOR02", error_message="email is already exists")            
 
        new_author = Author(
            full_name=user_full_name,
            email=user_email,
            password=user_password, 
            avatar='7a00d33a-cd87-4bc1-921a-98171e4a84c1',
            aboutme='Blog Member'
        )        
        db.session.add(new_author)
        db.session.commit()
        return new_author, 201
    
    @auth_required
    def delete(self, email):
        if email is None:
            raise BusinessValidationError(status_code=400, error_code="AUTHOR04", error_message="email is required input")
        
        # check if author exists
        author = db.session.query(Author).filter(user_login.email == email).first()
        if author is None:
            raise BusinessValidationError(status_code=400, error_code="AUTHOR03", error_message="Author not found") 

        posts = Post.query.filter(author == user_login.full_name).all()

        for post in posts:
            db.session.delete(post)
        db.session.commit()

        db.session.delete(author)
        db.session.commit()
        return "Author removed successfully", 200

class PostAPI(Resource):
    @marshal_with(post_resource_fields)
    @auth_required
    def get(self, user_id):
        posts = db.session.query(Post).filter_by(user_id=user_id, live=True).order_by(Post.publish_date.desc()).all()      
        if posts != None:
            return posts, 200
        else:
            raise NotFoundError(status_code=404)

    @marshal_with(post_resource_fields)
    @auth_required
    def put(self, post_id=None):
        args = update_post_parser.parse_args()
        post_title = args.get("post_title", None)
        post_body = args.get("post_body", None)
        post_category = args.get("post_category", None)
        post_tags = args.get("post_tags", None)       
        if post_id is None:
            raise BusinessValidationError(status_code=400, error_code="POST02", error_message="Post id is required input")

        post = Post.query.filter(Post.id == post_id).first()
        if post is None:
            raise BusinessValidationError(status_code=400, error_code="POST03", error_message="Post not found")            
        
        category = Category.query.filter_by(id=post_category).first_or_404()

        if post_title is not None:
            post.title = post_title
        if post_body is not None:
            post.body = post_body
        if category is not None:
            post.category = category
        if post_tags is not None:
            _save_tags(post, post_tags)

        db.session.add(post)
        db.session.commit()

        # do the slug
        slug = slugify(str(post.id) + '-' + post.title)
        post.slug = slug
        db.session.commit()
        return post, 201               

    @marshal_with(post_resource_fields)
    @auth_required
    def post(self):
        args = create_post_parser.parse_args()
        post_title = args.get("post_title", None)
        post_body = args.get("post_body", None)
        post_category = args.get("post_category", None)
        post_author = args.get("post_author", None)
        post_tags = args.get("post_tags", None)
        if post_title is None or post_body is None or post_category is None or post_author is None:
            raise BusinessValidationError(status_code=400, error_code="POST01", error_message="Title, Body, Category and Author are required inputs")
        
        author = db.session.query(Author).filter_by(id=post_author).first()
        print(author)
        if author is None:
            raise BusinessValidationError(status_code=409, error_code="AUTHOR03", error_message="Author not found")            
        
        category = Category.query.filter_by(id=post_category).first_or_404()
        
        post = Post(
            author=author,
            title=post_title,
            body=post_body,
            category=category
        )

        # process tags
        if post_tags is not None:
            _save_tags(post, post_tags)
        
        db.session.add(post)
        db.session.commit()

        # do the slug
        slug = slugify(str(post.id) + '-' + post.title)
        post.slug = slug
        db.session.commit()
        return post, 201                
    @auth_required
    def delete(self, post_id=None):
        if post_id is None:
            raise BusinessValidationError(status_code=400, error_code="POST02", error_message="Post id is required input")
       
        # check if post exists
        post = Post.query.filter(Post.id == post_id).first()
        print(post)
        if post is None:
            raise BusinessValidationError(status_code=400, error_code="POST03", error_message="Post not found")            

        post.live = False
        db.session.commit()
        return "Post deleted successfully", 200
    
class CommentAPI(Resource):
    @marshal_with(comment_resource_fields)
    @auth_required
    def get(self, postid=None):
        posts = db.session.query(Post).filter_by(id=post_id, live=True).order_by(Post.publish_date.desc()).all()      
        if posts != None:
            return posts, 200
        else:
            raise NotFoundError(status_code=404)

    @marshal_with(comment_resource_fields)
    @auth_required
    def put(self, id=None):
        args = update_comment_parser.parse_args()
        comment_text = args.get("comment_text", None)   
        if id is None:
            raise BusinessValidationError(status_code=400, error_code="COMMENT01", error_message="Comment id is required input")
        
        comment = Comment.query.filter(Comment.id == id).first()
        if comment is None:
            raise BusinessValidationError(status_code=400, error_code="COMMENT02", error_message="Comment not found")            
        
        comment.text = comment_text
        comment.date= datetime.now()

        db.session.commit()
        return comment, 201               

    @marshal_with(comment_resource_fields)
    @auth_required
    def post(self):
        args = create_comment_parser.parse_args()
        comment_text = args.get("comment_text", None)
        comment_author = args.get("comment_author", None)
        comment_postid = args.get("comment_postid", None) 
        if comment_text is None or comment_author is None or comment_postid is None:
            raise BusinessValidationError(status_code=400, error_code="COMMENT01", error_message="Comment and Author are required inputs")
        post = Post.query.filter(Post.id == comment_postid).first()
        if post is None:
            raise BusinessValidationError(status_code=400, error_code="POST03", error_message="Post not found")            

        author = db.session.query(Author).filter_by(full_name=comment_author).first()
        if author is None:
            raise BusinessValidationError(status_code=409, error_code="AUTHOR03", error_message="Author not found")            

        # do the slug
        slug = slugify(str(post.id) + '-' + post.title)
        
        comment = Comment(name = user_login.full_name,
                              text = comment_text,
                              post_id = slug,
                              date= datetime.now()
                              )

        db.session.add(comment)
        db.session.commit()
        return comment, 201                
