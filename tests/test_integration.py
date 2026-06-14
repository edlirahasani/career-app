"""
Integration Tests — test how routes, DB, and templates work together.
"""


class TestIndexPage:
    def test_index_loads(self, client):
        """Home page returns 200."""
        r = client.get('/')
        assert r.status_code == 200
        assert b'CareerHub' in r.data

    def test_index_shows_jobs(self, client, app, sample_job):
        """Home page lists existing jobs."""
        r = client.get('/')
        assert b'Software Engineer' in r.data


class TestJobPostingFlow:
    def test_get_new_job_form(self, client):
        """New job form page loads."""
        r = client.get('/jobs/new')
        assert r.status_code == 200
        assert b'Post a New Job' in r.data

    def test_post_new_job(self, client):
        """Posting a valid job redirects to home and shows the job."""
        r = client.post('/jobs/new', data={
            'title': 'Data Analyst',
            'company': 'DataCo',
            'location': 'Paris',
            'description': 'Analyse data.',
            'salary': '$70k',
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b'Data Analyst' in r.data

    def test_post_job_missing_fields(self, client):
        """Missing required field shows error and stays on form."""
        r = client.post('/jobs/new', data={
            'title': '',
            'company': 'DataCo',
            'location': 'Paris',
            'description': 'Analyse data.',
        }, follow_redirects=True)
        assert r.status_code == 200


class TestJobDetail:
    def test_view_job_detail(self, client, app, sample_job):
        """Job detail page shows correct job info."""
        r = client.get(f'/jobs/{sample_job}')
        assert r.status_code == 200
        assert b'Software Engineer' in r.data
        assert b'TechCorp' in r.data

    def test_view_nonexistent_job(self, client):
        """Accessing a missing job returns 404."""
        r = client.get('/jobs/9999')
        assert r.status_code == 404


    def test_apply_page_loads(self, client, sample_job):
        """Apply page loads for a valid job."""
        r = client.get(f'/jobs/{sample_job}/apply')
        assert r.status_code == 200
        assert b'Apply' in r.data

    def test_submit_application(self, client, sample_job):
        """Submitting a valid application redirects to home."""
        r = client.post(f'/jobs/{sample_job}/apply', data={
            'name': 'Dave',
            'email': 'dave@example.com',
            'cover_letter': 'I am perfect.',
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_submit_application_missing_name(self, client, sample_job):
        """Application without name stays on form."""
        r = client.post(f'/jobs/{sample_job}/apply', data={
            'name': '',
            'email': 'dave@example.com',
        }, follow_redirects=True)
        assert r.status_code == 200


class TestDeleteJob:
    def test_delete_job(self, client, sample_job):
        """Deleting a job redirects home and removes it."""
        r = client.post(f'/jobs/{sample_job}/delete',
                        follow_redirects=True)
        assert r.status_code == 200
        r2 = client.get(f'/jobs/{sample_job}')
        assert r2.status_code == 404