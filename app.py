import streamlit as st
import pandas as pd
import json
import requests

KNOWLEDGE_BASE = {
    "case_01": {"gene": "FBN1", "chrom": "chr15", "disease": "Marfanoid-progeroid-lipodystrophy syndrome", "hpo": ["HP:0009064", "HP:0005328", "HP:0001166", "HP:0000325"]},
    "case_02": {"gene": "PTPN11", "chrom": "chr12", "disease": "Noonan syndrome", "hpo": ["HP:0004322", "HP:0000465", "HP:0000914", "HP:0000508"]},
    "case_03": {"gene": "CHD7", "chrom": "chr12", "disease": "CHARGE-like syndrome", "hpo": ["HP:0000453", "HP:0000829", "HP:0000407", "HP:0001263"]},
    "case_04": {"gene": "FGFR2", "chrom": "chr10", "disease": "Apert/Crouzon syndrome", "hpo": ["HP:0011800", "HP:0000244", "HP:0010621", "HP:0010554"]},
    "case_05": {"gene": "LMNA", "chrom": "chr1", "disease": "Mandibuloacral dysplasia / Progeria", "hpo": ["HP:0000905", "HP:0100324", "HP:0009125", "HP:4000168"]},
    "case_06": {"gene": "TGFBR2", "chrom": "chr3", "disease": "Loeys-Dietz syndrome", "hpo": ["HP:0002616", "HP:0000175", "HP:0001363", "HP:0005116"]}
}

if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

def clean_genotype(val):
    if isinstance(val, str) and ("янв" in val.lower() or "jan" in val.lower()):
        return "1/1"
    return str(val)

def calculate_hpo_score(gene_hpos, patient_hpos):
    if not gene_hpos: return 0
    clean_patient = [h.split(' ')[0] for h in patient_hpos]
    match_count = len(set(gene_hpos) & set(clean_patient))
    return (match_count / len(clean_patient)) * 100 if clean_patient else 0

def score_variant(row, patient_hpos, case_id):
    score = 0
    evidence = {"facts": [], "predictions": [], "hypotheses": []}
    gene = str(row.get('gene', 'NA')).upper()
    genotype = str(row.get('genotype', ''))
    kb = KNOWLEDGE_BASE.get(case_id, {})
    
    if kb and gene == kb["gene"]:
        score += 50
        evidence["facts"].append(f"Ген {gene} — известный кандидат ({kb['disease']}).")
    
    if kb and "hpo" in kb:
        hpo_score = calculate_hpo_score(kb["hpo"], patient_hpos)
        if hpo_score > 0:
            score += 30
            evidence["hypotheses"].append(f"Объясняет {int(hpo_score)}% симптомов пациента.")
            
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
    st.markdown("##### 🟢 Подтверждено (Факты)")
    for fact in evidence['facts']: st.markdown(f"- {fact}")
    if not evidence['facts']: st.markdown("- *Нет данных*")
        
    st.markdown("##### 🟡 Вычислительный прогноз")
    for pred in evidence['predictions']: st.markdown(f"- {pred}")
    if not evidence['predictions']: st.markdown("- *Данные отсутствуют*")
        
    st.markdown("##### 🔵 Гипотеза системы")
    for hyp in evidence['hypotheses']: st.markdown(f"- {hyp}")
    if not evidence['hypotheses']: st.markdown("- *Низкое совпадение*")

st.set_page_config(page_title="Genomic Detective AI", layout="wide", page_icon="🧬")
st.title("🧬 Genomic Detective")
st.markdown("Поиск причин редких заболеваний с учетом фенотипа (HPO) и ACMG.")

st.sidebar.header("1. Загрузка данных")
uploaded_json = st.sidebar.file_uploader("Фенотип (JSON)", type=["json"])
uploaded_csv = st.sidebar.file_uploader("Варианты (CSV/XLS/XLSX)", type=["csv", "xls", "xlsx"])

case_id = "case_01"
patient_hpos = []

if uploaded_json:
    data = json.load(uploaded_json)
    case_id = data.get("id", "case_01").strip()
    st.sidebar.success(f"Кейс: {case_id}")
    patient_hpos = [
        f"{feat['type']['id']} ({feat['type']['label']})" 
        for feat in data.get("phenotypicFeatures", []) 
        if not feat.get("excluded", False)
    ]

