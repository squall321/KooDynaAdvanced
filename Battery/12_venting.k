*KEYWORD
*TITLE
Li-ion Cell - Electrolyte Venting / Gas Generation Model
$ B11: 전해질 가스 발생 및 벤팅 모델
$   - 전해질 열분해 시 가스 발생 (80~200°C)
$   - *AIRBAG_SIMPLE_AIRBAG_MODEL 기반 파우치 팽창
$   - *DEFINE_FUNCTION 12010: 온도 기반 Arrhenius 가스 발생율
$ 
$ 물리적 배경:
$   1. 60~80°C: SEI 분해 → CO2, C2H4 발생 시작
$   2. 120°C: 전해질 환원 반응 → H2, CO, CH4
$   3. 150°C: 전해질 산화 분해 → CO2, H2O (대량)
$   4. 200°C+: 급격한 가스 발생, 벤팅 (파우치 파열)
$ 
$ 포함: Phase 3 main 파일에서 *INCLUDE
$ 자동 생성: generate_venting.py (battery_config.yaml → 12_venting.k)
$
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$
$ ============================================================
$ 1. 파우치 내면 세그먼트 셋 (AIRBAG 밀폐면)
$ ============================================================
$
$ SET_SEGMENT_GENERAL PART 옵션: 파우치 셸 내면 자동 생성
$ AIRBAG은 밀폐된 세그먼트 셋 필요 — 파우치 전체면 사용
$
*SET_SEGMENT_GENERAL
$      SID       DA1       DA2       DA3       DA4
       503       0.0       0.0       0.0       0.0
$   OPTION        E1        E2        E3
      PART        10        11        12
$
$ SID=503: 파우치 전면 (PID 10=상면, 11=하면, 12=측면)
$
$ ============================================================
$ 2. AIRBAG 모델 — 파우치 내부 가스 팽창
$ ============================================================
$
$ Per Vol_I p.408 (R16): AIRBAG_SIMPLE_AIRBAG_MODEL
$   Card 1 (core): SID, SIDTYP, RBID, VSCA, PSCA, VINI, MWD, SPSF
$   Card 3: CV, CP, T, LCID, MU, AREA, PE, RO
$   Card 4b (CV≠0): LOU
$
*AIRBAG_SIMPLE_AIRBAG_MODEL
$ Card 1 (core): 파우치 내면 세그먼트 셋
$      SID    SIDTYP      RBID      VSCA      PSCA      VINI       MWD      SPSF
       503         0         0       1.0       1.0       0.0       0.0       0.0
$ Card 3: 가스 열역학 특성
$       CV        CP         T      LCID        MU      AREA        PE        RO
     723.0    1004.0    298.15    -12010       0.6      -12003       0.1  1.0E-09
$ CV=723 J/kg/K (분해가스 정적 비열)
$ CP=1004 J/kg/K (정압 비열)
$ T=298.15 K (유입 가스 온도)
$ LCID=-12010: FUNCTID 12010 호출 (온도 기반 Arrhenius 가스 발생율)
$ MU=0.6: 벤팅 오리피스 형상 계수
$ AREA=-12003: 벤팅 면적 vs 절대압력 커브 (safety valve 모델)
$ PE=0.1 MPa (대기압)
$ RO=1.0E-09 ton/mm³ (대기 밀도)
$
$ Card 4b (CV≠0이므로 Card 4b 사용):
$      LOU
         0
$ LOU=0: MU+AREA 방식으로 벤팅 (LOU curve 미사용)
$
$ ============================================================
$ 3. 가스 발생율 커브 (placeholder, FUNCTID 12010이 우선)
$ ============================================================
$
$ LCID 12001: 질량유입율 (ton/s) vs 시간
$ 실제 구동은 DEFINE_FUNCTION 12010으로 대체
$
*DEFINE_CURVE_TITLE
Gas Generation Rate vs Time (placeholder)
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
     12001         0         1         1       0.0       0.0         0
               0               0
           0.001               0
           0.005           1e-12
            0.01           5e-12
            0.05           1e-10
             0.1           5e-10
               1           1e-09
              10           5e-09
              60           5e-09
