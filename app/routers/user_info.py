from fastapi import APIRouter, Depends, HTTPException, status
from app.database.database import update_user_details, update_user_password, delete_user_account, get_user, \
    verify_password
from app.pydantic_models.userModel import User, FullUpdateRequest
from app.routers.userAuthentication.security import get_current_user, create_access_token, create_refresh_token, \
    get_current_userID

user_info_router = APIRouter()

@user_info_router.get("/fullname_email")
async def read_user_fullname_email(current_user: User = Depends(get_current_user)):
    return {"fullname": current_user.fullname, "email": current_user.email, "password": current_user.hashed_password}

@user_info_router.post("/verify-password")
async def verify_current_password(password: str, current_user: User = Depends(get_current_user)):
    if not await verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    return {"message": "Current password is correct"}

@user_info_router.put("/update")
async def update_user_info(
        update_request: FullUpdateRequest,
        current_user: User = Depends(get_current_user)
):
    updated_fields = False

    if update_request.fullname:
        await update_user_details(
            email=current_user.email,
            fullname=update_request.fullname
        )
        updated_fields = True

    if update_request.new_password:
        if not update_request.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required to update password"
            )

        if not await verify_password(update_request.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        if update_request.new_password == update_request.confirm_password:
            await update_user_password(
                email=current_user.email,
                new_password=update_request.new_password
            )
            updated_fields = True
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )

    if not updated_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )
    return {
        "message": "User details updated successfully",
    }

@user_info_router.delete("/delete-account")
async def delete_account(current_user: User = Depends(get_current_user)):
    result = await delete_user_account(email=current_user.email)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )
    return {"message": "User account deleted successfully"}
