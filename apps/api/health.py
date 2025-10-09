from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# Giả sử mày có một module quản lý database và blockchain
from .dependencies import get_db
from .blockchain import get_blockchain_node_status

router = APIRouter(
    prefix="/health",
    tags=["Health Check"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", status_code=status.HTTP_200_OK)
async def check_system_health(db: Session = Depends(get_db)):
    """
    Kiểm tra toàn diện sức khỏe của hệ thống:
    - Trạng thái API Server.
    - Kết nối tới Database.
    - Kết nối tới Blockchain Node.
    """
    try:
        # 1. Kiểm tra kết nối DB
        db.execute('SELECT 1')
        db_status = "OK"
    except Exception as e:
        db_status = f"ERROR: {e}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"api_status": "OK", "database_status": db_status}
        )

    # 2. Kiểm tra kết nối Blockchain Node
    is_node_connected, node_message = await get_blockchain_node_status()
    if not is_node_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "api_status": "OK",
                "database_status": db_status,
                "blockchain_node_status": f"ERROR: {node_message}"
            }
        )
    
    blockchain_status = f"OK - {node_message}"

    return {
        "api_status": "OK",
        "database_status": db_status,
        "blockchain_node_status": blockchain_status
    }