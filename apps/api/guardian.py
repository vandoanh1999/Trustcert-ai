from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import uuid

from .auth import get_current_user
from .blockchain import hash_data, anchor_log_to_blockchain
# Giả lập các module AI chuyên dụng
from .ai_models import image_analyzer, text_analyzer, risk_engine

router = APIRouter(
    prefix="/guardian",
    tags=["Guardian AI - Cognitive Immunity"],
)

# --- Models ---
class SafetyDirective(BaseModel):
    level: str # e.g., "SAFE", "WARNING", "CRITICAL_ALERT"
    priority_action: str # e.g., "ANSWER", "CORRECT_AND_ANSWER", "WARN_AND_ABORT"
    message_to_user: str
    evidence_summary: dict
    audit_log_id: str
    blockchain_tx_hash: Optional[str] = None

# --- CORE LOGIC ---
@router.post("/analyze", response_model=SafetyDirective)
async def analyze_interaction(
    user_text: str = Form(...),
    image_file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Đây là Endpoint đột phá của AI Giám Hộ.
    Nó không chỉ trả lời, nó BẢO VỆ.
    """
    audit_log = {
        "log_id": str(uuid.uuid4()),
        "user": current_user['username'],
        "timestamp": datetime.utcnow().isoformat(),
        "user_input_text": user_text,
        "has_image": image_file is not None,
        "steps": []
    }

    # === BƯỚC 1: XÁC THỰC TIỀN ĐỀ (PREMISE VERIFICATION) ===
    # Phân tích độc lập các nguồn dữ liệu
    text_premise = await text_analyzer.extract_premise(user_text)
    audit_log["steps"].append({"step": "text_analysis", "result": text_premise})
    
    image_evidence = None
    if image_file:
        image_content = await image_file.read()
        image_evidence = await image_analyzer.identify_objects(image_content)
        audit_log["steps"].append({"step": "image_analysis", "result": image_evidence})

    # === BƯỚC 2: PHÁT HIỆN MÂU THUẪN & ĐÁNH GIÁ RỦI RO ===
    # So sánh tiền đề người dùng với bằng chứng thực tế
    contradiction, risk_input = detect_contradiction(text_premise, image_evidence)
    audit_log["steps"].append({"step": "contradiction_detection", "result": contradiction})
    
    # Đưa vào cỗ máy phân tích rủi ro
    risk_assessment = await risk_engine.evaluate(risk_input)
    audit_log["steps"].append({"step": "risk_assessment", "result": risk_assessment})

    # === BƯỚC 3: PHẢN HỒI DỰA TRÊN MỨC ĐỘ NGUY HIỂM (RISK-BASED RESPONSE) ===
    # Quy tắc tối cao: AN TOÀN > HỮU ÍCH
    if risk_assessment["level"] == "CRITICAL":
        response_message = f"!!! CẢNH BÁO KHẨN CẤP !!! {risk_assessment['warning']}. HƯỚNG DẪN: {risk_assessment['guidance']}"
        priority_action = "WARN_AND_ABORT"
    elif risk_assessment["level"] == "WARNING":
        response_message = f"LƯU Ý: {risk_assessment['correction']}. {text_premise['benign_answer']}"
        priority_action = "CORRECT_AND_ANSWER"
    else: # SAFE
        response_message = text_premise['benign_answer']
        priority_action = "ANSWER"
        
    audit_log["final_decision"] = {
        "level": risk_assessment["level"], 
        "action": priority_action, 
        "message": response_message
    }

    # === BƯỚC 4: NIÊM PHONG BẰNG CHỨNG (IMMUTABLE AUDIT TRAIL) ===
    # Hash toàn bộ nhật ký phân tích và neo lên blockchain
    log_hash = hash_data(str(audit_log).encode('utf-8'))
    tx_hash = await anchor_log_to_blockchain(log_hash, audit_log["log_id"])
    audit_log["blockchain_tx_hash"] = tx_hash

    # Lưu log đầy đủ vào DB (quan trọng cho việc truy vết và cải tiến model)
    # save_log_to_db(audit_log)

    return SafetyDirective(
        level=risk_assessment["level"],
        priority_action=priority_action,
        message_to_user=response_message,
        evidence_summary={"text_premise": text_premise, "image_evidence": image_evidence},
        audit_log_id=audit_log["log_id"],
        blockchain_tx_hash=tx_hash
    )

# --- Các hàm logic phụ (giả lập) ---
def detect_contradiction(text, image):
    # Logic so sánh ở đây. Ví dụ:
    if image and "snake" in image["objects"] and "worm" in text["entities"]:
        contradiction_details = "User mentions 'worm', but image clearly shows a 'snake'."
        # Dữ liệu đầu vào cho cỗ máy rủi ro
        risk_input = {"object": "snake", "user_action": text["action"]}
        return contradiction_details, risk_input
    return "No significant contradiction.", {"object": text["entities"], "user_action": text["action"]}

