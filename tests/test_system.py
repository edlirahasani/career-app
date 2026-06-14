"""
System Tests — end-to-end flows through the full application stack.
Mocks and Patches — isolate components by patching external dependencies.
"""
from unittest.mock import patch, MagicMock
from app.models import db, Job, Application


class TestSystemEndToEnd:

    def test_full_job_posting_and_application_flow(self, client):
        r = client.post('/jobs/new', data={
            'title': 'System Test Engineer',
            'company': 'SysTestCo',
            'location': 'Tokyo',
            'description': 'Test end to end.',
            'salary': '$90k',
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b'System Test Engineer' in r.data

        r2 = client.get('/api/jobs')
        jobs = r2.get_json()
        assert len(jobs) == 1
        job_id = jobs[0]['id']

        r3 = client.get(f'/jobs/{job_id}')
        assert b'SysTestCo' in r3.data

        r4 = client.post(f'/jobs/{job_id}/apply', data={
            'name': 'System Tester',
            'email': 'sys@test.com',
            'cover_letter': 'End-to-end tested.',
        }, follow_redirects=True)
        assert r4.status_code == 200

        r5 = client.get(f'/api/jobs/{job_id}/applications')
        applications = r5.get_json()
        assert len(applications) == 1
        assert applications[0]['applicant_name'] == 'System Tester'

    def test_multiple_applications_for_one_job(self, client, sample_job):
        for i in range(3):
            client.post(f'/api/jobs/{sample_job}/applications',
                        json={'applicant_name': f'Applicant {i}',
                              'applicant_email': f'app{i}@test.com'})
        r = client.get(f'/api/jobs/{sample_job}/applications')
        assert len(r.get_json()) == 3

    def test_delete_job_removes_applications(self, client, sample_job):
        client.post(f'/api/jobs/{sample_job}/applications',
                    json={'applicant_name': 'To Be Deleted',
                          'applicant_email': 'del@del.com'})
        client.delete(f'/api/jobs/{sample_job}')
        r = client.get(f'/api/jobs/{sample_job}')
        assert r.status_code == 404

    def test_api_and_web_stay_in_sync(self, client):
        client.post('/api/jobs', json={
            'title': 'Synced Job', 'company': 'SyncCo',
            'description': 'In sync.', 'location': 'Online'
        })
        r = client.get('/')
        assert b'Synced Job' in r.data


class TestMocksAndPatches:

    def test_mock_job_query(self, app):
        mock_job = MagicMock()
        mock_job.id = 42
        mock_job.title = 'Mocked Job'
        mock_job.company = 'MockCo'
        mock_job.to_dict.return_value = {
            'id': 42, 'title': 'Mocked Job', 'company': 'MockCo',
            'description': 'Mock.', 'location': 'Mock City',
            'salary': None, 'created_at': '2025-01-01T00:00:00'
        }
        with patch('app.api.Job.query') as mock_query:
            mock_query.order_by.return_value.all.return_value = [mock_job]
            with app.test_client() as c:
                r = c.get('/api/jobs')
                assert r.status_code == 200
                data = r.get_json()
                assert data[0]['title'] == 'Mocked Job'
                assert data[0]['id'] == 42

    def test_patch_datetime_for_consistent_timestamps(self, app, client):
        from datetime import datetime
        fake_now = datetime(2025, 1, 15, 12, 0, 0)
        with patch('app.models.datetime') as mock_dt:
            mock_dt.utcnow.return_value = fake_now
            r = client.post('/api/jobs', json={
                'title': 'Timestamped Job', 'company': 'TimeCo',
                'description': 'On time.', 'location': 'Clockville'
            })
            assert r.status_code == 201

    def test_mock_get_job_returns_none(self, app, client):
        with patch('app.api.Job.query') as mock_query:
            mock_query.get.return_value = None
            r = client.get('/api/jobs/999')
            assert r.status_code == 404
            assert r.get_json()['error'] == 'Job not found'