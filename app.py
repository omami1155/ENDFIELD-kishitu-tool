from dataclasses import dataclass
from itertools import combinations
from typing import Dict, FrozenSet, Iterable, Literal, Tuple
from collections import defaultdict
import json

import streamlit as st

固定スロット = Literal["付加効果", "スキル効果"]

基礎効果ID_to_名前: Dict[int, str] = {
    1: "敏捷UP",
    2: "筋力UP",
    3: "意志UP",
    4: "知性UP",
    5: "メイン能力UP",
}

付加効果ID_to_名前: Dict[int, str] = {
    1: "攻撃力UP",
    2: "物理ダメージUP",
    3: "灼熱ダメージUP",
    4: "電磁ダメージUP",
    5: "寒冷ダメージUP",
    6: "自然ダメージUP",
    7: "会心率UP",
    8: "必殺技効率UP",
    9: "アーツ強度UP",
    10: "アーツダメージUP",
    11: "回復効率UP",
    12: "HPアップ",
}

スキル効果ID_to_名前: Dict[int, str] = {
    1: "強攻",
    2: "圧制",
    3: "追襲",
    4: "破砕",
    5: "巧技",
    6: "噴発",
    7: "流回",
    8: "効率",
    9: "昂揚",
    10: "付術",
    11: "治癒",
    12: "切骨",
    13: "残虐",
    14: "夜幕",
}

基礎効果名_to_ID: Dict[str, int] = {v: k for k, v in 基礎効果ID_to_名前.items()}
付加効果名_to_ID: Dict[str, int] = {v: k for k, v in 付加効果ID_to_名前.items()}
スキル効果名_to_ID: Dict[str, int] = {v: k for k, v in スキル効果ID_to_名前.items()}

def 表示_基礎(i: int) -> str:
    return 基礎効果ID_to_名前.get(i, f"未定義({i})")

def 表示_付加(i: int) -> str:
    return 付加効果ID_to_名前.get(i, f"未定義({i})")

def 表示_スキル(i: int) -> str:
    return スキル効果ID_to_名前.get(i, f"未定義({i})")

@dataclass(frozen=True)
class 武器:
    name: str
    基礎効果: int
    付加効果: int
    スキル効果: int

@dataclass(frozen=True)
class ダンジョン:
    name: str
    出る基礎効果: FrozenSet[int]
    出る付加効果: FrozenSet[int]
    出るスキル効果: FrozenSet[int]

@dataclass(frozen=True)
class 絞り込み:
    dungeon: str
    基礎効果候補: FrozenSet[int]
    固定する枠: 固定スロット
    固定する効果: int

@dataclass(frozen=True)
class 周回プラン:
    dungeon: str
    絞り: 絞り込み
    同時に狙える武器: Tuple[武器, ...]
    スコア: Tuple[int, int]

DUNGEONS: dict[str, ダンジョン] = {
    "中枢エリア": ダンジョン(
        name="中枢エリア",
        出る基礎効果=frozenset({1, 2, 3, 4, 5}),
        出る付加効果=frozenset({1, 3, 4, 5, 6, 8, 9, 10}),
        出るスキル効果=frozenset({1, 2, 3, 4, 5, 6, 7, 8}),
    ),
    "原石研究パーク": ダンジョン(
        name="原石研究パーク",
        出る基礎効果=frozenset({1, 2, 3, 4, 5}),
        出る付加効果=frozenset({1, 2, 4, 5, 6, 7, 8, 10}),
        出るスキル効果=frozenset({2, 3, 5, 8, 9, 10, 11, 12}),
    ),
    "鉱山エリア": ダンジョン(
        name="鉱山エリア",
        出る基礎効果=frozenset({1, 2, 3, 4, 5}),
        出る付加効果=frozenset({2, 3, 5, 6, 7, 9, 11, 12}),
        出るスキル効果=frozenset({1, 2, 5, 6, 8, 10, 13, 14}),
    ),
    "エネルギー高地": ダンジョン(
        name="エネルギー高地",
        出る基礎効果=frozenset({1, 2, 3, 4, 5}),
        出る付加効果=frozenset({1, 2, 3, 6, 7, 9, 11, 12}),
        出るスキル効果=frozenset({3, 4, 7, 9, 10, 11, 12, 13}),
    ),
    "武陵城": ダンジョン(
        name="武陵城",
        出る基礎効果=frozenset({1, 2, 3, 4, 5}),
        出る付加効果=frozenset({1, 4, 5, 7, 8, 10, 11, 12}),
        出るスキル効果=frozenset({1, 4, 6, 7, 11, 12, 13, 14}),
    ),
}

