# 프로젝트 디렉토리 구조

## 생성 완료된 구조

```
network_cce_checker/
│
├── __init__.py                         # 패키지 초기화
├── README.md                           # 프로젝트 설명서
├── requirements.txt                    # Python 의존성
├── .env.example                       # 환경 변수 템플릿
├── .gitignore                         # Git 제외 파일
│
├── main.py                            # [TODO] 메인 실행 파일
├── config.py                          # [TODO] 설정 관리
├── validators.py                      # [TODO] 검증 로직
│
├── ai_clients/                        # AI 클라이언트 구현
│   ├── __init__.py
│   ├── base.py                       # [TODO] 추상 베이스 클래스
│   ├── openai_client.py             # [TODO] OpenAI 클라이언트
│   ├── anthropic_client.py          # [TODO] Anthropic 클라이언트
│   └── local_llm_client.py          # [TODO] 로컬 LLM 클라이언트 (Ollama)
│
├── stages/                            # 4단계 평가 프로세스
│   ├── __init__.py
│   ├── asset_identification.py      # [TODO] 단계 1: 자산 식별
│   ├── criteria_mapping.py          # [TODO] 단계 2: 기준 매핑
│   ├── config_parsing.py            # [TODO] 단계 3: 설정 파싱
│   └── vulnerability_assessment.py  # [TODO] 단계 4: 취약점 판정
│
├── utils/                             # 유틸리티
│   ├── __init__.py
│   ├── logger.py                    # [TODO] 로깅 시스템
│   ├── file_handler.py              # [TODO] 파일 처리
│   ├── json_parser.py               # [TODO] JSON 추출
│   └── cache.py                     # [TODO] 캐싱 시스템
│
├── templates/                         # 템플릿
│   ├── prompts/                     # AI 프롬프트 템플릿
│   │   ├── stage1_asset_identification.txt      # [TODO]
│   │   ├── stage2_criteria_mapping.txt          # [TODO]
│   │   ├── stage3_config_parsing.txt            # [TODO]
│   │   └── stage4_vulnerability_assessment.txt  # [TODO]
│   └── reports/                     # 보고서 템플릿
│       ├── html_report.jinja2       # [TODO]
│       └── styles.css               # [TODO]
│
├── config/                            # 설정 파일
│   ├── cce_baseline.json            # [TODO] CCE 기준선
│   └── device_profiles.json         # [TODO] 장비별 프로필
│
├── tests/                             # 테스트
│   ├── __init__.py
│   ├── test_validators.py           # [TODO]
│   ├── test_stages.py               # [TODO]
│   └── test_integration.py          # [TODO]
│
└── data/                              # 데이터 디렉토리
    ├── sample_configs/                # 샘플 설정 파일
    │   └── .gitkeep
    ├── outputs/                       # 평가 결과
    │   └── .gitkeep
    └── cache/                         # 캐시
        └── .gitkeep
```

## 핵심 컴포넌트 설명

### 1. AI 클라이언트 (ai_clients/)
세 가지 방식의 AI 호출을 지원:
- **OpenAI**: GPT-4, GPT-4 Turbo 지원
- **Anthropic**: Claude 3.5 Sonnet 지원
- **Local LLM**: Ollama를 통한 로컬 모델 (Llama 3, Mistral 등)

### 2. 평가 단계 (stages/)
CCE 평가 4단계:
1. **Asset Identification**: 장비 타입, OS 버전 식별
2. **Criteria Mapping**: 적용 가능한 CCE 점검 항목 선택
3. **Config Parsing**: 실제 설정값 추출
4. **Vulnerability Assessment**: Pass/Fail 판정

### 3. 유틸리티 (utils/)
- **logger.py**: 구조화된 로깅, 각 단계별 JSON 저장
- **file_handler.py**: 설정 파일 로드/저장
- **json_parser.py**: AI 응답에서 JSON 추출 (마크다운 제거)
- **cache.py**: 기준 매핑 결과 캐싱으로 비용 절감

### 4. 템플릿 (templates/)
- **prompts/**: 각 단계별 AI 프롬프트 템플릿
- **reports/**: HTML 보고서 Jinja2 템플릿

### 5. 설정 (config/)
- **cce_baseline.json**: CCE 점검 항목 정의
- **device_profiles.json**: 장비별 특화 설정

## 구현 우선순위

### Phase 1: 코어 인프라 (1주)
- [ ] config.py: 환경 변수 로드, 설정 관리
- [ ] ai_clients/base.py: 추상 클래스 정의
- [ ] ai_clients/anthropic_client.py: Claude 클라이언트 구현
- [ ] utils/logger.py: 로깅 시스템
- [ ] utils/json_parser.py: JSON 파싱 유틸리티

### Phase 2: AI 클라이언트 (1주)
- [ ] ai_clients/openai_client.py: OpenAI 클라이언트
- [ ] ai_clients/local_llm_client.py: Ollama 클라이언트
- [ ] 클라이언트 팩토리 패턴 구현

### Phase 3: 평가 단계 (2주)
- [ ] validators.py: 모든 검증 함수
- [ ] stages/asset_identification.py + 프롬프트 템플릿
- [ ] stages/criteria_mapping.py + 프롬프트 템플릿
- [ ] stages/config_parsing.py + 프롬프트 템플릿
- [ ] stages/vulnerability_assessment.py + 프롬프트 템플릿

### Phase 4: 통합 및 보고서 (1주)
- [ ] main.py: 전체 워크플로우 통합
- [ ] utils/file_handler.py: 파일 처리
- [ ] templates/reports/: HTML 보고서 생성
- [ ] utils/cache.py: 캐싱 구현

### Phase 5: 테스트 및 문서화 (1주)
- [ ] tests/: 단위 테스트, 통합 테스트
- [ ] config/: CCE 기준선, 장비 프로필
- [ ] 샘플 설정 파일 준비
- [ ] 사용자 가이드 작성

## 다음 단계

1. **config.py 구현**: Pydantic Settings를 사용한 타입 안전 설정
2. **AI 클라이언트 추상화**: 세 가지 백엔드 모두 지원하는 통합 인터페이스
3. **프롬프트 템플릿 작성**: 설계 문서 기반 4단계 프롬프트
4. **검증 로직 구현**: validators.py에 모든 단계 검증 함수

## 공공 배포 고려사항

✅ **완료**
- 깔끔한 디렉토리 구조
- .gitignore로 민감 정보 보호
- .env.example로 설정 가이드
- MIT 라이선스 명시
- 상세한 README

🔄 **진행 중**
- 구현 진행

📋 **예정**
- 샘플 데이터 제공
- 사용자 가이드 확장
- CI/CD 파이프라인
- Docker 이미지
- 웹 UI (선택사항)
