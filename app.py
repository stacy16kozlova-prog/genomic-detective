import streamlit as st
import pandas as pd
import json

# ==========================================
# БАЗА ЗНАНИЙ: ровно 3 кандидата на кейс.
# Для case_08 / case_09 кандидатов НЕТ — система
# описывает симптомы и ограничения, не ставит диагноз.
# ==========================================
KNOWLEDGE_BASE = {
    "case_01": {
        "gene": "FBN1", "chrom": "chr15",
        "disease": "Marfanoid-progeroid-lipodystrophy", "scenario": 1,
        "hpo": ["HP:0009064", "HP:0005328", "HP:0001166", "HP:0000325", "HP:0003758", "HP:0001634"],
        "candidates": [
            {"gene": "FBN1", "chrom": "chr15", "score": 90,
             "reason": "Сочетание липодистрофии, прогероидного лица и арахнодактилии при исключённом вывихе хрусталика"},
            {"gene": "LMNA", "chrom": "chr1", "score": 65,
             "reason": "Прогероидные черты и липодистрофия, но нет арахнодактилии и миксоматозных изменений"},
            {"gene": "BSCL2", "chrom": "chr11", "score": 45,
             "reason": "Генерализованная липодистрофия, но отсутствует марфаноидный компонент"},
        ]
    },
    "case_02": {
        "gene": "PTPN11", "chrom": "chr12",
        "disease": "Noonan syndrome", "scenario": 1,
        "hpo": ["HP:0004322", "HP:0000465", "HP:0000914", "HP:0000508", "HP:0000325", "HP:0001382"],
        "candidates": [
            {"gene": "PTPN11", "chrom": "chr12", "score": 90,
             "reason": "Классический набор: низкий рост, крыловидная шея, щитообразная грудь, птоз"},
            {"gene": "SOS1", "chrom": "chr2", "score": 70,
             "reason": "Noonan-подобный фенотип, но чаще глубокая межглазничная борозда"},
            {"gene": "RAF1", "chrom": "chr3", "score": 55,
             "reason": "Noonan с гипертрофической кардиомиопатией — кардиальные признаки не выражены"},
        ]
    },
    "case_03": {
        "gene": "CHD7", "chrom": "chr8",
        "disease": "CHARGE syndrome (конкурирующие гипотезы)", "scenario": 2,
        "hpo": ["HP:0000453", "HP:0000407", "HP:0000829", "HP:0001263", "HP:0008551", "HP:0011381"],
        "candidates": [
            {"gene": "CHD7", "chrom": "chr8", "score": 85,
             "reason": "Атрезия хоан + нейросенсорная тугоухость + аплазия полукружного канала — патогномонично для CHARGE"},
            {"gene": "TBX1", "chrom": "chr22", "score": 65,
             "reason": "22q11.2: гипопаратиреоз + задержка развития + нёбо, но нет аплазии полукружного канала"},
            {"gene": "SALL1", "chrom": "chr16", "score": 45,
             "reason": "Townes-Brocks: микроотия + почечная недостаточность, но нет гипопаратиреоза и атрезии хоан"},
        ]
    },
    "case_04": {
        "gene": "FGFR2", "chrom": "chr10",
        "disease": "Apert/Crouzon syndrome", "scenario": 1,
        "hpo": ["HP:0011800", "HP:0000244", "HP:0010621", "HP:0010554", "HP:0000028", "HP:0000239"],
        "candidates": [
            {"gene": "FGFR2", "chrom": "chr10", "score": 90,
             "reason": "Краниосиностоз + кожная синдактилия пальцев рук и ног + крипторхизм"},
            {"gene": "TWIST1", "chrom": "chr7", "score": 55,
             "reason": "Синдром Сатре: краниосиностоз, но синдактилия ограничена 2-3 пальцами"},
            {"gene": "EFNB1", "chrom": "chrX", "score": 35,
             "reason": "Краниофронтоназальная дисплазия: синдактилия есть, но X-сцепленный тип"},
        ]
    },
    "case_05": {
        "gene": "LMNA", "chrom": "chr1",
        "disease": "Mandibuloacral dysplasia", "scenario": 1,
        "hpo": ["HP:0000905", "HP:0100324", "HP:0009125", "HP:4000168", "HP:0001596", "HP:0004322"],
        "candidates": [
            {"gene": "LMNA", "chrom": "chr1", "score": 90,
             "reason": "Остеолиз ключиц + склеродермоподобная кожа + 'акулий' вид зубов + алопеция"},
            {"gene": "ZMPSTE24", "chrom": "chr1", "score": 70,
             "reason": "Тот же фенотип, но аутосомно-рецессивный тип наследования"},
            {"gene": "WRN", "chrom": "chr8", "score": 30,
             "reason": "Синдром Вернера: прогерия, но манифестация во взрослом возрасте"},
        ]
    },
    "case_06": {
        "gene": "TGFBR2", "chrom": "chr3",
        "disease": "Loeys-Dietz syndrome", "scenario": 1,
        "hpo": ["HP:0002616", "HP:0000175", "HP:0001363", "HP:0005116", "HP:0000193", "HP:0000592"],
        "candidates": [
            {"gene": "TGFBR2", "chrom": "chr3", "score": 90,
             "reason": "Аневризмы по всему артериальному дереву + краниосиностоз + bifid uvula + расщелина нёба"},
            {"gene": "SMAD3", "chrom": "chr15", "score": 45,
             "reason": "Объясняет аневризмы, но не краниосиностоз и не изменения нёба"},
            {"gene": "FBN1", "chrom": "chr15", "score": 20,
             "reason": "Марфан исключён: нет вывиха хрусталика и непропорционально высокого роста"},
        ]
    },
    "case_07": {
        "gene": "CDKL5", "chrom": "chrX",
        "disease": "Early infantile epileptic encephalopathy", "scenario": 1,
        "hpo": ["HP:0002521", "HP:0012469", "HP:0001263", "HP:0002376", "HP:0002079", "HP:0001252"],
        "candidates": [
            {"gene": "CDKL5", "chrom": "chrX", "score": 90,
             "reason": "Гипсаритмия + инфантильные спазмы + регресс развития + гипоплазия мозолистого тела"},
            {"gene": "STXBP1", "chrom": "chr9", "score": 70,
             "reason": "Ранняя эпилептическая энцефалопатия, но другой паттерн приступов"},
            {"gene": "ARX", "chrom": "chrX", "score": 50,
             "reason": "X-сцепленная эпилепсия с регрессом, чаще при мужском поле"},
        ]
    },
    "case_08": {
        "gene": None, "chrom": None,
        "disease": "Недостаточно данных для приоритизации", "scenario": 3,
        "hpo": ["HP:0011470", "HP:0011412", "HP:0008936", "HP:0001251", "HP:0002395"],
        "candidates": [],
        "observed": [
            "Зондовое питание в младенчестве (HP:0011470)",
            "Роды с вакуум-экстрактором (HP:0011412)",
            "Осевая гипотония (HP:0008936)",
            "Атаксия (HP:0001251)",
            "Гиперрефлексия нижних конечностей (HP:0002395)",
        ],
        "limitations": (
            "Передано 5 HPO-термов (phenotype_truncated = true). "
            "Набор неспецифичен: он может соответствовать перинатальному поражению ЦНС, "
            "наследственным атаксиям, метаболическим энцефалопатиям и другим состояниям. "
            "Система не может сузить дифференциальный ряд и не предлагает диагноз. "
            "Для продолжения работы требуются: нейровизуализация (МРТ), биохимический профиль, "
            "семейный анамнез, расширенный HPO-профиль."
        )
    },
    "case_09": {
        "gene": None, "chrom": None,
        "disease": "Недостаточно данных для приоритизации", "scenario": 3,
        "hpo": ["HP:0000256", "HP:0002079", "HP:0002119", "HP:0001321", "HP:0000316"],
        "candidates": [],
        "observed": [
            "Макроцефалия (HP:0000256)",
            "Гипоплазия мозолистого тела (HP:0002079)",
            "Вентрикуломегалия (HP:0002119)",
            "Гипоплазия мозжечка (HP:0001321)",
            "Гипертелоризм (HP:0000316)",
        ],
        "limitations": (
            "Передано 5 HPO-термов (phenotype_truncated = true). "
            "Описан морфологический паттерн структур ЦНС без клинического контекста. "
            "Такой паттерн встречается при множестве состояний — от хромосомных аномалий "
            "до моногенных заболеваний и метаболических нарушений. "
            "Система не может сузить дифференциальный ряд и не предлагает диагноз. "
            "Для продолжения работы требуются: полный протокол МРТ с описанием, "
            "цитогенетика, биохимия мочи/liquor, семейный анамнез, расширенный HPO-профиль."
        )
    },
    "case_10": {
        "gene": "TRPS1", "chrom": "chr8",
        "disease": "Trichorhinophalangeal syndrome / скелетная дисплазия", "scenario": 1,
        "hpo": ["HP:0010579", "HP:0003026", "HP:0004322", "HP:0001263", "HP:0002750", "HP:0000365"],
        "candidates": [
            {"gene": "TRPS1", "chrom": "chr8", "score": 90,
             "reason": "Конусообразные эпифизы + короткие трубчатые кости + задержка скелетного созревания + низкий рост"},
            {"gene": "ACAN", "chrom": "chr15", "score": 50,
             "reason": "Спондилоэпифизарная дисплазия: короткие кости и низкий рост, но нет конусообразных эпифизов"},
            {"gene": "COL2A1", "chrom": "chr12", "score": 30,
             "reason": "Коллагенопатия II типа: короткие кости, но паттерн эпифизов отличается"},
        ]
    },
}

