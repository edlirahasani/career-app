from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, Job, Application

main = Blueprint('main', __name__)

@main.route('/')
def index():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('index.html', jobs=jobs)

@main.route('/jobs/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)

@main.route('/jobs/new', methods=['GET', 'POST'])
def new_job():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        salary = request.form.get('salary', '').strip()

        if not title or not company or not description or not location:
            flash('Please fill in all required fields.', 'error')
            return render_template('new_job.html')

        job = Job(title=title, company=company, description=description,
                  location=location, salary=salary or None)
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('new_job.html')

@main.route('/jobs/<int:job_id>/apply', methods=['GET', 'POST'])
def apply(job_id):
    job = Job.query.get_or_404(job_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        cover_letter = request.form.get('cover_letter', '').strip()

        if not name or not email:
            flash('Name and email are required.', 'error')
            return render_template('apply.html', job=job)

        application = Application(job_id=job_id, applicant_name=name,
                                  applicant_email=email, cover_letter=cover_letter or None)
        db.session.add(application)
        db.session.commit()
        flash('Application submitted!', 'success')
        return redirect(url_for('main.index'))

    return render_template('apply.html', job=job)

@main.route('/jobs/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted.', 'success')
    return redirect(url_for('main.index'))