$
$ ============================================================
$ 4. 벤팅 면적 커브 (safety valve / burst disk 모델)
$ ============================================================
$
$ LCID 12003: 벤팅 출구 면적 (mm²) vs 절대압력 (MPa)
$ Per Vol_I p.409: AREA<0 → |AREA|=LCID, 면적 vs 절대압력
$
*DEFINE_CURVE_TITLE
Vent Exit Area vs Absolute Pressure (safety valve model)
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
     12003         0         1         1       0.0       0.0         0
               0               0
             0.1               0
             0.2               0
             0.3             0.2
             0.4             0.8
             0.6             1.6
               1               2
               2               2
               5               2
              10               2
$
$ ============================================================
$ 5. 가스 발생 온도 트리거 함수 (Arrhenius)
$ ============================================================
$
$ 2-stage Arrhenius: sei_decomposition(80°C), electrolyte_decomposition(150°C)
$ MW=40 g/mol, max_rate=1.0E-07 ton/s
$
*DEFINE_FUNCTION
     12010
float gas_rate(float time, float temp, float pressure, float volume)
{
    // 인수: (time[s], temp[K], pressure[MPa], volume[mm3])
    // AIRBAG LCID=-12010 규약: 4-arg (time, temp, pressure, volume)
    float R_gas = 8.314;       // J/(mol*K)
    float rate  = 0.0;
    float T = (temp > 250.0) ? temp : 298.15;

    // sei decomposition (T > 353 K = 80 C)
    if (T > 353.0)
    {
        rate = rate + 1.0000E+06 * exp(-60000.0 / (R_gas * T));
    }

    // electrolyte decomposition (T > 423 K = 150 C)
    if (T > 423.0)
    {
        rate = rate + 1.0000E+08 * exp(-80000.0 / (R_gas * T));
    }

    // mol/s -> ton/s (MW=40 g/mol, 1ton=1e6g -> 4.0E-05 ton/mol)
    rate = rate * 4.0000E-05;

    // 최대 발생율 제한
    if (rate > 1.0E-07) rate = 1.0E-07;

    return rate;
}
$
$ ============================================================
$ 6. 가스 물성 보조 커브 (placeholder)
$ ============================================================
$
$ 온도 의존 가스 압력-체적 관계 (솔버 연동 시 자동 갱신)
$
*DEFINE_CURVE_TITLE
Gas Temperature vs Time (from thermal solver coupling)
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
     12005         0         1         1       0.0       0.0         0
               0          298.15
           0.005          298.15
            0.01             320
            0.05             400
             0.1             500
               1             600
              10             500
              60             400
$
$ ============================================================
$ 7. 파우치 파열 기준 — 내압 연동
$ ============================================================
$
$ 파우치 압력 기반 파괴 (AMMGID 참조)
$ 내압 > 0.5MPa 이고 변형률 > 0.15 이면 파열
$ → 기존 MAT_ADD_EROSION에 MXPRS 추가 또는 여기서 별도 정의 가능
$
$ (MAT_024 MID=6에 이미 FAIL 미지정 → 필요 시 아래 활성화)
$*MAT_ADD_EROSION
$        6       0       0.5       0.0       0.0       0.0       0.2      0.0
$       0.0       0.0       0.0       0.0
$
$ ============================================================
$ 참고 (Implementation Notes)
$ ============================================================
$
$
$ [활성화 방법]
$  1. 파우치 내부면 → *SET_SEGMENT (SID=503) 으로 밀폐면 정의
$     (generate_mesh_*.py에서 파우치 내면 세그먼트 셋 생성 필요)
$  2. Phase 3 main 파일에 *INCLUDE 12_venting.k 추가
$  3. 벤팅 면적(VNTCA) 및 개방 압력 → 실험 데이터로 보정
$
$ [대안: SPH 가스]
$  AIRBAG 대신 *PARTICLE_BLAST 또는 *ALE_MULTI-MATERIAL_GROUP
$  으로 가스 거동을 직접 시뮬레이션 가능 (C14와 통합 고려)
$
$ [보정 포인트]
$  - sei decomposition: A=1.0E+06, Ea=60000 J/mol → ARC/DSC 실험으로 보정
$  - electrolyte decomposition: A=1.0E+08, Ea=80000 J/mol → ARC/DSC 실험으로 보정
$  - 벤팅 면적/압력: 파우치 씰 강도 실험으로 결정
$
*END
