#!/usr/bin/env python3
"""
Create truly verb-specific hints by deeply analyzing each verb-noun relationship.
Version 5.0.0 - Manual semantic analysis approach.
"""

import json
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import os
import sys

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def load_collocations(filepath: str) -> dict:
    """Load the complete collocations data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_verb_semantics(verb_data: dict, verb_kanji: str) -> Dict[str, List[str]]:
    """
    Manually analyze a verb and create specific semantic hint groups.
    Returns a dictionary of hint -> list of nouns.
    """

    nouns = verb_data['matches']['nouns']
    noun_list = [(n['word'], n['english']) for n in nouns]

    # Manual semantic analysis for each major verb
    if verb_kanji == 'ある':
        return {
            "free time you have": ["時間", "ころ", "暇", "昼間", "週末", "休み", "明日", "今日", "昨日"],
            "reasons why": ["理由", "原因", "わけ", "せい"],
            "problems that occur": ["問題", "故障", "けが", "風邪", "病気", "事故"],
            "things you enjoy": ["興味", "趣味", "楽しみ", "好き"],
            "possibilities": ["機会", "可能性", "つもり", "場合", "チャンス", "予定"],
            "places in town": ["店", "銀行", "駅", "公園", "交番", "郵便局", "図書館", "病院", "会社", "学校"],
            "parts of buildings": ["玄関", "台所", "部屋", "廊下", "階段", "屋上", "地下", "エレベーター"],
            "special events": ["誕生日", "お祭り", "展覧会", "式", "会議", "パーティー", "コンサート"],
            "disasters": ["台風", "火事", "地震", "洪水"],
            "physical objects": ["贈り物", "お釣り", "忘れ物", "荷物", "財布", "鍵", "傘", "お金", "切手", "薬"],
            "days of the week": ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"],
            "comparisons": ["関係", "違い", "別", "代わり", "反対"],
            "responsibilities": ["責任", "義務", "仕事", "宿題", "用事"],
            "feelings and states": ["自信", "勇気", "元気", "気持ち", "意味", "価値"],
            "quantities": ["たくさん", "少し", "全部", "半分", "残り", "ほとんど"]
        }

    elif verb_kanji == '行く':
        return {
            "places to study": ["学校", "図書館", "大学", "高校", "小学校", "中学校", "教室", "塾"],
            "places to work": ["会社", "仕事", "オフィス", "工場", "職場"],
            "medical places": ["病院", "医者", "歯医者", "薬局", "クリニック"],
            "shopping places": ["店", "デパート", "スーパー", "コンビニ", "市場", "商店街", "本屋"],
            "transportation": ["駅", "空港", "バス停", "港", "停留所"],
            "nature spots": ["海", "山", "公園", "川", "森", "庭", "湖", "島"],
            "entertainment": ["映画館", "レストラン", "カフェ", "遊園地", "美術館", "博物館", "劇場"],
            "daily necessities": ["トイレ", "お風呂", "台所", "部屋"],
            "destinations": ["東京", "日本", "アメリカ", "外国", "海外", "田舎", "都市", "町"],
            "people to visit": ["友達", "彼女", "彼", "先生", "親", "家族", "おじいさん", "おばあさん"],
            "directions": ["右", "左", "前", "後ろ", "上", "下", "向こう", "こちら"],
            "home-related": ["家", "うち", "実家", "アパート", "マンション", "寮"],
            "events": ["結婚式", "パーティー", "会議", "授業", "試合", "コンサート"],
            "travel methods": ["旅行", "散歩", "ドライブ", "ハイキング"]
        }

    elif verb_kanji == 'する':
        return {
            "work you do": ["仕事", "勉強", "研究", "アルバイト", "宿題", "レポート", "プレゼン"],
            "housework": ["料理", "掃除", "洗濯", "買い物", "片付け", "修理"],
            "exercise": ["運動", "スポーツ", "テニス", "水泳", "柔道", "ジョギング", "サッカー", "野球"],
            "talking": ["話", "質問", "説明", "相談", "会話", "挨拶", "議論", "発表"],
            "preparations": ["準備", "用意", "支度", "予習", "復習", "計画"],
            "competitions": ["試合", "試験", "競争", "コンテスト", "テスト"],
            "life events": ["結婚", "卒業", "入学", "引っ越し", "就職", "退職"],
            "mishaps": ["失敗", "故障", "喧嘩", "間違い", "事故", "怪我"],
            "planning": ["予約", "計画", "会議", "約束", "予定", "スケジュール"],
            "worrying": ["注意", "心配", "安心", "緊張", "努力", "我慢"],
            "communication": ["連絡", "電話", "メール", "返事", "報告", "お知らせ"],
            "experiences": ["経験", "体験", "冒険", "挑戦"],
            "decisions": ["決定", "選択", "判断", "決心"],
            "helping": ["手伝い", "協力", "援助", "サポート", "ボランティア"]
        }

    elif verb_kanji == '来る':
        return {
            "people arriving": ["友達", "先生", "客", "親", "子供", "彼", "彼女", "家族", "医者"],
            "vehicles arriving": ["バス", "電車", "タクシー", "飛行機", "船", "新幹線"],
            "seasons and time": ["春", "夏", "秋", "冬", "朝", "夜", "明日", "来週", "来月", "来年"],
            "from places": ["学校", "会社", "家", "外国", "日本", "アメリカ", "東京", "病院"],
            "bringing things": ["手紙", "荷物", "プレゼント", "お土産", "書類", "メッセージ"],
            "weather coming": ["雨", "雪", "台風", "嵐"],
            "occasions": ["誕生日", "クリスマス", "正月", "休み", "週末"],
            "appointments": ["約束", "予定", "面接", "会議"],
            "news and info": ["ニュース", "連絡", "知らせ", "結果", "返事"]
        }

    elif verb_kanji == '見る':
        return {
            "entertainment": ["映画", "テレビ", "ビデオ", "アニメ", "ドラマ", "ニュース", "番組"],
            "reading materials": ["本", "新聞", "雑誌", "手紙", "メール", "地図", "メニュー", "写真"],
            "art and culture": ["絵", "展覧会", "美術館", "博物館", "コンサート"],
            "nature": ["空", "星", "月", "海", "山", "景色", "花", "鳥"],
            "people watching": ["子供", "赤ちゃん", "友達", "先生", "人", "顔"],
            "checking things": ["時計", "カレンダー", "スケジュール", "予定", "値段", "答え"],
            "documents": ["資料", "書類", "レポート", "宿題", "試験"],
            "places": ["家", "部屋", "店", "学校", "会社", "町"],
            "dreams and future": ["夢", "未来", "将来"],
            "problems": ["問題", "間違い", "事故", "けが"]
        }

    elif verb_kanji == '言う':
        return {
            "greetings": ["おはよう", "こんにちは", "こんばんは", "さようなら", "ありがとう", "すみません"],
            "opinions": ["意見", "考え", "気持ち", "感想", "批判", "文句"],
            "information": ["名前", "住所", "電話番号", "答え", "理由", "説明"],
            "words and phrases": ["言葉", "日本語", "英語", "文", "単語"],
            "truth and lies": ["本当", "嘘", "真実", "秘密"],
            "requests": ["お願い", "頼み", "命令", "注文"],
            "stories": ["話", "物語", "冗談", "例え", "昔話"],
            "responses": ["はい", "いいえ", "返事", "答え"],
            "complaints": ["文句", "不満", "苦情", "愚痴"]
        }

    elif verb_kanji == '食べる':
        return {
            "Japanese food": ["寿司", "天ぷら", "ラーメン", "うどん", "そば", "丼", "弁当", "おにぎり"],
            "meals": ["朝ご飯", "昼ご飯", "晩ご飯", "ご飯", "食事", "おやつ"],
            "meat": ["肉", "牛肉", "豚肉", "鶏肉", "魚", "エビ"],
            "vegetables": ["野菜", "サラダ", "大根", "人参", "キャベツ", "トマト"],
            "fruits": ["果物", "りんご", "みかん", "バナナ", "いちご", "ぶどう"],
            "sweets": ["ケーキ", "アイスクリーム", "チョコレート", "お菓子", "デザート"],
            "bread and pasta": ["パン", "サンドイッチ", "ピザ", "パスタ", "スパゲッティ"],
            "drinks with meals": ["スープ", "味噌汁"],
            "cooking styles": ["料理", "和食", "洋食", "中華"],
            "portions": ["たくさん", "少し", "全部", "半分"]
        }

    elif verb_kanji == '飲む':
        return {
            "hot drinks": ["お茶", "コーヒー", "紅茶", "ココア", "スープ", "味噌汁"],
            "cold drinks": ["水", "ジュース", "牛乳", "コーラ", "アイスコーヒー", "アイスティー"],
            "alcohol": ["ビール", "ワイン", "日本酒", "ウイスキー", "酒"],
            "medicine": ["薬", "栄養剤", "ビタミン"],
            "amounts": ["たくさん", "少し", "一杯", "コップ", "グラス"]
        }

    elif verb_kanji == '書く':
        return {
            "correspondence": ["手紙", "メール", "はがき", "年賀状", "メッセージ", "カード"],
            "academic": ["レポート", "論文", "宿題", "答え", "作文", "感想文"],
            "personal": ["日記", "メモ", "ノート", "予定", "計画"],
            "official": ["書類", "申請書", "履歴書", "契約書", "サイン"],
            "creative": ["小説", "詩", "物語", "本", "記事"],
            "information": ["名前", "住所", "電話番号", "番号", "漢字", "ひらがな", "カタカナ"],
            "lists": ["リスト", "メニュー", "プログラム", "スケジュール"]
        }

    elif verb_kanji == '読む':
        return {
            "books": ["本", "小説", "教科書", "辞書", "雑誌", "漫画"],
            "news": ["新聞", "ニュース", "記事", "ブログ"],
            "correspondence": ["手紙", "メール", "メッセージ", "はがき"],
            "academic": ["論文", "レポート", "資料", "文献", "研究"],
            "documents": ["書類", "契約書", "説明書", "マニュアル"],
            "poetry": ["詩", "俳句", "短歌"],
            "information": ["地図", "メニュー", "看板", "広告", "お知らせ"],
            "japanese": ["漢字", "ひらがな", "カタカナ", "文", "文章"]
        }

    elif verb_kanji == '作る':
        return {
            "cooking": ["料理", "ご飯", "弁当", "ケーキ", "パン", "お菓子", "サラダ", "スープ"],
            "crafts": ["服", "人形", "おもちゃ", "アクセサリー", "家具"],
            "documents": ["書類", "レポート", "資料", "リスト", "予定表", "計画"],
            "creative": ["歌", "曲", "詩", "物語", "映画", "ビデオ", "ウェブサイト"],
            "relationships": ["友達", "仲間", "グループ", "チーム", "会社"],
            "abstract": ["時間", "機会", "ルール", "法律", "システム", "関係"],
            "problems": ["問題", "間違い", "失敗", "トラブル"]
        }

    elif verb_kanji == '買う':
        return {
            "food": ["パン", "肉", "野菜", "果物", "魚", "お菓子", "弁当"],
            "drinks": ["ジュース", "ビール", "お茶", "コーヒー", "水", "牛乳"],
            "clothing": ["服", "靴", "帽子", "かばん", "シャツ", "ズボン", "スカート"],
            "electronics": ["テレビ", "パソコン", "カメラ", "電話", "ゲーム", "冷蔵庫"],
            "books and media": ["本", "雑誌", "新聞", "CD", "DVD", "切手"],
            "gifts": ["プレゼント", "お土産", "花", "おもちゃ"],
            "tickets": ["切符", "チケット", "入場券"],
            "household": ["家具", "食器", "タオル", "石鹸", "シャンプー"],
            "transportation": ["車", "自転車", "バイク"],
            "property": ["家", "土地", "マンション", "アパート"]
        }

    elif verb_kanji == '聞く':
        return {
            "audio entertainment": ["音楽", "歌", "ラジオ", "CD", "コンサート"],
            "information": ["話", "ニュース", "説明", "講義", "授業", "発表"],
            "questions": ["質問", "意見", "答え", "返事", "アドバイス"],
            "sounds": ["声", "音", "物音", "足音", "鳥の声"],
            "people": ["先生", "友達", "親", "子供", "医者", "専門家"],
            "stories": ["話", "物語", "昔話", "経験", "思い出"],
            "requests": ["お願い", "頼み", "命令", "注意", "警告"],
            "languages": ["日本語", "英語", "言葉", "単語", "発音"]
        }

    elif verb_kanji == '話す':
        return {
            "languages": ["日本語", "英語", "中国語", "韓国語", "フランス語", "言葉"],
            "topics": ["仕事", "勉強", "趣味", "家族", "将来", "夢", "計画"],
            "stories": ["話", "経験", "思い出", "昔話", "冗談"],
            "people to talk with": ["友達", "先生", "親", "子供", "彼女", "彼", "同僚"],
            "discussions": ["意見", "考え", "問題", "相談", "アドバイス"],
            "information": ["ニュース", "情報", "秘密", "本当", "嘘"],
            "phone": ["電話", "スマホ", "ケータイ"],
            "feelings": ["気持ち", "感想", "不満", "喜び", "悲しみ"]
        }

    elif verb_kanji == '使う':
        return {
            "tools": ["ペン", "鉛筆", "はさみ", "ナイフ", "フォーク", "箸", "スプーン"],
            "electronics": ["パソコン", "電話", "カメラ", "テレビ", "冷蔵庫", "洗濯機"],
            "money": ["お金", "カード", "現金", "小銭", "財布"],
            "transport": ["車", "自転車", "バス", "電車", "エレベーター", "エスカレーター"],
            "resources": ["時間", "力", "頭", "エネルギー", "電気", "水", "ガス"],
            "language": ["日本語", "英語", "言葉", "辞書", "文法"],
            "materials": ["紙", "布", "木", "石", "ガラス", "プラスチック"],
            "facilities": ["トイレ", "お風呂", "台所", "部屋", "教室"]
        }

    elif verb_kanji == '知る':
        return {
            "people": ["人", "友達", "先生", "彼", "彼女", "名前", "家族"],
            "information": ["情報", "ニュース", "答え", "結果", "理由", "原因", "意味"],
            "places": ["場所", "住所", "道", "店", "レストラン", "学校"],
            "facts": ["事実", "真実", "本当", "嘘", "秘密"],
            "knowledge": ["日本語", "英語", "文化", "歴史", "方法", "やり方"],
            "feelings": ["気持ち", "愛", "喜び", "悲しみ", "幸せ"],
            "contact": ["電話番号", "メールアドレス", "連絡先"]
        }

    elif verb_kanji == '入る':
        return {
            "buildings": ["家", "部屋", "店", "レストラン", "ホテル", "病院", "会社"],
            "education": ["学校", "大学", "高校", "小学校", "クラス", "教室"],
            "bathing": ["お風呂", "温泉", "シャワー", "プール"],
            "transportation": ["車", "バス", "電車", "タクシー", "エレベーター"],
            "containers": ["かばん", "ポケット", "財布", "冷蔵庫", "箱"],
            "groups": ["会社", "クラブ", "チーム", "グループ", "組織"],
            "abstract": ["気分", "調子", "習慣", "気持ち"]
        }

    elif verb_kanji == '出る':
        return {
            "leaving places": ["家", "部屋", "学校", "会社", "店", "ホテル", "病院"],
            "appearing": ["太陽", "月", "星", "虹"],
            "publishing": ["本", "雑誌", "新聞", "記事", "レポート"],
            "results": ["結果", "答え", "成績", "点数"],
            "problems": ["問題", "宿題", "質問", "テスト"],
            "bodily": ["声", "涙", "汗", "血", "熱"],
            "events": ["会議", "パーティー", "式", "コンサート", "試合"]
        }

    elif verb_kanji == '教える':
        return {
            "subjects": ["日本語", "英語", "数学", "科学", "歴史", "音楽", "体育"],
            "skills": ["料理", "運転", "泳ぎ方", "使い方", "やり方", "方法"],
            "information": ["道", "住所", "電話番号", "名前", "場所", "時間"],
            "people taught": ["学生", "子供", "生徒", "友達", "後輩"],
            "knowledge": ["文法", "単語", "漢字", "発音", "文化", "マナー"],
            "answers": ["答え", "解決", "コツ", "秘密", "真実"]
        }

    elif verb_kanji == '起きる':
        return {
            "times to wake up": ["朝", "午前", "早く", "遅く", "六時", "七時", "八時"],
            "events that happen": ["事故", "地震", "火事", "問題", "事件", "戦争"],
            "from sleeping": ["ベッド", "布団", "眠り", "夢", "昼寝"],
            "body getting up": ["体", "頭", "身体", "顔"]
        }

    elif verb_kanji == 'いる':
        return {
            "family at home": ["母", "父", "兄", "姉", "弟", "妹", "子供", "赤ちゃん", "祖父", "祖母"],
            "people in places": ["学生", "先生", "友達", "人", "一人", "二人", "三人", "みんな", "誰か"],
            "locations where you stay": ["家", "部屋", "学校", "会社", "公園", "店", "ここ", "そこ", "あそこ"],
            "animals": ["猫", "犬", "鳥", "魚", "動物"],
            "professionals": ["医者", "警官", "おまわりさん", "公務員", "店員", "看護師"],
            "countries and regions": ["日本", "アメリカ", "中国", "国", "外国", "田舎", "都市", "町"]
        }

    elif verb_kanji == 'かかる':
        return {
            "time it takes": ["時間", "一時間", "二時間", "三時間", "分", "日", "週間", "月", "年"],
            "money it costs": ["お金", "円", "ドル", "費用", "料金", "値段"],
            "on the phone": ["電話", "携帯", "スマホ"],
            "medical issues": ["病気", "風邪", "インフルエンザ", "医者"],
            "hanging things": ["絵", "時計", "カレンダー", "鏡", "ポスター"],
            "bridges crossed": ["橋", "道路"],
            "locks and security": ["鍵", "ロック", "セキュリティ"]
        }

    elif verb_kanji == 'なる':
        return {
            "professions you become": ["医者", "先生", "学生", "社長", "大人", "親"],
            "states you reach": ["元気", "病気", "健康", "幸せ", "上手", "下手", "静か", "賑やか"],
            "times that arrive": ["春", "夏", "秋", "冬", "朝", "夜", "明日", "来週"],
            "ages you turn": ["二十歳", "三十歳", "歳", "大人"],
            "weather changes": ["晴れ", "雨", "曇り", "暖かく", "寒く", "暑く", "涼しく"]
        }

    elif verb_kanji == 'わかる':
        return {
            "languages understood": ["日本語", "英語", "中国語", "韓国語", "言葉", "意味", "文法"],
            "answers found": ["答え", "解答", "結果", "理由", "原因", "解決"],
            "directions known": ["道", "場所", "住所", "行き方", "地図"],
            "feelings understood": ["気持ち", "心", "愛", "感情"],
            "knowledge gained": ["方法", "やり方", "使い方", "ルール", "法律"],
            "information learned": ["名前", "電話番号", "時間", "値段", "番号"]
        }

    elif verb_kanji == '乗る':
        return {
            "public transport": ["バス", "電車", "地下鉄", "新幹線", "タクシー", "モノレール"],
            "personal vehicles": ["車", "自転車", "バイク", "スクーター"],
            "air and sea": ["飛行機", "船", "ヨット", "ボート", "フェリー"],
            "animals to ride": ["馬", "象", "らくだ", "ロバ"],
            "building transport": ["エレベーター", "エスカレーター", "リフト"]
        }

    elif verb_kanji == '終わる':
        return {
            "classes ending": ["授業", "学校", "レッスン", "講義", "ゼミ", "クラス"],
            "work finishing": ["仕事", "会議", "プロジェクト", "残業", "バイト"],
            "events concluding": ["パーティー", "コンサート", "試合", "式", "祭り"],
            "time periods ending": ["夏休み", "冬休み", "週末", "一日", "一年", "学期"],
            "media finishing": ["映画", "ドラマ", "番組", "本", "話"]
        }

    elif verb_kanji == '始まる':
        return {
            "classes starting": ["授業", "学校", "レッスン", "講義", "ゼミ", "新学期"],
            "work beginning": ["仕事", "会議", "プロジェクト", "営業"],
            "events commencing": ["パーティー", "コンサート", "試合", "式", "祭り", "オリンピック"],
            "time periods beginning": ["夏休み", "新年", "一日", "朝", "週"],
            "seasons arriving": ["春", "夏", "秋", "冬", "梅雨"],
            "new things": ["新生活", "戦争", "恋", "友情"]
        }

    # Default case - group by semantic similarity
    hint_groups = defaultdict(list)

    # Try to group nouns by their semantic categories
    for noun, english in noun_list:
        # Simple heuristic grouping based on English meanings
        english_lower = english.lower()

        if any(word in english_lower for word in ['time', 'day', 'week', 'month', 'year', 'hour', 'minute']):
            hint_groups["time-related things"].append(noun)
        elif any(word in english_lower for word in ['place', 'location', 'building', 'room', 'house']):
            hint_groups["places and locations"].append(noun)
        elif any(word in english_lower for word in ['person', 'people', 'friend', 'family', 'teacher']):
            hint_groups["people you interact with"].append(noun)
        elif any(word in english_lower for word in ['feel', 'emotion', 'happy', 'sad', 'angry']):
            hint_groups["emotions and feelings"].append(noun)
        elif any(word in english_lower for word in ['food', 'drink', 'eat', 'meal']):
            hint_groups["food and drinks"].append(noun)
        elif any(word in english_lower for word in ['work', 'job', 'business', 'office']):
            hint_groups["work-related things"].append(noun)
        else:
            hint_groups["other things"].append(noun)

    return dict(hint_groups)

def create_refined_hints(input_file: str, output_file: str):
    """Create the refined hints JSON with manual semantic analysis."""

    # Load data
    print("Loading collocation data...")
    data = load_collocations(input_file)

    # Get verbs sorted by noun count
    verb_stats = []
    for word, word_data in data['words'].items():
        if word_data['type'] == 'verb' and 'nouns' in word_data['matches']:
            noun_count = len(word_data['matches']['nouns'])
            verb_stats.append((word, noun_count))

    verb_stats.sort(key=lambda x: x[1], reverse=True)

    print(f"Found {len(verb_stats)} verbs")
    print("\nTop 20 verbs by noun count:")
    for verb, count in verb_stats[:20]:
        print(f"  {verb}: {count} nouns")

    # Process top 20 verbs with manual analysis
    refined_hints = {
        "version": "5.0.0",
        "description": "Manually analyzed verb-specific semantic hints",
        "verbs": {}
    }

    top_20_verbs = [v[0] for v in verb_stats[:20]]

    for verb_kanji in top_20_verbs:
        if verb_kanji not in data['words']:
            continue

        verb_data = data['words'][verb_kanji]
        print(f"\nAnalyzing {verb_kanji} ({verb_data['english']})...")

        # Get semantic hint groups for this verb
        hint_groups = analyze_verb_semantics(verb_data, verb_kanji)

        # Create the hints structure
        verb_hints = {
            "word": verb_kanji,
            "reading": verb_data['reading'],
            "english": verb_data['english'],
            "total_nouns": len(verb_data['matches']['nouns']),
            "hints": []
        }

        # Convert hint groups to hint list with noun assignments
        noun_to_hint = {}
        for hint_text, nouns in hint_groups.items():
            if nouns:  # Only add hints that have nouns
                hint_entry = {
                    "hint": hint_text,
                    "noun_count": len(nouns),
                    "example_nouns": nouns[:5],  # Show first 5 as examples
                    "all_nouns": nouns
                }
                verb_hints["hints"].append(hint_entry)

                # Map each noun to its hint
                for noun in nouns:
                    noun_to_hint[noun] = hint_text

        # Add noun assignments
        verb_hints["noun_assignments"] = noun_to_hint

        # Statistics
        verb_hints["statistics"] = {
            "total_hints": len(verb_hints["hints"]),
            "avg_nouns_per_hint": round(len(verb_data['matches']['nouns']) / len(verb_hints["hints"]), 1) if verb_hints["hints"] else 0,
            "max_nouns_in_hint": max(len(h["all_nouns"]) for h in verb_hints["hints"]) if verb_hints["hints"] else 0,
            "min_nouns_in_hint": min(len(h["all_nouns"]) for h in verb_hints["hints"]) if verb_hints["hints"] else 0
        }

        refined_hints["verbs"][verb_kanji] = verb_hints

    # Save the refined hints
    print(f"\nSaving refined hints to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(refined_hints, f, ensure_ascii=False, indent=2)

    # Print statistics
    print("\n" + "="*60)
    print("HINT CREATION STATISTICS")
    print("="*60)

    for i, verb_kanji in enumerate(top_20_verbs[:5], 1):
        if verb_kanji not in refined_hints["verbs"]:
            continue

        verb_hints = refined_hints["verbs"][verb_kanji]
        print(f"\n{i}. {verb_kanji} ({verb_hints['english']}):")
        print(f"   Total nouns: {verb_hints['total_nouns']}")
        print(f"   Total hints: {verb_hints['statistics']['total_hints']}")
        print(f"   Avg nouns per hint: {verb_hints['statistics']['avg_nouns_per_hint']}")
        print(f"   Hint distribution:")

        for hint in verb_hints["hints"][:5]:  # Show first 5 hints
            print(f"     - \"{hint['hint']}\": {hint['noun_count']} nouns")
            print(f"       Examples: {', '.join(hint['example_nouns'])}")

    # Check for generic hints
    print("\n" + "="*60)
    print("SPECIFICITY CHECK")
    print("="*60)

    generic_terms = ["general", "various", "other", "misc", "common", "things"]
    generic_found = False

    for verb_kanji, verb_hints in refined_hints["verbs"].items():
        for hint in verb_hints["hints"]:
            if any(term in hint["hint"].lower() for term in generic_terms):
                if not generic_found:
                    print("\n⚠️  WARNING: Generic hints found:")
                    generic_found = True
                print(f"  {verb_kanji}: \"{hint['hint']}\"")

    if not generic_found:
        print("\n✓ No generic hints found! All hints are specific and semantic.")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✓ Processed {len(refined_hints['verbs'])} verbs")
    print(f"✓ Created manual semantic hints for each verb")
    print(f"✓ Version: {refined_hints['version']}")
    print(f"✓ Output saved to: {output_file}")

def main():
    """Main execution."""
    input_file = r"C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocations_complete.json"
    output_file = r"C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocation_hints_refined.json"

    # Check input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return

    create_refined_hints(input_file, output_file)
    print("\n✅ Hint creation complete!")

if __name__ == "__main__":
    main()