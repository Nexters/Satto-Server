from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class DBMiddleware(BaseHTTPMiddleware):
    """
    API 요청(Request 객체 생성) 시 DB 세션 주입
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        async with request.app.state.mysql.session() as session:
            try:
                request.state.db_session = session
                response = await call_next(request)
                await session.commit()
                return response
            except Exception as e:
                await session.rollback()
                raise e