WEAPONS: list[武器] = [
    武器("片手剣-鋼鉄余音", 1, 2, 5),
    武器("片手剣-堅城鋳造者", 4, 8, 9),
    武器("片手剣-フィンチェイサー3.0", 2, 5, 2),
    武器("片手剣-十二問", 1, 1, 10),
    武器("片手剣-O.B.J.軽刃", 1, 1, 7),
    武器("片手剣-仰止", 1, 2, 14),
    武器("片手剣-大願", 1, 1, 10),
    武器("片手剣-不知帰", 3, 1, 7),
    武器("片手剣-フレイムフォージ", 4, 1, 14),
    武器("片手剣-ダークトーチ", 4, 3, 10),
    武器("片手剣-フーヤオ", 5, 7, 14),
    武器("片手剣-テルミット·カッター", 3, 1, 7),
    武器("片手剣-輝かしき名声", 5, 2, 13),
    武器("片手剣-白夜新星", 5, 9, 10),
    武器("大剣-探龍", 2, 8, 6),
    武器("大剣-千古恒常", 2, 9, 13),
    武器("大剣-最期の声", 2, 12, 11),
    武器("大剣-O.B.J.重責", 2, 12, 8),
    武器("大剣-大雷斑", 2, 12, 11),
    武器("大剣-クラヴェンガー", 2, 1, 6),
    武器("大剣-鑑", 5, 1, 2),
    武器("大剣-昔日の逸品", 3, 12, 8),
    武器("大剣-破砕君主", 2, 7, 4),
    武器("長柄武器-正義嵌合", 2, 8, 13),
    武器("長柄武器-O.B.J.鋭矛", 3, 2, 10),
    武器("長柄武器-求心の槍", 3, 4, 2),
    武器("長柄武器-負山", 1, 2, 8),
    武器("長柄武器-勇猛", 1, 2, 5),
    武器("長柄武器-J.E.T.", 5, 1, 2),
    武器("拳銃-作品:衆生", 1, 10, 10),
    武器("拳銃-O.B.J.迅速", 1, 8, 6),
    武器("拳銃-合理的決別", 2, 3, 3),
    武器("拳銃-芸術の独裁者", 4, 7, 12),
    武器("拳銃-ナビゲーター", 4, 5, 10),
    武器("拳銃-楔", 5, 7, 10),
    武器("拳銃-同類共食", 5, 10, 10),
    武器("アーツユニット-弔いの詩", 4, 1, 14),
    武器("アーツユニット-術無", 3, 8, 9),
    武器("アーツユニット-荒野迷走", 4, 4, 10),
    武器("アーツユニット-布教の自由", 3, 11, 11),
    武器("アーツユニット-O.B.J.術識", 4, 9, 3),
    武器("アーツユニット-使命必達", 3, 8, 3),
    武器("アーツユニット-蒼星の囁き", 4, 11, 10),
    武器("アーツユニット-作品:蝕跡", 3, 6, 2),
    武器("アーツユニット-破壊ユニット", 5, 9, 6),
    武器("アーツユニット-遺忘", 4, 10, 14),
    武器("アーツユニット-騎士精神", 3, 12, 11),
]

def 正解基質がダンジョンで出る(w: 武器, d: ダンジョン) -> bool:
    return (
        (w.基礎効果 in d.出る基礎効果) and
        (w.付加効果 in d.出る付加効果) and
        (w.スキル効果 in d.出るスキル効果)
    )

def 絞り込みで正解が拾える(w: 武器, d: ダンジョン, f: 絞り込み) -> bool:
    if f.dungeon != d.name:
        return False
    if not 正解基質がダンジョンで出る(w, d):
        return False
    if w.基礎効果 not in f.基礎効果候補:
        return False
    if f.固定する枠 == "付加効果":
        return w.付加効果 == f.固定する効果
    return w.スキル効果 == f.固定する効果

