from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class BudgetPlanDB(Base):
    __tablename__ = "budget_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    planned_income = Column(Float, nullable=False)
    planned_expenses = Column(Float, nullable=False)
    user_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transactions = relationship("TransactionDB", back_populates="plan")


class TransactionDB(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("budget_plans.id"), nullable=False)
    type = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(500))
    category = Column(String(100))
    user_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    plan = relationship("BudgetPlanDB", back_populates="transactions") 