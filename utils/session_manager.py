from middleware.api_middleware import SessionApiMiddleware

user_data = {}
session_middleware = SessionApiMiddleware(user_data)