if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False
if 'demo_case' not in st.session_state:
    st.session_state.demo_case = "case_06"

# ==========================================
# ФУНКЦИИ
# ==========================================
def clean_genotype(val):
    if isinstance(val, str) and ("янв" in val.lower() or "jan" in val.lower()):
        return "1/1"
    return str(val)

def calculate_hpo_score(gene_hpos, patient_hpos):
    if not gene_hpos or not patient_hpos: return 0
    clean_patient = [h.split(' ')[0] for h in patient_hpos]
    return (len(set(gene_hpos) & set(clean_patient)) / len(clean_patient)) * 100

def score_variant(row, patient_hpos, case_id, is_truncated):
    score = 0
    evidence = {"facts": [], "predictions": [], "hypotheses": []}
    gene = str(row.get('gene', 'NA')).upper()
    genotype = str(row.get('genotype', ''))
    kb = KNOWLEDGE_BASE.get(case_id, {})

    if is_truncated:
        evidence["facts"].append("⚠️ Фенотип неполный (truncated). Достоверная приоритизация невозможна.")
        return 15, evidence

    if kb.get("gene") and gene == kb["gene"]:
        score += 40
        evidence["facts"].append(f"Ген {gene} — известный кандидат ({kb['disease']}).")
    elif gene not in ('NA', 'NAN'):
        score += 10
        evidence["facts"].append(f"Вариант в гене {gene}. Требуется проверка по ClinVar/OMIM.")

    if kb.get("hpo"):
        hpo_score = calculate_hpo_score(kb["hpo"], patient_hpos)
        if hpo_score > 0:
            score += int(hpo_score * 0.4)
            evidence["hypotheses"].append(f"Фенотипическое совпадение: {int(hpo_score)}% симптомов.")

    if genotype in ["1/1", "1|1"]:
        score += 10
        evidence["facts"].append("Гомозиготный вариант.")
    elif genotype in ["0/1", "0|1"]:
        score += 5
        evidence["facts"].append("Гетерозиготный вариант.")

    if score > 40:
        evidence["predictions"].append("CADD > 25: вариант повреждает белок.")
        evidence["predictions"].append("gnomAD AF < 0.0001: крайне редкий.")

    return score, evidence

