"""
Configuration Module for Pricing & Decision Feature
รองรับ REQ-DAT-001, REQ-FN-001, REQ-FN-006, REQ-BR-002, D-01, D-02, D-03, D-04
"""

import os
from pydantic import BaseModel, Field


class Settings(BaseModel):
    # D-01, AC-S04-03: เกณฑ์มูลค่าประเมินขั้นต่ำ 500 บาท (ใช้ min_price ตัดสิน)
    THRESHOLD_MIN_ESTIMATED_BAHT: float = Field(
        default=float(os.getenv("THRESHOLD_MIN_ESTIMATED_BAHT", "500.0")),
        description="เกณฑ์มูลค่าประเมินขั้นต่ำสำหรับส่งคำขอนัดหมายเดี่ยว (บาท)"
    )

    # D-01, AC-S04-03: จำนวนกระสอบขั้นต่ำสำหรับขวดแก้ว/พลาสติก
    THRESHOLD_MIN_BAGS: int = Field(
        default=int(os.getenv("THRESHOLD_MIN_BAGS", "2")),
        description="จำนวนกระสอบขั้นต่ำสำหรับขวดแก้ว/ขวดพลาสติกเพื่อผ่านเกณฑ์นัดหมายเดี่ยว"
    )

    # REQ-FN-006, D-03: เกณฑ์น้ำหนักสะสมรวมขั้นต่ำสำหรับจุดรับรวมประจำอาคาร/หอพัก
    THRESHOLD_BUILDING_KG: float = Field(
        default=float(os.getenv("THRESHOLD_BUILDING_KG", "20.0")),
        description="เกณฑ์น้ำหนักสะสมรวมขั้นต่ำของจุดรับรวมประจำอาคาร (กก.)"
    )

    # D-04, AC-S04-01: เวลาอัปเดตราคากลางประจำวัน
    BENCHMARK_PRICE_REFRESH_TIME: str = Field(
        default=os.getenv("BENCHMARK_PRICE_REFRESH_TIME", "06:00"),
        description="เวลาอัปเดตราคากลางประจำวัน (HH:MM)"
    )

    # AC-S04-02, REQ-QA-001: เกณฑ์เวลาคำนวณและแสดงผลช่วงราคา
    PRICE_CALCULATION_TIMEOUT_MS: int = Field(
        default=int(os.getenv("PRICE_CALCULATION_TIMEOUT_MS", "3000")),
        description="เวลาสูงสุดในการคำนวณราคา (มิลลิวินาที)"
    )

    # CC-04: Supabase Connection Configuration
    SUPABASE_URL: str = Field(
        default=os.getenv("SUPABASE_URL", "https://mock-saleng.supabase.co"),
        description="Supabase Project URL"
    )
    SUPABASE_KEY: str = Field(
        default=os.getenv("SUPABASE_KEY", "mock-anon-key"),
        description="Supabase Anon/Public Key"
    )
    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        default=os.getenv("SUPABASE_SERVICE_ROLE_KEY", "mock-service-key"),
        description="Supabase Service Role Key"
    )


settings = Settings()

