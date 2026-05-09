"""
API routes for Solgri application
"""

from flask import Blueprint, jsonify, request

# Create a blueprint for api routes
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/data', methods=['GET'])
def get_data():
    """Fetch data from backend"""
    sample_data = {
        'items': [
            {'id': 1, 'name': 'Item 1', 'description': 'First item'},
            {'id': 2, 'name': 'Item 2', 'description': 'Second item'},
        ]
    }
    return jsonify(sample_data)

@api.route('/data', methods=['POST'])
def create_data():
    """Create new data in backend"""
    data = request.get_json()
    
    # Basic validation
    if not data or 'name' not in data:
        return jsonify({'error': 'Missing required field: name'}), 400
    
    # Return created data
    return jsonify({
        'message': 'Data created successfully',
        'data': data
    }), 201
