from chains.nl_to_sql import build_nl_to_sql_chain
from chains.sql_to_text import explain_result
from config.settings import *  # Lädt und validiert die Konfiguration

def main():
    print("🚀 NLQ-to-SQL System gestartet!")
    print("=" * 50)
    
    try:
        chain = build_nl_to_sql_chain()
        question = input("\nAsk a business question: ")

        print("\n⏳ Verarbeite Frage...")
        response = chain.invoke({"question": question})

        # Bereits in der Chain validiert -- vor der Ausfuehrung, nicht danach.
        safe_sql = response["intermediate_steps"][0]
        result = response["result"]

        explanation = explain_result(
    question=question,
    sql_query=safe_sql,
    result=result
)


        print("\n" + "=" * 50)
        print("📊 SQL Query:")
        print("-" * 50)
        print(safe_sql)
        print("\n💡 Explanation:")
        print("-" * 50)
        print(explanation)
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        raise

if __name__ == "__main__":
    main()

