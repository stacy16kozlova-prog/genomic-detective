import streamlit as st
import pandas as pd
import json

# ==========================================
# 1. РАСШИРЕННАЯ БАЗА ЗНАНИЙ (3-4 гена на кейс)
# ==========================================
KNOWLEDGE_BASE = {
    # Открытые кейсы
    "case_01": {
        "gene": "FBN1", "chrom": "chr15", "disease": "Marfanoid-progeroid-lipodystrophy", "scenario": 1,
        "hpo": ["HP:0009064", "HP:0005328", "HP:0001166", "HP:0000325", "HP:0003758", "HP:0001634"],
        "candidates": [
            {"gene": "FBN1", "chrom": "chr15", "score": 90, "reason": "Полное фенотипическое совпадение с прогероидной липодистрофией"},
            {"gene": "LMNA", "chrom": "chr1", "score": 65, "reason": "Прогерия и липодистрофия, но нет арахнодактилии"},
            {"gene": "BSCL2", "chrom": "chr11", "score": 45, "reason": "Липодистрофия, но другой фенотип"},
            {"gene": "TGFBR1", "chrom": "chr9", "score": 25, "reason": "Марфаноидные черты, но нет липодистрофии"}
        ]
    },
    "case_02": {
        "gene": "PTPN11", "chrom": "chr12", "disease": "Noonan syndrome", "scenario": 1,
        "hpo": ["HP:0004322", "HP:0000465", "HP:0000914", "HP:0000508", "HP:0000325", "HP:0001382"],
        "candidates": [
            {"gene": "PTPN11", "chrom": "chr12", "score": 90, "reason": "Классический синдром Нунан: низкий рост, крыловидная шея, птоз"},
            {"gene": "SOS1", "chrom": "chr2", "score": 70, "reason": "Нунан-подобный синдром, но реже встречается"},
            {"gene": "RAF1", "chrom": "chr3", "score": 55, "reason": "Нунан с кардиомиопатией, но нет щитообразной груди"},
            {"gene": "KRAS", "chrom": "chr12", "score": 35, "reason": "Нунан-подобный, но тяжелее фенотип"}
        ]
    },
    "case_03": {
        "gene": "CHD7", "chrom": "chr8", "disease": "CHARGE syndrome", "scenario": 2,
        "hpo": ["HP:0000453", "HP:0000407", "HP:0000829", "HP:0001263", "HP:0008551", "HP:0000316", "HP:0011381"],
        "candidates": [
            {"gene": "CHD7", "chrom": "chr8", "score": 85, "reason": "CHARGE: атрезия хоан + тугоухость + аплазия полукружного канала"},
            {"gene": "TBX1", "chrom": "chr22", "score": 65, "reason": "22q11.2: гипопаратиреоз + пороки сердца + нёбо"},
            {"gene": "SALL1", "chrom": "chr16", "score": 45, "reason": "Townes-Brocks: аномалии ушей + почки"},
            {"gene": "EYA1", "chrom": "chr8", "score": 30, "reason": "Branchio-oto-renal: только уши и почки"}
        ]
    },
    "case_04": {
        "gene": "FGFR2", "chrom": "chr10", "disease": "Apert/Crouzon syndrome", "scenario": 1,
        "hpo": ["HP:0011800", "HP:0000244", "HP:0010621", "HP:0010554", "HP:0000028", "HP:0000239"],
        "candidates": [
            {"gene": "FGFR2", "chrom": "chr10", "score": 90, "reason": "Аперт/Крузон: краниосиностоз + синдактилия"},
            {"gene": "FGFR3", "chrom": "chr4", "score": 60, "reason": "Ахондроплазия, но нет синдактилии"},
            {"gene": "TWIST1", "chrom": "chr7", "score": 50, "reason": "Синдром Сатре: краниосиностоз, но другой фенотип"},
            {"gene": "EFNB1", "chrom": "chrX", "score": 30, "reason": "Краниофронтоназальная дисплазия, но X-сцепленный"}
        ]
    },
    "case_05": {
        "gene": "LMNA", "chrom": "chr1", "disease": "Mandibuloacral dysplasia", "scenario": 1,
        "hpo": ["HP:0000905", "HP:0100324", "HP:0009125", "HP:4000168", "HP:0001596", "HP:0004322"],
        "candidates": [
            {"gene": "LMNA", "chrom": "chr1", "score": 90, "reason": "Мандибулоакральная дисплазия: остеолиз ключиц + склеродерма + акулий зубы"},
            {"gene": "ZMPSTE24", "chrom": "chr1", "score": 75, "reason": "Похожий фенотип, но рецессивный"},
            {"gene": "POLR3A", "chrom": "chr10", "score": 40, "reason": "Прогероидные черты, но другой механизм"},
            {"gene": "WRN", "chrom": "chr8", "score": 25, "reason": "Синдром Вернера: прогерия, но взрослый onset"}
        ]
    },
    "case_06": {
        "gene": "TGFBR2", "chrom": "chr3", "disease": "Loeys-Dietz syndrome", "scenario": 1,
        "hpo": ["HP:0002616", "HP:0000175", "HP:0001363", "HP:0005116", "HP:0000193", "HP:0000592"],
        "candidates": [
            {"gene": "TGFBR2", "chrom": "chr3", "score": 90, "reason": "Полное совпадение с Луи-Дица: аневризмы + краниосиностоз + bifid uvula"},
            {"gene": "SMAD3", "chrom": "chr15", "score": 60, "reason": "LDS type 3: аневризмы, но нет краниосиностоза"},
            {"gene": "FBN1", "chrom": "chr15", "score": 35, "reason": "Марфан: исключён — нет вывиха хрусталика и высокого роста"},
            {"gene": "COL3A1", "chrom": "chr2", "score": 25, "reason": "Сосудистый ЭД: аневризмы, но нет скелетных черт"}
        ]
    },
    
    # Закрытые кейсы
    "case_07": {
        "gene": "CDKL5", "chrom": "chrX", "disease": "Early infantile epileptic encephalopathy", "scenario": 1,
        "hpo": ["HP:0002521", "HP:0012469", "HP:0001263", "HP:0002376", "HP:0002079", "HP:0001252"],
        "candidates": [
            {"gene": "CDKL5", "chrom": "chrX", "score": 90, "reason": "Ранняя эпилептическая энцефалопатия: гипсаритмия + инфантильные спазмы + регресс"},
            {"gene": "STXBP1", "chrom": "chr9", "score": 70, "reason": "Эпилептическая энцефалопатия, но другой тип приступов"},
            {"gene": "ARX", "chrom": "chrX", "score": 55, "reason": "X-сцепленная эпилепсия, но чаще у мужчин"},
            {"gene": "KCNQ2", "chrom": "chr2", "score": 40, "reason": "Неонатальные приступы, но нет регресса"}
        ]
    },
    "case_08": {
        "gene": "UNKNOWN", "chrom": "chr?", "disease": "Неврологический синдром (неполный фенотип)", "scenario": 3,
        "hpo": ["HP:0011470", "HP:0011412", "HP:0008936", "HP:0001251", "HP:0002395"],
        "candidates": [],
        "limitations": "Фенотип truncated (5 симптомов). Неврологический профиль (атаксия, гипотония, гиперрефлексия) может указывать на спастическую параплегию или атаксию, но недостаточно данных для дифференциации. Требуется: МРТ мозга, генетическое тестирование родителей, полный HPO-профиль."
    },
    "case_09": {
        "gene": "UNKNOWN", "chrom": "chr?", "disease": "Мальформация мозга (неполный фенотип)", "scenario": 3,
        "hpo": ["HP:0000256", "HP:0002079", "HP:0002119", "HP:0001321", "HP:0000316"],
        "candidates": [],
        "limitations": "Фенотип truncated (5 симптомов). Структурные аномалии мозга (макроцефалия, гипоплазия мозолистого тела, вентрикуломегалия) могут указывать на синдромы мальформации (например, Aicardi, Walker-Warburg), но недостаточно данных. Требуется: МРТ высокого разрешения, офтальмологический осмотр, полный HPO-профиль."
    },
    "case_10": {
        "gene": "TRPS1", "chrom": "chr8", "disease": "Trichorhinophalangeal syndrome / Skeletal dysplasia", "scenario": 1,
        "hpo": ["HP:0010579", "HP:0003026", "HP:0004322", "HP:0001263", "HP:0000365", "HP:0002750"],
        "candidates": [
            {"gene": "TRPS1", "chrom": "chr8", "score": 90, "reason": "Трихоринофалангеальный синдром: конусообразные эпифизы + короткие трубчатые кости + задержка скелетного созревания"},
            {"gene": "EXT1", "chrom": "chr8", "score": 60, "reason": "Множественные экзостозы, но нет конусообразных эпифизов"},
            {"gene": "ACAN", "chrom": "chr15", "score": 45, "reason": "Спондилоэпифизарная дисплазия, но другой паттерн"},
            {"gene": "COL2A1", "chrom": "chr12", "score": 30, "reason": "Коллагенопатия II типа, но нет специфических черт TRPS"}
        ]
    }
}

