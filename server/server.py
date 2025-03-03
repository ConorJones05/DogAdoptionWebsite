import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid

load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_dogs(name, image, breed, price):
    dog_id = str(uuid.uuid4())
    response = supabase.table("dogs").insert({
        "id": dog_id,
        "name": name,
        "image": image,
        "breed": breed,
        "price": price
    }).execute()
    return response.data

app = Flask(__name__)

@app.route('/dogs', methods=['GET'])
def get_dogs():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = 20 
        offset = (page - 1) * page_size 

        response = (supabase.table("dogs")
            .select("*")
            .order("id")
            .range(offset, offset + page_size - 1)
            .execute())

        dogs = response.data

        return jsonify({"page": page, "dogs": dogs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/admin', methods=['POST', 'DELETE', 'PUT'])
def admin_dogs():
    try:
        if request.method == 'DELETE':
            dog_id = request.json.get('id') if request.is_json else request.args.get('id')
            if not dog_id:
                return jsonify({"error": "Missing dog id"}), 400
                
            response = (supabase.table("dogs")
                .delete()
                .eq("id", dog_id)
                .execute())
            return jsonify({"message": "Dog deleted", "data": response.data}), 200
            
        elif request.method == 'POST':
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400
                
            data = request.json
            name = data.get('name')
            image = data.get('image')
            breed = data.get('breed')
            price = data.get('price')
            
            if not all([name, image, breed, price]):
                return jsonify({"error": "Missing required fields"}), 400
                
            result = add_dogs(name, image, breed, price)
            return jsonify({"message": "Dog added successfully"}), 200
        
        elif request.method == 'PUT':
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400
            
            dog_id = request.json.get('id')
            if not dog_id:
                return jsonify({"error": "Missing dog id"}), 400
            
            update_data = {k: v for k, v in request.json.items() 
                  if k in ['name', 'image', 'breed', 'price']}
                  
            if not update_data:
                return jsonify({"error": "No valid fields to update"}), 400
            
            response = (supabase.table("dogs")
            .update(update_data)
            .eq("id", dog_id)
            .execute())
            return jsonify({"message": "Dog updated", "data": response.data}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
