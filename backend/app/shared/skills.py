# Canonical skill name -> list of aliases (all lowercase)
# Used by both parser (extraction) and insights (overlap computation)
SKILL_ALIASES = {
    # ── Data / AI / ML ──────────────────────────────────────────────────────
    "machine learning":     ["machine learning", "ml model", "supervised learning", "unsupervised learning"],
    "deep learning":        ["deep learning", "neural network", "neural networks"],
    "nlp":                  ["nlp", "natural language processing", "text mining", "text analytics"],
    "computer vision":      ["computer vision", "image recognition", "object detection"],
    "data science":         ["data science", "data scientist"],
    "data analysis":        ["data analysis", "data analyst", "data analytics", "eda", "exploratory data analysis"],
    "data visualization":   ["data visualization", "data viz", "tableau", "power bi", "powerbi", "looker", "matplotlib", "seaborn", "plotly"],
    "statistics":           ["statistics", "statistical analysis", "statistical modeling", "hypothesis testing"],
    "feature engineering":  ["feature engineering", "feature selection"],
    "model deployment":     ["model deployment", "mlops", "model serving"],
    "time series":          ["time series", "forecasting", "arima"],
    "llm":                  ["llm", "large language model", "gpt", "bert", "transformers", "huggingface"],
    "a/b testing":          ["a/b testing", "ab testing", "split testing"],
    # ── Python ecosystem ────────────────────────────────────────────────────
    "python":               ["python"],
    "pandas":               ["pandas"],
    "numpy":                ["numpy"],
    "scikit-learn":         ["scikit-learn", "sklearn", "scikit learn"],
    "tensorflow":           ["tensorflow"],
    "keras":                ["keras"],
    "pytorch":              ["pytorch"],
    "xgboost":              ["xgboost", "lightgbm", "gradient boosting"],
    "scipy":                ["scipy"],
    "jupyter":              ["jupyter"],
    # ── Databases ───────────────────────────────────────────────────────────
    "sql":                  ["sql", "mysql", "postgresql", "postgres", "sqlite"],
    "nosql":                ["mongodb", "cassandra", "dynamodb", "nosql"],
    # ── Big Data / Infra ────────────────────────────────────────────────────
    "spark":                ["spark", "pyspark", "apache spark"],
    "hadoop":               ["hadoop", "hive", "hdfs"],
    "kafka":                ["kafka"],
    "airflow":              ["airflow", "luigi"],
    # ── Cloud ───────────────────────────────────────────────────────────────
    "aws":                  ["aws", "amazon web services", "sagemaker"],
    "azure":                ["azure", "microsoft azure"],
    "gcp":                  ["gcp", "google cloud", "bigquery", "dataflow"],
    # ── DevOps ──────────────────────────────────────────────────────────────
    "docker":               ["docker"],
    "kubernetes":           ["kubernetes", "k8s"],
    "git":                  ["git", "github", "gitlab"],
    "linux":                ["linux", "unix", "bash", "shell scripting"],
    "ci/cd":                ["ci/cd", "jenkins", "github actions"],
    "devops":               ["devops"],
    "mlflow":               ["mlflow"],
    # ── Web / Frontend ──────────────────────────────────────────────────────
    "javascript":           ["javascript"],
    "typescript":           ["typescript"],
    "react":                ["react", "reactjs"],
    "vue":                  ["vue", "vuejs"],
    "angular":              ["angular"],
    "api":                  ["rest api", "restful api", "fastapi", "flask", "django"],
    # ── Other languages ─────────────────────────────────────────────────────
    "java":                 ["java"],
    "scala":                ["scala"],
    "r":                    ["r programming", "rstudio", "tidyverse"],
    # ── Productivity ────────────────────────────────────────────────────────
    "excel":                ["excel", "spreadsheet"],
    "power bi":             ["power bi", "powerbi"],
    "tableau":              ["tableau"],
    "reinforcement learning": ["reinforcement learning"],
    # ── Civil Engineering ────────────────────────────────────────────────────
    "civil engineering":    ["civil engineering", "civil engineer"],
    "structural engineering": ["structural engineering", "structural engineer", "structural analysis", "structural design"],
    "autocad":              ["autocad", "auto cad", "cad design", "cad drafting"],
    "staad pro":            ["staad pro", "staad.pro", "staad"],
    "etabs":                ["etabs"],
    "revit":                ["revit", "revit structure", "revit architecture"],
    "construction management": ["construction management", "site management", "site engineer", "construction site"],
    "project management":   ["project management", "project planning", "project scheduling", "ms project"],
    "surveying":            ["surveying", "land surveying", "topographic survey"],
    "geotechnical":         ["geotechnical", "soil mechanics", "foundation design", "geotechnical engineering"],
    "highway engineering":  ["highway engineering", "road design", "pavement design", "highway design"],
    "water resources":      ["water resources", "hydraulics", "hydrology", "irrigation engineering"],
    "concrete design":      ["concrete design", "rcc design", "reinforced concrete", "concrete structures"],
    "steel design":         ["steel design", "steel structures", "structural steel"],
    "quantity surveying":   ["quantity surveying", "bill of quantities", "boq", "cost estimation"],
    "primavera":            ["primavera", "p6", "oracle primavera"],
    "building codes":       ["building codes", "is codes", "aci codes", "eurocode", "nbc"],
    # ── Mechanical Engineering ───────────────────────────────────────────────
    "mechanical engineering": ["mechanical engineering", "mechanical engineer"],
    "solidworks":           ["solidworks", "solid works"],
    "ansys":                ["ansys", "fea", "finite element analysis"],
    "catia":                ["catia"],
    "manufacturing":        ["manufacturing", "production engineering", "cnc", "machining"],
    "thermodynamics":       ["thermodynamics", "heat transfer", "fluid mechanics"],
    # ── Electrical Engineering ───────────────────────────────────────────────
    "electrical engineering": ["electrical engineering", "electrical engineer"],
    "plc":                  ["plc", "scada", "dcs", "automation"],
    "power systems":        ["power systems", "power electronics", "electrical power"],
    "circuit design":       ["circuit design", "pcb design", "embedded systems"],
    # ── Healthcare / Medical ─────────────────────────────────────────────────
    "clinical":             ["clinical", "clinical research", "clinical trials"],
    "medical":              ["medical", "healthcare", "patient care"],
    "nursing":              ["nursing", "registered nurse", "rn"],
    "pharmacy":             ["pharmacy", "pharmacology", "pharmaceutical"],
    # ── Finance / Accounting ─────────────────────────────────────────────────
    "accounting":           ["accounting", "bookkeeping", "accounts"],
    "financial analysis":   ["financial analysis", "financial modeling", "valuation"],
    "tally":                ["tally", "tally erp"],
    "sap":                  ["sap", "sap fi", "sap mm", "sap sd"],
    # ── Marketing ────────────────────────────────────────────────────────────
    "digital marketing":    ["digital marketing", "online marketing", "performance marketing"],
    "seo":                  ["seo", "search engine optimization"],
    "social media":         ["social media", "social media marketing", "smm"],
    "content marketing":    ["content marketing", "content writing", "copywriting"],
    # ── Education / Teaching ─────────────────────────────────────────────────
    "teaching":             ["teaching", "teacher", "instructor", "educator", "lecturer"],
    "curriculum":           ["curriculum", "curriculum development", "lesson planning"],
    # ── Legal ────────────────────────────────────────────────────────────────
    "legal":                ["legal", "law", "litigation", "contract law"],
    "compliance":           ["compliance", "regulatory compliance"],
    # ── Design / UX ──────────────────────────────────────────────────────────
    "ux design":            ["ux design", "ui design", "user experience", "user interface", "figma", "sketch", "adobe xd"],
    "graphic design":       ["graphic design", "adobe photoshop", "illustrator", "indesign"],
}

# Domain keywords for job title matching
# Maps domain keywords → related terms found in resumes
DOMAIN_KEYWORDS = {
    "civil engineer":       ["civil", "structural", "construction", "autocad", "site engineer"],
    "mechanical engineer":  ["mechanical", "solidworks", "manufacturing", "thermodynamics"],
    "electrical engineer":  ["electrical", "plc", "power systems", "circuit"],
    "software engineer":    ["software", "programming", "developer", "coding"],
    "data scientist":       ["data science", "machine learning", "python", "statistics"],
    "data engineer":        ["data engineering", "spark", "airflow", "pipeline"],
    "devops engineer":      ["devops", "docker", "kubernetes", "ci/cd"],
    "doctor":               ["medical", "clinical", "mbbs", "physician", "hospital"],
    "teacher":              ["teaching", "education", "curriculum", "school"],
    "marketing manager":    ["marketing", "digital marketing", "seo", "brand"],
    "ux designer":          ["ux design", "ui design", "figma", "user experience"],
    "lawyer":               ["legal", "law", "litigation", "attorney"],
    "accountant":           ["accounting", "finance", "tally", "audit"],
}