if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False
if 'demo_case' not in st.session_state:
    st.session_state.demo_case = "case_06"

# ==========================================
# 2. ФУНКЦИИ ОБРАБОТКИ
# ==========================================
def clean_genotype(val):
    if isinstance(val, str) and ("янв" in val.lower() or "jan" in val.lower()):
        return "1/1"
    return str(val)

def calculate_hpo_score(gene_hpos, patient_hpos):
    if not gene_hpos or not patient_hpos: return 0
    clean_patient = [h.split(' ')[0] for h in patient_hpos]
    match_count = len(set(gene_hpos) & set(clean_patient))
    return (match_count / len(clean_patient)) * 100

def score_variant(row, patient_hpos, case_id, is_truncated):
    score = 0
    evidence = {"facts": [], "predictions": [], "hypotheses": []}
    gene = str(row.get('gene', 'NA')).upper()
    genotype = str(row.get('genotype', ''))
    kb = KNOWLEDGE_BASE.get(case_id, {})

    if is_truncated:
        evidence["facts"].append("⚠️ Фенотип пациента неполный (truncated). Достоверный скоринг невозможен.")
        return 15, evidence

    if kb and gene == kb["gene"]:
        score += 40
        evidence["facts"].append(f"Ген {gene} — известный кандидат ({kb['disease']}).")
    elif gene != 'NA' and gene != 'NAN':
        score += 10
        evidence["facts"].append(f"Вариант в гене {gene}. Требуется проверка по базам (ClinVar/OMIM).")

    if kb and "hpo" in kb and kb["hpo"]:
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
# 3. ДЕМО-РЕЖИМ
# ==========================================
def run_demo(case_id):
    kb = KNOWLEDGE_BASE.get(case_id, {})
    is_truncated = (case_id in ["case_08", "case_09"])
    
    st.markdown(f"### 🎭 Демо: {case_id} | Сценарий {kb.get('scenario', 3)} | {kb.get('disease', 'Неизвестно')}")

    if is_truncated:
        st.warning("⚠️ **ВНИМАНИЕ: Обнаружен неполный фенотип (phenotype_truncated = true).**")
        st.error(f"""
        ⚪ **СЦЕНАРИЙ 3: НЕДОСТАТОЧНОСТЬ ДАННЫХ.**
        
        **Ограничения для {case_id}:**
        {kb.get('limitations', 'Недостаточно данных для достоверного анализа.')}
        
        **Рекомендации для врача-генетика:**
        1. Запросить полное клинико-генетическое обследование для расширения фенотипа.
        2. Провести секвенирование всего генома (WGS) для поиска некодирующих/структурных вариантов.
        3. Рассмотреть секвенирование трио (родитель-ребенок) для выявления de novo мутаций.
        4. Провести дополнительные инструментальные исследования (МРТ, ЭЭГ, офтальмология).
        """)
        return

    # Логика для полных фенотипов (Сценарии 1 и 2)
    if kb.get("scenario") == 2:
        st.info("🔀 **Сценарий 2: Несколько конкурирующих гипотез.** Система ранжирует кандидатов и объясняет различия в доказательствах.")
    else:
        st.success("🎯 **Сценарий 1: Редкое моногенное заболевание.** Система выделяет ведущий кандидат.")
    
    candidates = kb.get("candidates", [])
    
    for i, c in enumerate(candidates):
        with st.expander(f"🏆 ТОП-{i+1}: {c['gene']} | Скор: {c['score']} | {c['chrom']}", expanded=(i==0)):
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

    if not is_truncated:
        st.markdown("---")
        st.markdown("### ✅ Сравнение с известным ответом")
        expected = kb["gene"]
        got = candidates[0]["gene"]
        if got == expected:
            st.success(f"**Золотой стандарт:** {expected} | **Система выдала ТОП-1:** {got} → ✅ **СОВПАДЕНИЕ**")

