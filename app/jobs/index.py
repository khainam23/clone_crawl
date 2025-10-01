class RegisterJobs:
    jobs = []  # Management job want run
    
    def __init__(self):
        pass
    
    def register(self, job):
        self.jobs.append(job)
    
    def add_jobs(self, scheduler):
        """Add all registered jobs to scheduler"""
        for job_config in self.jobs:
            scheduler.add_job(**job_config)

# Global instance
job_registry = RegisterJobs()