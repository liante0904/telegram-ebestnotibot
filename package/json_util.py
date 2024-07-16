import os
import json
import datetime
import argparse

# 전역 변수로 필터링할 증권사 목록 정의
EXCLUDED_FIRMS = {"하나증권", "신한투자증권", "이베스트증권","이베스트투자증권"}

def save_data_to_local_json(filename, sec_firm_order, article_board_order, firm_nm, attach_url, article_title, main_ch_send_yn="N"):
    directory = os.path.dirname(filename)

    # 디렉터리가 존재하는지 확인하고, 없으면 생성합니다.
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"디렉터리 '{directory}'를 생성했습니다.")

    # 현재 시간을 저장합니다.
    current_time = datetime.datetime.now().isoformat()
    
    # 새 데이터를 딕셔너리로 저장합니다.
    new_data = {
        "SEC_FIRM_ORDER": sec_firm_order,
        "ARTICLE_BOARD_ORDER": article_board_order,
        "FIRM_NM": firm_nm,
        "ATTACH_URL": attach_url,
        "ARTICLE_TITLE": article_title,
        "MAIN_CH_SEND_YN": main_ch_send_yn,  # main_ch_send_yn 값을 대문자로 변환하지 않음
        "SAVE_TIME": current_time
    }

    # 기존 데이터를 읽어옵니다.
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    # 중복 체크 (FIRM_NM, ARTICLE_TITLE 중복 확인)
    is_duplicate = any(
        existing_item["FIRM_NM"] == new_data["FIRM_NM"] and
        existing_item["ARTICLE_TITLE"] == new_data["ARTICLE_TITLE"]
        for existing_item in existing_data
    )

    if not is_duplicate:
        existing_data.append(new_data)
        
        # 업데이트된 데이터를 JSON 파일로 저장합니다.
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
        
        print(f"새 데이터가 {filename}에 성공적으로 저장되었습니다.")
        
        # 중복되지 않은 항목을 템플릿 형식으로 반환
        return format_message(new_data)
    else:
        print("중복된 데이터가 발견되어 저장하지 않았습니다.")
        return ''

def format_message(data):
    EMOJI_PICK = u'\U0001F449'  # 이모지 설정
    ARTICLE_TITLE = data['ARTICLE_TITLE']
    ARTICLE_URL = data['ATTACH_URL']
    
    sendMessageText = ""
    # 게시글 제목(굵게)
    sendMessageText += "*" + ARTICLE_TITLE.replace("_", " ").replace("*", "") + "*" + "\n"
    # 원문 링크
    sendMessageText += EMOJI_PICK  + "[링크]" + "("+ ARTICLE_URL + ")"  + "\n"
    
    return sendMessageText

def update_json_with_main_ch_send_yn(file_path):
    directory = os.path.dirname(file_path)

    # 디렉터리가 존재하는지 확인하고, 없으면 생성합니다.
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"디렉터리 '{directory}'를 생성했습니다.")
    
    if not os.path.exists(file_path):
        print(f"파일 경로 '{file_path}'가 존재하지 않습니다.")
        return

    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # 각 항목에 MAIN_CH_SEND_YN 키를 추가합니다.
    for item in data:
        item["MAIN_CH_SEND_YN"] = "N"
        
        # SAVE_TIME을 마지막에 유지하기 위해 삭제 후 다시 추가
        save_time = item.pop("SAVE_TIME", None)
        if save_time:
            item["SAVE_TIME"] = save_time

    # 업데이트된 데이터를 다시 JSON 파일로 저장합니다.
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    
    print(f"{file_path} 파일에 MAIN_CH_SEND_YN 키가 업데이트되었습니다.")

def format_message_with_firm(data, include_firm_nm):
    EMOJI_PICK = u'\U0001F449'  # 이모지 설정
    FIRM_NM = data['FIRM_NM']
    ARTICLE_TITLE = data['ARTICLE_TITLE']
    ARTICLE_URL = data['ATTACH_URL']
    
    sendMessageText = ""
    if include_firm_nm:
        sendMessageText += "●" + FIRM_NM + "\n"
    sendMessageText += "*" + ARTICLE_TITLE.replace("_", " ").replace("*", "") + "*" + "\n"
    sendMessageText += EMOJI_PICK + "[링크]" + "(" + ARTICLE_URL + ")" + "\n"
    
    return sendMessageText

def get_unsent_main_ch_data_to_local_json(filename):
    directory = os.path.dirname(filename)
    
    # 디렉터리가 존재하는지 확인하고, 없으면 생성합니다.
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"디렉터리 '{directory}'를 생성했습니다.")
    
    # 현재 날짜를 가져옵니다.
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # json 파일을 읽어옵니다.
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
    else:
        print(f"파일 경로 '{filename}'가 존재하지 않습니다.")
        return ''

    # 중복 확인을 위해 json/data_main_daily_send.json의 FIRM_NM 목록을 가져옵니다.
    main_daily_send_path = 'json/data_main_daily_send.json'
    if os.path.exists(main_daily_send_path) and os.path.getsize(main_daily_send_path) > 0:
        with open(main_daily_send_path, 'r', encoding='utf-8') as json_file:
            main_daily_data = json.load(json_file)
            sent_firms = {item["FIRM_NM"] for item in main_daily_data}
            print(f"중복 확인을 위해 로드된 FIRM_NM 목록: {sent_firms}")  # 디버깅 로그 추가
    else:
        sent_firms = set()

    # 전역 변수의 필터링할 증권사를 sent_firms에 추가
    sent_firms.update(EXCLUDED_FIRMS)
    print(f"최종 필터링할 FIRM_NM 목록: {sent_firms}")  # 디버깅 로그 추가

    # 조건에 맞는 데이터를 필터링합니다.
    unsent_data = [
        item for item in data
        if item["SAVE_TIME"].startswith(today_str) and item["MAIN_CH_SEND_YN"] == "N" and item["FIRM_NM"] not in sent_firms
    ]

    # 디버깅 로그 추가
    print(f"필터링된 unsent_data: {unsent_data}")

    # 데이터 형식화
    messages = []
    current_message = ""
    previous_firm_nm = None

    for item in unsent_data:
        include_firm_nm = (item["FIRM_NM"] != previous_firm_nm)
        message_part = format_message_with_firm(item, include_firm_nm)

        if len(current_message) + len(message_part) > 3000:
            messages.append(current_message)
            current_message = message_part
        else:
            current_message += message_part

        previous_firm_nm = item["FIRM_NM"]

    if current_message:
        messages.append(current_message)

    return messages

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process JSON files with specified action.')
    parser.add_argument('action', choices=['update', 'send'], help='Action to perform: update or send')
    parser.add_argument('file_path', type=str, help='Path to the JSON file to process')

    args = parser.parse_args()

    if args.action == 'update':
        update_json_with_main_ch_send_yn(args.file_path)
    elif args.action == 'send':
        results = get_unsent_main_ch_data_to_local_json(args.file_path)
        for result in results:
            print(result)
            print("\n" + "="*50 + "\n")  # 구분선 추가