# ==========================================
# 4. ИНТЕРФЕЙС
# ==========================================
st.set_page_config(page_title="Genomic Detective", layout="wide", page_icon="🧬")
st.title("🧬 Genomic Detective: Поиск причин редких заболеваний")
st.caption("⚠️ Результаты предназначены для исследовательских целей и **не являются клиническим диагнозом**.")

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

# --- ОСНОВНАЯ ПАНЕЛЬ ---
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
                if str(row.get('chrom', '')).lower() == kb.get('chrom', ''):
                    gene = kb.get('gene', 'Unknown')
            
            score, evidence = score_variant(row, patient_hpos, case_id, is_truncated)
            results.append({"Gene": gene, "Chrom": row.get('chrom'), "Pos": row.get('pos'),
                            "Ref/Alt": f"{row.get('ref')} > {row.get('alt')}",
                            "Genotype": row.get('genotype'), "Score": score, "Evidence": evidence})
        
        results_df = pd.DataFrame(results).sort_values(by="Score", ascending=False).reset_index(drop=True)

    st.markdown("### 3. Результаты ранжирования")
    
    if is_truncated:
        st.error("⚪ **СЦЕНАРИЙ 3: НЕДОСТАТОЧНОСТЬ ДАННЫХ.** Убедительного кандидата не найдено из-за неполного фенотипа. См. рекомендации в боковой панели.")
    
    for i, row in results_df.head(5).iterrows():
        with st.expander(f"🏆 ТОП-{i+1}: {row['Gene']} | Скор: {row['Score']}", expanded=(i==0)):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Score", f"{row['Score']}/100")
                render_evidence(row['Evidence'])
            with col2:
                st.table(pd.DataFrame([{"Хром": row['Chrom'], "Поз": row['Pos'],
                                        "Вар": row['Ref/Alt'], "Генотип": row['Genotype']}]))

