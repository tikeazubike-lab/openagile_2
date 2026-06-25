import datetime
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import relationship
from app.database import Base


class DomainCode(Base):
    __tablename__ = "domain_codes"

    code = Column(String(4), primary_key=True)
    label = Column(Text, nullable=False)
    folder_slug = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    test_cases = relationship("TestCase", back_populates="domain")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(String(40), primary_key=True)
    domain_code = Column(String(4), ForeignKey("domain_codes.code"), nullable=False)
    workflow = Column(String(20), nullable=False)
    layer = Column(String(4), nullable=False)
    test_type = Column(String(4), nullable=False)
    sequence_no = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    requirement_ref = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("domain_code", "workflow", "layer", "test_type", "sequence_no"),
    )

    domain = relationship("DomainCode", back_populates="test_cases")
    runs = relationship("TestRun", back_populates="test_case", order_by="TestRun.run_number")


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(String(40), ForeignKey("test_cases.id"), nullable=False)
    run_number = Column(Integer, nullable=False)
    execution_path = Column(Text, nullable=False)
    expected_result = Column(Text, nullable=False)
    actual_result = Column(Text, nullable=False)
    status = Column(String(10), nullable=False)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("test_case_id", "run_number"),
        CheckConstraint("status IN ('Passed','Failed')", name="ck_run_status"),
    )

    test_case = relationship("TestCase", back_populates="runs")
    bug_report = relationship("BugReport", uselist=False, back_populates="test_run")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    markdown = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class BugReport(Base):
    __tablename__ = "bug_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False)
    markdown = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    test_run = relationship("TestRun", back_populates="bug_report")
