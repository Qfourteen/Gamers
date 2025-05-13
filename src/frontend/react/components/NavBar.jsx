import React, { useState, useEffect } from 'react';
import { Navbar, Nav, Container, Button, Modal, Form } from 'react-bootstrap';
import RegisterModal from './RegisterModal';

function NavBar() {
  {/* 인증 상태 관리 */}
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  {/* 모달 상태 관리 */}
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);


  useEffect(() => {
    const checkAuth = () => {
      const hasCookie = document.cookie.split(';').some(item => item.trim().startsWith('auth_token='));
      setIsAuthenticated(hasCookie);
    };
    
    checkAuth();
  }, []);

  {/* 모달 핸들러 */}
  const handleCloseLogin = () => setShowLoginModal(false);
  const handleCloseRegister = () => setShowRegisterModal(false);
  
  {/* 회원가입 처리 */}
  const handleRegister = async (userData) => {
    try {
      // 백엔드에서는 username으로 필드명을 사용하므로 변환
      const requestData = {
        username: userData.nickname,
        password: userData.password
      };

      // 회원가입 API 호출
      const response = await fetch('/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      // 응답 데이터 확인
      const data = await response.json();
      
      // 회원가입 실패 시
      if (!response.ok) {
        const errorMessage = data.detail || '회원가입에 실패했습니다.';
        return { 
          success: false, 
          message: errorMessage 
        };
      }

      // 회원가입 성공 시 자동 로그인 처리
      const loginSuccess = await autoLogin(requestData.username, requestData.password);
      
      if (loginSuccess) {
        return { 
          success: true, 
          message: `${requestData.username}님, 회원가입 및 로그인이 완료되었습니다.` 
        };
      } else {
        return { 
          success: true, 
          message: `${requestData.username}님, 회원가입이 완료되었습니다. 로그인 해주세요.` 
        };
      }
    } catch (error) {
      console.error('회원가입 처리 중 오류:', error);
      return { 
        success: false, 
        message: '회원가입 처리 중 오류가 발생했습니다.' 
      };
    }
  };
  
  // 자동 로그인 처리
  const autoLogin = async (username, password) => {
    try {
      // HTTP Basic Auth에 필요한 인코딩 (username:password를 base64로 인코딩)
      const credentials = btoa(`${username}:${password}`);
      
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${credentials}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        // 로그인 상태 업데이트
        setIsAuthenticated(true);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('자동 로그인 처리 중 오류:', error);
      return false;
    }
  };

  {/* 모달 열기 핸들러 */}
  const handleShowLogin = () => setShowLoginModal(true);
  const handleShowRegister = () => setShowRegisterModal(true);
  
  {/* 로그아웃 핸들러 */}
  const handleLogout = async () => {
    try {
      const response = await fetch('/auth/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.success) {
        // 로그아웃 성공 시 페이지 새로고침
        window.location.reload();
      } else {
        console.error('로그아웃 실패:', data.message);
      }
    } catch (error) {
      console.error('로그아웃 요청 중 오류 발생:', error);
    }
  };

  {/* 내 정보 조회 핸들러 */}
  const handleMyInfo = () => {
    window.location.href = '/auth/users/me';
  };

  return (
    <>
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand href="/">Gamers</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link href={"/introduce"}>소개</Nav.Link>
              <Nav.Link href={"/policy"}>개인정보 처리 방침</Nav.Link>
            </Nav>
            <Nav>
              {isAuthenticated ? (
                <>
                  <Button variant="outline-light" className="me-2 mb-2" onClick={handleMyInfo}>
                    내 정보
                  </Button>
                  <Button variant="outline-light" onClick={handleLogout}>
                    로그아웃
                  </Button>
                </>
              ) : (
                <>
                  <Button variant="outline-light" className="me-2 mb-2" onClick={handleShowLogin}>
                    로그인
                  </Button>
                  <Button variant="light" onClick={handleShowRegister}>
                    회원가입
                  </Button>
                </>
              )}
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      
      {/* 로그인 모달 */}
      <Modal show={showLoginModal} onHide={handleCloseLogin}>
        <Modal.Header closeButton>
          <Modal.Title>로그인</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3" controlId="loginID">
              <Form.Label>ID</Form.Label>
              <Form.Control type="text" placeholder="ID를 입력하세요" />
            </Form.Group>
            <Form.Group className="mb-3" controlId="loginPassword">
              <Form.Label>비밀번호</Form.Label>
              <Form.Control type="password" placeholder="비밀번호를 입력하세요" />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseLogin}>
            취소
          </Button>
          <Button variant="primary">
            로그인
          </Button>
        </Modal.Footer>
      </Modal>
      
      {/* 회원가입 모달 */}
      <RegisterModal 
        show={showRegisterModal} 
        onHide={handleCloseRegister}
        onRegister={handleRegister}
      />
    </>
  );
}

export default NavBar;