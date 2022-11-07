from sqladmin.authentication import AuthenticationBackend

from fastapi import Request


class MyBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        # TODO validate user
        # Validate username/password credentials
        # And update session
        request.session.update({"token": "..."})

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token
        return True


authentication_backend = MyBackend(secret_key="hello_world")
