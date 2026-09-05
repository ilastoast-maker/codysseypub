"""파이프라인에서 공통으로 사용하는 오류 기록 유틸."""

LLM_PARSE_ERROR = "LLM_PARSE_ERROR"
LLM_REPORT_ERROR = "LLM_REPORT_ERROR"
AUTH_ERROR = "AUTH_ERROR"
NETWORK_ERROR = "NETWORK_ERROR"
HTTP_ERROR = "HTTP_ERROR"
QUOTA_ERROR = "QUOTA_ERROR"
REQUEST_ERROR = "REQUEST_ERROR"
RESPONSE_ERROR = "RESPONSE_ERROR"
EMPTY_RESULT = "EMPTY_RESULT"
CACHE_ERROR = "CACHE_ERROR"


def add_error(errors: list, step: str, err_type: str, message: str) -> None:
    errors.append({"step": step, "type": err_type, "message": str(message)})
