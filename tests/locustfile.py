from locust import HttpUser, task, between


class FastFlixUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def get_movies(self):
        self.client.get("/api/v1/movies/?page=1&size=10")
