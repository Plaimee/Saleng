/**
 * Vitest Component Test สำหรับ AC-S02-04: PhotoUploadManager
 * รองรับ UC-02, REQ-FN-004, EV-03, EV-08, AC-S02-04
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PhotoUploadManager from '../src/components/PhotoUploadManager';

describe('AC-S02-04: PhotoUploadManager Component', () => {
  it('displays photo thumbnails and handles removing photos', () => {
    const handleRemove = vi.fn();
    const mockPhotos = [
      'data:image/png;base64,mock1',
      'data:image/png;base64,mock2',
    ];

    render(
      <PhotoUploadManager
        photos={mockPhotos}
        onAddPhoto={vi.fn()}
        onRemovePhoto={handleRemove}
      />
    );

    // ตรวจสอบข้อความนับจำนวนรูป 2/5 รูป
    expect(screen.getByText('(2/5 รูป)')).not.toBeNull();

    // ตรวจสอบ thumbnail ทั้ง 2 รูป
    expect(screen.getByTestId('photo-thumbnail-0')).not.toBeNull();
    expect(screen.getByTestId('photo-thumbnail-1')).not.toBeNull();

    // ลบรูปแรก
    const removeBtn = screen.getByTestId('remove-photo-btn-0');
    fireEvent.click(removeBtn);
    expect(handleRemove).toHaveBeenCalledWith(0);

    // ปุ่มเพิ่มรูปยังแสดงอยู่เพราะยังไม่ถึง 5 รูป
    expect(screen.getByTestId('upload-photo-label')).not.toBeNull();
  });

  it('hides upload button when 5 photos are uploaded', () => {
    const fivePhotos = [
      'data:img1',
      'data:img2',
      'data:img3',
      'data:img4',
      'data:img5',
    ];

    render(
      <PhotoUploadManager
        photos={fivePhotos}
        onAddPhoto={vi.fn()}
        onRemovePhoto={vi.fn()}
      />
    );

    expect(screen.getByText('(5/5 รูป)')).not.toBeNull();
    expect(screen.queryByTestId('upload-photo-label')).toBeNull();
  });
});