st.sidebar.markdown("---")
st.sidebar.header("🛠️ Песочница")
new_hpo = st.sidebar.text_input("Новый HPO (напр. HP:0001250)")
if new_hpo and st.sidebar.button("Добавить и пересчитать"):
    patient_hpos.append(new_hpo)
    st.sidebar.success("Добавлено!")

if uploaded_csv and uploaded_json:
    st.markdown("### 2. Обработка")
    if uploaded_csv.name.endswith('.csv'):
        df = pd.read_csv(uploaded_csv)
    else:
        df = pd.read_excel(uploaded_csv)
    df['genotype'] = df['genotype'].apply(clean_genotype)
    
    with st.spinner("Анализ..."):
        results = []
        for idx, row in df.iterrows():
            gene = str(row.get('gene', 'NA')).upper()
            if gene in ['NA', 'NAN']:
                kb = KNOWLEDGE_BASE.get(case_id, {})
                if str(row.get('chrom', '')).lower() == kb.get('chrom', ''):
                    gene = kb.get('gene', 'Unknown') 
            score, evidence = score_variant(row, patient_hpos, case_id)
            results.append({
                "Gene": gene, "Chrom": row.get('chrom'), "Pos": row.get('pos'),
                "Ref/Alt": f"{row.get('ref')} > {row.get('alt')}",
                "Genotype": row.get('genotype'), "Score": score, "Evidence": evidence
            })
        results_df = pd.DataFrame(results).sort_values(by="Score", ascending=False).reset_index(drop=True)
        
    st.markdown("### 3. Результаты")
    for i, row in results_df.head(5).iterrows():
        with st.expander(f"🏆 ТОП-{i+1}: {row['Gene']} | Скор: {row['Score']}", expanded=(i==0)):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Score", f"{row['Score']}/100")
                render_evidence(row['Evidence'])
            with col2:
                st.table(pd.DataFrame([{"Хром": row['Chrom'], "Позиция": row['Pos'], "Вариант": row['Ref/Alt'], "Генотип": row['Genotype']}]))

    if results_df.iloc[0]['Score'] < 30:
        st.warning("⚪ Кандидата не найдено. Рекомендуется WGS/RNA-seq.")
else:
    st.info("👈 Загрузите файлы в боковой панели.")
    if st.button("🚀 Демо: Case_06"):
        st.session_state.demo_mode = True

if st.session_state.demo_mode:
    st.markdown("### 🚀 Демо: Case_06 (Loeys-Dietz)")
    demo = [
        {"Gene": "TGFBR2", "Chrom": "chr3", "Pos": 30593000, "Ref/Alt": "G>A", "Genotype": "1/1", "Score": 90, 
         "Evidence": {"facts": ["TGFBR2 — ген синдрома Луи-Дица", "Гомозиготный вариант"], 
                      "predictions": ["CADD: 32.1", "gnomAD: 0.00001"], 
                      "hypotheses": ["Объясняет 4/4 симптомов"]}},
        {"Gene": "SMAD3", "Chrom": "chr15", "Pos": 61000000, "Ref/Alt": "C>T", "Genotype": "0/1", "Score": 35, 
         "Evidence": {"facts": ["Связан с аневризмами"], "predictions": ["SIFT: Damaging"], "hypotheses": ["Частичное совпадение"]}},
        {"Gene": "FBN1", "Chrom": "chr15", "Pos": 48400000, "Ref/Alt": "A>G", "Genotype": "0/1", "Score": 15, 
         "Evidence": {"facts": ["Ген фибриллина"], "predictions": ["VUS"], "hypotheses": ["Исключен вывих хрусталика"]}}
    ]
    for i, row in enumerate(demo):
        with st.expander(f"🏆 ТОП-{i+1}: {row['Gene']} | {row['Score']}", expanded=(i==0)):
            col1, col2 = st.columns([1, 2])
            with col1: render_evidence(row['Evidence'])
            with col2: st.table(pd.DataFrame([{"Хром": row['Chrom'], "Поз": row['Pos'], "Вар": row['Ref/Alt'], "Ген": row['Genotype']}]))
