import React, { useState, useEffect } from 'react';
import { Navbar, Nav, Container, Button, Modal, Form, Alert } from 'react-bootstrap';

function NavBar() {
  {/* 인증 상태 관리 */}
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  {/* 모달 상태 관리 */}
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  
  {/* 회원가입 폼 상태 관리 */}
  const [termsAgreed, setTermsAgreed] = useState(false);
  const [nickname, setNickname] = useState('');
  const [nicknameValid, setNicknameValid] = useState(false);
  const [nicknameMessage, setNicknameMessage] = useState('');
  const [nicknameRules, setNicknameRules] = useState(null);
  const [nicknameValidating, setNicknameValidating] = useState(false);
  
  // 비밀번호 유효성 검증 상태
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [passwordValidation, setPasswordValidation] = useState({
    is_valid: false,
    strength: '',
    color: '',
    feedback: [],
    score: 0
  });
  const [passwordRules, setPasswordRules] = useState(null);
  const [passwordValidating, setPasswordValidating] = useState(false);
  const [passwordsMatch, setPasswordsMatch] = useState(true);

  // 닉네임 규칙 가져오기
  const fetchNicknameRules = async () => {
    try {
      const response = await fetch('/auth/nickname-rules');
      const data = await response.json();
      setNicknameRules(data);
    } catch (error) {
      console.error('닉네임 규칙 조회 중 오류:', error);
    }
  };

  // 비밀번호 규칙 가져오기
  const fetchPasswordRules = async () => {
    try {
      const response = await fetch('/auth/password-rules');
      const data = await response.json();
      setPasswordRules(data);
    } catch (error) {
      console.error('비밀번호 규칙 조회 중 오류:', error);
    }
  };

  // 닉네임 유효성 검증
  const validateNickname = async (name) => {
    if (!name) {
      setNicknameValid(false);
      setNicknameMessage('');
      return;
    }
    
    setNicknameValidating(true);
    try {
      const response = await fetch(`/auth/validate-nickname?nickname=${encodeURIComponent(name)}`);
      const data = await response.json();
      
      setNicknameValid(data.valid);
      setNicknameMessage(data.message);
    } catch (error) {
      console.error('닉네임 검증 중 오류:', error);
      setNicknameValid(false);
      setNicknameMessage('검증 중 오류가 발생했습니다.');
    } finally {
      setNicknameValidating(false);
    }
  };
  
  // 비밀번호 유효성 검증
  const validatePassword = async (pwd) => {
    if (!pwd) {
      setPasswordValidation({
        is_valid: false,
        strength: '',
        color: '',
        feedback: [],
        score: 0
      });
      return;
    }
    
    setPasswordValidating(true);
    try {
      const response = await fetch('/auth/validate-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password: pwd })
      });
      const data = await response.json();
      setPasswordValidation(data);
    } catch (error) {
      console.error('비밀번호 검증 중 오류:', error);
      setPasswordValidation({
        is_valid: false,
        strength: '오류',
        color: 'danger',
        feedback: ['검증 중 오류가 발생했습니다.'],
        score: 0
      });
    } finally {
      setPasswordValidating(false);
    }
  };
  
  // 비밀번호 일치 여부 확인
  const checkPasswordsMatch = () => {
    if (!passwordConfirm) {
      setPasswordsMatch(true);
      return;
    }
    
    setPasswordsMatch(password === passwordConfirm);
  };

  useEffect(() => {
    const checkAuth = () => {
      const hasCookie = document.cookie.split(';').some(item => item.trim().startsWith('auth_token='));
      setIsAuthenticated(hasCookie);
    };
    
    checkAuth();
    
    // 회원가입 모달용 규칙 로드
    fetchNicknameRules();
    fetchPasswordRules();
  }, []);
  
  // 닉네임이 변경될 때마다 유효성 검증
  useEffect(() => {
    const timer = setTimeout(() => {
      if (nickname) {
        validateNickname(nickname);
      }
    }, 300); // 디바운스 타이머: 타이핑 중간중간 API 호출 방지
    
    return () => clearTimeout(timer);
  }, [nickname]);
  
  // 비밀번호가 변경될 때마다 유효성 검증
  useEffect(() => {
    const timer = setTimeout(() => {
      if (password) {
        validatePassword(password);
      }
      if (passwordConfirm) {
        checkPasswordsMatch();
      }
    }, 300); // 디바운스 타이머
    
    return () => clearTimeout(timer);
  }, [password]);
  
  // 비밀번호 확인이 변경될 때마다 일치 여부 검증
  useEffect(() => {
    if (passwordConfirm) {
      checkPasswordsMatch();
    }
  }, [passwordConfirm]);

  {/* 모달 닫기 핸들러 */}
  const handleCloseLogin = () => setShowLoginModal(false);
  const handleCloseRegister = () => {
    setShowRegisterModal(false);
    setTermsAgreed(false); // 모달 닫을 때 약관 동의 상태 초기화
    setNickname(''); // 닉네임 초기화
    setNicknameValid(false); 
    setNicknameMessage('');
    // 비밀번호 관련 상태 초기화
    setPassword('');
    setPasswordConfirm('');
    setPasswordValidation({
      is_valid: false,
      strength: '',
      color: '',
      feedback: [],
      score: 0
    });
    setPasswordsMatch(true);
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
      <Modal show={showRegisterModal} onHide={handleCloseRegister}>
        <Modal.Header closeButton>
          <Modal.Title>회원가입</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3" controlId="registerID">
              <Form.Label>ID</Form.Label>
              <Form.Control 
                type="text" 
                placeholder="ID를 입력하세요" 
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                isValid={nickname && nicknameValid}
                isInvalid={nickname && !nicknameValid}
              />
              
              {nicknameMessage && (
                <Form.Text 
                  className={nicknameValid ? "text-success" : "text-danger"}
                >
                  {nicknameMessage}
                </Form.Text>
              )}
              
              {/* 닉네임 유효성 규칙 안내 */}
              {nicknameRules && (
                <div className="mt-2 mb-2">
                  <details>
                    <summary className="text-muted">ID 생성 규칙</summary>
                    <div className="p-2 mt-2 bg-light rounded">
                      <small>
                        <ul className="mb-0 ps-3">
                          {nicknameRules.rules.map((rule, index) => (
                            <li key={index}>{rule}</li>
                          ))}
                        </ul>
                      </small>
                    </div>
                  </details>
                </div>
              )}
            </Form.Group>
            
            <Form.Group className="mb-3" controlId="registerPassword">
              <Form.Label>비밀번호</Form.Label>
              <Form.Control 
                type="password" 
                placeholder="비밀번호를 입력하세요" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                isValid={password && passwordValidation.is_valid}
                isInvalid={password && !passwordValidation.is_valid}
              />
              
              {password && (
                <div className="mt-2">
                  <div className="d-flex align-items-center">
                    <div className="me-2">
                      비밀번호 강도:
                    </div>
                    <div 
                      className={`badge bg-${passwordValidation.color} flex-grow-0`}
                      style={{ minWidth: '70px' }}
                    >
                      {passwordValidation.strength || '검증 중...'}
                    </div>
                  </div>
                  
                  {/* 비밀번호 강도 시각화 */}
                  <div className="progress mt-1" style={{ height: '5px' }}>
                    <div 
                      className={`progress-bar bg-${passwordValidation.color}`} 
                      role="progressbar" 
                      style={{ width: `${(passwordValidation.score / 7) * 100}%` }} 
                      aria-valuenow={passwordValidation.score} 
                      aria-valuemin="0" 
                      aria-valuemax="7"
                    />
                  </div>
                  
                  {/* 피드백 메시지 표시 */}
                  {passwordValidation.feedback && passwordValidation.feedback.length > 0 && (
                    <div className="mt-1">
                      <small className="text-muted">
                        <ul className="mb-0 ps-3">
                          {passwordValidation.feedback.map((feedback, idx) => (
                            <li key={idx}>{feedback}</li>
                          ))}
                        </ul>
                      </small>
                    </div>
                  )}
                  
                  {/* 비밀번호 규칙 안내 */}
                  {passwordRules && (
                    <div className="mt-2">
                      <details>
                        <summary className="text-muted">비밀번호 생성 규칙</summary>
                        <div className="p-2 mt-2 bg-light rounded">
                          <small>
                            <div className="mb-2">
                              <strong>필수 요구사항:</strong>
                              <ul className="mb-2 ps-3">
                                {passwordRules.requirements.map((rule, index) => (
                                  <li key={index}>{rule}</li>
                                ))}
                              </ul>
                            </div>
                            
                            <div>
                              <strong>권장사항(선택):</strong>
                              <ul className="mb-0 ps-3">
                                {passwordRules.recommendations.map((rule, index) => (
                                  <li key={index}>{rule}</li>
                                ))}
                              </ul>
                            </div>
                          </small>
                        </div>
                      </details>
                    </div>
                  )}
                </div>
              )}
            </Form.Group>
            
            <Form.Group className="mb-3" controlId="registerPasswordConfirm">
              <Form.Label>비밀번호 확인</Form.Label>
              <Form.Control 
                type="password" 
                placeholder="비밀번호를 다시 입력하세요"
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)} 
                isValid={passwordConfirm && passwordsMatch}
                isInvalid={passwordConfirm && !passwordsMatch}
              />
              {passwordConfirm && !passwordsMatch && (
                <Form.Text className="text-danger">
                  비밀번호가 일치하지 않습니다.
                </Form.Text>
              )}
            </Form.Group>
            
            <Form.Group className="mb-3" controlId="termsCheckbox">
              <Form.Check 
                type="checkbox" 
                checked={termsAgreed}
                onChange={(e) => setTermsAgreed(e.target.checked)}
                label={
                  <span>
                    <a href="/policy" target="_blank" rel="noopener noreferrer">개인정보 처리 방침</a>에 동의합니다
                  </span>
                }
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseRegister}>
            취소
          </Button>
          <Button 
            variant="primary" 
            disabled={
              !termsAgreed || 
              !nicknameValid || 
              nicknameValidating || 
              !nickname || 
              !passwordValidation.is_valid || 
              passwordValidating ||
              !password ||
              !passwordConfirm ||
              !passwordsMatch
            }
          >
            {nicknameValidating || passwordValidating ? '검증 중...' : '가입하기'}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}

export default NavBar;