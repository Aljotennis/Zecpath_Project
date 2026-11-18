
from rest_framework.response import Response


def success_response(
    data=None,
    message="Request successful.",
    status_code=200
):
    return Response(
        {
            "success": True,
            "status_code": status_code,
            "message": message,
            "data": data
        },
        status=status_code
    )