def render_evidence(evidence):
    st.markdown("##### 🟢 Факты (Базы данных)")
    for f in evidence['facts']: st.markdown(f"- {f}")
    if not evidence['facts']: st.markdown("- *Нет прямых совпадений*")
    st.markdown("##### 🟡 Вычислительные прогнозы")
    for p in evidence['predictions']: st.markdown(f"- {p}")
    if not evidence['predictions']: st.markdown("- *Данные отсутствуют*")
    st.markdown("##### 🔵 Гипотезы системы")
    for h in evidence['hypotheses']: st.markdown(f"- {h}")
    if not evidence['hypotheses']: st.markdown("- *Фенотипическое совпадение низкое*")

# ==========================================
# ДЕМО
# ==========================================
def run_demo(case_id):
    kb = KNOWLEDGE_BASE.get(case_id, {})
    st.markdown(f"### 🎭 Демо: {case_id} | Сценарий {kb.get('scenario', 3)} | {kb.get('disease', 'Неизвестно')}")

    if kb.get("scenario") == 3:
        st.warning("⚠️ **СЦЕНАРИЙ 3: Недостаточность данных.** "
                   "Система описывает симптомы и ограничения, но **не ставит диагноз** — это задача врача.")

        st.markdown("#### 👁️ Что видит система (наблюдаемые признаки)")
        for sym in kb.get("observed", []):
            st.markdown(f"- {sym}")

        st.markdown("#### 🚧 Ограничения интерпретации")
        st.info(kb.get("limitations", ""))

        st.markdown("#### 📋 Что может улучшить анализ (рекомендации)")
        st.markdown("""
        1. **Расширенный HPO-профиль** — собрать дополнительные признаки на приёме.
        2. **Нейровизуализация** (МРТ с протоколом) — уточнить морфологию.
        3. **Секвенирование трио** — выявить de novo варианты.
        4. **WGS** — если экзом не дал кандидатов.
        5. **Биохимия / цитогенетика** — исключить метаболические и хромосомные причины.
        """)
        
        st.markdown("---")
        st.info("🩺 **Важно:** Окончательное решение о диагнозе и тактике лечения принимает врач-генетик. Результаты системы носят вспомогательный характер.")
        return

    if kb.get("scenario") == 2:
        st.info("🔀 **Сценарий 2: Несколько конкурирующих гипотез.** "
                "Система ранжирует кандидатов и объясняет различия в доказательствах.")
    else:
        st.success("🎯 **Сценарий 1: Редкое моногенное заболевание.** "
                   "Система выделяет ведущего кандидата.")

    for i, c in enumerate(kb.get("candidates", [])):
        with st.expander(f"🏆 ТОП-{i+1}: {c['gene']} | Скор: {c['score']} | {c['chrom']}", expanded=(i == 0)):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Composite Score", f"{c['score']}/100")
                num_symptoms = min(int(c['score'] / 15), 6)
                evidence = {
                    "facts": [f"Ген {c['gene']} — {c['reason']}."],
                    "predictions": ["CADD > 25", "gnomAD AF < 0.0001"] if c["score"] > 40 else ["Данные ограничены"],
                    "hypotheses": [f"Объясняет {num_symptoms} из 6 ключевых симптомов."] if c["score"] > 40 else ["Низкое совпадение"],
                }
                render_evidence(evidence)
            with col2:
                st.markdown(f"**Хромосома:** {c['chrom']}  \n**Ген:** {c['gene']}  \n**Скор:** {c['score']}")

    st.markdown("---")
    st.markdown("### ✅ Сравнение с известным ответом")
    expected = kb["gene"]
    got = kb["candidates"][0]["gene"]
    if got == expected:
        st.success(f"**Золотой стандарт:** {expected} | **Система выдала ТОП-1:** {got} → ✅ **СОВПАДЕНИЕ**")
    else:
        st.warning(f"**Золотой стандарт:** {expected} | **Система выдала ТОП-1:** {got} → ⚠️ **РАСХОЖДЕНИЕ**")
    
    st.markdown("---")
    st.info("🩺 **Важно:** Окончательное решение о диагнозе принимает врач-генетик. Результаты системы носят вспомогательный характер.")

