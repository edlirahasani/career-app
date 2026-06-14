"""
REST API Tests — test all /api/* endpoints for correctness and error handling.
"""


class TestJobsAPI:
    def test_get_jobs_empty(self, client):
        """GET /api/jobs returns empty list when no jobs."""
        r = client.get('/api/jobs')
        assert r.status_code == 200
        assert r.get_json() == []

    def test_create_job(self, client):
        """POST /api/jobs creates a job and returns 201."""
        payload = {'title': 'Backend Dev', 'company': 'Acme',
                   'description': 'Code.', 'location': 'NYC'}
        r = client.post('/api/jobs', json=payload)
        assert r.status_code == 201
        data = r.get_json()
        assert data['title'] == 'Backend Dev'
        assert 'id' in data

    def test_create_job_missing_field(self, client):
        """POST /api/jobs with missing required field returns 400."""
        r = client.post('/api/jobs', json={'title': 'Only Title'})
        assert r.status_code == 400
        assert 'error' in r.get_json()

    def test_create_job_no_body(self, client):
        """POST /api/jobs with no body returns 400."""
        r = client.post('/api/jobs', data='',
                        content_type='application/json')
        assert r.status_code == 400

    def test_get_job_by_id(self, client, sample_job):
        """GET /api/jobs/<id> returns the correct job."""
        r = client.get(f'/api/jobs/{sample_job}')
        assert r.status_code == 200
        data = r.get_json()
        assert data['title'] == 'Software Engineer'

    def test_get_job_not_found(self, client):
        """GET /api/jobs/9999 returns 404."""
        r = client.get('/api/jobs/9999')
        assert r.status_code == 404
        assert 'error' in r.get_json()

    def test_update_job(self, client, sample_job):
        """PUT /api/jobs/<id> updates job fields."""
        r = client.put(f'/api/jobs/{sample_job}',
                       json={'salary': '$100k', 'location': 'Berlin'})
        assert r.status_code == 200
        data = r.get_json()
        assert data['salary'] == '$100k'
        assert data['location'] == 'Berlin'

    def test_update_job_not_found(self, client):
        """PUT /api/jobs/9999 returns 404."""
        r = client.put('/api/jobs/9999', json={'title': 'X'})
        assert r.status_code == 404

    def test_delete_job(self, client,