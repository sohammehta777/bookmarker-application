from flask import Blueprint, jsonify, request
from typing import Dict, Any, Tuple
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.constants.http_status_codes import (HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK,HTTP_404_NOT_FOUND,HTTP_204_NO_CONTENT)
from src.database import Bookmark, db
from flasgger import swag_from
import validators

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")

@bookmarks.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_bookmarks() -> Any:
    current_user = get_jwt_identity()
    
    if request.method == 'POST':
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')
        
        if not validators.url(url):
            return jsonify({
                'error': 'Enter a valid url'
            }), HTTP_400_BAD_REQUEST
        
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error': 'URL already exists'
            }), HTTP_409_CONFLICT
        
        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()
        
        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'body': bookmark.body,  
            'created_at': bookmark.created_at.isoformat(),
            'updated_at': bookmark.updated_at.isoformat()
        }), HTTP_201_CREATED
    
    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 3, type=int)  # Changed to 3
        pagination = Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)
        
        bookmarks = pagination.items
        data = []
        
        for bookmark in bookmarks:
            data.append({
                'id': bookmark.id,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visits': bookmark.visits,
                'body': bookmark.body,  
                'created_at': bookmark.created_at.isoformat(),
                'updated_at': bookmark.updated_at.isoformat()
            })
            
        meta = {
            'page': pagination.page,
            'pages': pagination.pages,
            'total_count': pagination.total,
            'prev_page': pagination.prev_num,
            'next_page': pagination.next_num,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }
        return jsonify({'data': data, 'meta': meta}), HTTP_200_OK
    
    
@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id: int) -> Tuple[Dict[str, Any], int]:
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()
    
    if not bookmark:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND
    
    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,  
        'created_at': bookmark.created_at.isoformat(),
        'updated_at': bookmark.updated_at.isoformat()
    }), HTTP_200_OK

@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def editbookmark(id: int) -> Tuple[Dict[str, Any], int]:
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()
    
    if not bookmark:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND
    
    data = request.get_json()
    
    if 'url' in data:
        url = data['url']
        if not validators.url(url):
            return jsonify({'error': 'Enter a valid url'}), HTTP_400_BAD_REQUEST
        bookmark.url = url
    
    if 'body' in data:
        bookmark.body = data['body']
    
    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at.isoformat(),
        'updated_at': bookmark.updated_at.isoformat()
    }), HTTP_200_OK


@bookmarks.delete("/<int:id>")
@jwt_required()
def delete_bookmark(id: int):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()
    
    if not bookmark:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND
    
    db.session.delete(bookmark)
    db.session.commit()
    
    return jsonify({}), HTTP_204_NO_CONTENT


@bookmarks.get("/stats")
@swag_from("docs/bookmarks/stats.yaml")
def get_stats():
    current_user = get_jwt_identity()
    items = Bookmark.query.filter_by(user_id=current_user).all()
    
    for item in items:
        new_link = {
            'visits': item.visits,
            'url': item.url,
            'id': item.id,
            'short_url': item.short_url,
        }

        data.append(new_link)

    return jsonify({'data': data}), HTTP_200_OK



@bookmarks.get('/all')
def get_all() -> Dict[str, Any]:
    return {"bookmarks": []}