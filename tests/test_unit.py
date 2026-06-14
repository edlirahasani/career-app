"""
Unit Tests — test individual model methods in isolation.
"""
import pytest
from app.models import Job, Application, db


class TestJobModel:
    def test_job_creation(self, app):
        """Job is created with correct attributes."""
        with app.app_context():
            job = Job(title='Dev', company='Corp', description='Work hard.',
                      location='NYC', salary='$60k')
            db.session.add(job)
            db.session.commit()
            fetched = Job.query.get(job.id)
            assert fetched.title == 'Dev'
            assert fetched.company == 'Corp'
            assert fetched.location == 'NYC'
            assert fetched.salary == '$60k'

    def test_job_to_dict(self, app):
        """to_dict() returns all expected keys."""
        with app.app_context():
            job = Job(title='QA Engineer', company='TestCo',
                      description='Test stuff.', location='Berlin')
            db.session.add(job)
            db.session.commit()
            d = job.to_dict()
            assert 'id' in d
            assert d['title'] == 'QA Engineer'
            assert d['company'] == 'TestCo'
            assert 'created_at' in d

    def test_job_salary_optional(self, app):
        """Job salary can be None."""
        with app.app_context():
            job = Job(title='Intern', company='StartUp',
                      description='Learn.', location='London')
            db.session.add(job)
            db.session.commit()
            assert job.salary is None

    def test_job_requires_title(self, app):
        """Job without title raises an error."""
        with app.app_context():
            job = Job(title=None, company='X', description='Y', location='Z')
            db.session.add(job)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()


class TestApplicationModel:
    def test_application_creation(self, app, sample_job):
        """Application links to a job and stores applicant info."""
        with app.app_context():
            app_obj = Application(job_id=sample_job, applicant_name='Alice',
                                  applicant_email='alice@example.com',
                                  cover_letter='Hire me!')
            db.session.add(app_obj)
            db.session.commit()
            fetched = Application.query.get(app_obj.id)
            assert fetched.applicant_name == 'Alice'
            assert fetched.job_id == sample_job

    def test_application_to_dict(self, app, sample_job):
        """to_dict() returns all expected fields."""
        with app.app_context():
            app_obj = Application(job_id=sample_job, applicant_name='Bob',
                                  applicant_email='bob@example.com')
            db.session.add(app_obj)
            db.session.commit()
            d = app_obj.to_dict()
            assert d['applicant_name'] == 'Bob'
            assert d['job_id'] == sample_job
            assert 'applied_at' in d

    def test_cascade_delete(self, app, sample_job):
        """Deleting a job also deletes its applications."""
        with app.app_context():
            app_obj = Application(job_id=sample_job, applicant_name='Carol',
                                  applicant_email='carol@example.com')
            db.session.add(app_obj)
            db.session.commit()
            app_id = app_obj.id

            job = Job.query.get(sample_job)
            db.session.delete(job)
            db.session.commit()
            assert Application.query.get(app_id) is None