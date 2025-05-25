import React, { useState } from 'react';
import { Modal, Button, Form, Alert } from 'react-bootstrap';

function UserInfoModal({ show, onHide, userInfo }) {
  const [showDeactivateConfirm, setShowDeactivateConfirm] = useState(false);
  const [deactivateReason, setDeactivateReason] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // 비활성화 확인 모달 토글
  const toggleDeactivateConfirm = () => {
    setShowDeactivateConfirm(!showDeactivateConfirm);
    setError('');
    setSuccess('');
  };

  // 계정 비활성화 요청 처리
  const handleDeactivateAccount = async () => {
    try {
      const response = await fetch('/auth/users/deactivate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          reason: deactivateReason || '사용자 요청에 의한 계정 비활성화'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess('계정이 성공적으로 삭제되었습니다.');
        
        // 쿠키 삭제가 백엔드에서 처리되므로 페이지 새로고침으로 상태 업데이트
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      } else {
        const error = await response.json();
        setError(error.detail || '계정 삭제 중 오류가 발생했습니다.');
      }
    } catch (err) {
      console.error('계정 삭제 요청 중 오류:', err);
      setError('계정 삭제 처리 중 오류가 발생했습니다.');
    }
  };

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>내 정보</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {userInfo && (
          <div>
            <p><strong>사용자명:</strong> {userInfo.username}</p>
            <p><strong>계정 상태:</strong> {userInfo.disabled ? '비활성화됨' : '활성화됨'}</p>
            {userInfo.is_admin && <p><strong>관리자 권한:</strong> 있음</p>}
            {userInfo.disabled && (
              <>
                <p><strong>비활성화 사유:</strong> {userInfo.disabled_reason || '없음'}</p>
                <p><strong>비활성화 일시:</strong> {userInfo.disabled_at ? new Date(userInfo.disabled_at).toLocaleString() : '없음'}</p>
              </>
            )}

            {/* 계정 비활성화 섹션 */}
            {!userInfo.disabled && !showDeactivateConfirm && (
              <div className="mt-4 pt-3 border-top">
                <Button 
                  variant="danger" 
                  size="sm"
                  onClick={toggleDeactivateConfirm}
                >
                  계정 삭제
                </Button>
                <p className="text-muted mt-2 small">
                  모든 점수 정보가 사라집니다.
                  <br/>
                  계정 자체는 다시 복구할 수 있습니다. 다만 관리자에 의해 수동으로 복구해야 합니다.
                </p>
              </div>
            )}

            {/* 비활성화 확인 폼 */}
            {showDeactivateConfirm && (
              <div className="mt-3 p-3 border rounded bg-light">
                <h6 className="text-danger">계정 삭제 확인</h6>
                
                {error && <Alert variant="danger">{error}</Alert>}
                {success && <Alert variant="success">{success}</Alert>}
                
                <Form.Group className="mb-3">
                  <Form.Label>삭제 사유 (선택사항)</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={2}
                    value={deactivateReason}
                    onChange={(e) => setDeactivateReason(e.target.value)}
                    placeholder="삭제 사유를 입력해주세요 (선택사항)"
                  />
                </Form.Group>
                
                <div className="d-flex gap-2">
                  <Button 
                    variant="danger" 
                    size="sm"
                    onClick={handleDeactivateAccount}
                    disabled={!!success}
                  >
                    계정 삭제 확인
                  </Button>
                  <Button 
                    variant="secondary" 
                    size="sm"
                    onClick={toggleDeactivateConfirm}
                    disabled={!!success}
                  >
                    취소
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          닫기
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export default UserInfoModal;