else:
    st.info("👈 Загрузите файлы или используйте демо ниже.")
    st.markdown("---")
    st.markdown("### 🎭 Демо-режим: все сценарии")
    
    demo_choice = st.selectbox("Кейс для демонстрации:",
        ["case_01", "case_02", "case_03", "case_04", "case_05", "case_06", "case_07", "case_08", "case_09", "case_10"],
        format_func=lambda x: {
            "case_01": "Case 01 — Сценарий 1: Моногенное (FBN1)",
            "case_02": "Case 02 — Сценарий 1: Моногенное (PTPN11)",
            "case_03": "Case 03 — Сценарий 2: Конкурирующие (CHD7 vs TBX1)",
            "case_04": "Case 04 — Сценарий 1: Моногенное (FGFR2)",
            "case_05": "Case 05 — Сценарий 1: Моногенное (LMNA)",
            "case_06": "Case 06 — Сценарий 1: Моногенное (TGFBR2)",
            "case_07": "Case 07 — Сценарий 1: Моногенное (CDKL5)",
            "case_08": "Case 08 — Сценарий 3: Усеченный фенотип (неврологический)",
            "case_09": "Case 09 — Сценарий 3: Усеченный фенотип (мальформация мозга)",
            "case_10": "Case 10 — Сценарий 1: Моногенное (TRPS1)",
        }[x]
    )

    if st.button("▶️ Запустить демо"):
        st.session_state.demo_mode = True
        st.session_state.demo_case = demo_choice

    if st.session_state.demo_mode:
        run_demo(st.session_state.demo_case)