def 武器名から周回プランを提案(
    weapon_name: str,
    weapons: Iterable[武器],
    dungeons: dict[str, ダンジョン],
    top_n: int = 5,
) -> list[周回プラン]:
    target = next((w for w in weapons if w.name == weapon_name), None)
    if target is None:
        return []

    plans: list[周回プラン] = []

    for d in dungeons.values():
        if not 正解基質がダンジョンで出る(target, d):
            continue

        pool = [w for w in weapons if 正解基質がダンジョンで出る(w, d)]

        for fixed_slot in ("付加効果", "スキル効果"):
            fixed_value = target.付加効果 if fixed_slot == "付加効果" else target.スキル効果

            if fixed_slot == "付加効果" and fixed_value not in d.出る付加効果:
                continue
            if fixed_slot == "スキル効果" and fixed_value not in d.出るスキル効果:
                continue

            same_fixed = [
                w for w in pool
                if (w.付加効果 == fixed_value if fixed_slot == "付加効果" else w.スキル効果 == fixed_value)
            ]
            possible_bases = sorted({w.基礎効果 for w in same_fixed})

            for k in (1, 2, 3):
                for combo in combinations(possible_bases, k):
                    if target.基礎効果 not in combo:
                        continue

                    f = 絞り込み(
                        dungeon=d.name,
                        基礎効果候補=frozenset(combo),
                        固定する枠=fixed_slot,
                        固定する効果=fixed_value,
                    )

                    matched = tuple(w for w in pool if 絞り込みで正解が拾える(w, d, f))
                    if target not in matched:
                        continue

                    score = (len(matched), -len(f.基礎効果候補))
                    plans.append(周回プラン(
                        dungeon=d.name,
                        絞り=f,
                        同時に狙える武器=matched,
                        スコア=score,
                    ))

    plans.sort(key=lambda x: (-x.スコア[0], x.dungeon, x.スコア[1], x.絞り.固定する枠, x.絞り.固定する効果))
    return plans[:top_n]

def 逆引き_基質に一致する武器(基礎: int, 付加: int, スキル: int, weapons: Iterable[武器]) -> list[武器]:
    out: list[武器] = []
    for w in weapons:
        if w.基礎効果 == 基礎 and w.付加効果 == 付加 and w.スキル効果 == スキル:
            out.append(w)
    out.sort(key=lambda x: x.name)
    return out

def 武器種と武器名に分解(name: str) -> Tuple[str, str]:
    t, n = name.split("-", 1)
    return t, n

def フィルタ済み武器(weapons: Iterable[武器], 除外_未所持: bool, 除外_達成済: bool) -> list[武器]:
    out: list[武器] = []
    for w in weapons:
        if 除外_未所持 and not st.session_state["owned"].get(w.name, False):
            continue
        if 除外_達成済 and st.session_state["done"].get(w.name, False):
            continue
        out.append(w)
    return out

st.set_page_config(page_title="基質周回最適化ツール", layout="wide")
st.title("基質周回最適化ツール")

if "owned" not in st.session_state:
    st.session_state["owned"] = {w.name: False for w in WEAPONS}
if "done" not in st.session_state:
    st.session_state["done"] = {w.name: False for w in WEAPONS}

def 状態をJSONにする() -> str:
    data = {
        "owned": st.session_state["owned"],
        "done": st.session_state["done"],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)

def JSONから状態を復元する(json_text: str) -> None:
    data = json.loads(json_text)

    owned_in = data.get("owned", {})
    done_in = data.get("done", {})

    for w in WEAPONS:
        st.session_state["owned"][w.name] = bool(owned_in.get(w.name, False))
        st.session_state["done"][w.name] = bool(done_in.get(w.name, False))

if "plans_result" not in st.session_state:
    st.session_state["plans_result"] = None
if "plans_weapon" not in st.session_state:
    st.session_state["plans_weapon"] = None
if "reverse_result" not in st.session_state:
    st.session_state["reverse_result"] = None
if "reverse_key" not in st.session_state:
    st.session_state["reverse_key"] = None

st.sidebar.header("フィルタ")
除外_未所持 = st.sidebar.checkbox("未所持の武器を除外", value=True)
除外_達成済 = st.sidebar.checkbox("正解基質を獲得済みの武器を除外", value=True)

st.sidebar.subheader("保存 / 復元")

json_text = 状態をJSONにする()
st.sidebar.download_button(
    label="状態を保存（JSON）",
    data=json_text,
    file_name="kisitu_state.json",
    mime="application/json",
)

up = st.sidebar.file_uploader("状態を読み込み（JSON）", type=["json"])
if up is not None:
    try:
        JSONから状態を復元する(up.read().decode("utf-8"))
        st.sidebar.success("復元しました。")
    except Exception as e:
        st.sidebar.error(f"読み込みに失敗しました: {e}")

if st.sidebar.button("状態を初期化（全未所持/未達成）"):
    st.session_state["owned"] = {w.name: False for w in WEAPONS}
    st.session_state["done"] = {w.name: False for w in WEAPONS}
    st.sidebar.success("初期化しました。")
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("所持 / 達成の編集")

武器種一覧_sidebar = sorted({武器種と武器名に分解(w.name)[0] for w in WEAPONS})
編集_武器種 = st.sidebar.selectbox("武器種", 武器種一覧_sidebar, key="edit_type")