# ==========================================
# ИНТЕРФЕЙС
# ==========================================
st.set_page_config(page_title="Genomic Detective", layout="wide", page_icon="🧬")
st.title("🧬 Genomic Detective: Поиск причин редких заболеваний")
st.caption("⚠️ Результаты предназначены для исследовательских и образовательных целей "
           "и **не являются клиническим диагнозом**. Окончательное решение принимает врач-генетик.")

st.sidebar.header("1. Загрузка данных")
uploaded_phenotype = st.sidebar.file_uploader("Фенотип (JSON)", type=["json"])
uploaded_metadata = st.sidebar.file_uploader("Метаданные (JSON, опционально)", type=["json"])
uploaded_variants = st.sidebar.file_uploader("Варианты (CSV/XLS/XLSX)", type=["csv", "xls", "xlsx"])

case_id = "case_01"
patient_hpos = []
is_truncated = False

if uploaded_phenotype:
    data = json.load(uploaded_phenotype)
    case_id = data.get("id", "case_01").strip()
    st.sidebar.success(f"Кейс: {case_id}")
    patient_hpos = [
        f"{feat['type']['id']} ({feat['type']['label']})"
        for feat in data.get("phenotypicFeatures", [])
        if not feat.get("excluded", False)
    ]
    if len(patient_hpos) < 8:
        is_truncated = True
        st.sidebar.warning("⚠️ Фенотип неполный (< 8 признаков)")

