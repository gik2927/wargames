import os

# firewall.py 파일이 위치한 디렉토리를 기준으로 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYWORDS_FILE = os.path.join(BASE_DIR, 'key.txt')

def get_keywords():
    """
    keywords.txt 파일에서 차단 키워드 목록을 실시간으로 읽어옵니다.
    """
    keywords = []
    try:
        # 파일을 매번 새로 엽니다.
        with open(KEYWORDS_FILE, 'r') as f:
            # 한 줄에 하나씩 키워드를 읽고, 공백/줄바꿈 제거
            keywords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        # (CTF 힌트) 파일이 없으면 방화벽이 사실상 비활성화됩니다.
        print(f"Firewall: !! {KEYWORDS_FILE} not found. Running with no keywords. !!")
    except Exception as e:
        print(f"Firewall: Error reading {KEYWORDS_FILE}: {e}")
    
    return keywords

def is_safe(input_string):
    """
    사용자 입력이 안전한지 동적으로 로드된 키워드로 검사합니다.
    """
    if not isinstance(input_string, str):
        return True # 문자열이 아니면 검사하지 않음

    lower_str = input_string.lower()
    
    # --- !! CTF 핵심 !! ---
    # is_safe 함수가 호출될 때마다 키워드 파일을 *다시 읽어옵니다.*
    # 참가자가 keywords.txt 파일을 빈 파일로 덮어쓰면,
    # 서버 재시작 없이 방화벽이 즉시 무력화됩니다.
    blacklist = get_keywords()
    
    if not blacklist:
        # 키워드 목록이 비어있으면(파일이 없거나, 빈 파일이면) 무조건 통과
        return True
        
    for keyword in blacklist:
        if keyword in lower_str:
            print(f"Firewall: Detected keyword '{keyword}'")
            return False
            
    return True
