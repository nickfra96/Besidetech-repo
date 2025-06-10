# Besidetech


# 🧑‍💻 Besidetech - Estrazione Criteri da Excel e Documenti (PDF/DOCX/XLSX)

Questa repository contiene **due script principali** per l’estrazione e la strutturazione di criteri, requisiti o punti di valutazione da file Excel e da documenti in PDF, Word, o Excel tramite interfaccia web (Streamlit).
Estrazione “manuale” (basata su pattern), sia una “semantica” tramite intelligenza artificiale.

---

## 🟢 Script 1: Estrazione criteri da Excel con Streamlit

**File principale:**
`excel_criteria_extractor.py`

### **Funzionalità**

* Carica file **Excel** (`.xls`, `.xlsx`) tramite interfaccia Streamlit
* Mostra i fogli disponibili e permette la selezione
* Permette di scegliere una **colonna** e l’intervallo di righe su cui lavorare
* Analizza le celle della colonna e **estrae i criteri** (rileva pattern come `A1`, `CRITERIO X`, `B2.3` ecc.)
* Permette di **selezionare i codici da esportare**
* Mostra un’anteprima del risultato in **JSON**
* Permette di **scaricare il JSON** estratto

### **Tecnologie principali**

* `streamlit`
* `openpyxl`
* `re` (regex Python)
* `json`

### **Utilizzo rapido**

```bash
pip install streamlit openpyxl
streamlit run excel_criteria_extractor.py
```

---

## 🟠 Script 2: Estrazione semantica di criteri da PDF, Word, Excel tramite OpenAI

**File principale:**
`semantic_criteria_extractor.py`

### **Funzionalità**

* Carica documenti in formato **PDF**, **Word DOCX**, **Excel**
* Estrae il testo dai documenti, mostrando una preview
* Utilizza il modello **OpenAI GPT-4o-mini** per **identificare e strutturare automaticamente criteri/requisiti anche se non sono esplicitamente codificati**
* Supporta identificazione di:

  * Codici espliciti (es. “A1”, “Art. 2”, ecc.)
  * Titoli di sezione significativi
  * Criteri “inferiti” da frasi/paragrafi centrali
* L’utente può scaricare il risultato come **JSON** (`criterio_id` e `descrizione`)
* Supporta file di grandi dimensioni (finestra di contesto modello permettendo)
* Tutta l’analisi avviene via interfaccia Streamlit **locale**: i file non vengono mai caricati su server esterni (eccetto l’estratto di testo inviato a OpenAI, se si usa quella funzione)

### **Tecnologie principali**

* `streamlit`
* `openai`
* `PyPDF2`
* `pandas`
* `docx` (`python-docx`)
* `json`

### **Utilizzo rapido**

```bash
pip install streamlit openai PyPDF2 pandas python-docx
streamlit run semantic_criteria_extractor.py
```

---

## 📊 **Output JSON - Formato atteso**

```json
[
  {
    "criterio_id": "A1",
    "descrizione": "Testo descrittivo del criterio A1..."
  }
]
```

---

## 📝 **Note**

* Per usare la versione AI serve una API Key OpenAI valida.
* I pattern di riconoscimento sono personalizzabili nei regex all’inizio degli script.
