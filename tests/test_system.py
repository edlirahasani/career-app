"""
System Tests — end-to-end flows through the full application stack.
Mocks & Patches — isolate components by patching external dependencies.
"""
from unittest.mock import patch, MagicMock
from app.models import db, Job, Application


class TestSystemEndToEnd:
    """Full user journey tests."""

    def test_full_job_posting_and_application_flow(self, client):
        """User posts a job, views it, and applies — full journey."""
        # 1. Post a job via web form
        r = client.post('/jobs/new', data={
            'title': 'System Test Engineer',
            'company': 'SysTestCo',
            'location': 'Tokyo',
            'description': 'Test end to end.',
            'salary': '$90k',
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b'System Test Engineer' in r.data

        # 2. Find the job via API
        r2 = client.get('/api/jobs')
        jobs = r2.get_json()
        assert len(jobs) == 1
        job_id = jobs[0]['id']

        # 3. View job detail page
        r3 = client.get(f'/jobs/{job_id}')
        assert b'SysTestCo' in r3.data

        # 4. Apply for the job
        r4 = client.post(f'/jobs/{job_id}/apply', data={
            'name': 'System Tester',
            'email': 'sys@test.com',
            'cover_letter': 'End-to-end tested.',
        }, follow_redirects=True)
        assert r4.status_code == 200

        # 5. Verify application via API
        r5 = client.get(f'/api/jobs/{job_id}/applications')
        applications = r5.get_json()
        assert len(applications) == 1
        assert applications[0]['applicant_name'] == 'System Tester'

    def test_multiple_applications_for_one_job(self, client, sample_job):
        """Multiple people can apply for the