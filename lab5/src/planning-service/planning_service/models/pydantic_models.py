from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class PlanStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Input models (для создания)
class BudgetPlanCreate(BaseModel):
    title: str = Field(..., description="Title of the budget plan")
    description: Optional[str] = Field(None, description="Detailed description of the budget plan")
    planned_income: float = Field(..., description="Planned total income amount", ge=0)
    planned_expenses: float = Field(..., description="Planned total expenses amount", ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Monthly Budget",
                "description": "Personal monthly budget for 2024",
                "planned_income": 5000.0,
                "planned_expenses": 3500.0
            }
        }
    )


class BudgetPlanUpdate(BaseModel):
    title: Optional[str] = Field(None, description="New title for the budget plan")
    description: Optional[str] = Field(None, description="New description for the budget plan")
    planned_income: Optional[float] = Field(None, description="Updated planned income amount", ge=0)
    planned_expenses: Optional[float] = Field(None, description="Updated planned expenses amount", ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated Budget Plan",
                "planned_income": 6000.0,
                "planned_expenses": 4000.0
            }
        }
    )


class TransactionCreate(BaseModel):
    plan_id: int = Field(..., description="ID of the budget plan this transaction belongs to")
    type: TransactionType = Field(..., description="Type of transaction: income or expense")
    amount: float = Field(..., description="Transaction amount", gt=0)
    description: Optional[str] = Field(None, description="Description of the transaction")
    category: Optional[str] = Field(None, description="Category of the transaction")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "plan_id": 1,
                "type": "expense",
                "amount": 150.0,
                "description": "Grocery shopping",
                "category": "Food"
            }
        }
    )


# Response models
class BudgetPlan(BaseModel):
    id: int = Field(..., description="Unique identifier of the budget plan")
    title: str = Field(..., description="Title of the budget plan")
    description: Optional[str] = Field(None, description="Description of the budget plan")
    planned_income: float = Field(..., description="Planned total income amount")
    planned_expenses: float = Field(..., description="Planned total expenses amount")
    status: PlanStatus = Field(PlanStatus.ACTIVE, description="Status of the budget plan")
    created_at: datetime = Field(..., description="When the plan was created")
    owner: str = Field(..., description="Username of the plan owner")

    model_config = ConfigDict(from_attributes=True)


class Transaction(BaseModel):
    id: int = Field(..., description="Unique identifier of the transaction")
    plan_id: int = Field(..., description="ID of the budget plan this transaction belongs to")
    type: TransactionType = Field(..., description="Type of transaction")
    amount: float = Field(..., description="Transaction amount")
    description: Optional[str] = Field(None, description="Description of the transaction")
    category: Optional[str] = Field(None, description="Category of the transaction")
    created_at: datetime = Field(..., description="When the transaction was created")
    owner: str = Field(..., description="Username of the transaction owner")

    model_config = ConfigDict(from_attributes=True)


class PlanAnalytics(BaseModel):
    plan_id: int = Field(..., description="ID of the budget plan")
    planned_income: float = Field(..., description="Originally planned income")
    planned_expenses: float = Field(..., description="Originally planned expenses")
    actual_income: float = Field(..., description="Actual income recorded")
    actual_expenses: float = Field(..., description="Actual expenses recorded")
    income_variance: float = Field(..., description="Difference between planned and actual income")
    expense_variance: float = Field(..., description="Difference between planned and actual expenses")
    balance: float = Field(..., description="Current balance (actual income - actual expenses)")
    planned_balance: float = Field(..., description="Originally planned balance")


class BudgetPlanResponse(BaseModel):
    id: int = Field(..., description="Unique identifier of the budget plan")
    title: str = Field(..., description="Title of the budget plan")
    description: Optional[str] = Field(None, description="Description of the budget plan")
    planned_income: float = Field(..., description="Planned total income amount")
    planned_expenses: float = Field(..., description="Planned total expenses amount")
    user_id: str = Field(..., description="Username of the plan owner")
    created_at: Optional[datetime] = Field(None, description="When the plan was created")
    updated_at: Optional[datetime] = Field(None, description="When the plan was last updated")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Monthly Budget",
                "description": "Personal monthly budget for 2024",
                "planned_income": 5000.0,
                "planned_expenses": 3500.0,
                "user_id": "admin",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )


class TransactionResponse(BaseModel):
    id: int = Field(..., description="Unique identifier of the transaction")
    plan_id: int = Field(..., description="ID of the budget plan this transaction belongs to")
    type: TransactionType = Field(..., description="Type of transaction")
    amount: float = Field(..., description="Transaction amount")
    description: Optional[str] = Field(None, description="Description of the transaction")
    category: Optional[str] = Field(None, description="Category of the transaction")
    user_id: str = Field(..., description="Username of the transaction owner")
    created_at: Optional[datetime] = Field(None, description="When the transaction was created")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "plan_id": 1,
                "type": "expense",
                "amount": 150.0,
                "description": "Grocery shopping",
                "category": "Food",
                "user_id": "admin",
                "created_at": "2024-01-15T14:30:00"
            }
        }
    )


class AnalyticsResponse(BaseModel):
    plan_id: int = Field(..., description="ID of the budget plan")
    total_income: float = Field(..., description="Total income recorded for this plan")
    total_expenses: float = Field(..., description="Total expenses recorded for this plan")
    balance: float = Field(..., description="Current balance (total income - total expenses)")
    planned_income: float = Field(..., description="Originally planned income")
    planned_expenses: float = Field(..., description="Originally planned expenses")
    income_vs_planned: float = Field(..., description="Income variance as percentage")
    expenses_vs_planned: float = Field(..., description="Expenses variance as percentage")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "plan_id": 1,
                "total_income": 4800.0,
                "total_expenses": 3200.0,
                "balance": 1600.0,
                "planned_income": 5000.0,
                "planned_expenses": 3500.0,
                "income_vs_planned": -4.0,
                "expenses_vs_planned": -8.57
            }
        }
    ) 