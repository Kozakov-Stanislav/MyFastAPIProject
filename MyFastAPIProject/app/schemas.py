from pydantic import BaseModel
from datetime import datetime  
from typing import List, Optional

class UserResponse(BaseModel):
    issuance_date: str
    is_closed: bool
    return_date: Optional[str]
    body: int
    percent: int
    payments_sum: int
    return_deadline: Optional[str]
    overdue_days: int
    payments_body_sum: int
    payments_interest_sum: int

class PlanResponse(BaseModel):
    month: str
    category: int
    plan_sum: int
    credits_sum: int
    payments_sum: int
    performance_percentage: float

class YearPerformanceResponse(BaseModel):
    month: int
    total_credits: int
    plan_sum: int
    payments_count: int

class PaymentCreate(BaseModel):
    user_id: int
    amount: float
    payment_date: datetime

    class Config:
        arbitrary_types_allowed = True 
    
