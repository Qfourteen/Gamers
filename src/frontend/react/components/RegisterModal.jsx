import React, { useState, useEffect } from 'react';
import { Modal, Form, Button, Alert, Spinner } from 'react-bootstrap';

function RegisterModal({ show, onHide, onRegister }) {
  // 회원가입 폼 상태 관리
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
  
  // 회원가입 처리 상태
  const [isRegistering, setIsRegistering] = useState(false);
  const [registrationStatus, setRegistrationStatus] = useState({
    message: '',
    type: '', // 'success' 또는 'error'
    show: false
  });

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

  // 컴포넌트 마운트 시 규칙 로드
  useEffect(() => {
    if (show) {
      fetchNicknameRules();
      fetchPasswordRules();
    }
  }, [show]);
  
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

  // 모달 닫기 및 상태 초기화
  const handleClose = () => {
    onHide();
    resetForm();
  };

  // 폼 초기화
  const resetForm = () => {
    setTermsAgreed(false);
    setNickname('');
    setNicknameValid(false);
    setNicknameMessage('');
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
    setRegistrationStatus({
      message: '',
      type: '',
      show: false
    });
  };

  // 회원가입 제출 처리
  const handleSubmit = async () => {
    if (isFormValid()) {
      setIsRegistering(true);
      setRegistrationStatus({
        message: '',
        type: '',
        show: false
      });
      
      try {
        const userData = {
          nickname,
          password
        };
        
        const result = await onRegister(userData);
        
        if (result.success) {
          setRegistrationStatus({
            message: result.message,
            type: 'success',
            show: true
          });
          
          // 성공 시 3초 후 모달 닫기
          setTimeout(() => {
            handleClose();
          }, 3000);
          
        } else {
          setRegistrationStatus({
            message: result.message,
            type: 'error',
            show: true
          });
        }
      } catch (error) {
        console.error('회원가입 제출 중 오류:', error);
        setRegistrationStatus({
          message: '회원가입 처리 중 오류가 발생했습니다.',
          type: 'error',
          show: true
        });
      } finally {
        setIsRegistering(false);
      }
    }
  };

  // 폼 유효성 검사
  const isFormValid = () => {
    return (
      termsAgreed && 
      nicknameValid && 
      !nicknameValidating && 
      nickname && 
      passwordValidation.is_valid && 
      !passwordValidating &&
      password &&
      passwordConfirm &&
      passwordsMatch
    );
  };

  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>회원가입</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {registrationStatus.show && (
          <Alert 
            variant={registrationStatus.type === 'success' ? 'success' : 'danger'}
            className="mb-3"
          >
            {registrationStatus.message}
          </Alert>
        )}
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
        <Button variant="secondary" onClick={handleClose}>
          취소
        </Button>
        <Button 
          variant="primary" 
          disabled={!isFormValid() || isRegistering}
          onClick={handleSubmit}
        >
          {isRegistering ? (
            <>
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                aria-hidden="true"
                className="me-2"
              />
              처리 중...
            </>
          ) : nicknameValidating || passwordValidating ? (
            '검증 중...'
          ) : (
            '가입하기'
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export default RegisterModal;