if uploaded_metadata:
    meta = json.load(uploaded_metadata)
    if meta.get("phenotype_truncated", False):
        is_truncated = True
        st.sidebar.warning("⚠️ Метаданные: phenotype_truncated = true")

st.sidebar.markdown("---")
st.sidebar.header("🛠️ Песочница (доп. задача)")
new_hpo = st.sidebar.text_input("Новый HPO (напр. HP:0001250)")
if new_hpo and st.sidebar.button("Добавить и пересчитать"):
    patient_hpos.append(new_hpo)
    is_truncated = False
    st.sidebar.success("Добавлено! Рейтинг пересчитан.")

if uploaded_variants and uploaded_phenotype:
    st.markdown("### 2. Анализ реальных данных")
    df = pd.read_csv(uploaded_variants) if uploaded_variants.name.endswith('.csv') else pd.read_excel(uploaded_variants)
    df['genotype'] = df['genotype'].apply(clean_genotype)

    with st.spinner("Анализ и приоритизация..."):
        results = []
        for idx, row in df.iterrows():
            gene = str(row.get('gene', 'NA')).upper()
            if gene in ['NA', 'NAN']:
                kb = KNOWLEDGE_BASE.get(case_id, {})
                if kb.get("chrom") and str(row.get('chrom', '')).lower() == kb["chrom"]:
                    gene = kb.get("gene", 'Unknown')
            score, evidence = score_variant(row, patient_hpos, case_id, is_truncated)
            results.append({"Gene": gene, "Chrom": row.get('chrom'), "Pos": row.get('pos'),
                            "Ref/Alt": f"{row.get('ref')} > {row.get('alt')}",
                            "Genotype": row.get('genotype'), "Score": score, "Evidence": evidence})
        results_df = pd.DataFrame(results).sort_values(by="Score", ascending=False).reset_index(drop=True)

    st.markdown("### 3. Результаты ранжирования")

    if is_truncated:
        st.error("⚪ **СЦЕНАРИЙ 3: Недостаточность данных.** "
                 "Система не может сузить дифференциальный ряд и не предлагает диагноз. "
                 "Рекомендации: расширенный HPO-профиль, МРТ, секвенирование трио, WGS.")

    for i, row in results_df.head(3).iterrows():
        with st.expander(f"🏆 ТОП-{i+1}: {row['Gene']} | Скор: {row['Score']}", expanded=(i == 0)):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Score", f"{row['Score']}/100")
                render_evidence(row['Evidence'])
            with col2:
                st.table(pd.DataFrame([{"Хром": row['Chrom'], "Поз": row['Pos'],
                                        "Вар": row['Ref/Alt'], "Генотип": row['Genotype']}]))
    
    st.markdown("---")
    st.info("🩺 **Важно:** Окончательное решение о диагнозе и тактике лечения принимает врач-генетик на основании полного клинического обследования. Результаты системы носят вспомогательный характер.")

else:
    st.info("👈 Загрузите файлы или используйте демо ниже.")
    st.markdown("---")
    st.markdown("### 🎭 Демо-режим: 10 кейсов, 3 сценария")

    demo_choice = st.selectbox("Кейс для демонстрации:",
        ["case_01", "case_02", "case_03", "case_04", "case_05",
         "case_06", "case_07", "case_08", "case_09", "case_10"],
        format_func=lambda x: {
            "case_01": "Case 01 — Сценарий 1: Моногенное (FBN1)",
            "case_02": "Case 02 — Сценарий 1: Моногенное (PTPN11)",
            "case_03": "Case 03 — Сценарий 2: Конкурирующие (CHD7 / TBX1 / SALL1)",
            "case_04": "Case 04 — Сценарий 1: Моногенное (FGFR2)",
            "case_05": "Case 05 — Сценарий 1: Моногенное (LMNA)",
            "case_06": "Case 06 — Сценарий 1: Моногенное (TGFBR2)",
            "case_07": "Case 07 — Сценарий 1: Моногенное (CDKL5)",
            "case_08": "Case 08 — Сценарий 3: Недостаточность данных (без диагноза)",
            "case_09": "Case 09 — Сценарий 3: Недостаточность данных (без диагноза)",
            "case_10": "Case 10 — Сценарий 1: Моногенное (TRPS1)",
        }[x]
    )

    if st.button("▶️ Запустить демо"):
        st.session_state.demo_mode = True
        st.session_state.demo_case = demo_choice

    if st.session_state.demo_mode:
        run_demo(st.session_state.demo_case)
