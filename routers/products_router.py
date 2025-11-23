from fastapi import APIRouter, Depends

from auth_utils import get_current_user, check_access_rights

products_router = APIRouter()


@products_router.get("", response_model=list[dict])
def get_all_products(
    user=Depends(get_current_user),
    _=Depends(check_access_rights),
):
    products = [
        {"id": 1, "name": "", "description": "", "price": 100},
        {"id": 2, "name": "", "description": "", "price": 200},
        {"id": 3, "name": "", "description": "", "price": 300}
    ]
    return products


@products_router.get("/my", response_model=list[dict])
def get_my_products(
    user=Depends(get_current_user),
    _=Depends(check_access_rights),
):
    products = [
        {"id": 1, "name": "", "description": "", "price": 100},
    ]
    return products


@products_router.post("/my", response_model=dict)
def create_my_product(
    user=Depends(get_current_user),
    _=Depends(check_access_rights),
):
    product = {"id": 4, "name": "", "description": "", "price": 400}
    return product


@products_router.patch("/my/{id}")
def update_my_product(
    id: int,
    user = Depends(get_current_user),
    _ = Depends(check_access_rights),
):
    product = {"id": id, "name": "", "description": "", "price": 400}
    return product


@products_router.delete("/my/{id}")
def delete_my_product(
    id: int,
    user=Depends(get_current_user),
    _=Depends(check_access_rights),
):
    return None
