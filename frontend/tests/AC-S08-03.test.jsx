import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import FaqAccordionView from "../src/components/FaqAccordionView";

describe("AC-S08-03: Categorized FAQ Knowledge Base with Search Component Test", () => {
  const mockCategories = [
    {
      category_id: "MINIMUM_AND_BOOKING",
      category_name: "เงื่อนไขขั้นต่ำและการนัดหมาย",
      faqs: [
        {
          id: "FAQ-01",
          question: "เกณฑ์ขั้นต่ำในการเรียกรถคือเท่าใด?",
          answer: "ยอดประเมินรวมไม่ต่ำกว่า 500 บาท หรือ 2 กระสอบ",
          category: "MINIMUM_AND_BOOKING",
        },
      ],
    },
    {
      category_id: "PAYMENT",
      category_name: "การชำระเงิน",
      faqs: [
        {
          id: "FAQ-07",
          question: "ชำระเงินผ่าน PromptPay ได้หรือไม่?",
          answer: "ได้ครับ โดยสแกน QR Code หน้างาน",
          category: "PAYMENT",
        },
      ],
    },
  ];

  it("renders categorized FAQs and toggles accordion view on click (Q-03)", () => {
    const handleSearch = vi.fn();
    render(
      <FaqAccordionView
        categories={mockCategories}
        searchQuery=""
        onSearchChange={handleSearch}
      />
    );

    expect(screen.getByTestId("faq-accordion-view")).toBeDefined();
    expect(screen.getByText(/เงื่อนไขขั้นต่ำและการนัดหมาย/i)).toBeDefined();

    // Default: FAQ-01 is open
    expect(screen.getByText("ยอดประเมินรวมไม่ต่ำกว่า 500 บาท หรือ 2 กระสอบ")).toBeDefined();

    // Toggle FAQ-07 เพื่อเปิดคำตอบ
    const toggleFaq07 = screen.getByTestId("faq-toggle-FAQ-07");
    fireEvent.click(toggleFaq07);
    expect(screen.getByText("ได้ครับ โดยสแกน QR Code หน้างาน")).toBeDefined();

    // Search filter input
    const searchInput = screen.getByTestId("faq-search-input");
    fireEvent.change(searchInput, { target: { value: "PromptPay" } });
    expect(handleSearch).toHaveBeenCalledWith("PromptPay");
  });
});

