from fastapi import status
from fastapi.responses import JSONResponse, Response  
from typing import Union

def reponse(*, code=200, data: Union[list, dict, str]= None, message="Success") -> Response:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'code': code,
            'message': message,
            'data': data,
        }
    )