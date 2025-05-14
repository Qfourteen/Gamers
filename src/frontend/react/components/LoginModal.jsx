import React, { useState } from 'react';
import { Modal, Form, Button, Alert, Spinner } from 'react-bootstrap';

function LoginModal({ show, onHide, onLogin }) {
  // 로그인 폼 상태 관리
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [loginStatus, setLoginStatus] = useState({
    message: '',
    type: '',
    show: false
  });

  // 모달 닫기 및 상태 초기화
  const handleClose = () => {
    onHide();
    resetForm();
  };

  // 폼 초기화
  const resetForm = () => {
    setUsername('');
    setPassword('');
    setLoginStatus({
      message: '',
      type: '',
      show: false
    });
  };

  // 로그인 제출 처리
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (username && password) {
      setIsLoggingIn(true);
      setLoginStatus({
        message: '',
        type: '',
        show: false
      });
      
      try {
        const result = await onLogin(username, password);
        
        if (result.success) {
          setLoginStatus({
            message: result.message || '로그인 성공!',
            type: 'success',
            show: true
          });
          
          // 성공 시 1초 후 모달 닫기
          setTimeout(() => {
            handleClose();
          }, 1000);
        } else {
          setLoginStatus({
            message: result.message || '로그인 실패',
            type: 'error',
            show: true
          });
        }
      } catch (error) {
        console.error('로그인 제출 중 오류:', error);
        setLoginStatus({
          message: '로그인 처리 중 오류가 발생했습니다.',
          type: 'error',
          show: true
        });
      } finally {
        setIsLoggingIn(false);
      }
    }
  };

  // 폼 유효성 검사
  const isFormValid = () => {
    return username.trim() !== '' && password.trim() !== '';
  };

  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>로그인</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loginStatus.show && (
          <Alert 
            variant={loginStatus.type === 'success' ? 'success' : 'danger'}
            className="mb-3"
          >
            {loginStatus.message}
          </Alert>
        )}
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3" controlId="loginUsername">
            <Form.Label>ID</Form.Label>
            <Form.Control 
              type="text" 
              placeholder="ID를 입력하세요" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isLoggingIn}
            />
          </Form.Group>
          
          <Form.Group className="mb-3" controlId="loginPassword">
            <Form.Label>비밀번호</Form.Label>
            <Form.Control 
              type="password" 
              placeholder="비밀번호를 입력하세요"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoggingIn}
            />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose} disabled={isLoggingIn}>
          취소
        </Button>
        <Button 
          variant="primary" 
          disabled={!isFormValid() || isLoggingIn}
          onClick={handleSubmit}
        >
          {isLoggingIn ? (
            <>
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                aria-hidden="true"
                className="me-2"
              />
              로그인 중...
            </>
          ) : (
            '로그인'
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export default LoginModal;