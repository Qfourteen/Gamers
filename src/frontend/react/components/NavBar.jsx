import React, { useState, useEffect } from 'react';
import { Navbar, Nav, Container, Button, Modal, Form } from 'react-bootstrap';

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

  {/* 모달 닫기 핸들러 */}
  const handleCloseLogin = () => setShowLoginModal(false);
  const handleCloseRegister = () => setShowRegisterModal(false);

  {/* 모달 열기 핸들러 */}
  const handleShowLogin = () => setShowLoginModal(true);
  const handleShowRegister = () => setShowRegisterModal(true);
  
  {/* 로그아웃 핸들러 */}
  const handleLogout = () => {
    window.location.href = '/auth/logout';
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
              <Nav.Link href={"/"}>홈</Nav.Link>
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
      <Modal show={showRegisterModal} onHide={handleCloseRegister}>
        <Modal.Header closeButton>
          <Modal.Title>회원가입</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3" controlId="registerID">
              <Form.Label>ID</Form.Label>
              <Form.Control type="text" placeholder="ID를 입력하세요" />
            </Form.Group>
            <Form.Group className="mb-3" controlId="registerPassword">
              <Form.Label>비밀번호</Form.Label>
              <Form.Control type="password" placeholder="비밀번호를 입력하세요" />
            </Form.Group>
            <Form.Group className="mb-3" controlId="registerPasswordConfirm">
              <Form.Label>비밀번호 확인</Form.Label>
              <Form.Control type="password" placeholder="비밀번호를 다시 입력하세요" />
            </Form.Group>
            
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseRegister}>
            취소
          </Button>
          <Button variant="primary">
            가입하기
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}

export default NavBar;