編集対象 = sorted([w.name for w in WEAPONS if 武器種と武器名に分解(w.name)[0] == 編集_武器種])

for name in 編集対象:
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        st.session_state["owned"][name] = st.checkbox(name, value=st.session_state["owned"].get(name, False), key=f"owned_{name}")
    with col2:
        done_val = st.checkbox("達成", value=st.session_state["done"].get(name, False), key=f"done_{name}")
        st.session_state["done"][name] = done_val
        if done_val:
            st.session_state["owned"][name] = True
            st.session_state[f"owned_{name}"] = True

tab1, tab2 = st.tabs(["周回プラン", "基質逆引き"])

with tab1:
    武器種ごと = defaultdict(list)
    for w in WEAPONS:
        t, _ = 武器種と武器名に分解(w.name)
        武器種ごと[t].append(w.name)

    武器種一覧 = sorted(武器種ごと.keys())
    武器種 = st.selectbox("武器種", 武器種一覧, key="weapon_type")

    candidates = []
    for name in sorted(武器種ごと[武器種]):
        if 除外_未所持 and not st.session_state["owned"].get(name, False):
            continue
        if 除外_達成済 and st.session_state["done"].get(name, False):
            continue
        candidates.append(name)

    if not candidates:
        st.warning("この条件だと選べる武器がありません（サイドバーで所持/達成を調整してください）。")
    else:
        武器名 = st.selectbox("武器名", candidates, key="weapon_name")

        表示件数 = st.slider("表示件数", min_value=1, max_value=30, value=5, step=1, key="topn")

        if st.button("検索", type="primary", key="search_btn"):
            wf = フィルタ済み武器(WEAPONS, 除外_未所持, 除外_達成済)
            plans = 武器名から周回プランを提案(武器名, wf, DUNGEONS, top_n=表示件数)
            st.session_state["plans_result"] = plans
            st.session_state["plans_weapon"] = 武器名

    plans = st.session_state.get("plans_result")
    target_name = st.session_state.get("plans_weapon")

    if plans is not None and target_name is not None:
        if not plans:
            st.warning("プランが見つかりませんでした。")
        else:
            st.subheader(f"検索武器: {target_name}")
            for pl in plans:
                base_list = " / ".join(表示_基礎(i) for i in sorted(pl.絞り.基礎効果候補))
                fixed_value_str = 表示_付加(pl.絞り.固定する効果) if pl.絞り.固定する枠 == "付加効果" else 表示_スキル(pl.絞り.固定する効果)
                others = [w.name for w in pl.同時に狙える武器 if w.name != target_name]

                st.markdown(f"### ■ {pl.dungeon}")
                st.write(f"基礎効果候補: {base_list}")
                st.write(f"{pl.絞り.固定する枠}固定: {fixed_value_str}")
                if others:
                    st.write("一緒に狙える武器: " + ", ".join(others))
                else:
                    st.write("一緒に狙える武器はありません")

with tab2:
    基礎名 = st.selectbox("基礎効果", sorted(基礎効果名_to_ID.keys()), key="rev_base")
    付加名 = st.selectbox("付加効果", sorted(付加効果名_to_ID.keys()), key="rev_add")
    スキル名 = st.selectbox("スキル効果", sorted(スキル効果名_to_ID.keys()), key="rev_skill")

    if st.button("逆引き検索", type="primary", key="rev_btn"):
        b = 基礎効果名_to_ID[基礎名]
        a = 付加効果名_to_ID[付加名]
        s = スキル効果名_to_ID[スキル名]

        wf = フィルタ済み武器(WEAPONS, 除外_未所持, 除外_達成済)
        ws = 逆引き_基質に一致する武器(b, a, s, wf)

        st.session_state["reverse_result"] = ws
        st.session_state["reverse_key"] = (基礎名, 付加名, スキル名)

    ws = st.session_state.get("reverse_result")
    k = st.session_state.get("reverse_key")

    if ws is not None and k is not None:
        基礎名2, 付加名2, スキル名2 = k
        st.subheader(f"選択基質: {基礎名2} / {付加名2} / {スキル名2}")

        if not ws:
            st.warning("一致する武器はありません。")
        else:
            grp: dict[str, list[str]] = defaultdict(list)
            for w in ws:
                t, n = 武器種と武器名に分解(w.name)
                grp[t].append(n)

            for t in sorted(grp.keys()):
                st.markdown(f"### ■ {t}")
                for n in sorted(grp[t]):
                    st.write(f"- {t}-{n}")
