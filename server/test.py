import psycopg2  # 동기 드라이버
import sys

def test_sync_connection():
    print("--- [순수 psycopg2 (동기) 접속 테스트] ---")
    
    # .env 정보 그대로
    DSN = "postgresql://devlog:devlog_password@127.0.0.1:5432/devlog_db"
    
    print(f"대상: {DSN}")
    print("연결 시도 중...")

    try:
        conn = psycopg2.connect(DSN)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"\n✅ [성공] 접속 됩니다! DB 버전: {version}")
        print("결론: 네트워크/계정은 정상입니다. asyncpg 라이브러리가 문제였습니다.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"\n❌ [실패] 동기 접속도 안 됩니다: {e}")
        print("결론: DB 계정(devlog)이 없거나, 포트(5432)가 막혀있습니다.")

if __name__ == "__main__":
    test_sync_connection()