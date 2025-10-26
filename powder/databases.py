from connections.db import db_local
import pandas as pd


def load_all_tables_from_db():
        conn = db_local()
        if conn is None:
            print("⚠️ Não foi possível conectar ao banco.")
            return {}

        dataframes = {}
        try:
            query = """
            SELECT TABLE_SCHEMA, TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE';
            """
            tables = pd.read_sql(query, conn)

            for _, row in tables.iterrows():
                schema = row["TABLE_SCHEMA"]
                table = row["TABLE_NAME"]
                full_table_name = f"{schema}.{table}"

                try:
                    df = pd.read_sql(f"SELECT * FROM {full_table_name};", conn)
                    dataframes[table] = df
                    print(f"✅ {full_table_name} carregada ({len(df)} linhas, {len(df.columns)} colunas)")
                except Exception as e:
                    print(f"⚠️ Falha ao carregar {full_table_name}: {e}")

            conn.close()
        except Exception as e:
            print(f"❌ Erro ao listar tabelas: {e}")

        print(f"\n📊 Total de tabelas carregadas: {len(dataframes)}")
        return dataframes

def describe_tables(self):
        """Gera uma descrição textual das tabelas e suas colunas"""
        description = ""
        for name, df in self.dataframes.items():
            columns = ", ".join(df.columns[:15])  # mostra as primeiras 15 colunas
            description += f"Tabela '{name}' contém colunas: {columns}.\n"
        return description

def table_relationships(self):
    """Lê as relações entre tabelas (foreign keys) diretamente do banco de dados"""
    conn = db_local()
    if conn is None:
        print("⚠️ Não foi possível conectar ao banco.")
        return {}

    try:
        query = """
        SELECT
            fk.name AS FK_Name,
            tp.name AS ParentTable,
            cp.name AS ParentColumn,
            tr.name AS ReferencedTable,
            cr.name AS ReferencedColumn
        FROM sys.foreign_keys fk
        INNER JOIN sys.foreign_key_columns fkc
            ON fkc.constraint_object_id = fk.object_id
        INNER JOIN sys.tables tp
            ON fkc.parent_object_id = tp.object_id
        INNER JOIN sys.columns cp
            ON fkc.parent_object_id = cp.object_id
            AND fkc.parent_column_id = cp.column_id
        INNER JOIN sys.tables tr
            ON fkc.referenced_object_id = tr.object_id
        INNER JOIN sys.columns cr
            ON fkc.referenced_object_id = cr.object_id
            AND fkc.referenced_column_id = cr.column_id
        ORDER BY tp.name, tr.name;
        """

        df_rel = pd.read_sql(query, conn)
        conn.close()

        relationships = {}
        for _, row in df_rel.iterrows():
            parent = row["ParentTable"]
            referenced = row["ReferencedTable"]
            parent_col = row["ParentColumn"]
            ref_col = row["ReferencedColumn"]

            if parent not in relationships:
                relationships[parent] = {"relations": {}}

            relationships[parent]["relations"][parent_col] = f"{referenced}.{ref_col}"

        print(f"🔗 {len(df_rel)} relações encontradas entre tabelas.")
        return relationships

    except Exception as e:
        print(f"❌ Erro ao ler relações do banco: {e}")
        return {}