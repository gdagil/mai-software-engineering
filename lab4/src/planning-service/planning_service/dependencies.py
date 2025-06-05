from fastapi import Header, HTTPException


async def get_current_user(x_user: str = Header(..., alias="X-User")) -> str:
    if not x_user or x_user.strip() == "":
        raise HTTPException(status_code=422, detail="X-User header cannot be empty")
    return x_user 