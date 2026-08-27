import duckdb
import re
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from config.settings import *
from validation.sql_guard import validate_sql

def extract_sql_from_response(response: str) -> str:
    """Extrahiert SQL aus einer Antwort, die möglicherweise Text vor/nach SQL enthält"""
    response = response.strip()
    
    # Entferne Markdown-Formatierung
    if "```sql" in response.lower():
        # Extrahiere SQL aus ```sql ... ```
        match = re.search(r'```sql\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    elif "```" in response:
        # Extrahiere aus ``` ... ```
        match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # Suche nach SQL-Keywords im Text (nicht nur am Zeilenanfang)
    sql_keywords = ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE']
    
    # Suche nach dem ersten Vorkommen eines SQL-Keywords
    response_upper = response.upper()
    sql_start_pos = None
    sql_keyword = None
    
    for keyword in sql_keywords:
        pos = response_upper.find(keyword)
        if pos != -1 and (sql_start_pos is None or pos < sql_start_pos):
            sql_start_pos = pos
            sql_keyword = keyword
    
    if sql_start_pos is not None:
        # Extrahiere alles ab dem SQL-Keyword
        sql_text = response[sql_start_pos:]
        
        # Finde das Ende der SQL-Query (erste Zeile die nicht mit SQL-Syntax übereinstimmt)
        lines = sql_text.split('\n')
        sql_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Wenn die Zeile mit einem SQL-Keyword beginnt oder SQL-Syntax enthält, füge sie hinzu
            line_upper = line_stripped.upper()
            is_sql = (
                any(line_upper.startswith(kw) for kw in sql_keywords) or
                any(kw in line_upper for kw in ['FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'UNION', 'AS']) or
                ';' in line_stripped or
                '(' in line_stripped or ')' in line_stripped
            )
            
            if is_sql or len(sql_lines) > 0:  # Wenn wir schon SQL-Linien haben, füge weitere hinzu
                sql_lines.append(line_stripped)
                # Wenn die Zeile mit ; endet, ist das wahrscheinlich das Ende
                if line_stripped.rstrip().endswith(';'):
                    break
            else:
                # Wenn wir noch keine SQL-Linien haben und diese Zeile nicht SQL ist, überspringe sie
                continue
        
        if sql_lines:
            return ' '.join(sql_lines).strip()
    
    # Falls kein SQL gefunden wird, versuche die gesamte Antwort (könnte nur SQL sein)
    return response

class DuckDBWrapper:
    """Wrapper für DuckDB, der die SQLDatabase-API nachahmt"""
    
    def __init__(self, db_path):
        self.conn = duckdb.connect(db_path)
        self._table_info = None
    
    def get_table_info(self):
        """Holt Tabelleninformationen direkt aus DuckDB"""
        if self._table_info is None:
            # Hole alle Tabellennamen
            tables = self.conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
            ).fetchall()
            
            table_info_parts = []
            for (table_name,) in tables:
                # Hole Spalteninformationen für jede Tabelle
                columns = self.conn.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND table_schema = 'main'
                    ORDER BY ordinal_position
                """).fetchall()
                
                column_defs = [f"{col[0]} ({col[1]})" for col in columns]
                table_info_parts.append(f"Table: {table_name}\nColumns: {', '.join(column_defs)}")
            
            self._table_info = "\n\n".join(table_info_parts)
        
        return self._table_info
    
    def run(self, query):
        """Führt eine SQL-Query aus und gibt das Ergebnis zurück"""
        result = self.conn.execute(query).fetchall()
        # Konvertiere zu einem lesbaren String
        if not result:
            return "No results found."
        
        # Formatiere Ergebnis
        if len(result) == 1 and len(result[0]) == 1:
            return str(result[0][0])
        else:
            return "\n".join([str(row) for row in result])
    
    def close(self):
        """Schließt die Datenbankverbindung"""
        self.conn.close()

def build_nl_to_sql_chain():
    # Debug: Zeige den verwendeten Endpoint
    print(f"🔍 Verwende Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"🔍 Deployment: {AZURE_OPENAI_DEPLOYMENT}")
    print(f"🔍 API Version: {AZURE_OPENAI_API_VERSION}")
    
    llm = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        deployment_name=AZURE_OPENAI_DEPLOYMENT,
        api_version=AZURE_OPENAI_API_VERSION,
        temperature=0
    )

    db = DuckDBWrapper(DB_PATH)
    
    # Prompt für SQL-Generierung
    sql_prompt = PromptTemplate.from_template("""
You are a SQL expert. Given the following table schemas, write ONLY a SQL SELECT query to answer the user's question.
Do NOT include any explanations, comments, or text before or after the SQL query.
Return ONLY the SQL query, nothing else.

Table schemas:
{table_info}

Question: {input}

Return ONLY the SQL query:""")
    
    # Chain die SQL generiert und ausführt
    def execute_query(inputs):
        if isinstance(inputs, str):
            question = inputs
        else:
            question = inputs.get("question", inputs.get("input", ""))
        
        # Generiere SQL Query
        table_info = db.get_table_info()
        prompt = sql_prompt.format(table_info=table_info, input=question)
        response = llm.invoke(prompt).content.strip()
        
        # Debug: Zeige die rohe Antwort (kann später entfernt werden)
        print(f"\n🔍 LLM Antwort (roh): {response[:200]}...")
        
        # Extrahiere SQL aus der Antwort (kann Text vor/nach SQL enthalten)
        query = extract_sql_from_response(response)

        # Debug: Zeige die extrahierte Query
        print(f"🔍 Extrahierte SQL Query: {query[:200]}...")

        # Guardrail VOR der Ausfuehrung. Der Prompt verlangt SELECT, aber ein
        # Prompt ist eine Bitte, keine Kontrolle -- erzwungen wird es hier.
        # validate_sql wirft bei allem, was nicht genau ein SELECT ist, und
        # ergaenzt sonst ein LIMIT.
        safe_query = validate_sql(query)

        result = db.run(safe_query)
        return {
            "result": result,
            "intermediate_steps": [safe_query]
        }
    
    chain = RunnablePassthrough() | execute_query
    return chain

