import mysql.connector
from konlpy.tag import Okt
from wordcloud import WordCloud
import numpy as np
import matplotlib.pyplot as plt
import re
from collections import Counter


def count_token_freq(reviews):
    # 1. 리뷰 텍스트 전처리
    reviews_processed = []
    for review in reviews:
        emoji_dingbat_removed = re.sub("["
                           u"\U00002700-\U000027BF" # 특수기호(딩뱃)
                           u"\U0001F000-\U0001FAF0" # 이모지
                           "]+", r'', review)
        newline_tab_return_removed = re.sub('\n\t\r+', r'', emoji_dingbat_removed)

        # 전처리 후 한글이 아예 없는 리뷰는 제외하고 나머지로만 토큰화 - 반대로 말하면 한글이 하나라도 있을 때에만 전처리 대상으로 올리기
        if re.findall('[가-힣ㄱ-ㅎ]+', newline_tab_return_removed):
            reviews_processed.append(newline_tab_return_removed)
    
    # 2. 토큰화
    # 토큰화 라이브러리는 어간을 추출해 용언의 원형을 자동으로 생성해주는 Okt 사용
    okt = Okt()

    # 명사, 동사, 형용사가 가장 해당 음식점의 음식들에 대한 설명을 잘 해줄 것으로 판단
    # 리뷰 텍스트 중 명사, 형용사, 동사로 구분되는 토큰만 담기
    nva_tokens = []

    for review in reviews_processed:
        tokens = okt.morphs(review, stem = True)    
        valid_pos = ['Noun', 'Verb', 'Adjective']

        for token in tokens:
            for subtoken, pos in okt.pos(token):
                if (pos in valid_pos) and (len(subtoken) > 1):
                    nva_tokens.append(subtoken)
    
    # 3. Counter로 각 단어가 몇 번 등장했는지 세어준 딕셔너리를 반환
    return Counter(nva_tokens)


def generate_wordcloud(restaurant_id, vocab_cnt):
    # 1. 워드클라우드 제목 한글 설정
    plt.rc('font', family = 'Malgun Gothic')

    # 2. 워드클라우드 틀 생성
    frame = WordCloud(width = 1000, height = 1000,
                      font_path = 'C:/Users/User/AppData/Local/Microsoft/Windows/Fonts/BMHANNA_11yrs_ttf.ttf',
                      background_color = 'white')

    # 3. 워드클라우드 생성
    # 리뷰가 아예 없으면 흰색 빈 화면이 나오게 하기
    if len(vocab_cnt) == 0:
        array = np.ones((1000, 1000, 3))
    # 그 외의 경우는 워드클라우드 생성
    else:
        cloud = frame.generate_from_frequencies(vocab_cnt)
        array = cloud.to_array()

    plt.figure(figsize = (10, 10))
    plt.imshow(array)
    plt.axis('off')

    # 4. 워드클라우드를 이미지 파일로 저장
    path = f'wordclouds/wc{restaurant_id}.png' # 여기서 path라는 건 로컬 드라이브 상에서의 path랑은 다르다고 하더라
    plt.savefig(path)

    # 5. 워드클라우드를 저장한 경로를 반환
    return path


def save_wc_to_db(db_id, db_pw, host, port = 3306):
    # 1. DB 접근
    db = mysql.connector.connect(
        host = host,
        port = port,
        user = db_id,
        passwd = db_pw,
        database = 'bae_bi'
    )
    
    # 2. DB에서 가게별 리뷰 데이터만 가져오기
    cur = db.cursor()
    cur.execute(f'SELECT content, store_id FROM board_review;')
    result = cur.fetchall()
    reviews_by_restaurant = {r_id: [] for _, r_id in result}
    for review, r_id in result:
        reviews_by_restaurant[r_id].append(review)


    # 3. 데이터에서 워드클라우드 만들기
    for restaurant, reviews in reviews_by_restaurant.items():
        vocab_cnt = count_token_freq(reviews)
        generate_wordcloud(restaurant, vocab_cnt)


if __name__ == '__main__':
    save_wc_to_db(db_id = 'root',
                  db_pw = 'tladnwhd23',
                  host = 'localhost',
                  port = 8888)