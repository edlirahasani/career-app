from flask import Blueprint, jsonify, request
from .models import db, Job, Application

api = Blueprint('api', __name__)

# --- Jobs ---

@api.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return jsonify([j.to_dict() for j in jobs]), 200

@api.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job.to_dict()), 200

@api.route('/jobs', methods=['POST'])
def create_job():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['title', 'company', 'description', 'location']
    missing = [f for f in required if not data.get(f, '').strip()]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    job = Job(
        title=data['title'].strip(),
        company=data['company'].strip(),
        description=data['description'].strip(),
        location=data['location'].strip(),
        salary=data.get('salary', None),
    )
    db.session.add(job)
    db.session.commit()
    return jsonify(job.to_dict()), 201

@api.route('/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    for field in ['title', 'company', 'description', 'location', 'salary']:
        if field in data:
            setattr(job, field, data[field])
    db.session.commit()
    return jsonify(job.to_dict()), 200

@api.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': 'Job deleted'}), 200

# --- Applications ---

@api.route('/jobs/<int:job_id>/applications', methods=['GET'])
def get_applications(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify([a.to_dict() for a in job.applications]), 200

@api.route('/jobs/<int:job_id>/applications', methods=['POST'])
def create_application(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['applicant_name', 'applicant_email']
    missing = [f for f in required if not data.get(f, '').strip()]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    app_obj = Application(
        job_id=job_id,
        applicant_name=data['applicant_name'].strip(),
        applicant_email=data['applicant_email'].strip(),
        cover_letter=data.get('cover_letter', None),
    )
    db.session.add(app_obj)
    db.session.commit()
    return jsonify(app_obj.to_dict()), 201

@api.route('/applications/<int:app_id>', methods=['DELETE'])
def delete_application(app_id):
    app_obj = Application.query.get(app_id)
    if not app_obj:
        return jsonify({'error': 'Application not found'}), 404
    db.session.delete(app_obj)
    db.session.commit()
    return jsonify({'message': 'Application deleted'}), 200